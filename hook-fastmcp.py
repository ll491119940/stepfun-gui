# PyInstaller hook for fastmcp
# 解决打包后 fastmcp 无法读取版本信息的问题

from PyInstaller.utils.hooks import collect_data_files, collect_submodules
import os

# 收集 fastmcp 的所有子模块
hiddenimports = collect_submodules('fastmcp')

# 收集 fastmcp 的数据文件（包括元数据）
datas = collect_data_files('fastmcp', includes=['*.dist-info'])

# 尝试找到 fastmcp 的 .dist-info 目录
try:
    import site
    import fastmcp
    
    # 查找 fastmcp 的安装位置
    fastmcp_path = os.path.dirname(fastmcp.__file__)
    site_packages = None
    
    # 找到包含 fastmcp 的 site-packages 目录
    for sp in site.getsitepackages():
        if fastmcp_path.startswith(sp):
            site_packages = sp
            break
    
    if site_packages:
        # 查找 fastmcp 的 .dist-info 目录
        import glob
        dist_info_pattern = os.path.join(site_packages, 'fastmcp-*.dist-info')
        dist_info_dirs = glob.glob(dist_info_pattern)
        
        if dist_info_dirs:
            dist_info_dir = dist_info_dirs[0]
            dist_info_name = os.path.basename(dist_info_dir)
            # 添加到 datas，保持目录结构
            datas.append((dist_info_dir, dist_info_name))
except Exception:
    pass

