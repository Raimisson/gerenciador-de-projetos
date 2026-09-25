<#
  Instalador do plugin Scientific Research para Windows
  ------------------------------------------------------
  Uso (PowerShell):
    1. Extraia o pacote em C:\Users\raimi\Documents\claude
    2. Abra o PowerShell e execute:
         cd C:\Users\raimi\Documents\claude
         powershell -ExecutionPolicy Bypass -File .\instalar-plugin.ps1
#>
param(
    [string]$Destino = (Join-Path $env:USERPROFILE "Documents\claude")
)

$ErrorActionPreference = "Continue"   # comandos nativos: sucesso conferido por $LASTEXITCODE
$Marketplace = "raimisson-research"
$Plugin = "scientific-research@$Marketplace"

function Info($msg)  { Write-Host "  $msg" -ForegroundColor Cyan }
function Ok($msg)    { Write-Host "  [OK] $msg" -ForegroundColor Green }
function Aviso($msg) { Write-Host "  [AVISO] $msg" -ForegroundColor Yellow }
function Erro($msg)  { Write-Host "  [ERRO] $msg" -ForegroundColor Red }

Write-Host ""
Write-Host "=== Instalação do plugin Scientific Research ===" -ForegroundColor White
Write-Host ""

# 1. Copiar os arquivos para a pasta de destino (se o script foi executado de outro lugar)
$Origem = $PSScriptRoot
if (-not (Test-Path $Destino)) { New-Item -ItemType Directory -Path $Destino | Out-Null }
if ((Resolve-Path $Origem).Path.TrimEnd('\') -ne (Resolve-Path $Destino).Path.TrimEnd('\')) {
    Info "Copiando o plugin para $Destino ..."
    Copy-Item -Path (Join-Path $Origem ".claude-plugin") -Destination $Destino -Recurse -Force
    Copy-Item -Path (Join-Path $Origem "scientific-research") -Destination $Destino -Recurse -Force
    Copy-Item -Path (Join-Path $Origem "instalar-plugin.ps1") -Destination $Destino -Force
    Copy-Item -Path (Join-Path $Origem "LEIA-ME.txt") -Destination $Destino -Force -ErrorAction SilentlyContinue
}
$Manifesto = Join-Path $Destino ".claude-plugin\marketplace.json"
$PluginJson = Join-Path $Destino "scientific-research\.claude-plugin\plugin.json"
if (-not (Test-Path $Manifesto) -or -not (Test-Path $PluginJson)) {
    Erro "Arquivos do plugin não encontrados em $Destino."
    Erro "Extraia o pacote para essa pasta (devem existir '.claude-plugin' e 'scientific-research')."
    exit 1
}
Ok "Arquivos do plugin em $Destino"

# 2. Verificar o Claude Code
if (-not (Get-Command claude -ErrorAction SilentlyContinue)) {
    Erro "O comando 'claude' (Claude Code) não foi encontrado."
    Info "Instale o Claude Code (https://code.claude.com) e execute este script novamente."
    exit 1
}
$ver = (& claude --version 2>&1 | Out-String).Trim()
Ok "Claude Code encontrado: $ver"

# 3. Verificar o Python (recomendado: hooks e scripts de validação)
$py = $null
foreach ($c in @("python", "py", "python3")) {
    if (Get-Command $c -ErrorAction SilentlyContinue) {
        try { $v = & $c --version 2>&1; if ($v -match "Python 3") { $py = "$c ($v)"; break } } catch {}
    }
}
if ($py) { Ok "Python encontrado: $py" }
else { Aviso "Python 3 não encontrado. O plugin funciona, mas sem validações automáticas e proteções (hooks). Instale em https://www.python.org/downloads/ marcando 'Add python.exe to PATH'." }

# 4. Registrar o marketplace local e instalar o plugin (reinstalação limpa, se já existir)
Info "Registrando o marketplace local..."
& claude plugin uninstall $Plugin *> $null
& claude plugin marketplace remove $Marketplace *> $null
claude plugin marketplace add "$Destino"
if ($LASTEXITCODE -ne 0) { Erro "Falha ao registrar o marketplace."; exit 1 }

Info "Instalando o plugin..."
claude plugin install $Plugin
if ($LASTEXITCODE -ne 0) { Erro "Falha ao instalar o plugin."; exit 1 }

Write-Host ""
claude plugin list
Write-Host ""
Ok "Plugin instalado a partir de $Destino"
Write-Host ""
Write-Host "Próximos passos:" -ForegroundColor White
Info "1. Feche e abra novamente o Claude Code (ou digite /reload-plugins)."
Info "2. Numa conversa, digite /scientific-research:research-project para começar."
Info "3. Leia o manual: $Destino\scientific-research\MANUAL.md"
Write-Host ""
Info "Para atualizar no futuro: substitua a pasta 'scientific-research' e execute este script de novo."
Info "Para desinstalar: claude plugin uninstall $Plugin ; claude plugin marketplace remove $Marketplace"
Write-Host ""
