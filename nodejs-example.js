/**
 * Node.js 启动 GELab-Zero MCP Server 示例
 * 
 * 使用方法：
 *   node nodejs-example.js
 * 
 * 或者作为模块导入：
 *   const { MCPServerManager } = require('./nodejs-example');
 */

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

class MCPServerManager {
  constructor(options = {}) {
    this.process = null;
    this.options = {
      // 可执行文件路径（如果为 null，会自动检测）
      exePath: options.exePath || null,
      // 默认端口
      port: options.port || null,
      // 默认 API key（如果为 null，使用 model_config.yaml 中的默认配置）
      apiKey: options.apiKey || null,
      // 模型提供商：'stepfun' 或 'local'
      provider: options.provider || 'stepfun',
      // 工作目录
      cwd: options.cwd || process.cwd(),
      // 环境变量
      env: options.env || { ...process.env },
      // 日志回调
      onStdout: options.onStdout || ((data) => console.log(`[MCP Server] ${data}`)),
      onStderr: options.onStderr || ((data) => console.error(`[MCP Server Error] ${data}`)),
      // 进程退出回调
      onExit: options.onExit || ((code, signal) => {
        console.log(`[MCP Server] 进程退出，代码: ${code}, 信号: ${signal}`);
      }),
      // 错误回调
      onError: options.onError || ((error) => {
        console.error(`[MCP Server] 启动错误: ${error.message}`);
      }),
    };
  }

  /**
   * 检测系统架构
   * @returns {string} 'arm64' 或 'x86_64'
   */
  detectArchitecture() {
    const arch = process.arch;
    if (arch === 'arm64') {
      return 'arm64';
    } else if (arch === 'x64' || arch === 'x86_64') {
      return 'x86_64';
    } else {
      throw new Error(`不支持的架构: ${arch}`);
    }
  }

  /**
   * 获取可执行文件路径
   * @returns {string} 可执行文件的完整路径
   */
  getExecutablePath() {
    if (this.options.exePath) {
      return this.options.exePath;
    }

    // 自动检测可执行文件路径
    const arch = this.detectArchitecture();
    const exeName = `gelab-mcp-server-${arch}`;
    
    // 尝试多个可能的路径
    const possiblePaths = [
      // 当前目录的 dist 文件夹
      path.join(this.options.cwd, 'dist', exeName),
      // 相对于当前文件的路径（如果在 gelab-zero 目录中）
      path.join(__dirname, 'dist', exeName),
      // 绝对路径（如果可执行文件在特定位置）
      path.join(process.cwd(), 'dist', exeName),
    ];

    for (const exePath of possiblePaths) {
      if (fs.existsSync(exePath)) {
        return exePath;
      }
    }

    throw new Error(`找不到可执行文件: ${exeName}。请检查路径或通过 options.exePath 指定。`);
  }

  /**
   * 构建命令行参数
   * @returns {string[]} 命令行参数数组
   */
  buildArgs() {
    const args = [];

    // 添加 API key（如果提供）
    if (this.options.apiKey) {
      args.push('--api-key', this.options.apiKey);
    }

    // 添加 provider（如果提供）
    if (this.options.provider) {
      args.push('--provider', this.options.provider);
    }

    // 添加端口（如果提供）
    if (this.options.port) {
      args.push('--port', this.options.port.toString());
    }

    return args;
  }

  /**
   * 启动 MCP 服务器
   * @returns {Promise<ChildProcess>} 返回子进程对象
   */
  start() {
    // 如果已经运行，先停止
    if (this.process) {
      console.warn('[MCP Server] 服务器已在运行，先停止旧进程...');
      this.stop();
    }

    try {
      const exePath = this.getExecutablePath();
      const args = this.buildArgs();

      console.log(`[MCP Server] 启动服务器: ${exePath}`);
      console.log(`[MCP Server] 参数: ${args.join(' ')}`);

      this.process = spawn(exePath, args, {
        cwd: path.dirname(exePath),
        env: this.options.env,
        stdio: ['ignore', 'pipe', 'pipe'], // 忽略 stdin，捕获 stdout 和 stderr
      });

      // 处理标准输出
      this.process.stdout.on('data', (data) => {
        const output = data.toString().trim();
        if (output) {
          this.options.onStdout(output);
        }
      });

      // 处理标准错误
      this.process.stderr.on('data', (data) => {
        const output = data.toString().trim();
        if (output) {
          this.options.onStderr(output);
        }
      });

      // 处理进程退出
      this.process.on('exit', (code, signal) => {
        this.process = null;
        this.options.onExit(code, signal);
      });

      // 处理启动错误
      this.process.on('error', (error) => {
        this.process = null;
        this.options.onError(error);
      });

      return Promise.resolve(this.process);
    } catch (error) {
      this.options.onError(error);
      return Promise.reject(error);
    }
  }

  /**
   * 停止 MCP 服务器
   * @param {string} signal 发送的信号，默认为 'SIGTERM'
   * @returns {boolean} 是否成功发送停止信号
   */
  stop(signal = 'SIGTERM') {
    if (!this.process) {
      return false;
    }

    try {
      console.log(`[MCP Server] 停止服务器 (信号: ${signal})...`);
      this.process.kill(signal);
      return true;
    } catch (error) {
      console.error(`[MCP Server] 停止服务器失败: ${error.message}`);
      return false;
    }
  }

  /**
   * 重启 MCP 服务器
   * @returns {Promise<ChildProcess>} 返回新的子进程对象
   */
  async restart() {
    this.stop();
    // 等待进程完全退出
    await new Promise(resolve => setTimeout(resolve, 1000));
    return this.start();
  }

  /**
   * 检查服务器是否正在运行
   * @returns {boolean}
   */
  isRunning() {
    return this.process !== null && this.process.exitCode === null;
  }

  /**
   * 获取进程 PID
   * @returns {number|null}
   */
  getPid() {
    return this.process ? this.process.pid : null;
  }
}

// ============================================
// 使用示例
// ============================================

// 示例 1: 基本使用（使用默认配置）
function example1() {
  const manager = new MCPServerManager();

  manager.start()
    .then(() => {
      console.log('MCP 服务器已启动');
    })
    .catch((error) => {
      console.error('启动失败:', error);
    });

  // 10 秒后停止
  setTimeout(() => {
    manager.stop();
  }, 10000);
}

// 示例 2: 使用自定义 API key
function example2() {
  const manager = new MCPServerManager({
    apiKey: 'YOUR_API_KEY_HERE',
    provider: 'stepfun',
    port: 8705,
    onStdout: (data) => {
      console.log(`[输出] ${data}`);
    },
    onStderr: (data) => {
      console.error(`[错误] ${data}`);
    },
    onExit: (code, signal) => {
      console.log(`服务器退出: code=${code}, signal=${signal}`);
    },
  });

  manager.start();
}

// 示例 3: 在 Electron 应用中使用
function example3() {
  // 假设在 Electron 主进程中
  const { app } = require('electron');
  const manager = new MCPServerManager({
    // Electron 打包后的路径
    exePath: process.env.NODE_ENV === 'production'
      ? path.join(process.resourcesPath, 'bin', `gelab-mcp-server-${process.arch === 'arm64' ? 'arm64' : 'x86_64'}`)
      : path.join(__dirname, 'dist', `gelab-mcp-server-${process.arch === 'arm64' ? 'arm64' : 'x86_64'}`),
    apiKey: null, // 使用默认配置
  });

  app.whenReady().then(() => {
    manager.start();
  });

  app.on('before-quit', () => {
    manager.stop();
  });
}

// 示例 4: 完整的生命周期管理
function example4() {
  const manager = new MCPServerManager({
    apiKey: 'YOUR_API_KEY',
    port: 8704,
    onStdout: (data) => {
      // 检查服务器是否已启动成功
      if (data.includes('正在启动 MCP 服务器')) {
        console.log('✓ 服务器启动成功');
      }
    },
    onExit: (code) => {
      if (code !== 0) {
        console.error('服务器异常退出，尝试重启...');
        setTimeout(() => {
          manager.restart();
        }, 2000);
      }
    },
  });

  // 启动服务器
  manager.start();

  // 定期检查服务器状态
  const healthCheck = setInterval(() => {
    if (!manager.isRunning()) {
      console.log('服务器未运行，尝试重启...');
      manager.restart();
    }
  }, 5000);

  // 优雅退出
  process.on('SIGINT', () => {
    console.log('\n正在关闭服务器...');
    clearInterval(healthCheck);
    manager.stop();
    setTimeout(() => {
      process.exit(0);
    }, 1000);
  });
}

// ============================================
// 如果直接运行此文件
// ============================================
if (require.main === module) {
  // 从命令行参数获取配置
  const args = process.argv.slice(2);
  const options = {};

  for (let i = 0; i < args.length; i++) {
    switch (args[i]) {
      case '--api-key':
        options.apiKey = args[++i];
        break;
      case '--provider':
        options.provider = args[++i];
        break;
      case '--port':
        options.port = parseInt(args[++i], 10);
        break;
      case '--exe-path':
        options.exePath = args[++i];
        break;
      case '--help':
        console.log(`
使用方法:
  node nodejs-example.js [选项]

选项:
  --api-key <key>       API key（可选，不提供则使用默认配置）
  --provider <name>     模型提供商: stepfun 或 local（默认: stepfun）
  --port <number>      服务器端口（可选）
  --exe-path <path>    可执行文件路径（可选，会自动检测）
  --help                显示此帮助信息

示例:
  # 使用默认配置启动
  node nodejs-example.js

  # 使用自定义 API key 启动
  node nodejs-example.js --api-key YOUR_API_KEY

  # 指定所有参数
  node nodejs-example.js --api-key YOUR_API_KEY --provider stepfun --port 8705
        `);
        process.exit(0);
    }
  }

  const manager = new MCPServerManager(options);

  // 启动服务器
  manager.start()
    .then(() => {
      console.log('✓ MCP 服务器已启动');
      console.log(`  PID: ${manager.getPid()}`);
      console.log('  按 Ctrl+C 停止服务器');
    })
    .catch((error) => {
      console.error('✗ 启动失败:', error.message);
      process.exit(1);
    });

  // 优雅退出处理
  process.on('SIGINT', () => {
    console.log('\n正在停止服务器...');
    manager.stop();
    setTimeout(() => {
      process.exit(0);
    }, 1000);
  });

  process.on('SIGTERM', () => {
    manager.stop();
    setTimeout(() => {
      process.exit(0);
    }, 1000);
  });
}

// 导出类供其他模块使用
module.exports = { MCPServerManager };

