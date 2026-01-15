# 在导入其他模块之前，先应用运行时补丁（修复 PyInstaller 打包后的问题）
import sys
import os
import types
if "." not in sys.path:
    sys.path.append(".")

# 禁用 OpenTelemetry（打包后缺少元数据/entry_points 引发 baggage 等导入失败）
if getattr(sys, "frozen", False) or os.environ.get("OTEL_SDK_DISABLED", "").lower() == "true":
    os.environ["OTEL_SDK_DISABLED"] = "true"

    class UniversalMock(types.ModuleType):
        """万能 Mock 类：可以被当作模块、类、函数使用，且访问任何属性都返回自身。"""
        def __init__(self, name):
            super().__init__(name)
            self.__path__ = []
            self.__file__ = "<mock>"
            self.__all__ = []
            # 设置 spec 满足某些库的包检查
            try:
                import importlib.machinery
                self.__spec__ = importlib.machinery.ModuleSpec(name, loader=None, is_package=True)
            except Exception:
                pass

        def __getattr__(self, name):
            if name in ("__path__", "__file__", "__spec__", "__loader__", "__name__", "__package__", "__mro_entries__"):
                return super().__getattribute__(name)
            # 访问任何不存在的属性时，自动创建一个新的万能 Mock
            child = UniversalMock(f"{self.__name__}.{name}")
            setattr(self, name, child)
            return child

        def __mro_entries__(self, bases):
            # 支持被继承：返回一个动态创建的类
            return (type(self.__name__.split('.')[-1], (), {}),)

        def __or__(self, other): return self  # 支持 Type | None 语法
        def __ror__(self, other): return self # 支持 None | Type 语法

        def __call__(self, *args, **kwargs): return self
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def __getitem__(self, key): return self
        def __iter__(self): return iter([])

    class OtelMockFinder:
        """导入拦截器：拦截所有 opentelemetry 开头的导入"""
        def find_spec(self, fullname, path, target=None):
            if fullname.startswith("opentelemetry"):
                from importlib.machinery import ModuleSpec
                return ModuleSpec(fullname, self)
            return None
        def create_module(self, spec):
            return UniversalMock(spec.name)
        def exec_module(self, module):
            pass

    # 将拦截器插入导入链的最前端
    sys.meta_path.insert(0, OtelMockFinder())

    # 清理掉可能已经部分加载的模块，确保拦截器生效
    for mod_name in list(sys.modules.keys()):
        if mod_name.startswith("opentelemetry"):
            del sys.modules[mod_name]
else:
    # 非冻结环境且未禁用 OTEL 时的逻辑
    os.environ["OTEL_PYTHON_CONTEXT"] = "contextvars_context"
    os.environ["OTEL_PYTHON_PROPAGATOR"] = "tracecontext"
    os.environ["OTEL_PYTHON_PROPAGATORS"] = "tracecontext"

    # 直接初始化 otel runtime context，绕过 entry_points
    try:
        from opentelemetry.context.contextvars_context import ContextVarsRuntimeContext
        import opentelemetry.context as ctx_mod

        ctx_mod._load_runtime_context = lambda: ContextVarsRuntimeContext()
        ctx_mod._RUNTIME_CONTEXT = ctx_mod._load_runtime_context()
    except Exception:
        pass

    # 直接设置 propagator，避免 tracecontext 入口点缺失
    try:
        from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
        import opentelemetry.propagate as prop_mod

        prop_mod._GLOBAL_TEXTMAP = TraceContextTextMapPropagator()
        # 同时确保全局工厂只返回 tracecontext，避免 baggage 被尝试加载
        try:
            prop_mod._PROPAGATOR_FACTORY = lambda *_args, **_kwargs: [TraceContextTextMapPropagator()]
        except Exception:
            pass
    except Exception:
        pass

    # 兜底 importlib_metadata.version，防止 otel 包元数据缺失时报 PackageNotFoundError
    try:
        import importlib_metadata
        _orig_version = importlib_metadata.version

        def _safe_version(name):
            try:
                return _orig_version(name)
            except importlib_metadata.PackageNotFoundError:
                if name in ("opentelemetry-sdk", "opentelemetry-api", "opentelemetry-exporter-prometheus"):
                    return "1.39.1"
                raise

        importlib_metadata.version = _safe_version
    except Exception:
        pass

# 导入运行时补丁（必须在 fastmcp 之前）
try:
    import runtime_patch
except ImportError:
    # 如果 runtime_patch 不存在，继续执行（开发环境）
    pass

from fastmcp import FastMCP

import argparse

from copilot_front_end.mobile_action_helper import list_devices, get_device_wm_size
from copilot_agent_server.local_server import LocalServer

from copilot_agent_client.pu_client import evaluate_task_on_device

import yaml
from megfile import smart_open
from tools.config_path_helper import get_config_path

from typing import Annotated
from pydantic import Field

from mcp_server.mcp_backend_implements import (
    get_device_list,
    get_screenshot,
    execute_task,
)

mcp = FastMCP(name="Gelab-MCP-Server", instructions="""
This MCP server provides tools to interact with connected mobile devices using a GUI agent.               
              """
            )


@mcp.tool
def list_connected_devices() -> list:
    """
        List all connected mobile devices.
        
        Returns:
            list: A list of connected device IDs.
    """
    devices = get_device_list()
    print("Connected devices:", devices)
    return devices


@mcp.tool
def ask_agent_start_new_task(

    device_id: Annotated[str, Field(description="ID of the device to perform the task on. listed by list_connected_devices tool.")],

    task: Annotated[str | None, Field(description="The task that the agent needs to perform on the mobile device. if this is not None, the agent will try to perform this task. if None, the session_id must be provided to continue the previous session.")],
    
    # reset_environment: Annotated[bool, Field(description="Whether to reset the environment before executing the task, close current app, and back to home screen. If you want to execute a independent task, set this to True will make it easy to execute. If you want to continue the previous session, set this to False.")] = False,

    max_steps: Annotated[int, Field(description="Maximum number of steps the agent can take to complete the task.")] = 20,

    # session_id: Annotated[str | None, Field(description="Optional, session ID must provide when the last task endwith INFO action and you want to reply, the session id and device id and the reply from client must be provided.")] = None,

    # When the INFO action is called, how to handle it.
    # 1. "auto_reply": the INFO action will be handled automatically by calling the caption model to generate image captions.
    # 2. "no_reply": the INFO action will be ignored. THE AGENT MAY GET STUCK IF THE INFO ACTION IS IGNORED.
    # 3. "manual_reply": the INFO action will cause an interruption, and the user needs to provide the reply manually by input things in server's console.
    # 4. "pass_to_client": the INFO action will be returned to the MCP client to handle it. 
#     reply_mode: Annotated[str, Field(description='''
#         How to handle the INFO action during task execution.
        
#         Options:
#             - "auto_reply": Automatically generate image captions for INFO actions.
#             - "no_reply": Ignore INFO actions (may cause the agent to get stuck).
#             - "manual_reply": Interrupt and require user input for INFO actions.
#             - "pass_to_client": Pass INFO actions to the MCP client for handling.
# ''')] = "auto_reply",

    # reply_from_client: Annotated[str | None, Field(description="If the last task is ended with INFO action, and you want to give GUI agent a reply, provide the reply here. If you do so, you must provide last session id and last device id.")] = None,
) -> dict:

    """
# Ask GUI Agent to start performing a new task on a connected device.

Ask the GUI agent to perform the specified task on a connected device.
The GUI Agent can be able to understand natural language instructions and interact with the device accordingly.
The agent will be able to execute a high-level task description，if you have any additional requirements, write them down in detail at tast string.
This function will reset the environment before executing the task, close current app, and back to home screen.

if you have 

## The agent has the below limited capabilities:

1. The task must be related to an app that is already installed on the device. for example, "打开微信，帮我发一条消息给张三，说今天下午三点开会"; "帮我在淘宝上搜索一款性价比高的手机，并加入购物车"; "to purchase an ea on Amazon".

2. The task must be simple and specific. for example, "do yyy in xxx app"; "find xxx information in xxx app". ONE THING AT ONE APP AT A TIME.

3. The agent may not be able to handle complex tasks that require multi-step reasoning or planning. for example. You may need to break down complex tasks into simpler sub-tasks and ask the agent to perform them sequentially. For example, instead of asking the agent to "plan a trip to Paris for xxx", you can ask it to "search for flights to Paris on xxx app", "find hotels in Paris on xxx app", make the plan yourself and ask agent to "sent the plan to xxx via IM app like wechat".

4. The agent connot accept multimodal inputs now. if you want to provide additional information like screenshot captions, please include them in the task description.

## Usage guidance：

1. you should never directly ask an Agent to pay or order anything. If user want to make a purchase, you should ask agent to stop brfore ordering/paying, and let user to order/pay.

2. tell the agent, if human verification is appeared during the task execution, the agent should ask Client. when the you see the INFO, you should ask user to handle the verification manually. after user says "done", you can continue the task with the session_id and device_id and ask the agent to continue in reply_from_client.

3. IF the last agentic call is failed or you want to perform a new task in different app, you should always use this function to start a new task, so that the environment will be reset before executing the task.

Returns:
    dict: Execution log containing details of the task execution.
    with keys including
        - device_info: Information about the device used for task execution.
        - final_action: The final action taken by the agent to complete the task.
        - global_step_idx: The total number of steps taken during the task execution.
        - local_step_idx: The number of steps taken in the current session.
        - session_id: The session ID for maintaining context across multiple tasks.
        - stop_reason: The reason for stopping the task execution (e.g., TASK_COMPLETED_SUCCESSFULLY).
        - task: The original task description provided to the agent.
    """

    reply_mode = "pass_to_client"

    # if task is not None:
    #     assert session_id is None, "If task is provided, session_id must be None."
    #     # New task, so reset_environment is True
    #     reset_environment = True
    # else:
    #     assert session_id is not None, "If task is None, session_id must be provided to continue the previous session."
    #     # Continuing previous session, so reset_environment is False
    #     reset_environment = False

    reset_environment = True
    

    return_log = execute_task(
        device_id=device_id,

        task=task,

        reset_environment=reset_environment,
        max_steps=max_steps,

        # enable_intermediate_logs=False,
        # enable_intermediate_image_caption=False,
# 
        enable_intermediate_logs=True,
        # enable_intermediate_image_caption=False,
        enable_intermediate_image_caption=True,

        enable_intermediate_screenshots=False,

        enable_final_screenshot=False,
        # enable_final_image_caption=False,
        enable_final_image_caption=True,

        reply_mode=reply_mode,

        session_id=None,
        # session_id=session_id,
        reply_from_client=None,
        # reply_from_client=reply_from_client,


    )

    return return_log


@mcp.tool
def ask_agent_continue(

    device_id: Annotated[str, Field(description="ID of the device to perform the task on. listed by list_connected_devices tool.")],

    task: Annotated[str | None, Field(description="The task that the agent needs to perform on the mobile device. if this is not None, the agent will try to perform this task. if None, the session_id must be provided to continue the previous session.")],
    
    # reset_environment: Annotated[bool, Field(description="Whether to reset the environment before executing the task, close current app, and back to home screen. If you want to execute a independent task, set this to True will make it easy to execute. If you want to continue the previous session, set this to False.")] = False,

    max_steps: Annotated[int, Field(description="Maximum number of steps the agent can take to complete the task.")] = 20,

    # session_id: Annotated[str | None, Field(description="Optional, session ID must provide when the last task endwith INFO action and you want to reply, the session id and device id and the reply from client must be provided.")] = None,

    # When the INFO action is called, how to handle it.
    # 1. "auto_reply": the INFO action will be handled automatically by calling the caption model to generate image captions.
    # 2. "no_reply": the INFO action will be ignored. THE AGENT MAY GET STUCK IF THE INFO ACTION IS IGNORED.
    # 3. "manual_reply": the INFO action will cause an interruption, and the user needs to provide the reply manually by input things in server's console.
    # 4. "pass_to_client": the INFO action will be returned to the MCP client to handle it. 
#     reply_mode: Annotated[str, Field(description='''
#         How to handle the INFO action during task execution.
        
#         Options:
#             - "auto_reply": Automatically generate image captions for INFO actions.
#             - "no_reply": Ignore INFO actions (may cause the agent to get stuck).
#             - "manual_reply": Interrupt and require user input for INFO actions.
#             - "pass_to_client": Pass INFO actions to the MCP client for handling.
# ''')] = "auto_reply",

    # reply_from_client: Annotated[str | None, Field(description="If the last task is ended with INFO action, and you want to give GUI agent a reply, provide the reply here. If you do so, you must provide last session id and last device id.")] = None,
) -> dict:

    """
# Ask GUI Agent to continue performing a task on a connected device, using previous context.

Ask the GUI agent to perform the specified task on a connected device.
The GUI Agent can be able to understand natural language instructions and interact with the device accordingly.
The agent will be able to execute a high-level task description，if you have any additional requirements, write them down in detail at tast string.
This function will **NOT** reset the environment before executing the task, so that the agent can continue the previous session.

if you have 

## The agent has the below limited capabilities:

1. The task must be related to an app that is already installed on the device. for example, "打开微信，帮我发一条消息给张三，说今天下午三点开会"; "帮我在淘宝上搜索一款性价比高的手机，并加入购物车"; "to purchase an ea on Amazon".

2. The task must be simple and specific. for example, "do yyy in xxx app"; "find xxx information in xxx app". ONE THING AT ONE APP AT A TIME.

3. The agent may not be able to handle complex tasks that require multi-step reasoning or planning. for example. You may need to break down complex tasks into simpler sub-tasks and ask the agent to perform them sequentially. For example, instead of asking the agent to "plan a trip to Paris for xxx", you can ask it to "search for flights to Paris on xxx app", "find hotels in Paris on xxx app", make the plan yourself and ask agent to "sent the plan to xxx via IM app like wechat".

4. The agent connot accept multimodal inputs now. if you want to provide additional information like screenshot captions, please include them in the task description.

## Usage guidance：

1. you should never directly ask an Agent to pay or order anything. If user want to make a purchase, you should ask agent to stop brfore ordering/paying, and let user to order/pay.

2. tell the agent, if human verification is appeared during the task execution, the agent should ask Client. when the you see the INFO, you should ask user to handle the verification manually. after user says "done", you can continue the task with the session_id and device_id and ask the agent to continue in reply_from_client.

3. IF the last agentic call is successful or the last action is INFO or the new task is related to the previous task, you can use this function to continue the task, so that the agent can finish the task faster by leveraging the previous context.
    dict: Execution log containing details of the task execution.
    with keys including
        - device_info: Information about the device used for task execution.
        - final_action: The final action taken by the agent to complete the task.
        - global_step_idx: The total number of steps taken during the task execution.
        - local_step_idx: The number of steps taken in the current session.
        - session_id: The session ID for maintaining context across multiple tasks.
        - stop_reason: The reason for stopping the task execution (e.g., TASK_COMPLETED_SUCCESSFULLY).
        - task: The original task description provided to the agent.
    """

    reply_mode = "pass_to_client"

    # if task is not None:
    #     assert session_id is None, "If task is provided, session_id must be None."
    #     # New task, so reset_environment is True
    #     reset_environment = True
    # else:
    #     assert session_id is not None, "If task is None, session_id must be provided to continue the previous session."
    #     # Continuing previous session, so reset_environment is False
    #     reset_environment = False

    reset_environment = False
    

    return_log = execute_task(
        device_id=device_id,

        task=task,

        reset_environment=reset_environment,
        max_steps=max_steps,

        # enable_intermediate_logs=False,
        # enable_intermediate_image_caption=False,
# 
        enable_intermediate_logs=True,
        enable_intermediate_image_caption=True,

        enable_intermediate_screenshots=False,

        enable_final_screenshot=False,
        # enable_final_image_caption=False,
        enable_final_image_caption=True,

        reply_mode=reply_mode,

        session_id=None,
        # session_id=session_id,
        reply_from_client=None,
        # reply_from_client=reply_from_client,


    )

    return return_log


def update_model_config_api_key(api_key: str, provider: str = "stepfun"):
    """
    更新 model_config.yaml 中的 API key
    
    Args:
        api_key: 新的 API key
        provider: 模型提供商，默认为 "stepfun"
    """
    try:
        # 优先从打包的配置文件中读取默认配置
        config_path = get_config_path("model_config.yaml")
        
        # 读取现有配置
        with smart_open(config_path, "r") as f:
            model_config = yaml.safe_load(f) or {}
        
        # 更新 API key
        if provider not in model_config:
            model_config[provider] = {}
        
        # 保留原有的 api_base，只更新 api_key
        if "api_base" not in model_config[provider]:
            if provider == "stepfun":
                model_config[provider]["api_base"] = "https://api.stepfun.com/v1"
            elif provider == "local":
                model_config[provider]["api_base"] = "http://localhost:11434/v1"
            else:
                model_config[provider]["api_base"] = ""
        
        model_config[provider]["api_key"] = api_key
        
        # 将更新的配置写入工作目录
        # 这样 tools/ask_llm_v2.py 等模块就能读取到更新后的配置
        # 工作目录中的配置文件会覆盖打包文件中的配置
        work_dir_config_path = os.path.join(os.getcwd(), "model_config.yaml")
        with open(work_dir_config_path, "w") as f:
            yaml.dump(model_config, f, default_flow_style=False, allow_unicode=True)
        
    except Exception as e:
        print(f"警告: 更新 model_config.yaml 失败: {e}")
        print("将使用默认配置文件中的 API key")


def main():
    parser = argparse.ArgumentParser(
        description="Gelab MCP Server - 移动设备 GUI 代理服务",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 使用默认配置（model_config.yaml 中的配置）
  python simple_gelab_mcp_server_withcaption.py
  
  # 使用自定义 API key
  python simple_gelab_mcp_server_withcaption.py --api-key YOUR_API_KEY
  
  # 指定提供商和 API key
  python simple_gelab_mcp_server_withcaption.py --api-key YOUR_API_KEY --provider stepfun
  
  # 指定端口
  python simple_gelab_mcp_server_withcaption.py --port 8705
        """
    )
    
    parser.add_argument(
        "--api-key",
        type=str,
        default=None,
        help="API key for the model provider (如果提供，将更新 model_config.yaml 中的配置)"
    )
    
    parser.add_argument(
        "--provider",
        type=str,
        default="stepfun",
        choices=["stepfun", "local"],
        help="模型提供商 (默认: stepfun)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=None,
        help="MCP 服务器端口 (默认: 从 mcp_server_config.yaml 读取)"
    )
    
    args = parser.parse_args()
    
    # 如果提供了 API key，更新配置文件
    if args.api_key:
        update_model_config_api_key(args.api_key, args.provider)
        masked_key = '*' * (len(args.api_key) - 4) + args.api_key[-4:] if len(args.api_key) > 4 else '****'
        print(f"✓ 已通过命令行参数设置 {args.provider} 的 API key: {masked_key}")
    else:
        print(f"✓ 使用 model_config.yaml 中的默认配置 (provider: {args.provider})")
    
    # 读取 MCP 服务器配置
    mcp_server_config_path = get_config_path("mcp_server_config.yaml")
    with smart_open(mcp_server_config_path, "r") as f:
        mcp_server_config = yaml.safe_load(f)
    
    port = args.port or mcp_server_config['server_config'].get("mcp_server_port", 8704)
    
    print(f"正在启动 MCP 服务器，端口: {port}")
    print(f"模型提供商: {args.provider}")
    
    mcp.run(transport="http", port=port)


if __name__ == "__main__":
    main()