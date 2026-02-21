# NANDGuard+ Windows Service Registration Script
$AppPath = "$PSScriptRoot\dist\NANDGuard+.exe"
$ServiceName = "NANDGuardService"

if (-not (Test-Path $AppPath)) {
    Write-Error "Error: NANDGuard+.exe not found in dist/. Please build it first."
    exit
}

echo "Registering NANDGuard+ as a Windows Service..."

New-Service -Name $ServiceName `
            -BinaryPathName "$AppPath --service" `
            -DisplayName "NANDGuard+ Health Monitor" `
            -Description "Background AI storage health monitoring and failure prediction." `
            -StartupType Automatic

Start-Service -Name $ServiceName

echo "Successfully registered and started the NANDGuard+ service."
