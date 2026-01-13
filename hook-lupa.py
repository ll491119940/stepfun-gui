# PyInstaller hook for lupa
# lupa 是一个包含 C 扩展的包，需要特殊处理

from PyInstaller.utils.hooks import collect_all, collect_submodules, collect_data_files
import os

# 收集 lupa 的所有子模块
hiddenimports = collect_submodules('lupa')

# 尝试收集 lupa 的二进制文件和数据文件
try:
    datas, binaries, hiddenimports_lupa = collect_all('lupa')
    hiddenimports.extend(hiddenimports_lupa)
except Exception:
    pass

# 特别添加 lupa.lua51 模块
hiddenimports.append('lupa.lua51')
hiddenimports.append('lupa._lupa')

