"""
从 Open Library 获取书籍数据并写入到本地数据库的脚本。

使用方法:
    python openlibrary_import.py --count 1000 --query "subject:fiction"
"""

from __future__ import annotations

import argparse
import logging
import sys
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import requests

from database import Database
from models import BookModel

BASE_URL = "https://openlibrary.org/search.json"
MAX_RETRIES = 3
REQUEST_TIMEOUT = 20


@dataclass
class BookPayload:
    """保存清洗后的书籍字段。"""

    title: str
    author: str
    isbn: str
    category: str
    publisher: str
    publish_date: str
    total_copies: int


class OpenLibraryImporter:
    """负责从 Open Library 拉取并写入数据库。"""

    def __init__(self, db: Database, copies: int) -> None:
        self.db = db
        self.book_model = BookModel(db)
        self.default_copies = copies

    def import_books(
        self,
        query: str,
        target_count: int,
        batch_size: int,
        delay: float,
    ) -> Tuple[int, int]:
        """批量导入书籍，返回 (成功数量, 跳过数量)。"""
        stored = 0
        skipped = 0
        page = 1
        seen_isbns: set[str] = set()
        seen_titles: set[Tuple[str, str]] = set()

        logging.info(
            "开始导入 Open Library 书籍，目标: %s 本，查询: %s",
            target_count,
            query,
        )

        while stored < target_count:
            docs = self._fetch_batch(query=query, page=page, limit=batch_size)
            if not docs:
                logging.warning("第 %s 页无数据，提前结束。", page)
                break

            for doc in docs:
                if stored >= target_count:
                    break

                payload = self._build_payload(doc)
                if payload is None:
                    skipped += 1
                    continue

                if payload.isbn in seen_isbns:
                    skipped += 1
                    continue

                title_author = (payload.title, payload.author)
                if title_author in seen_titles:
                    skipped += 1
                    continue

                if payload.isbn and self._book_exists_by_isbn(payload.isbn):
                    skipped += 1
                    continue

                if self._book_exists_by_title_author(*title_author):
                    skipped += 1
                    continue

                success = self.book_model.add_book(
                    title=payload.title,
                    author=payload.author,
                    isbn=payload.isbn,
                    category=payload.category,
                    publisher=payload.publisher,
                    publish_date=payload.publish_date,
                    total_copies=payload.total_copies,
                )
                if success:
                    stored += 1
                    seen_isbns.add(payload.isbn)
                    seen_titles.add(title_author)
                    if stored % 50 == 0 or stored == target_count:
                        logging.info("已导入 %s/%s 本书。", stored, target_count)
                else:
                    skipped += 1

            page += 1
            time.sleep(delay)

        logging.info("导入结束: 成功 %s 本，跳过 %s 本。", stored, skipped)
        return stored, skipped

    def _fetch_batch(self, query: str, page: int, limit: int) -> List[Dict]:
        """请求 Open Library Search API。"""
        params = {"q": query, "page": page, "limit": limit}
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                response = requests.get(
                    BASE_URL,
                    params=params,
                    timeout=REQUEST_TIMEOUT,
                )
                response.raise_for_status()
                data = response.json()
                docs = data.get("docs", [])
                logging.debug(
                    "第 %s 页获取 %s 条记录 (尝试 %s/%s)。",
                    page,
                    len(docs),
                    attempt,
                    MAX_RETRIES,
                )
                return docs
            except requests.RequestException as exc:
                logging.warning(
                    "请求失败 (第 %s 次尝试/共 %s 次): %s",
                    attempt,
                    MAX_RETRIES,
                    exc,
                )
                time.sleep(1.5 * attempt)
        logging.error("无法从 Open Library 获取数据 (page=%s)。", page)
        return []

    def _fetch_work_details(self, work_key: str) -> Optional[Dict]:
        """通过作品 key 获取详细信息，用于提取 subjects。"""
        if not work_key:
            return None
        
        # 移除开头的 /works/ 或 /books/
        clean_key = work_key.lstrip('/')
        url = f"https://openlibrary.org/{clean_key}.json"
        
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                response = requests.get(url, timeout=REQUEST_TIMEOUT)
                response.raise_for_status()
                return response.json()
            except requests.RequestException as exc:
                logging.debug(
                    "获取作品详细信息失败 (尝试 %s/%s, key=%s): %s",
                    attempt,
                    MAX_RETRIES,
                    work_key,
                    exc,
                )
                if attempt < MAX_RETRIES:
                    time.sleep(0.5 * attempt)
                continue
        logging.warning("无法获取作品详细信息 (key=%s)，将使用默认分类", work_key)
        return None

    def _build_payload(self, doc: Dict) -> Optional[BookPayload]:
        """将 Open Library 文档转换成数据库需要的字段。"""
        title = (doc.get("title") or doc.get("title_suggest") or "").strip()
        if not title:
            return None
        title = title[:200]

        authors = doc.get("author_name") or []
        author = ", ".join(authors).strip() or "Unknown"
        author = author[:100]

        isbn = self._pick_isbn(doc)
        if not isbn:
            return None

        # 从作品详细信息中获取 subjects
        # 搜索 API 不返回 subject 字段，需要通过作品 key 获取详细信息
        category = "Unknown"
        work_key = doc.get("key")
        if work_key:
            work_details = self._fetch_work_details(work_key)
            if work_details:
                subjects = work_details.get("subjects") or []
                # 处理 subjects 可能是字符串、列表或其他类型的情况
                if subjects:
                    if isinstance(subjects, str):
                        subjects = [subjects]
                    elif not isinstance(subjects, list):
                        subjects = [str(subjects)]
                    
                    # subjects 是字符串列表，用逗号连接，最多保留前50个字符
                    category = ", ".join(str(s) for s in subjects)
                    category = category[:50]
                    logging.debug("提取到分类: %s (来源: %s)", category, work_key)
                else:
                    logging.debug("作品 %s 没有 subjects 信息", work_key)
            else:
                logging.debug("无法获取作品 %s 的详细信息", work_key)

        publishers = doc.get("publisher") or []
        publisher = publishers[0] if publishers else "Open Library"
        publisher = publisher[:100]

        publish_date = self._choose_publish_date(doc)
        copies = self.default_copies if self.default_copies > 0 else 1

        return BookPayload(
            title=title,
            author=author,
            isbn=isbn,
            category=category,
            publisher=publisher,
            publish_date=publish_date,
            total_copies=copies,
        )

    def _pick_isbn(self, doc: Dict) -> str:
        """优先选择13位 ISBN，其次10位，最后 fallback 到作品 key。"""
        isbn_candidates = doc.get("isbn") or []
        prioritized: List[str] = sorted(
            isbn_candidates,
            key=lambda value: 0 if len(value.replace("-", "")) == 13 else 1,
        )
        for raw in prioritized:
            cleaned = raw.replace("-", "").strip()
            if 9 < len(cleaned) <= 20:
                return cleaned[:20]

        key = doc.get("key")
        if not key:
            return ""
        fallback = key.replace("/works/", "").replace("/books/", "")
        return (fallback[:18] + "OL") if len(fallback) > 18 else f"{fallback}OL"

    def _choose_publish_date(self, doc: Dict) -> str:
        """格式化出版日期为 YYYY-MM-DD，缺省时使用 1900-01-01。"""
        year = doc.get("first_publish_year")
        if isinstance(year, int) and 0 < year < 3000:
            return f"{year}-01-01"

        publish_dates = doc.get("publish_date") or []
        for value in publish_dates:
            digits = "".join(ch for ch in value if ch.isdigit())
            if len(digits) >= 4:
                detected_year = int(digits[:4])
                if 0 < detected_year < 3000:
                    return f"{detected_year}-01-01"
        return "1900-01-01"

    def _book_exists_by_isbn(self, isbn: str) -> bool:
        """检查数据库中 ISBN 是否已存在。"""
        if not isbn:
            return False
        result = self.db.execute_query("SELECT id FROM books WHERE isbn = ?", (isbn,))
        return bool(result)

    def _book_exists_by_title_author(self, title: str, author: str) -> bool:
        """基于标题 + 作者检测重复。"""
        result = self.db.execute_query(
            "SELECT id FROM books WHERE title = ? AND author = ? LIMIT 1",
            (title, author),
        )
        return bool(result)


def parse_args(argv: List[str]) -> argparse.Namespace:
    """命令行参数解析。"""
    parser = argparse.ArgumentParser(
        description="从 Open Library 导入书籍记录到本地数据库。"
    )
    parser.add_argument(
        "--count",
        type=int,
        default=1000,
        help="需要导入的书籍数量，默认 1000。",
    )
    parser.add_argument(
        "--query",
        type=str,
        default="subject:fiction",
        help="Open Library 搜索查询参数，默认为 subject:fiction。",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=100,
        help="每次请求获取的记录数 (1-100)，默认 100。",
    )
    parser.add_argument(
        "--copies",
        type=int,
        default=3,
        help="为每本书设置的馆藏数量，默认 3 本。",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.5,
        help="每页请求之间的延时（秒），默认 0.5。",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="输出调试日志。",
    )
    return parser.parse_args(argv)


def configure_logging(verbose: bool) -> None:
    """配置日志格式。"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )


def main(argv: Optional[List[str]] = None) -> None:
    """脚本入口。"""
    args = parse_args(argv or sys.argv[1:])
    configure_logging(args.verbose)

    batch_size = max(1, min(args.batch_size, 100))
    total = max(1, args.count)

    db = Database()
    importer = OpenLibraryImporter(db=db, copies=args.copies)
    stored, skipped = importer.import_books(
        query=args.query,
        target_count=total,
        batch_size=batch_size,
        delay=max(0.1, args.delay),
    )
    logging.info("完成导入: 成功 %s，跳过 %s。", stored, skipped)


if __name__ == "__main__":
    main()


