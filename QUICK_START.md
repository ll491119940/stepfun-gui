# 快速开始 - 打包和使用 GELab-Zero MCP Server

## 一、打包步骤

### macOS / Linux

```bash
# 1. 进入项目目录
cd gelab-zero

# 2. 确保在虚拟环境中（推荐）
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# 或
.\venv\Scripts\activate  # Windows

# 3. 安装依赖
pip install -r requirements.txt
pip install pyinstaller

# 4. 执行打包
./build.sh

# 或手动打包
pyinstaller --clean --noconfirm gelab_mcp_server.spec
```

### Windows

```cmd
REM 1. 进入项目目录
cd gelab-zero

REM 2. 确保在虚拟环境中（推荐）
python -m venv venv
venv\Scripts\activate

REM 3. 安装依赖
pip install -r requirements.txt
pip install pyinstaller

REM 4. 执行打包
build.bat

REM 或手动打包
pyinstaller --clean --noconfirm gelab_mcp_server.spec
```

## 二、使用打包后的可执行文件

### 基本用法

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

## 三、在 Electron 中集成

### 1. 将可执行文件添加到 Electron 项目

在 `package.json` 中配置：

```json
{
  "build": {
    "extraResources": [
      {
        "from": "gelab-zero/dist/gelab-mcp-server",
        "to": "bin/gelab-mcp-server"
      }
    ]
  }
}
```

### 2. 在 Electron 主进程中启动

```javascript
const { spawn } = require('child_process');
const path = require('path');
const { app } = require('electron');

let mcpServerProcess = null;

function startMCPServer(apiKey) {
  const isDev = process.env.NODE_ENV === 'development';
  
  let exePath, args;
  
  if (isDev) {
    // 开发环境：直接运行 Python 脚本
    exePath = 'python3';
    const scriptPath = path.join(__dirname, '../gelab-zero/mcp_server/simple_gelab_mcp_server_withcaption.py');
    args = [scriptPath, '--api-key', apiKey];
  } else {
    // 生产环境：使用打包后的可执行文件
    exePath = process.platform === 'win32' 
      ? path.join(process.resourcesPath, 'bin', 'gelab-mcp-server', 'gelab-mcp-server.exe')
      : path.join(process.resourcesPath, 'bin', 'gelab-mcp-server', 'gelab-mcp-server');
    args = ['--api-key', apiKey];
  }
  
  mcpServerProcess = spawn(exePath, args, {
    cwd: path.dirname(exePath),
    env: { ...process.env }
  });
  
  mcpServerProcess.stdout.on('data', (data) => {
    console.log(`[MCP Server] ${data}`);
  });
  
  mcpServerProcess.stderr.on('data', (data) => {
    console.error(`[MCP Server Error] ${data}`);
  });
  
  mcpServerProcess.on('exit', (code) => {
    console.log(`[MCP Server] Process exited with code ${code}`);
  });
  
  return mcpServerProcess;
}

// 应用启动时启动 MCP 服务
app.whenReady().then(() => {
  const apiKey = 'YOUR_API_KEY'; // 从配置或用户输入获取
  startMCPServer(apiKey);
});

// 应用退出时停止 MCP 服务
app.on('before-quit', () => {
  if (mcpServerProcess) {
    mcpServerProcess.kill();
  }
});
```

## 四、验证

打包完成后，可以测试可执行文件：

```bash
# 测试帮助信息
./dist/gelab-mcp-server --help

# 测试启动（需要有效的 API key）
./dist/gelab-mcp-server --api-key YOUR_API_KEY
```

如果看到类似以下输出，说明启动成功：

```
已更新 stepfun 的 API key
✓ 已通过命令行参数设置 stepfun 的 API key
正在启动 MCP 服务器，端口: 8704
模型提供商: stepfun
API key: ****xxxx
```

## 五、常见问题

### Q: 打包失败，提示缺少模块

A: 检查 `gelab_mcp_server.spec` 中的 `hiddenimports`，添加缺失的模块。

### Q: 运行时找不到配置文件

A: 确保 `mcp_server_config.yaml` 和 `model_config.yaml` 在可执行文件同一目录。

### Q: 可执行文件体积很大

A: 这是正常的，因为包含了所有 Python 依赖。可以使用 UPX 压缩（已在 spec 中启用）。

## 六、下一步

- 查看 [BUILD_README.md](./BUILD_README.md) 了解详细说明
- 查看 [README_CN.md](./README_CN.md) 了解项目完整文档

