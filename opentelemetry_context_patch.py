"""
opentelemetry.context 补丁模块
在 PyInstaller 打包环境中修复 StopIteration 错误

问题分析：
- opentelemetry.context 在模块级别就会调用 _load_runtime_context()
- _load_runtime_context() 使用 next() 迭代器，在 PyInstaller 环境中可能失败
- 需要在模块执行前就准备好安全函数

解决方案：
1. 预先导入上下文模块
2. 在导入时捕获异常并修复
3. 使用简单的 __import__ 钩子，避免复杂的 MetaPathFinder
"""
import sys

# 检查是否在 PyInstaller 打包环境中
if getattr(sys, 'frozen', False):
    # 在打包环境中，我们需要修复 opentelemetry.context 的 _load_runtime_context 函数
    
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
                module = __import__(context_name, fromlist=[''])
                if module:
                    return module
            except (ImportError, StopIteration, AttributeError, KeyError, Exception):
                continue
        
        # 如果都失败了，返回 None（opentelemetry 会使用默认实现）
        return None
    
    # 预先导入上下文模块（在导入 opentelemetry.context 之前）
    # 这样可以避免 _load_runtime_context 中的动态导入失败
    try:
        __import__('opentelemetry.context.contextvars_context')
    except Exception:
        pass
    
    try:
        __import__('opentelemetry.context.threadlocal_context')
    except Exception:
        pass
    
    # 获取原始的 __import__ 函数
    if isinstance(__builtins__, dict):
        original_import = __builtins__.get('__import__', __import__)
    else:
        original_import = getattr(__builtins__, '__import__', __import__)
    
    def patched_import(name, globals=None, locals=None, fromlist=(), level=0):
        """修补的导入函数，在导入 opentelemetry.context 时捕获异常并修复"""
        try:
            # 先执行原始导入
            result = original_import(name, globals, locals, fromlist, level)
        except StopIteration:
            # 如果导入时抛出 StopIteration，说明 _load_runtime_context 失败了
            # 尝试修复并重新导入
            if name == 'opentelemetry.context':
                try:
                    # 如果模块已部分加载，修复它
                    if 'opentelemetry.context' in sys.modules:
                        ctx_module = sys.modules['opentelemetry.context']
                        ctx_module._load_runtime_context = safe_load_runtime_context
                    # 重新尝试导入
                    result = original_import(name, globals, locals, fromlist, level)
                except Exception:
                    # 如果还是失败，返回部分加载的模块或 None
                    result = sys.modules.get(name, None)
        except Exception:
            # 其他异常正常抛出
            raise
        
        # 如果成功导入了 opentelemetry.context，确保函数是安全版本
        if name == 'opentelemetry.context' or (fromlist and 'context' in fromlist):
            try:
                if 'opentelemetry.context' in sys.modules:
                    ctx_module = sys.modules['opentelemetry.context']
                    # 替换 _load_runtime_context 函数
                    ctx_module._load_runtime_context = safe_load_runtime_context
            except Exception:
                pass
        
        return result
    
    # 替换 __import__ 函数
    if isinstance(__builtins__, dict):
        __builtins__['__import__'] = patched_import
    else:
        setattr(__builtins__, '__import__', patched_import)
