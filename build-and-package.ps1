# 博实智能巡检平台 - 一键打包脚本

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  博实智能巡检平台 - Docker镜像打包" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# 1. 构建镜像
Write-Host "[1/5] 构建Docker镜像..." -ForegroundColor Green
docker build -f docker/Dockerfile -t boshi-inspection-platform:1.0 .
if ($LASTEXITCODE -ne 0) {
    Write-Host "`n❌ 镜像构建失败！" -ForegroundColor Red
    exit 1
}
Write-Host "✅ 镜像构建成功`n" -ForegroundColor Green

# 2. 保存镜像
Write-Host "[2/5] 保存镜像为tar文件..." -ForegroundColor Green
docker save boshi-inspection-platform:1.0 -o packages/boshi-inspection-platform-1.0.tar
if ($LASTEXITCODE -ne 0) {
    Write-Host "`n❌ 镜像保存失败！" -ForegroundColor Red
    exit 1
}
Write-Host "✅ 镜像保存成功`n" -ForegroundColor Green

# 3. 创建部署目录
$deployPath = "$env:USERPROFILE\Desktop\boshi-inspection-deploy"
Write-Host "[3/5] 创建部署目录..." -ForegroundColor Green
New-Item -Path $deployPath -ItemType Directory -Force | Out-Null
Write-Host "✅ 部署目录已创建: $deployPath`n" -ForegroundColor Green

# 4. 复制文件
Write-Host "[4/5] 复制文件到部署包..." -ForegroundColor Green
Copy-Item packages/boshi-inspection-platform-1.0.tar $deployPath -Force
Write-Host "  ✓ 已复制: boshi-inspection-platform-1.0.tar" -ForegroundColor Gray
Copy-Item docker/docker-compose.yml $deployPath -Force
Write-Host "  ✓ 已复制: docker-compose.yml" -ForegroundColor Gray
# 复制环境变量示例文件（部署时需要用户根据实际情况修改）
if (Test-Path .env.example) {
    Copy-Item .env.example "$deployPath\.env.example" -Force
    Write-Host "  ✓ 已复制: .env.example" -ForegroundColor Gray
} else {
    Write-Host "  ⚠️  .env.example 不存在，请手动创建环境变量配置文件" -ForegroundColor Yellow
}
Copy-Item scripts/init_database.sql $deployPath -Force
Write-Host "  ✓ 已复制: init_database.sql" -ForegroundColor Gray
Copy-Item packages/快速部署指南.md $deployPath -Force
Write-Host "  ✓ 已复制: 快速部署指南.md" -ForegroundColor Gray
Write-Host "✅ 所有文件复制完成`n" -ForegroundColor Green

# 5. 验证
Write-Host "[5/5] 验证部署包..." -ForegroundColor Green
Write-Host "`n部署包内容：" -ForegroundColor Cyan
Get-ChildItem $deployPath | Select-Object Name, LastWriteTime, @{Name="Size(MB)";Expression={if($_.PSIsContainer){"-"}else{[math]::Round($_.Length/1MB,2)}}} | Format-Table -AutoSize

# 验证镜像内配置
Write-Host "`n验证镜像配置..." -ForegroundColor Cyan
Write-Host "  检查 DEBUG 配置:" -ForegroundColor Gray
docker run --rm boshi-inspection-platform:1.0 cat /app/.env | Select-String "DEBUG"

Write-Host "  检查数据库配置:" -ForegroundColor Gray
docker run --rm boshi-inspection-platform:1.0 cat /app/.env | Select-String "DATABASE_URL"

Write-Host "  检查依赖版本:" -ForegroundColor Gray
docker run --rm --entrypoint pip boshi-inspection-platform:1.0 list | Select-String "bcrypt|passlib|numpy"

Write-Host "✅ 所有文件复制完成`n" -ForegroundColor Green

# 6. 压缩为zip文件
Write-Host "[6/7] 压缩部署包..." -ForegroundColor Green
$zipPath = "$env:USERPROFILE\Desktop\boshi-inspection-deploy.zip"
if (Test-Path $zipPath) {
    Remove-Item $zipPath -Force
    Write-Host "  清理旧的压缩包" -ForegroundColor Gray
}
$currentDir = Get-Location
Set-Location "$env:USERPROFILE\Desktop"
Compress-Archive -Path "boshi-inspection-deploy\*" -DestinationPath "boshi-inspection-deploy.zip" -Force
Set-Location $currentDir
Write-Host "✅ 压缩完成: boshi-inspection-deploy.zip`n" -ForegroundColor Green

# 7. 最终验证
Write-Host "[7/7] 最终验证..." -ForegroundColor Green
Write-Host "`n压缩包信息：" -ForegroundColor Cyan
Get-Item "$env:USERPROFILE\Desktop\boshi-inspection-deploy.zip" | Select-Object Name, @{Name="Size(MB)";Expression={[math]::Round($_.Length/1MB,2)}}, LastWriteTime | Format-Table -AutoSize

# 完成
Write-Host "`n========================================" -ForegroundColor Green
Write-Host "  ✅ 打包完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host "`n📦 部署文件:" -ForegroundColor Cyan
Write-Host "  • 文件夹: " -NoNewline -ForegroundColor Gray
Write-Host $deployPath -ForegroundColor Yellow
Write-Host "  • 压缩包: " -NoNewline -ForegroundColor Gray
Write-Host "$env:USERPROFILE\Desktop\boshi-inspection-deploy.zip" -ForegroundColor Yellow
Write-Host "`n📝 下一步:" -ForegroundColor Cyan
Write-Host "  1. 将压缩包 boshi-inspection-deploy.zip 传输到目标服务器" -ForegroundColor Gray
Write-Host "  2. 在目标服务器解压: unzip boshi-inspection-deploy.zip" -ForegroundColor Gray
Write-Host "  3. 参考 快速部署指南.md 进行部署" -ForegroundColor Gray
Write-Host "  4. 验证登录、文档、机器人列表等功能`n" -ForegroundColor Gray

