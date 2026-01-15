# 环境设置指南

## 问题：ModuleNotFoundError: No module named 'fastmcp'

这个错误是因为没有激活虚拟环境或没有安装依赖。

## 解决方案

### 方法 1: 使用启动脚本（推荐）

#### Linux/Mac 用户

```bash
# 使用启动脚本（会自动激活虚拟环境）
./run_server.sh

# 或传入 API key
./run_server.sh --api-key YOUR_API_KEY
```

#### Windows 用户

```cmd
REM 使用启动脚本（会自动激活虚拟环境）
run_server.bat

REM 或传入 API key
run_server.bat --api-key YOUR_API_KEY
```

### 方法 2: 手动激活虚拟环境

#### Linux/Mac 用户

```bash
# 1. 进入项目目录
cd gelab-zero

# 2. 激活虚拟环境
source venv/bin/activate

# 3. 检查依赖是否已安装
pip list | grep fastmcp

# 4. 如果未安装，安装依赖
pip install -r requirements.txt

# 5. 启动服务器
python3 mcp_server/simple_gelab_mcp_server_withcaption.py

# 或传入 API key
python3 mcp_server/simple_gelab_mcp_server_withcaption.py --api-key YOUR_API_KEY
```

#### Windows 用户

```cmd
REM 1. 进入项目目录
cd gelab-zero

REM 2. 激活虚拟环境
venv\Scripts\activate

REM 3. 检查依赖是否已安装
pip list | findstr fastmcp

REM 4. 如果未安装，安装依赖
pip install -r requirements.txt

REM 5. 启动服务器
python mcp_server\simple_gelab_mcp_server_withcaption.py

REM 或传入 API key
python mcp_server\simple_gelab_mcp_server_withcaption.py --api-key YOUR_API_KEY
```

### 方法 3: 创建新的虚拟环境

如果虚拟环境有问题，可以重新创建：

#### Linux/Mac 用户

```bash
# 1. 删除旧的虚拟环境（可选）
rm -rf venv

# 2. 创建新的虚拟环境
python3 -m venv venv

# 3. 激活虚拟环境
source venv/bin/activate

# 4. 升级 pip
pip install --upgrade pip

# 5. 安装依赖
pip install -r requirements.txt

# 6. 验证安装
python3 -c "import fastmcp; print('fastmcp 安装成功')"
```

#### Windows 用户

```cmd
REM 1. 删除旧的虚拟环境（可选）
rmdir /s /q venv

REM 2. 创建新的虚拟环境
python -m venv venv

REM 3. 激活虚拟环境
venv\Scripts\activate

REM 4. 升级 pip
python -m pip install --upgrade pip

REM 5. 安装依赖
pip install -r requirements.txt

REM 6. 验证安装
python -c "import fastmcp; print('fastmcp 安装成功')"
```

## 验证环境

运行以下命令验证环境是否正确设置：

#### Linux/Mac 用户

```bash
# 激活虚拟环境
source venv/bin/activate

# 检查关键依赖
python3 -c "import fastmcp; print('✓ fastmcp')"
python3 -c "import yaml; print('✓ yaml')"
python3 -c "import openai; print('✓ openai')"
python3 -c "import PIL; print('✓ PIL')"
```

#### Windows 用户

```cmd
REM 激活虚拟环境
venv\Scripts\activate

REM 检查关键依赖
python -c "import fastmcp; print('✓ fastmcp')"
python -c "import yaml; print('✓ yaml')"
python -c "import openai; print('✓ openai')"
python -c "import PIL; print('✓ PIL')"
```

## 常见问题

### Q: 为什么需要虚拟环境？

A: 虚拟环境可以隔离项目依赖，避免与系统 Python 或其他项目的依赖冲突。

### Q: 每次都需要激活虚拟环境吗？

A: 是的，每次在新的终端窗口中运行都需要激活。或者使用启动脚本自动处理：
- Linux/Mac: `./run_server.sh`
- Windows: `run_server.bat`

### Q: 如何退出虚拟环境？

A: 运行 `deactivate` 命令。

### Q: 打包时需要使用虚拟环境吗？

A: 是的，建议在虚拟环境中打包，确保依赖完整。

## 下一步

环境设置完成后，可以：

1. **运行服务器**：
   - Linux/Mac: `./run_server.sh`
   - Windows: `run_server.bat`
2. **打包应用**：
   - Linux/Mac: `./build.sh`
   - Windows: `build.bat`
3. **查看文档**：`README_CN.md`

