"""
运行时补丁：修复 PyInstaller 打包后的常见问题
"""
import sys
import os
import types

def apply_metadata_patch():
    packages_to_patch = {'fastmcp': '2.14.2', 'opentelemetry-api': '1.39.1', 'opentelemetry-sdk': '1.39.1'}
    for mod_name in ['importlib.metadata', 'importlib_metadata']:
        try:
            import importlib
            mod = importlib.import_module(mod_name)
            if hasattr(mod, 'version'):
                orig_v = mod.version
                mod.version = lambda n: orig_v(n) if n not in packages_to_patch else packages_to_patch[n]
        except: pass

def apply_certifi_patch():
    """彻底修复 PyInstaller 打包后的证书丢失和路径无效问题"""
    try:
        import os
        import sys
        import certifi
        
        if getattr(sys, 'frozen', False):
            # 1. 强制定位打包后的证书路径
            # PyInstaller 会把 collect_data_files('certifi') 的结果放在 certifi 子目录
            base_path = sys._MEIPASS
            cert_path = os.path.join(base_path, 'certifi', 'cacert.pem')
            
            # 如果不存在，尝试在根目录找
            if not os.path.exists(cert_path):
                cert_path = os.path.join(base_path, 'cacert.pem')
            
            # 2. 如果找到了证书，进行路径标准化
            if os.path.exists(cert_path):
                # 转换为长路径，防止 ~1 符号导致某些库识别失败
                if os.name == 'nt' and '~' in cert_path:
                    try:
                        import ctypes
                        kernel32 = ctypes.windll.kernel32
                        buf = ctypes.create_unicode_buffer(1024)
                        if kernel32.GetLongPathNameW(cert_path, buf, 1024) > 0:
                            cert_path = buf.value
                    except: pass
                
                # 3. 注入到所有可能的变量中
                os.environ['SSL_CERT_FILE'] = cert_path
                os.environ['REQUESTS_CA_BUNDLE'] = cert_path
                
                # 4. 暴力修补 certifi 模块，让所有依赖它的库（openai, requests, httpx）都强制使用这个路径
                certifi.where = lambda: cert_path
                
                # 5. 针对已经加载的 requests 库进行修补
                if 'requests' in sys.modules:
                    import requests.adapters
                    requests.adapters.DEFAULT_CA_BUNDLE_PATH = cert_path
                    
                # print(f"Cert fixed at: {cert_path}")
    except Exception:
        pass

# 执行
apply_metadata_patch()
apply_certifi_patch()
