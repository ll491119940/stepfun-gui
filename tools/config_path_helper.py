"""
配置文件路径辅助工具
处理 PyInstaller 打包后的配置文件路径问题
"""
import os
import sys
from pathlib import Path


def get_config_path(config_filename: str) -> str:
    """
    获取配置文件的路径，兼容开发环境和 PyInstaller 打包环境
    
    Args:
        config_filename: 配置文件名，如 "model_config.yaml"
    
    Returns:
        配置文件的完整路径
    """
    # 检查是否在 PyInstaller 打包环境中
    if getattr(sys, 'frozen', False):
        # 打包环境：配置文件在 sys._MEIPASS 中
        base_path = sys._MEIPASS
    else:
        # 开发环境：配置文件在项目根目录
        # 尝试从当前文件位置推断项目根目录
        current_file = Path(__file__).resolve()
        # tools/config_path_helper.py -> 项目根目录
        base_path = current_file.parent.parent
    
    config_path = os.path.join(base_path, config_filename)
    
    # 如果文件不存在，尝试在当前工作目录查找（作为后备方案）
    if not os.path.exists(config_path):
        fallback_path = os.path.join(os.getcwd(), config_filename)
        if os.path.exists(fallback_path):
            return fallback_path
    
    return config_path

