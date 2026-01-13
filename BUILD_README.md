# GELab-Zero MCP Server 打包说明

本文档说明如何使用 PyInstaller 将 GELab-Zero MCP Server 打包为可执行文件。

## 前置要求

1. **Python 3.12+** 环境
2. 已安装项目依赖（通过 `pip install -r requirements.txt`）
3. **PyInstaller**（打包脚本会自动安装）

## 快速开始

### macOS / Linux

```bash
# 1. 进入项目目录
cd gelab-zero

# 2. 运行打包脚本
./build.sh

# 3. 打包完成后，可执行文件位于 dist/gelab-mcp-server-<架构>
```

**macOS 架构说明**：
- 在 Apple Silicon (M1/M2/M3) Mac 上打包，默认生成 `arm64` 版本
- 在 Intel Mac 上打包，默认生成 `x86_64` 版本
- 可以指定架构：`./build.sh --arch arm64` 或 `./build.sh --arch x86_64`
- 为所有架构打包：`./build-all-archs.sh`（需要对应架构的 Mac 或 Rosetta 2）

### Windows

```cmd
REM 1. 进入项目目录
cd gelab-zero

REM 2. 运行打包脚本
build.bat

REM 3. 打包完成后，可执行文件位于 dist\gelab-mcp-server.exe
```

### 手动打包

如果不想使用脚本，也可以手动执行：

```bash
# 安装 PyInstaller（如果未安装）
pip install pyinstaller

# 执行打包
pyinstaller --clean --noconfirm gelab_mcp_server.spec
```

## 使用方法

打包完成后，可执行文件位于 `dist/` 目录下：

### 基本使用

```bash
# 使用默认配置（model_config.yaml 中的配置已包含在打包文件中）
./dist/gelab-mcp-server-arm64

# 或
./dist/gelab-mcp-server-x86_64
```

### 说明

- **使用默认配置**：打包时 `model_config.yaml` 中的 API key 已包含在可执行文件中
- **无需参数**：直接运行即可，会自动使用默认配置
- **配置文件位置**：配置文件已包含在可执行文件中，PyInstaller 会自动处理路径

### 示例

```bash
# 直接运行（使用打包时的默认配置）
./dist/gelab-mcp-server-arm64

# 应该看到类似输出：
# 正在启动 MCP 服务器，端口: 8704
```

## 打包内容

打包后的可执行文件包含：

- ✅ 所有 Python 依赖
- ✅ 项目源代码（copilot_agent_server, copilot_agent_client, copilot_front_end, tools, mcp_server）
- ✅ 配置文件（mcp_server_config.yaml, model_config.yaml）

**注意**：以下内容需要单独处理：

- ❌ ADB 工具（需要用户单独安装或打包）
- ❌ 模型文件（GELab-Zero-4B-preview，约 4-8GB，建议首次运行时下载）
- ❌ Ollama/vLLM（需要用户单独安装或打包）

## 在 Electron 中使用

### 重要说明

✅ **配置文件已包含**：打包时，`model_config.yaml` 和 `mcp_server_config.yaml` 已经包含在可执行文件中，**不需要单独复制**。

✅ **使用默认配置**：直接运行即可，会自动使用打包时 `model_config.yaml` 中的配置。

### 1. 将可执行文件添加到 Electron 项目

在 `package.json` 或 `electron-builder.yml` 中配置：

```json
{
  "build": {
    "extraResources": [
      {
        "from": "gelab-zero/dist/gelab-mcp-server-arm64",
        "to": "bin/gelab-mcp-server-arm64"
      },
      {
        "from": "gelab-zero/dist/gelab-mcp-server-x86_64",
        "to": "bin/gelab-mcp-server-x86_64"
      }
    ]
  }
}
```

### 2. 在 Electron 中启动 MCP 服务

```javascript
const { spawn } = require('child_process');
const path = require('path');
const { app } = require('electron');

// 使用默认配置（推荐）
function startMCPServer() {
  const isDev = process.env.NODE_ENV === 'development';
  const arch = process.arch; // 'arm64' 或 'x64'
  
  let exePath, args;
  
  if (isDev) {
    // 开发环境：直接运行 Python 脚本
    exePath = 'python3';
    const scriptPath = path.join(__dirname, '../gelab-zero/mcp_server/simple_gelab_mcp_server_withcaption.py');
    args = [scriptPath]; // 使用默认配置
  } else {
    // 生产环境：使用打包后的可执行文件
    const exeName = arch === 'arm64' 
      ? 'gelab-mcp-server-arm64' 
      : 'gelab-mcp-server-x86_64';
    exePath = path.join(process.resourcesPath, 'bin', exeName);
    args = []; // 使用默认配置
  }
  
  const mcpServerProcess = spawn(exePath, args, {
    cwd: path.dirname(exePath),
    env: { ...process.env }
  });
  
  mcpServerProcess.stdout.on('data', (data) => {
    console.log(`[MCP Server] ${data}`);
  });
  
  mcpServerProcess.stderr.on('data', (data) => {
    console.error(`[MCP Server Error] ${data}`);
  });
  
  return mcpServerProcess;
}

// 应用启动时启动 MCP 服务（使用默认配置）
app.whenReady().then(() => {
  startMCPServer(); // 使用打包时 model_config.yaml 中的默认配置
});
```

## 故障排除

### 问题 1: 运行时错误 `PackageNotFoundError: No package metadata was found for fastmcp`

**错误信息**：
```
importlib.metadata.PackageNotFoundError: No package metadata was found for fastmcp
```

**原因**：PyInstaller 打包后，`fastmcp` 包的元数据（`.dist-info` 目录）没有被包含，导致无法读取版本信息。

**解决方案**：代码中已经添加了运行时补丁来自动处理这个问题。补丁会在打包环境中自动使用默认版本 `2.14.2`。如果仍然遇到错误，可以：

1. **方法 1（推荐）**：设置环境变量指定 fastmcp 版本：
   ```bash
   export FASTMCP_VERSION=2.14.2  # 使用实际的 fastmcp 版本
   ./dist/gelab-mcp-server --api-key YOUR_API_KEY
   ```

2. **方法 2**：检查你的 fastmcp 版本，如果版本不是 2.14.2，可以修改 `mcp_server/simple_gelab_mcp_server_withcaption.py` 中的默认版本号。

### 问题 2: 运行时错误 `FileNotFoundError: No such file or directory: 'fakeredis/model/commands.json'`

**错误信息**：
```
FileNotFoundError: [Errno 2] No such file or directory: '.../fakeredis/model/commands.json'
```

**原因**：`fakeredis` 需要 `commands.json` 数据文件，但 PyInstaller 默认不会自动包含包的数据文件。

**解决方案**：
1. **已自动处理**：代码中已经添加了 `hook-fakeredis.py` 和 spec 文件中的自动查找逻辑，重新打包应该可以解决问题。

2. **如果仍然失败**：
   - 检查 `hook-fakeredis.py` 文件是否存在
   - 确保 spec 文件中的 `hookspath=['.']` 已设置
   - 手动检查 fakeredis 的安装位置：
     ```bash
     python3 -c "import fakeredis; import os; print(os.path.dirname(fakeredis.__file__))"
     ```

### 问题 3: 运行时错误 `ModuleNotFoundError: No module named 'lupa.lua51'`

**错误信息**：
```
ModuleNotFoundError: No module named 'lupa.lua51'
```

**原因**：`fakeredis`（fastmcp 的依赖）需要 `lupa` 包来支持 Lua 脚本功能，但 `lupa` 是一个包含 C 扩展的包，PyInstaller 可能无法自动检测。

**解决方案**：
1. **确保 lupa 已安装**：
   ```bash
   pip install lupa
   ```

2. **重新打包**：代码中已经添加了 `lupa` 相关的隐藏导入和 hook 文件，重新打包应该可以解决问题：
   ```bash
   ./build.sh
   ```

3. **如果仍然失败**：检查 `hook-lupa.py` 文件是否存在，并确保 spec 文件中的 `hookspath=['.']` 已设置。

### 问题 4: 打包失败，提示缺少模块

**解决方案**：检查 `gelab_mcp_server.spec` 文件中的 `hiddenimports` 列表，添加缺失的模块。

### 问题 5: 运行时找不到配置文件

**解决方案**：确保 `mcp_server_config.yaml` 和 `model_config.yaml` 在可执行文件同一目录，或使用绝对路径。

### 问题 6: 可执行文件体积过大

**解决方案**：
- 使用 `--onefile` 模式（但启动可能较慢）
- 排除不需要的模块（在 spec 文件的 `excludes` 中添加）
- 使用 UPX 压缩（已在 spec 中启用）

### 问题 7: macOS 架构相关问题

**问题**：在 macOS 上打包的可执行文件无法在其他架构的 Mac 上运行

**原因**：PyInstaller 打包的可执行文件是平台相关的：
- 在 `arm64` (Apple Silicon) Mac 上打包，生成的是 `arm64` 版本
- 在 `x86_64` (Intel) Mac 上打包，生成的是 `x86_64` 版本

**解决方案**：

1. **在对应架构的 Mac 上分别打包**（最推荐）：
   ```bash
   # 在 Apple Silicon Mac 上
   ./build.sh --arch arm64
   
   # 在 Intel Mac 上
   ./build.sh --arch x86_64
   ```

2. **在 ARM Mac 上打包 x86_64 版本**：
   ```bash
   # 需要先安装 x86_64 版本的 Python
   # 方法 1: 使用 Homebrew（通过 Rosetta 2）
   arch -x86_64 brew install python@3.12
   
   # 方法 2: 使用 Conda
   CONDA_SUBDIR=osx-64 conda create -n gelab-x64 python=3.12
   conda activate gelab-x64
   
   # 然后打包
   ./build.sh --arch x86_64
   ```
   
   详细说明请参考：[CROSS_COMPILE_GUIDE.md](./CROSS_COMPILE_GUIDE.md)

3. **使用全架构打包脚本**：
   ```bash
   ./build-all-archs.sh
   ```
   注意：需要安装对应架构的 Python 环境，某些情况下可能失败

3. **分发时包含架构信息**：
   - `gelab-mcp-server-arm64` - 适用于 Apple Silicon Mac
   - `gelab-mcp-server-x86_64` - 适用于 Intel Mac

4. **在 Electron 中处理**：
   ```javascript
   const arch = process.arch; // 'arm64' 或 'x64'
   const exeName = `gelab-mcp-server-${arch === 'arm64' ? 'arm64' : 'x86_64'}`;
   const exePath = path.join(process.resourcesPath, 'bin', exeName);
   ```

### 问题 8: Windows 下被杀毒软件拦截

**解决方案**：这是 PyInstaller 打包文件的常见问题，需要：
1. 添加数字签名
2. 向杀毒软件厂商提交误报
3. 使用代码签名证书

## 注意事项

1. **首次运行**：首次运行可能需要下载模型文件，确保有网络连接
2. **配置文件**：如果通过命令行传入 API key，会更新 `model_config.yaml`，请确保有写入权限
3. **端口占用**：确保指定的端口未被占用
4. **依赖环境**：打包后的可执行文件仍需要 ADB 和模型推理服务（Ollama/vLLM）

## 许可证

请参考项目根目录的 LICENSE 文件。

