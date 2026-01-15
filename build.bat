@echo off
REM GELab-Zero MCP Server 打包脚本 (Windows)
REM 使用 PyInstaller 将 MCP 服务器打包为可执行文件

setlocal enabledelayedexpansion

cd /d "%~dp0"

echo ==========================================
echo GELab-Zero MCP Server 打包脚本
echo ==========================================
echo.

REM 检查并激活虚拟环境
echo 1. 检查虚拟环境...
if "%VIRTUAL_ENV%"=="" (
    REM 优先检查 venv 文件夹（支持 Windows 和 MSYS2 两种结构）
    if exist "venv\Scripts\activate.bat" (
        echo    激活虚拟环境: venv (Windows)
        call venv\Scripts\activate.bat
        echo ✓ 虚拟环境已激活: %VIRTUAL_ENV%
    ) else if exist "venv\bin\activate.bat" (
        echo    激活虚拟环境: venv (MSYS2/Git Bash)
        call venv\bin\activate.bat
        echo ✓ 虚拟环境已激活: %VIRTUAL_ENV%
    ) else if exist "venv\bin\activate" (
        echo    激活虚拟环境: venv (Unix 风格)
        REM 对于 Unix 风格的 activate，在 Windows CMD 中需要使用不同的方式
        echo ⚠️  检测到 Unix 风格的虚拟环境，建议在 MSYS2/Git Bash 中运行此脚本
        set /p CONTINUE="是否继续尝试? (y/n): "
        if /i not "!CONTINUE!"=="y" (
            exit /b 1
        )
    ) else (
        echo ⚠️  警告: 未找到虚拟环境 venv，建议在虚拟环境中运行
        set /p CONTINUE="是否继续? (y/n): "
        if /i not "!CONTINUE!"=="y" (
            exit /b 1
        )
    )
) else (
    echo ✓ 虚拟环境已激活: %VIRTUAL_ENV%
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

REM 方法1: 尝试使用 --log-level=WARN 减少输出，并使用环境变量
echo    方法1: 使用环境变量禁用 hook 发现...
set PYINSTALLER_DISABLE_HOOK_DISCOVERY=1
pyinstaller --clean --noconfirm --log-level=WARN gelab_mcp_server.spec

REM 如果方法1失败，尝试方法2: 直接使用 spec 文件（hookspath 已设置为 None）
if %errorlevel% neq 0 (
    echo.
    echo ⚠️  方法1失败，尝试方法2: 使用 spec 文件（已禁用 hook）...
    set PYINSTALLER_DISABLE_HOOK_DISCOVERY=
    pyinstaller --clean --noconfirm --log-level=WARN gelab_mcp_server.spec
)

REM 如果还是失败，提供诊断信息
if %errorlevel% neq 0 (
    echo.
    echo ❌ 打包失败！可能的原因：
    echo    1. lupa 或其他 C 扩展库与当前 Python/PyInstaller 版本不兼容
    echo    2. 建议尝试：
    echo       - 升级 PyInstaller: pip install --upgrade pyinstaller
    echo       - 检查 lupa 版本: pip show lupa
    echo       - 尝试重新安装 lupa: pip uninstall lupa ^&^& pip install lupa
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

