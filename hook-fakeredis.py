# PyInstaller hook for fakeredis
# fakeredis 需要包含数据文件（如 commands.json）

from PyInstaller.utils.hooks import collect_data_files, collect_submodules, collect_all
import os

# 收集 fakeredis 的所有子模块
hiddenimports = collect_submodules('fakeredis')

# 收集 fakeredis 的所有数据文件和二进制文件
try:
    datas, binaries, hiddenimports_fakeredis = collect_all('fakeredis')
    hiddenimports.extend(hiddenimports_fakeredis)
except Exception:
    # 如果 collect_all 失败，尝试单独收集
    try:
        datas = collect_data_files('fakeredis', includes=['*.json', '*.yaml', '*.yml', '*.txt'])
    except Exception:
        datas = []
    
    try:
        # 特别确保 commands.json 被包含
        import fakeredis
        fakeredis_path = os.path.dirname(fakeredis.__file__)
        commands_json = os.path.join(fakeredis_path, 'model', 'commands.json')
        
        if os.path.exists(commands_json):
            # 添加到 datas，保持目录结构
            if (commands_json, 'fakeredis/model') not in datas:
                datas.append((commands_json, 'fakeredis/model'))
    except Exception:
        pass

