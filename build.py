#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
LexiSage 打包脚本
将项目文件打包成 .ankiaddon 格式供用户安装
"""

import os
import json
import zipfile
from datetime import datetime

# 读取版本信息
with open("manifest.json", "r", encoding="utf-8") as f:
    manifest = json.load(f)
    version = manifest["version"]
    package_name = manifest["package"]

# 文件白名单 - 只有这些文件和文件夹会被打包
whitelist = [
    "__init__.py",
    "config_ui.py",
    "ai_service.py",
    "prompts.py",
    "manifest.json",
    "meta.json",
    "config.json",
    "ankiweb.json"
]

# 清理并创建dist目录
dist_dir = "dist"
if os.path.exists(dist_dir):
    import shutil
    shutil.rmtree(dist_dir)
os.makedirs(dist_dir)

# 输出文件名
output_filename = f"{dist_dir}/{package_name}.ankiaddon"

# 创建zip文件
with zipfile.ZipFile(output_filename, "w", zipfile.ZIP_DEFLATED) as zf:
    for item in whitelist:
        if os.path.isfile(item):
            zf.write(item)
        elif os.path.isdir(item):
            for root, dirs, files in os.walk(item):
                for file in files:
                    if file.endswith(".py") or file.endswith(".json"):
                        zf.write(os.path.join(root, file))

print(f"打包完成！")
print(f"创建了文件: {output_filename}")
print(f"版本: {version}")
