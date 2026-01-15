@echo off
REM GELab-Zero MCP Server 打包脚本 (Windows 专用)
REM 使用 PyInstaller 将 MCP 服务器打包为可执行文件
REM 此脚本专门为 Windows 平台优化，与 build.sh (Mac) 分开维护

REM 设置编码为 UTF-8
chcp 65001 >nul 2>&1

setlocal enabledelayedexpansion

cd /d "%~dp0"

echo ==========================================
echo GELab-Zero MCP Server 打包脚本 (Windows)
echo ==========================================
echo.

REM 检查虚拟环境（简单检查）
echo 1. 检查虚拟环境...
if "%VIRTUAL_ENV%"=="" (
    echo ⚠️  未检测到虚拟环境，建议在虚拟环境中运行
) else (
    echo ✓ 虚拟环境: %VIRTUAL_ENV%
)
echo.


REM 检查 Python 环境
echo 2. 检查 Python 环境...
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 错误: 未找到 python，请先安装 Python 3.12+
    exit /b 1
)

python --version
echo.

REM 检查 PyInstaller
echo 3. 检查 PyInstaller...
python -c "import PyInstaller" >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 错误: 未找到 PyInstaller
    echo    请先安装: pip install pyinstaller
    exit /b 1
)
echo ✓ PyInstaller 已安装
echo.

REM 清理之前的构建
echo 4. 清理之前的构建...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist
if exist "*.spec.bak" del /q *.spec.bak
echo ✓ 清理完成
echo.

REM 执行打包
echo 5. 开始打包...
echo    使用 spec 文件: gelab_mcp_server.spec
echo.

REM 使用 Windows 专用的 spec 文件（如果存在）
if exist "gelab_mcp_server_windows.spec" (
    echo    使用 Windows 专用 spec 文件: gelab_mcp_server_windows.spec
    pyinstaller --clean --noconfirm --log-level=WARN gelab_mcp_server_windows.spec
) else (
    echo    使用通用 spec 文件: gelab_mcp_server.spec
    pyinstaller --clean --noconfirm gelab_mcp_server.spec
)

REM 检查打包结果
if %errorlevel% neq 0 (
    echo.
    echo ❌ 打包失败！
    echo.
    echo 可能的原因：
    echo    1. 缺少必要的依赖包
    echo    2. C 扩展库（如 lupa）与当前 Python/PyInstaller 版本不兼容
    echo    3. 建议尝试：
    echo       - 升级 PyInstaller: pip install --upgrade pyinstaller
    echo       - 检查依赖版本: pip list
    echo       - 重新安装依赖: pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

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

