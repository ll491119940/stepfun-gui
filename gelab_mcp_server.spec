# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for GELab-Zero MCP Server
打包 gelab-zero MCP 服务器为可执行文件
"""

import os
import site
from pathlib import Path

block_cipher = None

# 获取项目根目录（spec 文件所在目录）
try:
    # PyInstaller 会设置 SPECPATH
    project_root = Path(SPECPATH).parent
except NameError:
    # 如果不在 PyInstaller 环境中，使用当前文件所在目录
    project_root = Path(__file__).parent if '__file__' in globals() else Path.cwd()

# 准备 datas 列表
datas_list = [
    # 配置文件
    ('mcp_server_config.yaml', '.'),
    ('model_config.yaml', '.'),
    # Python 模块目录
    ('copilot_agent_server', 'copilot_agent_server'),
    ('copilot_agent_client', 'copilot_agent_client'),
    ('copilot_front_end', 'copilot_front_end'),
    ('copilot_tools', 'copilot_tools'),
    ('tools', 'tools'),
    ('mcp_server', 'mcp_server'),
]

# 尝试添加 fakeredis 的数据文件（commands.json）
try:
    import fakeredis
    fakeredis_path = Path(fakeredis.__file__).parent
    commands_json = fakeredis_path / 'model' / 'commands.json'
    
    if commands_json.exists():
        # 添加到 datas，保持目录结构
        datas_list.append((str(commands_json), 'fakeredis/model'))
        print(f"✓ 找到 fakeredis commands.json: {commands_json}")
    
    # 也尝试收集所有 fakeredis 的数据文件
    for data_file in fakeredis_path.rglob('*.json'):
        if data_file.is_file():
            rel_path = data_file.relative_to(fakeredis_path)
            datas_list.append((str(data_file), f'fakeredis/{rel_path.parent}'))
except Exception as e:
    print(f"⚠️  无法自动添加 fakeredis 数据文件: {e}")
    # 如果自动查找失败，尝试从 site-packages 查找
    try:
        for site_pkg in site.getsitepackages():
            fakeredis_path = Path(site_pkg) / 'fakeredis'
            if fakeredis_path.exists():
                commands_json = fakeredis_path / 'model' / 'commands.json'
                if commands_json.exists():
                    datas_list.append((str(commands_json), 'fakeredis/model'))
                    print(f"✓ 从 site-packages 找到 fakeredis commands.json: {commands_json}")
                    break
    except Exception:
        pass

# 分析主程序
a = Analysis(
    ['mcp_server/simple_gelab_mcp_server_withcaption.py'],
    pathex=[str(project_root)],
    binaries=[],
    datas=datas_list,
    hiddenimports=[
        # FastMCP 相关
        'fastmcp',
        'fastmcp.server',
        'fastmcp.tools',
        'importlib.metadata',
        'importlib.metadata.version',
        # docket 和 fakeredis 相关（fastmcp 的依赖）
        'docket',
        'docket.docket',
        'docket._redis',
        'fakeredis',
        'fakeredis.commands_mixins',
        'fakeredis.commands_mixins.scripting_mixin',
        # lupa 相关（fakeredis 的依赖，包含 C 扩展）
        'lupa',
        'lupa.lua51',
        'lupa._lupa',
        # 核心依赖
        'yaml',
        'pydantic',
        'PIL',
        'PIL.Image',
        'opencv-python',
        'cv2',
        'megfile',
        'jsonlines',
        'pandas',
        'openpyxl',
        'streamlit',
        'tqdm',
        'requests',
        'pymongo',
        'openai',
        'fastapi',
        'uvicorn',
        # 项目内部模块
        'copilot_agent_server',
        'copilot_agent_client',
        'copilot_front_end',
        'tools',
        'mcp_server',
        # 其他可能需要的模块
        'multiprocessing',
        'base64',
        'io',
        'uuid',
        'time',
        'json',
    ],
    hookspath=['.'],  # 使用当前目录的 hook 文件（hook-lupa.py, hook-fakeredis.py）
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'scipy',
        'numpy.distutils',
        'tkinter',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='gelab-mcp-server-arm64',  # 构建脚本会自动修改为包含架构的名称
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # 显示控制台窗口，方便查看日志
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

