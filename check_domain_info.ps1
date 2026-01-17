# Domain Kayıt Sağlayıcısını Tespit Etme Scripti

$domain = "novitskyarchive.com"

Write-Host "=== novitskyarchive.com Domain Bilgileri ===" -ForegroundColor Cyan
Write-Host ""

# Nameserver'ları kontrol et
Write-Host "[1/3] Nameserver'lar kontrol ediliyor..." -ForegroundColor Yellow
try {
    $ns = Resolve-DnsName $domain -Type NS -ErrorAction Stop
    Write-Host "Nameserver'lar:" -ForegroundColor Green
    $ns | ForEach-Object { 
        Write-Host "  - $($_.NameHost)" -ForegroundColor White
    }
} catch {
    Write-Host "  Nameserver bulunamadı" -ForegroundColor Red
}

Write-Host ""

# A kaydını kontrol et
Write-Host "[2/3] A kaydı kontrol ediliyor..." -ForegroundColor Yellow
try {
    $a = Resolve-DnsName $domain -Type A -ErrorAction Stop
    Write-Host "A kaydı IP adresi:" -ForegroundColor Green
    $a | ForEach-Object {
        Write-Host "  - $($_.IPAddress)" -ForegroundColor White
    }
} catch {
    Write-Host "  A kaydı bulunamadı" -ForegroundColor Yellow
}

Write-Host ""

# TXT kayıtlarını kontrol et
Write-Host "[3/3] TXT kayıtları kontrol ediliyor..." -ForegroundColor Yellow
try {
    $txt = Resolve-DnsName $domain -Type TXT -ErrorAction Stop
    Write-Host "TXT kayıtları:" -ForegroundColor Green
    $txt | ForEach-Object {
        $value = $_.Strings -join " "
        Write-Host "  - $value" -ForegroundColor White
    }
} catch {
    Write-Host "  TXT kaydı bulunamadı" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== Öneri ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Domain kayıt sağlayıcısını bulmak için:" -ForegroundColor White
Write-Host "1. Online WHOIS sorgusu yapın:" -ForegroundColor Yellow
Write-Host "   https://whois.net" -ForegroundColor Green
Write-Host "   https://www.whois.com/whois/$domain" -ForegroundColor Green
Write-Host ""
Write-Host "2. Nameserver'lara göre tespit:" -ForegroundColor Yellow
Write-Host "   - Google Domains: ns-cloud-d*.googledomains.com" -ForegroundColor White
Write-Host "   - Cloudflare: *.cloudflare.com" -ForegroundColor White
Write-Host "   - GoDaddy: *.domaincontrol.com" -ForegroundColor White
Write-Host "   - Namecheap: *.namecheaphosting.com" -ForegroundColor White
Write-Host ""
Write-Host "3. DNS yönetim paneli:" -ForegroundColor Yellow
Write-Host "   Nameserver'lara göre DNS panelini bulun" -ForegroundColor White
Write-Host ""
