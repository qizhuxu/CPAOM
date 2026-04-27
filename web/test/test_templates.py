#!/usr/bin/env python3
"""测试模板文件是否正确"""

import os
from jinja2 import Environment, FileSystemLoader

# 设置模板目录（从 test/ 目录向上一级到 web/，再进入 templates/）
template_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')
env = Environment(loader=FileSystemLoader(template_dir))

print(f"模板目录: {template_dir}")
print(f"模板目录存在: {os.path.exists(template_dir)}")
print()

# 列出所有模板
print("可用的模板文件:")
for root, dirs, files in os.walk(template_dir):
    for file in files:
        if file.endswith('.html'):
            rel_path = os.path.relpath(os.path.join(root, file), template_dir)
            print(f"  - {rel_path}")
print()

# 测试加载 dashboard.html
try:
    print("测试加载 dashboard.html...")
    template = env.get_template('dashboard.html')
    print("✅ dashboard.html 加载成功")
    
    # 读取第一行
    with open(os.path.join(template_dir, 'dashboard.html'), 'r', encoding='utf-8') as f:
        first_line = f.readline().strip()
        print(f"第一行内容: {first_line}")
except Exception as e:
    print(f"❌ 加载失败: {e}")
print()

# 测试加载 base.html
try:
    print("测试加载 base.html...")
    template = env.get_template('base.html')
    print("✅ base.html 加载成功")
except Exception as e:
    print(f"❌ 加载失败: {e}")
