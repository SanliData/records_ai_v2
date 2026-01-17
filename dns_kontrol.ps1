# DNS Kayıt Kontrol Scripti
# novitskyarchive.com için DNS kayıtlarını kontrol eder

$domain = "novitskyarchive.com"

Write-Host "=== DNS Kayıt Kontrol ===" -ForegroundColor Cyan
Write-Host "Domain: $domain" -ForegroundColor Yellow
Write-Host ""

# TXT kayıtlarını kontrol et
Write-Host "[TXT Kayıtları]" -ForegroundColor Green
try {
    $txt = Resolve-DnsName $domain -Type TXT -ErrorAction Stop
    foreach ($record in $txt) {
        $value = $record.Strings -join " "
        if ($value -like "*google-site-verification*") {
            Write-Host "  ✓ Doğrulama TXT kaydı bulundu:" -ForegroundColor Green
            Write-Host "    $value" -ForegroundColor White
        } elseif ($value -like "*spf*") {
            Write-Host "  ✓ SPF TXT kaydı bulundu:" -ForegroundColor Green
            Write-Host "    $value" -ForegroundColor White
        } else {
            Write-Host "  - TXT: $value" -ForegroundColor White
        }
    }
} catch {
    Write-Host "  ⚠ TXT kaydı bulunamadı" -ForegroundColor Yellow
}

Write-Host ""

# CNAME kaydını kontrol et
Write-Host "[CNAME Kaydı]" -ForegroundColor Green
try {
    $cname = Resolve-DnsName $domain -Type CNAME -ErrorAction Stop
    Write-Host "  ✓ CNAME kaydı bulundu:" -ForegroundColor Green
    Write-Host "    $($cname.NameHost)" -ForegroundColor White
    if ($cname.NameHost -like "*googlehosted*") {
        Write-Host "    ✓ Google Hosted kaydı doğru görünüyor" -ForegroundColor Green
    }
} catch {
    Write-Host "  ⚠ CNAME kaydı bulunamadı (normal, A kaydı kullanılıyor olabilir)" -ForegroundColor Yellow
}

Write-Host ""

# A kaydını kontrol et
Write-Host "[A Kaydı]" -ForegroundColor Green
try {
    $a = Resolve-DnsName $domain -Type A -ErrorAction Stop
    Write-Host "  ✓ A kaydı bulundu:" -ForegroundColor Green
    foreach ($ip in $a) {
        Write-Host "    $($ip.IPAddress)" -ForegroundColor White
        if ($ip.IPAddress -like "216.239.*" -or $ip.IPAddress -like "34.*") {
            Write-Host "      ✓ Google IP aralığında (muhtemelen Cloud Run)" -ForegroundColor Green
        }
    }
} catch {
    Write-Host "  ⚠ A kaydı bulunamadı" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== Öneri ===" -ForegroundColor Cyan
Write-Host "DNS kayıtlarını kontrol etmek için:" -ForegroundColor White
Write-Host "https://dnschecker.org/#A/$domain" -ForegroundColor Green
Write-Host ""
