#!/bin/bash

# GELab-Zero MCP Server 启动脚本
# 自动激活虚拟环境并启动服务器

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "❌ 错误: 未找到虚拟环境，请先创建虚拟环境"
    echo ""
    echo "运行以下命令创建虚拟环境："
    echo "  python3 -m venv venv"
    echo "  source venv/bin/activate"
    echo "  pip install -r requirements.txt"
    exit 1
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate

# 检查依赖
if ! python3 -c "import fastmcp" 2>/dev/null; then
    echo "⚠️  警告: fastmcp 未安装，正在安装依赖..."
    pip install -r requirements.txt
fi

# 启动服务器
echo "启动 MCP 服务器..."
echo ""

# 解析命令行参数
if [ "$1" == "--api-key" ] && [ -n "$2" ]; then
    python3 mcp_server/simple_gelab_mcp_server_withcaption.py --api-key "$2" "${@:3}"
else
    python3 mcp_server/simple_gelab_mcp_server_withcaption.py "$@"
fi

