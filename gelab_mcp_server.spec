# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for GELab-Zero MCP Server
打包 gelab-zero MCP 服务器为可执行文件
"""

import os
import site
from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files, copy_metadata

# 尝试禁用 PyInstaller 的 hook 自动发现功能（解决 Windows 访问冲突问题）
try:
    # 设置环境变量
    os.environ['PYINSTALLER_DISABLE_HOOK_DISCOVERY'] = '1'
    # 尝试 monkey patch PyInstaller 的 hook 发现功能
    try:
        import PyInstaller.building.build_main
        # 如果可能，禁用 hook 发现
        if hasattr(PyInstaller.building.build_main, 'discover_hook_directories'):
            original_discover = PyInstaller.building.build_main.discover_hook_directories
            def patched_discover():
                return []  # 返回空列表，禁用所有 hook 发现
            PyInstaller.building.build_main.discover_hook_directories = patched_discover
    except (ImportError, AttributeError):
        pass
except Exception:
    pass  # 如果失败，继续执行

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

# 添加 opentelemetry 元数据（避免 PyInstaller 丢失 entry_points 导致 StopIteration）
try:
    datas_list += collect_data_files('opentelemetry_api')
except Exception:
    try:
        datas_list += collect_data_files('opentelemetry')
    except Exception:
        pass

try:
    datas_list += collect_data_files('opentelemetry_sdk')
except Exception:
    try:
        datas_list += collect_data_files('opentelemetry.sdk')
    except Exception:
        pass

# 明确复制元数据以支持 importlib_metadata.version 查询
for _pkg_meta in ['opentelemetry-sdk', 'opentelemetry-api', 'opentelemetry-exporter-prometheus']:
    try:
        datas_list += copy_metadata(_pkg_meta)
    except Exception:
        pass

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

# 尝试添加 jsonschema_specifications 的数据文件（schemas 目录）
try:
    import jsonschema_specifications
    jsonschema_spec_path = Path(jsonschema_specifications.__file__).parent
    schemas_dir = jsonschema_spec_path / 'schemas'
    
    if schemas_dir.exists() and schemas_dir.is_dir():
        print(f"✓ 找到 jsonschema_specifications schemas 目录: {schemas_dir}")
        
        # 收集所有 schemas 目录下的文件，保持目录结构
        for schema_file in schemas_dir.rglob('*'):
            if schema_file.is_file():
                rel_path = schema_file.relative_to(schemas_dir)
                # 如果文件在根目录，直接放在 schemas 下；否则保持子目录结构
                if rel_path.parent == Path('.'):
                    datas_list.append((str(schema_file), 'jsonschema_specifications/schemas'))
                else:
                    datas_list.append((str(schema_file), f'jsonschema_specifications/schemas/{rel_path.parent}'))
        print(f"✓ 已添加 jsonschema_specifications schemas 文件")
except Exception as e:
    print(f"⚠️  无法自动添加 jsonschema_specifications 数据文件: {e}")
    # 如果自动查找失败，尝试从 site-packages 查找
    try:
        for site_pkg in site.getsitepackages():
            jsonschema_spec_path = Path(site_pkg) / 'jsonschema_specifications'
            if jsonschema_spec_path.exists():
                schemas_dir = jsonschema_spec_path / 'schemas'
                if schemas_dir.exists() and schemas_dir.is_dir():
                    print(f"✓ 从 site-packages 找到 jsonschema_specifications schemas 目录: {schemas_dir}")
                    # 收集所有文件
                    for schema_file in schemas_dir.rglob('*'):
                        if schema_file.is_file():
                            rel_path = schema_file.relative_to(schemas_dir)
                            if rel_path.parent == Path('.'):
                                datas_list.append((str(schema_file), 'jsonschema_specifications/schemas'))
                            else:
                                datas_list.append((str(schema_file), f'jsonschema_specifications/schemas/{rel_path.parent}'))
                    break
    except Exception:
        pass

# 分析主程序
# 注意：在 Windows 上，某些 C 扩展库（如 lupa）可能导致访问冲突
# 如果遇到 SubprocessDiedError，尝试：
# 1. 升级 PyInstaller: pip install --upgrade pyinstaller
# 2. 使用 --onedir 模式而不是 --onefile
# 3. 检查 lupa 版本兼容性
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
        'importlib_metadata',
        'importlib_metadata.version',
        'importlib_metadata._collections',
        'importlib.metadata',
        'importlib.metadata.version',
        # docket 和 fakeredis 相关（fastmcp 的依赖）
        'docket',
        'docket.docket',
        'docket._redis',
        'docket.agenda',
        'fakeredis',
        'fakeredis.commands_mixins',
        'fakeredis.commands_mixins.scripting_mixin',
        # opentelemetry 相关（docket 的依赖）
        'opentelemetry',
        'opentelemetry.trace',
        'opentelemetry.trace.__init__',
        'opentelemetry.context',
        'opentelemetry.context.__init__',
        'opentelemetry.context.contextvars_context',
        'opentelemetry.propagate',
        'opentelemetry.trace.propagation.tracecontext',
        # anyio 后端（asyncio 用于 uvicorn/fastapi 运行）
        'anyio',
        'anyio._backends',
        'anyio._backends._asyncio',
        # lupa 相关（fakeredis 的依赖，包含 C 扩展）
        'lupa',
        'lupa.lua51',
        'lupa._lupa',
        # jsonschema 相关（mcp 的依赖）
        'jsonschema',
        'jsonschema.validators',
        'jsonschema.exceptions',
        'jsonschema_specifications',
        'jsonschema_specifications._core',
        'referencing',
        'referencing._core',
        # 加入 cffi/cryptography 相关以确保 _cffi_backend 被打包
        'cffi',
        'cffi.backend_ctypes',
        '_cffi_backend',
        'cryptography',
        'cryptography.hazmat',
        'cryptography.hazmat.primitives',
        'cryptography.hazmat.primitives.hashes',
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
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.http.h11_impl',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.protocols.websockets.wsproto_impl',
        'uvicorn.lifespan.off',
        'uvicorn.lifespan.on',
        'uvicorn.loops.auto',
        'uvicorn.loops.asyncio',
        'chardet',
        'charset_normalizer',
        # 项目内部模块
        'copilot_agent_server',
        'copilot_agent_client',
        'copilot_front_end',
        'tools',
        'mcp_server',
        # 运行时补丁
        'runtime_patch',
        # 其他可能需要的模块
        'multiprocessing',
        'base64',
        'io',
        'uuid',
        'time',
        'json',
    ],
    hookspath=[str(project_root)],  # 使用项目根目录的 hook 文件（避免自动发现导致的 Windows 访问冲突）
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'scipy',
        'numpy.distutils',
        'tkinter',
        # 排除可能导致问题的模块
        'IPython',
        'jupyter',
        'notebook',
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
    name='gelab-mcp-server',  # 构建脚本会自动修改为包含架构的名称（Windows 上会添加 .exe）
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

