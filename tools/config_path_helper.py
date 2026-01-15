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
    # 允许通过环境变量显式指定配置目录（优先级最高）
    # 例如：GELAB_CONFIG_DIR=/path/to/configs
    env_config_dir = os.environ.get("GELAB_CONFIG_DIR")

    candidate_dirs: list[Path] = []
    if env_config_dir:
        candidate_dirs.append(Path(env_config_dir).expanduser())

    # PyInstaller 打包环境
    if getattr(sys, "frozen", False):
        # 1) 优先使用可执行文件同目录（便于用户直接修改配置并覆盖内置配置）
        try:
            candidate_dirs.append(Path(sys.executable).resolve().parent)
        except Exception:
            pass

        # 2) 其次使用 PyInstaller 的解包目录（onefile/onedir 都可能存在）
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            candidate_dirs.append(Path(meipass))
    else:
        # 开发环境：配置文件在项目根目录（tools/..）
        current_file = Path(__file__).resolve()
        candidate_dirs.append(current_file.parent.parent)

    # 3) 最后兜底：当前工作目录（某些启动方式会把配置放在 cwd）
    candidate_dirs.append(Path.cwd())

    # 去重（保序）
    seen: set[str] = set()
    unique_dirs: list[Path] = []
    for d in candidate_dirs:
        key = str(d)
        if key not in seen:
            seen.add(key)
            unique_dirs.append(d)

    for base_dir in unique_dirs:
        config_path = base_dir / config_filename
        if config_path.exists():
            return str(config_path)

    # 如果都找不到，返回一个“最可能”的路径，方便上层报错时更可读
    if unique_dirs:
        return str(unique_dirs[0] / config_filename)
    return config_filename

