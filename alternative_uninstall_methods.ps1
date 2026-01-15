# Python 3.14.2 卸载的替代方案
# 如果权限修复失败，可以尝试这些方法

Write-Host "=== Python 3.14.2 卸载替代方案 ===" -ForegroundColor Cyan
Write-Host ""

# 方案 1: 尝试直接删除 Config.Msi 文件夹
Write-Host "方案 1: 删除 Config.Msi 文件夹" -ForegroundColor Yellow
$configMsiPath = "D:\Config.Msi"
if (Test-Path $configMsiPath) {
    Write-Host "警告：删除 Config.Msi 文件夹可能会影响其他程序的卸载。" -ForegroundColor Red
    $confirm = Read-Host "是否继续删除？(Y/N)"
    if ($confirm -eq "Y" -or $confirm -eq "y") {
        try {
            Remove-Item -Path $configMsiPath -Recurse -Force -ErrorAction Stop
            Write-Host "✓ Config.Msi 文件夹已删除" -ForegroundColor Green
            Write-Host "现在可以尝试卸载 Python 3.14.2 了。" -ForegroundColor Green
        } catch {
            Write-Host "✗ 删除失败: $($_.Exception.Message)" -ForegroundColor Red
            Write-Host "需要管理员权限或文件正在被使用。" -ForegroundColor Red
        }
    }
} else {
    Write-Host "Config.Msi 文件夹不存在。" -ForegroundColor Green
}

Write-Host ""
Write-Host "方案 2: 使用 Windows 设置卸载" -ForegroundColor Yellow
Write-Host "1. 打开'设置' (Win + I)" -ForegroundColor Cyan
Write-Host "2. 进入'应用' > '已安装的应用'" -ForegroundColor Cyan
Write-Host "3. 搜索'Python 3.14.2'" -ForegroundColor Cyan
Write-Host "4. 点击'卸载'" -ForegroundColor Cyan

Write-Host ""
Write-Host "方案 3: 使用控制面板卸载" -ForegroundColor Yellow
Write-Host "1. 打开'控制面板' > '程序和功能'" -ForegroundColor Cyan
Write-Host "2. 找到'Python 3.14.2 (64-bit)'" -ForegroundColor Cyan
Write-Host "3. 右键点击 > '卸载'" -ForegroundColor Cyan

Write-Host ""
Write-Host "方案 4: 使用 Python 安装程序卸载" -ForegroundColor Yellow
Write-Host "1. 下载 Python 3.14.2 安装程序" -ForegroundColor Cyan
Write-Host "2. 运行安装程序" -ForegroundColor Cyan
Write-Host "3. 选择'Uninstall'选项" -ForegroundColor Cyan

Write-Host ""
Write-Host "方案 5: 使用第三方卸载工具" -ForegroundColor Yellow
Write-Host "推荐工具：" -ForegroundColor Cyan
Write-Host "- Revo Uninstaller (免费版)" -ForegroundColor Cyan
Write-Host "- IObit Uninstaller" -ForegroundColor Cyan
Write-Host "- Geek Uninstaller" -ForegroundColor Cyan

Write-Host ""
Write-Host "方案 6: 手动清理（高级用户）" -ForegroundColor Yellow
Write-Host "1. 停止所有 Python 进程" -ForegroundColor Cyan
Write-Host "   Get-Process python* | Stop-Process -Force" -ForegroundColor Gray
Write-Host "2. 删除 Python 安装目录" -ForegroundColor Cyan
Write-Host "   通常在: C:\Users\<用户名>\AppData\Local\Programs\Python\Python314\" -ForegroundColor Gray
Write-Host "3. 清理注册表（需谨慎）" -ForegroundColor Cyan
Write-Host "4. 从 PATH 环境变量中删除 Python 路径" -ForegroundColor Cyan

