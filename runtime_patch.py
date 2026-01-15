"""
运行时补丁：修复 PyInstaller 打包后的常见问题
1. fastmcp 无法读取版本信息
2. opentelemetry 上下文加载失败
在导入相关模块之前执行此补丁
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
    
    # 修复 opentelemetry 上下文加载问题
    # opentelemetry 在 PyInstaller 打包后，_load_runtime_context 中使用 next() 会抛出 StopIteration
    # 需要在 opentelemetry.context 模块被导入之前就拦截并修复
    try:
        import contextvars
        import threading
        
        # 保存原始的 __import__ 函数
        _original_import = __builtins__.__import__ if isinstance(__builtins__, dict) else __builtins__.__import__
        
        def safe_load_runtime_context():
            """安全的运行时上下文加载函数，避免 StopIteration 错误"""
            contexts_to_try = [
                'opentelemetry.context.contextvars_context',
                'opentelemetry.context.threadlocal_context',
            ]
            
            for context_name in contexts_to_try:
                try:
                    # 先检查是否已经在 sys.modules 中
                    if context_name in sys.modules:
                        return sys.modules[context_name]
                    
                    # 尝试导入
                    module = _original_import(context_name, fromlist=[''])
                    if module:
                        return module
                except (ImportError, StopIteration, AttributeError, KeyError, Exception):
                    continue
            
            # 如果都失败了，返回 None（opentelemetry 会使用默认实现）
            return None
        
        # 使用导入钩子在模块加载时立即修复
        class OpenTelemetryContextImportHook:
            """导入钩子，在 opentelemetry.context 加载时立即修复"""
            def find_spec(self, name, path, target=None):
                if name == 'opentelemetry.context':
                    # 返回一个 spec，让模块正常加载，但我们会拦截加载过程
                    return None
                return None
            
            def create_module(self, spec):
                return None
            
            def exec_module(self, module):
                # 在模块执行后立即修复
                if hasattr(module, '_load_runtime_context'):
                    module._load_runtime_context = safe_load_runtime_context
        
        # 注册导入钩子
        if not hasattr(sys, 'meta_path'):
            sys.meta_path = []
        
        # 检查是否已经注册了钩子
        hook_exists = any(isinstance(hook, OpenTelemetryContextImportHook) for hook in sys.meta_path)
        if not hook_exists:
            sys.meta_path.insert(0, OpenTelemetryContextImportHook())
        
        # 同时使用 __import__ 拦截作为备用方案
        def patched_import(name, globals=None, locals=None, fromlist=(), level=0):
            """修补的导入函数"""
            result = _original_import(name, globals, locals, fromlist, level)
            
            # 如果导入了 opentelemetry.context，立即修复
            if name == 'opentelemetry.context':
                try:
                    if 'opentelemetry.context' in sys.modules:
                        ctx_module = sys.modules['opentelemetry.context']
                        if hasattr(ctx_module, '_load_runtime_context'):
                            ctx_module._load_runtime_context = safe_load_runtime_context
                except Exception:
                    pass
            
            return result
        
        # 替换 __import__ 函数
        if isinstance(__builtins__, dict):
            __builtins__['__import__'] = patched_import
        else:
            __builtins__.__import__ = patched_import
            
    except Exception as e:
        # 如果补丁失败，至少记录错误（在开发环境中）
        if not getattr(sys, 'frozen', False):
            print(f"Warning: Failed to patch opentelemetry: {e}")
        pass

