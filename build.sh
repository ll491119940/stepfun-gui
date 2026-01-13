#!/bin/bash

# GELab-Zero MCP Server 打包脚本
# 使用 PyInstaller 将 MCP 服务器打包为可执行文件

set -e  # 遇到错误立即退出

echo "=========================================="
echo "GELab-Zero MCP Server 打包脚本"
echo "=========================================="
echo ""

# 检测当前架构
CURRENT_ARCH=$(uname -m)
echo "当前系统架构: $CURRENT_ARCH"
echo ""

# 解析命令行参数
TARGET_ARCH=""
if [ "$1" == "--arch" ] && [ -n "$2" ]; then
    TARGET_ARCH="$2"
    echo "指定目标架构: $TARGET_ARCH"
    echo ""
elif [ "$1" == "--help" ] || [ "$1" == "-h" ]; then
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  --arch ARCH    指定目标架构 (arm64 或 x86_64)"
    echo "                 如果不指定，将使用当前系统架构: $CURRENT_ARCH"
    echo "  --help, -h     显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0                    # 使用当前架构打包"
    echo "  $0 --arch arm64       # 打包 arm64 版本（Apple Silicon）"
    echo "  $0 --arch x86_64      # 打包 x86_64 版本（Intel）"
    echo ""
    exit 0
fi

# 如果没有指定架构，使用当前架构
if [ -z "$TARGET_ARCH" ]; then
    TARGET_ARCH="$CURRENT_ARCH"
fi

# 验证架构
if [ "$TARGET_ARCH" != "arm64" ] && [ "$TARGET_ARCH" != "x86_64" ]; then
    echo "❌ 错误: 不支持的架构 '$TARGET_ARCH'"
    echo "支持的架构: arm64, x86_64"
    exit 1
fi

# 如果目标架构与当前架构不同，需要特殊处理
if [ "$TARGET_ARCH" != "$CURRENT_ARCH" ]; then
    echo "⚠️  注意: 目标架构 ($TARGET_ARCH) 与当前系统架构 ($CURRENT_ARCH) 不同"
    echo "   将尝试通过 Rosetta 2 使用 x86_64 Python 环境"
    echo ""
    
    # 检查是否有 x86_64 版本的 Python
    if [ "$TARGET_ARCH" == "x86_64" ] && [ "$CURRENT_ARCH" == "arm64" ]; then
        # 在 ARM Mac 上打包 x86_64 版本
        if ! arch -x86_64 python3 --version &>/dev/null; then
            echo "❌ 错误: 未找到 x86_64 版本的 Python"
            echo ""
            echo "解决方案："
            echo "  1. 安装 x86_64 版本的 Python（通过 Rosetta 2）："
            echo "     brew install --cask python@3.12"
            echo ""
            echo "  2. 或使用 conda/miniforge 创建 x86_64 环境："
            echo "     CONDA_SUBDIR=osx-64 conda create -n gelab-x64 python=3.12"
            echo "     conda activate gelab-x64"
            echo ""
            echo "  3. 或在 Intel Mac 上打包 x86_64 版本"
            exit 1
        fi
        PYTHON_CMD="arch -x86_64 python3"
        echo "✓ 找到 x86_64 Python: $(arch -x86_64 python3 --version)"
    elif [ "$TARGET_ARCH" == "arm64" ] && [ "$CURRENT_ARCH" == "x86_64" ]; then
        # 在 Intel Mac 上打包 arm64 版本（通常不支持）
        echo "❌ 错误: 在 Intel Mac 上无法打包 arm64 版本"
        echo "   请在 Apple Silicon Mac 上打包 arm64 版本"
        exit 1
    fi
    echo ""
else
    PYTHON_CMD="python3"
fi

# 检查 Python 环境
echo "1. 检查 Python 环境..."
if [ -z "$PYTHON_CMD" ]; then
    if ! command -v python3 &> /dev/null; then
        echo "❌ 错误: 未找到 python3，请先安装 Python 3.12+"
        exit 1
    fi
    PYTHON_CMD="python3"
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✓ Python 版本: $($PYTHON_CMD --version 2>&1)"
echo "✓ Python 命令: $PYTHON_CMD"
echo ""

# 检查是否在虚拟环境中
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "⚠️  警告: 未检测到虚拟环境，建议在虚拟环境中运行"
    read -p "是否继续? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "✓ 虚拟环境: $VIRTUAL_ENV"
fi
echo ""

# 检查并安装依赖
echo "2. 检查依赖..."
if ! $PYTHON_CMD -c "import PyInstaller" 2>/dev/null; then
    echo "   安装 PyInstaller..."
    $PYTHON_CMD -m pip install pyinstaller
else
    echo "✓ PyInstaller 已安装"
fi

# 检查 requirements.txt 中的依赖
if [ -f "requirements.txt" ]; then
    echo "   检查项目依赖..."
    $PYTHON_CMD -m pip install -q -r requirements.txt
    echo "✓ 项目依赖已安装"
fi

# 检查 lupa（fakeredis 的依赖，包含 C 扩展，需要特殊处理）
if ! $PYTHON_CMD -c "import lupa" 2>/dev/null; then
    echo "   安装 lupa（fakeredis 的依赖）..."
    $PYTHON_CMD -m pip install lupa
    echo "✓ lupa 已安装"
else
    echo "✓ lupa 已安装"
fi
echo ""

# 清理之前的构建
echo "3. 清理之前的构建..."
rm -rf build/ dist/ *.spec.bak
echo "✓ 清理完成"
echo ""

# 执行打包
echo "4. 开始打包..."
echo "   使用 spec 文件: gelab_mcp_server.spec"
echo "   目标架构: $TARGET_ARCH"
echo ""

# 设置输出目录名称（包含架构信息）
OUTPUT_NAME="gelab-mcp-server-${TARGET_ARCH}"

# 修改 spec 文件中的输出名称（临时）
sed -i.bak "s/name='gelab-mcp-server'/name='${OUTPUT_NAME}'/g" gelab_mcp_server.spec

# 执行打包（使用对应的 Python 命令）
$PYTHON_CMD -m PyInstaller --clean --noconfirm gelab_mcp_server.spec

# 恢复 spec 文件
mv gelab_mcp_server.spec.bak gelab_mcp_server.spec 2>/dev/null || true

echo ""
echo "=========================================="
echo "打包完成！"
echo "=========================================="
echo ""
echo "可执行文件位置:"
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    echo "  dist/${OUTPUT_NAME}"
    echo ""
    echo "架构信息:"
    file "dist/${OUTPUT_NAME}" 2>/dev/null || echo "  (无法检测架构信息)"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    echo "  dist/${OUTPUT_NAME}"
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows
    echo "  dist/${OUTPUT_NAME}.exe"
fi
echo ""
echo "使用方法:"
echo "  ./dist/${OUTPUT_NAME}"
echo ""
echo "说明:"
echo "  - 使用 model_config.yaml 中的默认配置（API key 已包含在打包文件中）"
echo "  - 配置文件已包含在可执行文件中，无需单独配置"
echo "  - 直接运行即可启动 MCP 服务器"
echo ""
echo "注意:"
echo "  - 此版本为 $TARGET_ARCH 架构"
if [ "$TARGET_ARCH" == "arm64" ]; then
    echo "  - 适用于 Apple Silicon (M1/M2/M3) Mac"
elif [ "$TARGET_ARCH" == "x86_64" ]; then
    echo "  - 适用于 Intel Mac"
    echo "  - 在 Apple Silicon Mac 上可通过 Rosetta 2 运行"
fi
echo ""

