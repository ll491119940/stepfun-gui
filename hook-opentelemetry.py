# PyInstaller hook for opentelemetry
# opentelemetry 需要包含上下文相关的模块

from PyInstaller.utils.hooks import collect_submodules, collect_data_files
import os
from pathlib import Path

# 收集 opentelemetry 的所有子模块
hiddenimports = collect_submodules('opentelemetry')

# 特别添加上下文相关的模块（Windows 上容易出问题）
hiddenimports.extend([
    'opentelemetry.context',
    'opentelemetry.context.__init__',
    'opentelemetry.context.contextvars_context',
    'opentelemetry.context.threadlocal_context',
    'opentelemetry.trace',
    'opentelemetry.trace.__init__',
    'opentelemetry.trace.propagation',
    'opentelemetry.trace.propagation.tracecontext',
])

# 收集 opentelemetry 的数据文件
try:
    datas = collect_data_files('opentelemetry', includes=['*.json', '*.yaml', '*.yml', '*.txt'])
except Exception:
    datas = []

