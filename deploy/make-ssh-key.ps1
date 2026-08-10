# Генерация SSH-ключа для деплоя (запускаете ВЫ в PowerShell).
# Пароль от VPS в чат не отправляйте.

$ErrorActionPreference = "Stop"
$key = Join-Path $env:USERPROFILE ".ssh\id_ed25519_hungerbot"
$pub = "$key.pub"

New-Item -ItemType Directory -Force -Path (Join-Path $env:USERPROFILE ".ssh") | Out-Null

if (-not (Test-Path $key)) {
    ssh-keygen -t ed25519 -f $key -N '""' -C "hungerbot-deploy"
    Write-Host "Ключ создан: $key"
} else {
    Write-Host "Ключ уже есть: $key"
}

Write-Host ""
Write-Host "=== ВАШ ПУБЛИЧНЫЙ КЛЮЧ (его можно добавить на VPS) ==="
Get-Content $pub
Write-Host "========================================================="
Write-Host ""
Write-Host "Дальше на ВАШЕМ ПК (подставит пароль только в вашем терминале):"
Write-Host 'type $env:USERPROFILE\.ssh\id_ed25519_hungerbot.pub | ssh root@SERVER "mkdir -p ~/.ssh && chmod 700 ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"'
