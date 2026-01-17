# Google Workspace Domain DNS Kayıtları - Çözüm

## ❌ Sorun
Squarespace, Google Workspace üzerinden yönetilen domain'lerin DNS kayıtlarını düzenlemiyor.

## ✅ Çözüm: DNS Kayıtlarını Nerede Eklemeliyiz?

`novitskyarchive.com` Google Workspace'te birincil domain olarak görünüyor. DNS kayıtları şu yerlerden biri üzerinden yönetiliyor olabilir:

### Seçenek 1: Google Domains (Eğer domain orada kayıtlıysa)
- Domain Google Domains'te kayıtlıysa → Orada DNS ayarları var

### Seçenek 2: Başka bir Domain Registrar
- Domain başka bir sağlayıcıda kayıtlıysa → O sağlayıcının DNS panelinden yönetilmeli

### Seçenek 3: Google Workspace DNS Ayarları
- Bazı durumlarda Google Workspace kendi DNS'ini yönetir

---

## 🔍 Domain Kayıt Sağlayıcısını Bulma

### Yöntem 1: WHOIS Sorgusu
Domain'in nerede kayıtlı olduğunu bulmak için:

**PowerShell'de:**
```powershell
# WHOIS sorgusu (PowerShell 7+ gerekir)
Invoke-RestMethod -Uri "https://www.whoisxmlapi.com/whoisserver/WhoisService?apiKey=free&domainName=novitskyarchive.com&outputFormat=JSON"
```

**Online araçlar:**
- https://whois.net
- https://www.whois.com/whois/novitskyarchive.com

### Yöntem 2: DNS Nameserver Kontrolü
```powershell
# DNS nameserver'ları kontrol et
Resolve-DnsName novitskyarchive.com -Type NS
```

---

## 📋 Google Workspace DNS Ayarlarına Erişim

### Adım 1: Google Admin Console
1. https://admin.google.com → Giriş yapın
2. **Hesap** → **Alanlar** → **Alanları yönetin**
3. `novitskyarchive.com` üzerine tıklayın → **"Ayrıntıları Göster"**

### Adım 2: DNS Ayarlarını Kontrol Et
- Eğer **"DNS kayıtlarını göster"** veya **"DNS Settings"** seçeneği varsa
- Oradan DNS kayıtlarını ekleyebilirsiniz

### Adım 3: Alternatif - Gelişmiş DNS Ayarları
- Google Workspace Admin Console'da **"Gelişmiş ayarlar"** bölümünü kontrol edin
- **"DNS Configuration"** veya benzeri bir seçenek olabilir

---

## 🌐 DNS Kayıtlarını Nerede Eklemeli?

### Senaryo A: Domain Google Domains'te Kayıtlı
1. https://domains.google.com adresine gidin
2. `novitskyarchive.com` domain'ini seçin
3. **"DNS"** sekmesine gidin
4. Cloud Console'dan kopyaladığınız kayıtları buraya ekleyin

### Senaryo B: Domain Başka Bir Registrar'da Kayıtlı
1. Domain kayıt sağlayıcınızın kontrol panelinde giriş yapın
2. DNS yönetimi bölümüne gidin
3. Cloud Console'dan kopyaladığınız kayıtları ekleyin

**Yaygın Domain Registrar'lar:**
- Namecheap
- GoDaddy
- Cloudflare
- AWS Route 53
- Name.com
- vs.

### Senaryo C: Google Workspace DNS (Yerleşik)
1. Google Admin Console → Domain Settings
2. **"DNS records"** veya **"Custom DNS records"** bölümünü bulun
3. Kayıtları buraya ekleyin

---

## 🛠️ Domain Kayıt Sağlayıcısını Tespit Etme Scripti

Aşağıdaki PowerShell script'i domain'in nerede kayıtlı olduğunu bulmaya yardımcı olur:

```powershell
# Domain bilgilerini kontrol et
$domain = "novitskyarchive.com"

Write-Host "=== Domain Bilgileri ===" -ForegroundColor Cyan
Write-Host ""

# Nameserver'ları göster
Write-Host "Nameserver'lar:" -ForegroundColor Yellow
try {
    $ns = Resolve-DnsName $domain -Type NS -ErrorAction Stop
    $ns | ForEach-Object { Write-Host "  - $($_.NameHost)" }
} catch {
    Write-Host "  Nameserver bulunamadı" -ForegroundColor Red
}

Write-Host ""
Write-Host "Nameserver'lara göre tespit:" -ForegroundColor Yellow
Write-Host "  - Google Domains: ns-cloud-d1.googledomains.com" -ForegroundColor White
Write-Host "  - Google Workspace: ghs.googlehosted.com" -ForegroundColor White
Write-Host "  - Cloudflare: nameserver'lar cloudflare ile başlar" -ForegroundColor White
Write-Host ""
Write-Host "Domain'i kontrol etmek için:" -ForegroundColor Cyan
Write-Host "https://whois.net" -ForegroundColor Green
Write-Host "https://www.whois.com/whois/$domain" -ForegroundColor Green
```

---

## 📝 Yapılacaklar Listesi

1. [ ] Domain kayıt sağlayıcısını tespit et (WHOIS sorgusu)
2. [ ] Nameserver'ları kontrol et
3. [ ] DNS yönetim panelini bul (Google Domains / Registrar / Google Workspace)
4. [ ] Cloud Console'dan DNS kayıtlarını kopyala
5. [ ] DNS kayıtlarını doğru panele ekle
6. [ ] Doğrulamayı bekle (5-30 dakika)
7. [ ] Cloud Run domain mapping'inin "Active" olduğunu kontrol et

---

## 🔗 Hızlı Kontrol Linkleri

- **WHOIS Sorgusu:** https://www.whois.com/whois/novitskyarchive.com
- **DNS Kontrol:** https://dnschecker.org/#A/novitskyarchive.com
- **Google Domains:** https://domains.google.com (eğer orada kayıtlıysa)
- **Google Admin Console:** https://admin.google.com

---

## 💡 Öneri

Domain kayıt sağlayıcısını tespit ettikten sonra, DNS kayıtlarını doğrudan o sağlayıcının kontrol panelinden eklemek en güvenilir yoldur.
