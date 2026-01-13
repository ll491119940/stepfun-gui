#!/bin/bash

# 为所有架构打包的脚本
# 在 macOS 上分别打包 arm64 和 x86_64 版本

set -e

echo "=========================================="
echo "GELab-Zero MCP Server 全架构打包脚本"
echo "=========================================="
echo ""

CURRENT_ARCH=$(uname -m)
echo "当前系统架构: $CURRENT_ARCH"
echo ""

# 检查是否在 macOS 上
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ 错误: 此脚本仅适用于 macOS"
    exit 1
fi

# 清理之前的构建
echo "清理之前的构建..."
rm -rf build/ dist/
echo "✓ 清理完成"
echo ""

# 打包 arm64 版本
echo "=========================================="
echo "打包 arm64 版本（Apple Silicon）"
echo "=========================================="
echo ""

if [ "$CURRENT_ARCH" == "arm64" ]; then
    # 当前是 arm64，直接打包
    ./build.sh --arch arm64
else
    # 当前是 x86_64，尝试在 arm64 上打包（需要 Rosetta 2）
    echo "⚠️  当前系统是 x86_64，尝试通过 Rosetta 2 打包 arm64 版本..."
    arch -arm64 ./build.sh --arch arm64 || {
        echo "❌ arm64 打包失败，可能需要："
        echo "   1. 在 Apple Silicon Mac 上打包 arm64 版本"
        echo "   2. 或使用交叉编译工具"
    }
fi

echo ""
echo "=========================================="
echo "打包 x86_64 版本（Intel）"
echo "=========================================="
echo ""

if [ "$CURRENT_ARCH" == "x86_64" ]; then
    # 当前是 x86_64，直接打包
    ./build.sh --arch x86_64
else
    # 当前是 arm64，尝试在 x86_64 上打包（需要 Rosetta 2）
    echo "⚠️  当前系统是 arm64，尝试通过 Rosetta 2 打包 x86_64 版本..."
    arch -x86_64 ./build.sh --arch x86_64 || {
        echo "❌ x86_64 打包失败，可能需要："
        echo "   1. 在 Intel Mac 上打包 x86_64 版本"
        echo "   2. 或使用交叉编译工具"
    }
fi

echo ""
echo "=========================================="
echo "打包完成！"
echo "=========================================="
echo ""
echo "生成的文件:"
ls -lh dist/gelab-mcp-server-* 2>/dev/null || echo "  (未找到生成的文件)"
echo ""
echo "注意:"
echo "  - 如果某个架构打包失败，这是正常的（需要对应架构的 Mac）"
echo "  - 建议在对应架构的 Mac 上分别打包"
echo ""

