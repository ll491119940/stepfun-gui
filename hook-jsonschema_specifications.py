# PyInstaller hook for jsonschema_specifications
# jsonschema_specifications 需要包含 schemas 目录下的数据文件

from PyInstaller.utils.hooks import collect_data_files, collect_submodules
import os
from pathlib import Path

# 收集 jsonschema_specifications 的所有子模块
hiddenimports = collect_submodules('jsonschema_specifications')

# 收集 jsonschema_specifications 的数据文件（特别是 schemas 目录）
try:
    import jsonschema_specifications
    jsonschema_spec_path = Path(jsonschema_specifications.__file__).parent
    schemas_dir = jsonschema_spec_path / 'schemas'
    
    if schemas_dir.exists() and schemas_dir.is_dir():
        # 收集 schemas 目录下的所有文件
        datas = []
        for schema_file in schemas_dir.rglob('*'):
            if schema_file.is_file():
                rel_path = schema_file.relative_to(schemas_dir)
                # 保持目录结构
                datas.append((str(schema_file), f'jsonschema_specifications/schemas/{rel_path.parent}'))
        
        # 如果没有找到文件，至少添加目录本身
        if not datas:
            datas.append((str(schemas_dir), 'jsonschema_specifications/schemas'))
    else:
        # 如果 schemas 目录不存在，尝试使用 collect_data_files
        try:
            datas = collect_data_files('jsonschema_specifications', includes=['*.json', '*.yaml', '*.yml'])
        except Exception:
            datas = []
except Exception as e:
    # 如果导入失败，尝试从 site-packages 查找
    datas = []
    try:
        import site
        for site_pkg in site.getsitepackages():
            jsonschema_spec_path = Path(site_pkg) / 'jsonschema_specifications'
            if jsonschema_spec_path.exists():
                schemas_dir = jsonschema_spec_path / 'schemas'
                if schemas_dir.exists() and schemas_dir.is_dir():
                    for schema_file in schemas_dir.rglob('*'):
                        if schema_file.is_file():
                            rel_path = schema_file.relative_to(schemas_dir)
                            datas.append((str(schema_file), f'jsonschema_specifications/schemas/{rel_path.parent}'))
                    break
    except Exception:
        pass

# 也收集 referencing 模块（jsonschema_specifications 的依赖）
try:
    hiddenimports.extend(collect_submodules('referencing'))
except Exception:
    pass

