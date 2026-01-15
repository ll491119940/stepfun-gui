# 部署说明 - Windows 可执行文件

## 打包后的 exe 文件是否可以在其他电脑直接执行？

**简短回答：通常可以，但需要注意以下几点。**

## ✅ 可以直接执行的情况

PyInstaller 打包的 exe 文件是**自包含**的，包含了：
- Python 解释器
- 所有依赖的 Python 包
- 项目代码和资源文件

因此，在大多数情况下，**可以直接在其他 Windows 电脑上运行，无需安装 Python**。

## ⚠️ 可能需要的运行时依赖

### 1. Visual C++ Redistributable（最常见）

如果程序使用了包含 C 扩展的库（如 `lupa`、`opencv-python` 等），目标电脑可能需要安装：

- **Visual C++ Redistributable 2015-2022**
  - 下载地址：https://aka.ms/vs/17/release/vc_redist.x64.exe
  - 适用于 64 位 Windows
  - 大多数现代 Windows 系统已预装，但某些精简系统可能缺少

### 2. Windows 版本要求

- Windows 7 或更高版本（推荐 Windows 10/11）
- 64 位系统（如果打包的是 64 位版本）

### 3. 其他依赖

- **网络连接**：如果程序需要访问网络（API 调用等）
- **配置文件**：某些配置可能需要单独提供（如 `model_config.yaml`）

## 📦 分发建议

### 方法 1：单文件分发（当前方式）

```
gelab-mcp-server.exe  (单个文件，包含所有依赖)
```

**优点**：
- 简单，只需一个文件
- 用户无需安装任何东西

**缺点**：
- 文件较大（通常 100-300 MB）
- 启动稍慢（需要解压临时文件）

### 方法 2：目录分发（可选）

如果单文件有问题，可以修改 spec 文件使用 `--onedir` 模式：

```python
# 在 gelab_mcp_server.spec 中
exe = EXE(
    # ... 其他配置 ...
    # 改为目录模式
    # name='gelab-mcp-server',
    # ...
)

# 使用 COLLECT 创建目录
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='gelab-mcp-server',
)
```

**优点**：
- 启动更快
- 更容易调试

**缺点**：
- 需要分发整个文件夹
- 文件较多

## 🔍 测试建议

在分发前，建议在以下环境中测试：

1. **干净的 Windows 系统**（虚拟机）
   - 未安装 Python
   - 未安装 Visual C++ Redistributable（测试是否需要）

2. **不同版本的 Windows**
   - Windows 10
   - Windows 11
   - Windows Server（如果适用）

3. **不同架构**
   - 64 位系统（推荐）
   - 32 位系统（如果支持）

## 🛠️ 故障排除

### 问题 1：运行时缺少 DLL

**错误信息**：
```
The program can't start because MSVCP140.dll is missing
```

**解决方案**：
- 安装 Visual C++ Redistributable
- 或使用 `--collect-all` 选项重新打包

### 问题 2：杀毒软件误报

某些杀毒软件可能将 PyInstaller 打包的 exe 标记为可疑。

**解决方案**：
- 添加数字签名（需要代码签名证书）
- 或提供源代码让用户自行打包

### 问题 3：路径问题

如果程序使用相对路径，确保 exe 文件在正确的目录中运行。

## 📝 分发清单

分发 exe 文件时，建议包含：

1. ✅ `gelab-mcp-server.exe` - 主程序
2. ✅ `README.md` - 使用说明
3. ✅ `model_config.yaml` - 配置文件（如果需要）
4. ✅ `mcp_server_config.yaml` - 服务器配置（如果需要）
5. ⚠️ Visual C++ Redistributable 安装程序（可选，如果需要）

## 💡 最佳实践

1. **测试多个环境**：在不同配置的电脑上测试
2. **提供安装说明**：如果用户遇到问题，提供清晰的故障排除指南
3. **版本信息**：在 exe 中包含版本信息，方便用户报告问题
4. **日志功能**：确保程序能输出日志，方便调试

## 🔗 相关资源

- [PyInstaller 文档](https://pyinstaller.org/)
- [Visual C++ Redistributable 下载](https://aka.ms/vs/17/release/vc_redist.x64.exe)
- [Windows 兼容性指南](https://docs.microsoft.com/windows/win32/winprog/using-the-windows-headers)

