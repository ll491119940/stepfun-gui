# 打包检查清单

## 打包前检查

### 1. 确认配置文件中的 API Key

✅ **检查 `model_config.yaml`**：
```bash
cat model_config.yaml
```

确保 `stepfun` 或 `local` 的 `api_key` 已正确设置：
```yaml
stepfun:
    api_base: "https://api.stepfun.com/v1"
    api_key: "YOUR_API_KEY"  # 确保这里有正确的 key
```

### 2. 确认依赖已安装

```bash
# 激活虚拟环境
source venv/bin/activate

# 检查关键依赖
python3 -c "import fastmcp; print('✓ fastmcp')"
python3 -c "import lupa; print('✓ lupa')"
python3 -c "import fakeredis; print('✓ fakeredis')"
```

### 3. 测试运行（开发环境）

```bash
# 使用默认配置测试
python3 mcp_server/simple_gelab_mcp_server_withcaption.py
```

应该能正常启动，使用 `model_config.yaml` 中的默认配置。

## 打包步骤

### 1. 清理之前的构建

```bash
rm -rf build/ dist/
```

### 2. 执行打包

```bash
# macOS/Linux
./build.sh

# 或指定架构
./build.sh --arch arm64
./build.sh --arch x86_64
```

### 3. 验证打包结果

```bash
# 检查生成的文件
ls -lh dist/gelab-mcp-server-*

# 测试可执行文件（使用默认配置）
./dist/gelab-mcp-server-arm64

# 应该看到类似输出：
# 正在启动 MCP 服务器，端口: 8704
# 模型提供商: stepfun
```

## 打包后验证

### 1. 测试默认配置

```bash
# 不传任何参数，应该使用 model_config.yaml 中的默认配置
./dist/gelab-mcp-server-arm64
```

### 2. 验证默认配置

```bash
# 直接运行，应该使用 model_config.yaml 中的默认配置
./dist/gelab-mcp-server-arm64

# 检查输出，确认使用了正确的配置
```

## 在 Electron 中使用

### 必需文件

只需要打包后的可执行文件：
- `dist/gelab-mcp-server-arm64` (Apple Silicon)
- `dist/gelab-mcp-server-x86_64` (Intel Mac)

**不需要单独复制配置文件**，它们已经包含在可执行文件中。

### Electron 配置

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

### 启动代码

```javascript
// 使用默认配置（不传 --api-key）
const arch = process.arch;
const exeName = arch === 'arm64' 
  ? 'gelab-mcp-server-arm64' 
  : 'gelab-mcp-server-x86_64';
const exePath = path.join(process.resourcesPath, 'bin', exeName);

const mcpServerProcess = spawn(exePath, [], {
  cwd: path.dirname(exePath),
  env: { ...process.env }
});
```

## 常见问题

### Q: 打包后找不到配置文件？

A: 配置文件已经包含在可执行文件中，PyInstaller 会自动处理路径。如果遇到问题，检查 spec 文件中的 `datas` 列表是否包含配置文件。

### Q: 如何确认使用了默认配置？

A: 启动时不传 `--api-key` 参数，会使用打包时 `model_config.yaml` 中的配置。

### Q: 打包后如何更新 API key？

A: 需要重新打包：
1. 修改 `model_config.yaml` 中的 API key
2. 重新执行打包：`./build.sh`
3. 新的可执行文件会包含更新后的配置

## 总结

✅ **当前配置已支持**：
- 打包时包含 `model_config.yaml` 和 `mcp_server_config.yaml`
- 直接运行使用默认配置（model_config.yaml 中的配置）
- 配置文件路径在打包环境中自动处理

✅ **Electron 集成**：
- 只需要打包后的可执行文件
- 不需要单独复制配置文件
- 直接启动即可使用默认配置

