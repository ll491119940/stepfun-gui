"""
运行时补丁：修复 PyInstaller 打包后 fastmcp 无法读取版本信息的问题
在导入 fastmcp 之前执行此补丁
"""
import sys
import os

# 检查是否在 PyInstaller 打包环境中
if getattr(sys, 'frozen', False):
    # 在打包环境中，尝试修复 importlib.metadata 的版本查找
    
    # 方法1: 尝试从环境变量或硬编码版本
    try:
        import importlib.metadata
        
        # 如果 fastmcp 的版本查找失败，提供一个默认值
        original_version = importlib.metadata.version
        
        def patched_version(package_name):
            try:
                return original_version(package_name)
            except importlib.metadata.PackageNotFoundError:
                # 如果找不到包元数据，返回一个默认版本
                if package_name == 'fastmcp':
                    # 尝试从环境变量获取，或使用默认值
                    return os.environ.get('FASTMCP_VERSION', '2.14.2')
                raise
        
        # 替换 version 函数
        importlib.metadata.version = patched_version
        
    except Exception:
        pass

