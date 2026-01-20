# PyInstaller hook for fastmcp
# 解决打包后 fastmcp 无法读取版本信息的问题

from PyInstaller.utils.hooks import copy_metadata

# 收集 fastmcp 的元数据
datas = copy_metadata('fastmcp')
