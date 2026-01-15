# 快速修复 Config.Msi 权限 - 需要管理员权限运行
# 右键点击 PowerShell，选择"以管理员身份运行"

# 检查是否以管理员身份运行
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "错误：此脚本需要管理员权限！" -ForegroundColor Red
    Write-Host "请右键点击 PowerShell，选择'以管理员身份运行'，然后重新执行此脚本。" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "快速操作：" -ForegroundColor Cyan
    Write-Host "1. 按 Win + X，选择'Windows PowerShell (管理员)'" -ForegroundColor Cyan
    Write-Host "2. 或者右键点击开始菜单，选择'Windows PowerShell (管理员)'" -ForegroundColor Cyan
    exit 1
}

$configMsiPath = "D:\Config.Msi"

Write-Host "正在修复 $configMsiPath 的权限..." -ForegroundColor Yellow

try {
    if (-not (Test-Path $configMsiPath)) {
        Write-Host "Config.Msi 文件夹不存在，可能不需要修复。" -ForegroundColor Yellow
        exit 0
    }
    
    # 获取当前用户
    $currentUser = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
    Write-Host "当前用户: $currentUser" -ForegroundColor Cyan
    
    # 尝试获取 ACL
    try {
        $acl = Get-Acl $configMsiPath -ErrorAction Stop
    } catch {
        Write-Host "无法读取文件夹权限，尝试使用 takeown 命令获取所有权..." -ForegroundColor Yellow
        
        # 使用 takeown 命令获取所有权
        $takeownResult = Start-Process -FilePath "takeown.exe" -ArgumentList "/F", "`"$configMsiPath`"", "/R", "/D", "Y" -Wait -NoNewWindow -PassThru
        
        if ($takeownResult.ExitCode -eq 0) {
            Write-Host "✓ 已获取文件夹所有权" -ForegroundColor Green
            $acl = Get-Acl $configMsiPath
        } else {
            Write-Host "✗ takeown 命令执行失败，退出代码: $($takeownResult.ExitCode)" -ForegroundColor Red
            throw "无法获取文件夹权限"
        }
    }
    
    # 设置完全控制权限
    $permission = $currentUser, "FullControl", "ContainerInherit,ObjectInherit", "None", "Allow"
    $accessRule = New-Object System.Security.AccessControl.FileSystemAccessRule $permission
    $acl.SetAccessRule($accessRule)
    Set-Acl $configMsiPath $acl -ErrorAction Stop
    
    Write-Host "✓ 权限修复成功！" -ForegroundColor Green
    Write-Host "现在可以尝试卸载 Python 3.14.2 了。" -ForegroundColor Green
    
} catch {
    Write-Host "✗ 修复失败: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "替代方案：" -ForegroundColor Yellow
    Write-Host "1. 尝试手动删除整个 Config.Msi 文件夹（如果不再需要）" -ForegroundColor Cyan
    Write-Host "2. 使用第三方卸载工具（如 Revo Uninstaller）" -ForegroundColor Cyan
    Write-Host "3. 重启电脑后再尝试卸载" -ForegroundColor Cyan
    exit 1
}


