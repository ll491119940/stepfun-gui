# Python 3.14.2 卸载指南

## 问题描述
卸载 Python 3.14.2 时遇到权限错误：
- 错误：无法设置文件安全权限
- 文件：`D:\Config.Msi\44ef5f10.rbf`
- 错误代码：5（访问被拒绝）

## 解决方案

### 方案 1：以管理员身份卸载（最简单）

1. **关闭所有 Python 相关程序**
   - 关闭所有正在运行的 Python 脚本
   - 关闭 IDE（如 VS Code、PyCharm 等）
   - 关闭命令行窗口

2. **以管理员身份运行卸载程序**
   - 按 `Win + X`，选择"Windows PowerShell (管理员)"或"终端 (管理员)"
   - 或者右键点击"开始"菜单，选择"Windows PowerShell (管理员)"

3. **通过设置卸载**
   - 打开"设置" > "应用" > "已安装的应用"
   - 搜索"Python 3.14.2"
   - 点击"卸载"

### 方案 2：修复 Config.Msi 文件夹权限

1. **以管理员身份运行 PowerShell**

2. **执行修复脚本**
   ```powershell
   .\fix_config_msi_permissions.ps1
   ```

3. **或者手动修复权限**
   ```powershell
   # 获取当前用户
   $currentUser = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
   
   # 修复 D:\Config.Msi 权限
   $configMsiPath = "D:\Config.Msi"
   $acl = Get-Acl $configMsiPath
   $permission = $currentUser, "FullControl", "ContainerInherit,ObjectInherit", "None", "Allow"
   $accessRule = New-Object System.Security.AccessControl.FileSystemAccessRule $permission
   $acl.SetAccessRule($accessRule)
   Set-Acl $configMsiPath $acl
   ```

### 方案 3：使用 Python 官方卸载工具

1. 下载 Python 3.14.2 安装程序
2. 运行安装程序，选择"Uninstall"

### 方案 4：手动清理（不推荐，除非其他方法都失败）

1. **停止所有 Python 进程**
   ```powershell
   Get-Process python* | Stop-Process -Force
   ```

2. **删除 Python 安装目录**
   - 通常位于：`C:\Users\<用户名>\AppData\Local\Programs\Python\Python314\`
   - 或：`C:\Python314\`

3. **清理注册表**（需要谨慎）
   - 按 `Win + R`，输入 `regedit`
   - 搜索并删除 Python 3.14.2 相关项
   - **注意：修改注册表有风险，建议先备份**

4. **删除环境变量**
   - 打开"系统属性" > "环境变量"
   - 从 PATH 中删除 Python 3.14.2 相关路径

### 方案 5：使用第三方卸载工具

可以使用专业的卸载工具，如：
- Revo Uninstaller
- IObit Uninstaller
- Geek Uninstaller

这些工具可以强制删除并清理残留文件。

## 推荐操作顺序

1. ✅ 先尝试方案 1（以管理员身份卸载）
2. ✅ 如果失败，尝试方案 2（修复权限）
3. ✅ 如果还是失败，尝试方案 3（使用官方卸载工具）
4. ⚠️ 最后才考虑方案 4（手动清理）

## 卸载后验证

卸载完成后，检查：
```powershell
# 检查 Python 是否还在
where.exe python

# 检查 Python 版本
python --version
```


