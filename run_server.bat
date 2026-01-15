@echo off
REM GELab-Zero MCP Server 启动脚本 (Windows)
REM 自动激活虚拟环境并启动服务器

setlocal enabledelayedexpansion

cd /d "%~dp0"

REM 检查虚拟环境
if not exist "venv\" (
    echo ❌ 错误: 未找到虚拟环境，请先创建虚拟环境
    echo.
    echo 运行以下命令创建虚拟环境：
    echo   python -m venv venv
    echo   venv\Scripts\activate
    echo   pip install -r requirements.txt
    exit /b 1
)

REM 激活虚拟环境
echo 激活虚拟环境...
call venv\Scripts\activate.bat

REM 检查依赖
python -c "import fastmcp" >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  警告: fastmcp 未安装，正在安装依赖...
    pip install -r requirements.txt
)

REM 启动服务器
echo 启动 MCP 服务器...
echo.

REM 解析命令行参数
if "%1"=="--api-key" (
    if not "%2"=="" (
        python mcp_server\simple_gelab_mcp_server_withcaption.py --api-key %2 %3 %4 %5 %6 %7 %8 %9
    ) else (
        python mcp_server\simple_gelab_mcp_server_withcaption.py
    )
) else (
    python mcp_server\simple_gelab_mcp_server_withcaption.py %*
)

endlocal

