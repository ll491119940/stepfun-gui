# Node.js 启动 MCP 服务器指南

本文档说明如何在 Node.js 应用中启动和管理 GELab-Zero MCP Server。

## 快速开始

### 1. 基本使用

```javascript
const { MCPServerManager } = require('./nodejs-example');
const manager = new MCPServerManager();

// 启动服务器（使用默认配置）
manager.start()
  .then(() => {
    console.log('服务器已启动');
  })
  .catch((error) => {
    console.error('启动失败:', error);
  });

// 停止服务器
manager.stop();
```

### 2. 使用自定义 API key

```javascript
const { MCPServerManager } = require('./nodejs-example');

const manager = new MCPServerManager({
  apiKey: 'YOUR_API_KEY_HERE',
  provider: 'stepfun',  // 或 'local'
  port: 8704,          // 可选
});

manager.start();
```

### 3. 命令行使用

```bash
# 使用默认配置
node nodejs-example.js

# 使用自定义 API key
node nodejs-example.js --api-key YOUR_API_KEY

# 指定所有参数
node nodejs-example.js --api-key YOUR_API_KEY --provider stepfun --port 8705
```

## API 参考

### MCPServerManager 类

#### 构造函数选项

```javascript
const manager = new MCPServerManager({
  // 可执行文件路径（如果为 null，会自动检测）
  exePath: null,
  
  // 默认端口
  port: null,
  
  // 默认 API key（如果为 null，使用 model_config.yaml 中的默认配置）
  apiKey: null,
  
  // 模型提供商：'stepfun' 或 'local'
  provider: 'stepfun',
  
  // 工作目录
  cwd: process.cwd(),
  
  // 环境变量
  env: { ...process.env },
  
  // 日志回调
  onStdout: (data) => console.log(`[MCP Server] ${data}`),
  onStderr: (data) => console.error(`[MCP Server Error] ${data}`),
  
  // 进程退出回调
  onExit: (code, signal) => {
    console.log(`进程退出，代码: ${code}, 信号: ${signal}`);
  },
  
  // 错误回调
  onError: (error) => {
    console.error(`启动错误: ${error.message}`);
  },
});
```

#### 方法

##### `start()`
启动 MCP 服务器。

```javascript
manager.start()
  .then((process) => {
    console.log('服务器已启动，PID:', process.pid);
  })
  .catch((error) => {
    console.error('启动失败:', error);
  });
```

##### `stop(signal = 'SIGTERM')`
停止 MCP 服务器。

```javascript
manager.stop();           // 使用 SIGTERM（默认）
manager.stop('SIGKILL');  // 强制停止
```

##### `restart()`
重启 MCP 服务器。

```javascript
manager.restart()
  .then(() => {
    console.log('服务器已重启');
  });
```

##### `isRunning()`
检查服务器是否正在运行。

```javascript
if (manager.isRunning()) {
  console.log('服务器正在运行');
}
```

##### `getPid()`
获取进程 PID。

```javascript
const pid = manager.getPid();
console.log('服务器 PID:', pid);
```

## 完整示例

### 示例 1: 基本生命周期管理

```javascript
const { MCPServerManager } = require('./nodejs-example');

const manager = new MCPServerManager({
  apiKey: 'YOUR_API_KEY',
  onStdout: (data) => {
    console.log(`[输出] ${data}`);
  },
  onStderr: (data) => {
    console.error(`[错误] ${data}`);
  },
});

// 启动
manager.start();

// 10 秒后停止
setTimeout(() => {
  manager.stop();
}, 10000);
```

### 示例 2: 在 Express 应用中使用

```javascript
const express = require('express');
const { MCPServerManager } = require('./nodejs-example');

const app = express();
const manager = new MCPServerManager({
  apiKey: process.env.MCP_API_KEY,
  port: 8704,
});

// 启动服务器
app.listen(3000, () => {
  console.log('Express 服务器启动在端口 3000');
  manager.start();
});

// 优雅退出
process.on('SIGTERM', () => {
  console.log('正在关闭...');
  manager.stop();
  process.exit(0);
});
```

### 示例 3: 在 Electron 应用中使用

```javascript
const { app } = require('electron');
const path = require('path');
const { MCPServerManager } = require('./nodejs-example');

let manager = null;

app.whenReady().then(() => {
  manager = new MCPServerManager({
    // Electron 打包后的路径
    exePath: process.env.NODE_ENV === 'production'
      ? path.join(process.resourcesPath, 'bin', 
          `gelab-mcp-server-${process.arch === 'arm64' ? 'arm64' : 'x86_64'}`)
      : path.join(__dirname, 'dist', 
          `gelab-mcp-server-${process.arch === 'arm64' ? 'arm64' : 'x86_64'}`),
    // 使用默认配置
    apiKey: null,
  });

  manager.start();
});

app.on('before-quit', () => {
  if (manager) {
    manager.stop();
  }
});
```

### 示例 4: 自动重启和健康检查

```javascript
const { MCPServerManager } = require('./nodejs-example');

const manager = new MCPServerManager({
  apiKey: 'YOUR_API_KEY',
  onExit: (code) => {
    if (code !== 0) {
      console.error('服务器异常退出，2 秒后重启...');
      setTimeout(() => {
        manager.restart();
      }, 2000);
    }
  },
});

manager.start();

// 定期健康检查
setInterval(() => {
  if (!manager.isRunning()) {
    console.log('服务器未运行，尝试重启...');
    manager.restart();
  }
}, 5000);
```

## 可执行文件路径

`MCPServerManager` 会自动检测可执行文件路径，按以下顺序查找：

1. `options.exePath`（如果指定）
2. `./dist/gelab-mcp-server-<arch>`
3. `__dirname/dist/gelab-mcp-server-<arch>`
4. `process.cwd()/dist/gelab-mcp-server-<arch>`

如果找不到，会抛出错误。你可以通过 `options.exePath` 指定完整路径。

## 架构支持

- **arm64**: Apple Silicon (M1/M2/M3)
- **x86_64**: Intel Mac / Linux / Windows

系统架构会自动检测，无需手动指定。

## 注意事项

1. **默认配置**: 如果不提供 `--api-key`，服务器会使用打包时 `model_config.yaml` 中的默认配置。

2. **端口冲突**: 如果指定的端口已被占用，服务器启动会失败。确保端口可用。

3. **进程管理**: 建议在应用退出时调用 `stop()` 方法，确保进程被正确清理。

4. **错误处理**: 建议实现 `onError` 和 `onExit` 回调来处理异常情况。

5. **日志输出**: 可以通过 `onStdout` 和 `onStderr` 回调自定义日志处理。

## 故障排除

### 问题 1: 找不到可执行文件

**错误**: `找不到可执行文件: gelab-mcp-server-<arch>`

**解决方案**: 
- 确保已运行 `./build.sh` 打包服务器
- 通过 `options.exePath` 指定可执行文件的完整路径

### 问题 2: 端口已被占用

**错误**: 服务器启动失败，端口被占用

**解决方案**: 
- 使用 `--port` 参数指定其他端口
- 或者停止占用端口的其他进程

### 问题 3: 权限错误

**错误**: `EACCES: permission denied`

**解决方案**: 
- 确保可执行文件有执行权限: `chmod +x dist/gelab-mcp-server-<arch>`
- 在 macOS 上，可能需要允许可执行文件运行（系统偏好设置 > 安全性与隐私）

## 更多信息

- 查看 `BUILD_README.md` 了解打包过程
- 查看 `ELECTRON_INTEGRATION.md` 了解 Electron 集成详情
- 查看 `QUICK_START.md` 了解快速开始指南

