@echo off
REM GELab-Zero MCP Server 打包脚本 (Windows)
REM 使用 PyInstaller 将 MCP 服务器打包为可执行文件

setlocal enabledelayedexpansion

echo ==========================================
echo GELab-Zero MCP Server 打包脚本
echo ==========================================
echo.

REM 检查 Python 环境
echo 1. 检查 Python 环境...
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 错误: 未找到 python，请先安装 Python 3.12+
    exit /b 1
)

python --version
echo.

REM 检查是否在虚拟环境中
if "%VIRTUAL_ENV%"=="" (
    echo ⚠️  警告: 未检测到虚拟环境，建议在虚拟环境中运行
    set /p CONTINUE="是否继续? (y/n): "
    if /i not "!CONTINUE!"=="y" (
        exit /b 1
    )
) else (
    echo ✓ 虚拟环境: %VIRTUAL_ENV%
)
echo.

REM 检查并安装依赖
echo 2. 检查依赖...
python -c "import PyInstaller" >nul 2>&1
if %errorlevel% neq 0 (
    echo    安装 PyInstaller...
    pip install pyinstaller
) else (
    echo ✓ PyInstaller 已安装
)

REM 检查 requirements.txt 中的依赖
if exist "requirements.txt" (
    echo    检查项目依赖...
    pip install -q -r requirements.txt
    echo ✓ 项目依赖已安装
)

REM 检查 lupa（fakeredis 的依赖，包含 C 扩展，需要特殊处理）
%PYTHON_CMD% -c "import lupa" >nul 2>&1
if errorlevel 1 (
    echo    安装 lupa（fakeredis 的依赖）...
    pip install lupa
    echo ✓ lupa 已安装
) else (
    echo ✓ lupa 已安装
)
echo.

REM 清理之前的构建
echo 3. 清理之前的构建...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist
if exist "*.spec.bak" del /q *.spec.bak
echo ✓ 清理完成
echo.

REM 执行打包
echo 4. 开始打包...
echo    使用 spec 文件: gelab_mcp_server.spec
echo.

pyinstaller --clean --noconfirm gelab_mcp_server.spec

echo.
echo ==========================================
echo 打包完成！
echo ==========================================
echo.
echo 可执行文件位置:
echo   dist\gelab-mcp-server.exe
echo.
echo 使用方法:
echo   dist\gelab-mcp-server.exe --api-key YOUR_API_KEY
echo   或
echo   dist\gelab-mcp-server.exe --api-key YOUR_API_KEY --provider stepfun --port 8704
echo.

pause

