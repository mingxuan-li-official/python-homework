"""
诊断脚本：测试 server 和 client 是否能正常启动
"""
import sys
import traceback

print("=" * 60)
print("启动诊断测试")
print("=" * 60)
print()

# 测试 1: 检查数据库连接
print("【测试 1】检查数据库连接...")
try:
    from database import Database
    db = Database()
    print("[OK] 数据库连接成功")
except Exception as e:
    print(f"[ERROR] 数据库连接失败: {e}")
    print("   提示: 请确保 MySQL 服务已启动，并且 config.py 中的配置正确")
    print()
    sys.exit(1)

print()

# 测试 2: 检查 server 启动
print("【测试 2】检查 server 模块导入...")
try:
    from server import LibraryServer
    print("[OK] server 模块导入成功")
except Exception as e:
    print(f"[ERROR] server 模块导入失败: {e}")
    traceback.print_exc()
    sys.exit(1)

print()

# 测试 3: 检查 GUI 模块导入
print("【测试 3】检查 GUI 模块导入...")
try:
    from gui_login import LoginWindow
    print("[OK] GUI 模块导入成功")
except Exception as e:
    print(f"[ERROR] GUI 模块导入失败: {e}")
    traceback.print_exc()
    sys.exit(1)

print()

# 测试 4: 检查主题模块
print("【测试 4】检查主题模块...")
try:
    from ui_theme import PRIMARY_COLOR
    print("[OK] 主题模块导入成功")
except Exception as e:
    print(f"[ERROR] 主题模块导入失败: {e}")
    traceback.print_exc()
    sys.exit(1)

print()

# 测试 5: 检查图片文件
print("【测试 5】检查背景图片...")
import os
base_dir = os.path.dirname(os.path.abspath(__file__))
assets_dir = os.path.join(base_dir, "assets")
candidates = ["image.png", "image copy.png", "image copy 2.png", "image copy 3.png"]
found_images = []
for name in candidates:
    path = os.path.join(assets_dir, name)
    if os.path.exists(path):
        size = os.path.getsize(path) / 1024 / 1024  # MB
        found_images.append((name, size))
        print(f"   找到: {name} ({size:.2f} MB)")

if found_images:
    print(f"[OK] 找到 {len(found_images)} 张背景图片")
else:
    print("[WARN] 未找到背景图片，将使用纯色背景")

print()
print("=" * 60)
print("诊断完成！如果所有测试都通过，应该可以正常启动")
print("=" * 60)
print()
print("使用说明：")
print("1. 先运行 server.py 启动服务器")
print("2. 然后运行 main.py 启动客户端 GUI")
print("3. 如果 server 启动失败，请检查 MySQL 配置")
print("4. 如果 main.py 无响应，可能是图片太大，可以临时移除 assets 目录")

