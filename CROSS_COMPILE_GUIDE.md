# 交叉编译指南 - 在 ARM Mac 上打包 x86_64 版本

## 概述

在 Apple Silicon (ARM) Mac 上可以打包 x86_64 版本，但需要安装 x86_64 版本的 Python 环境。

## 方法 1: 使用 Homebrew 安装 x86_64 Python（推荐）

### 步骤

1. **安装 x86_64 版本的 Python**：
   ```bash
   # 通过 Rosetta 2 安装 x86_64 Python
   arch -x86_64 /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   
   # 或直接安装 Python（如果 Homebrew 已支持）
   arch -x86_64 brew install python@3.12
   ```

2. **验证安装**：
   ```bash
   arch -x86_64 python3 --version
   ```

3. **打包 x86_64 版本**：
   ```bash
   ./build.sh --arch x86_64
   ```

## 方法 2: 使用 Conda/Miniforge（推荐用于隔离环境）

### 步骤

1. **安装 Miniforge**（如果未安装）：
   ```bash
   curl -L -O "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh"
   bash Miniforge3-$(uname)-$(uname -m).sh
   ```

2. **创建 x86_64 环境**：
   ```bash
   # 设置 conda 使用 x86_64 子目录
   CONDA_SUBDIR=osx-64 conda create -n gelab-x64 python=3.12
   conda activate gelab-x64
   
   # 确保环境使用 x86_64
   conda config --env --set subdir osx-64
   ```

3. **安装依赖**：
   ```bash
   pip install -r requirements.txt
   pip install pyinstaller lupa
   ```

4. **打包**：
   ```bash
   ./build.sh --arch x86_64
   ```

## 方法 3: 使用 Docker（最可靠）

### 步骤

1. **创建 Dockerfile**：
   ```dockerfile
   FROM python:3.12-slim
   
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   RUN pip install pyinstaller lupa
   
   COPY . .
   CMD ["python", "mcp_server/simple_gelab_mcp_server_withcaption.py"]
   ```

2. **使用 Docker 打包**：
   ```bash
   # 构建镜像
   docker build -t gelab-builder .
   
   # 在容器中打包
   docker run --rm -v $(pwd):/output gelab-builder \
     pyinstaller --clean --noconfirm gelab_mcp_server.spec
   ```

## 方法 4: 使用 Rosetta 2 终端（简单但可能有限制）

### 步骤

1. **打开 Rosetta 2 终端**：
   ```bash
   # 在终端中运行
   arch -x86_64 $SHELL
   ```

2. **安装 Python 和依赖**：
   ```bash
   # 在这个终端中安装 Python
   brew install python@3.12
   
   # 安装依赖
   pip install -r requirements.txt
   pip install pyinstaller lupa
   ```

3. **打包**：
   ```bash
   ./build.sh --arch x86_64
   ```

## 验证

打包后验证架构：

```bash
# 检查可执行文件的架构
file dist/gelab-mcp-server-x86_64

# 应该显示：
# dist/gelab-mcp-server-x86_64: Mach-O 64-bit executable x86_64
```

## 常见问题

### Q: 为什么需要 x86_64 Python？

A: PyInstaller 会使用当前 Python 环境的架构来打包。如果使用 ARM Python，打包出来的也是 ARM 版本。

### Q: 可以同时打包两个架构吗？

A: 可以，使用 `./build-all-archs.sh` 脚本，但需要确保两个架构的 Python 环境都已安装。

### Q: 打包失败怎么办？

A: 
1. 确保使用的是对应架构的 Python
2. 检查依赖是否都已安装（特别是包含 C 扩展的包，如 lupa）
3. 某些 C 扩展可能不支持交叉编译，需要在实际架构上打包

### Q: 推荐哪种方法？

A: 
- **个人开发**：方法 1（Homebrew）或方法 2（Conda）
- **CI/CD**：方法 3（Docker）或方法 4（Rosetta 2）
- **最简单**：在对应架构的 Mac 上分别打包

## 注意事项

1. **C 扩展限制**：某些包含 C 扩展的包（如 lupa）可能无法在交叉编译环境中正常工作
2. **性能影响**：通过 Rosetta 2 运行 x86_64 Python 会有性能损失
3. **依赖问题**：确保所有依赖都有对应架构的版本

## 推荐方案

**最佳实践**：
- 在 Apple Silicon Mac 上打包 arm64 版本
- 在 Intel Mac 上打包 x86_64 版本
- 或使用 CI/CD 在不同架构的机器上分别打包

