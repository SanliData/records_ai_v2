# GitHub'a Push ve Production Deploy Rehberi

## Durum
Git Windows makinenizde kurulu değil. İki seçeneğiniz var:

---

## SEÇENEK A: Cloud Shell ile GitHub'a Push (Önerilen)

### Adım 1: Google Cloud Shell'i Açın
1. [Google Cloud Console](https://console.cloud.google.com) açın
2. Sağ üstteki **Cloud Shell** ikonuna tıklayın (terminal simgesi)
3. Terminal hazır olduğunda devam edin

### Adım 2: Repository'yi Clone Edin

```bash
cd ~
git clone https://github.com/SanliData/records_ai.git
cd records_ai
```

### Adım 3: Local Dosyaları Cloud Shell'e Yükleyin

**Yöntem 1: Cloud Shell Editor ile (Kolay)**
1. Cloud Shell'de sağ üstteki **Editor** ikonuna tıklayın (kalem simgesi)
2. Sol panelde **File → Upload Files** seçin
3. `C:\Users\issan\records_ai_v2` klasörünü ZIP olarak hazırlayın
4. ZIP dosyasını yükleyin
5. Terminalde çıkarın:
   ```bash
   unzip records_ai_v2.zip
   ```

**Yöntem 2: Komut satırı ile**
```bash
# Local'den Cloud Shell'e dosya yükleme (PowerShell'de çalıştırın)
gcloud cloud-shell scp --recurse local:* cloudshell:~/records_ai_v2
```

### Adım 4: Dosyaları Repository'ye Kopyalayın

```bash
# Cloud Shell'de
cd ~/records_ai
cp -r ~/records_ai_v2/* .
# veya eğer ZIP'ten çıkardıysanız:
cp -r ~/records_ai_v2/* .
```

### Adım 5: Git İşlemleri

```bash
cd ~/records_ai

# Durumu kontrol et
git status

# Tüm değişiklikleri ekle
git add .

# Commit oluştur
git commit -m "feat: Local changes from records_ai_v2"

# GitHub'a push et
git push origin main
```

**Not:** Eğer authentication hatası alırsanız:
1. GitHub'da Personal Access Token oluşturun:
   - Settings → Developer settings → Personal access tokens → Tokens (classic)
   - Scopes: `repo` seçin
2. Token ile push edin:
   ```bash
   git push https://YOUR_TOKEN@github.com/SanliData/records_ai.git main
   ```

---

## SEÇENEK B: Git Kurulumu (Uzun Vadeli Çözüm)

### Windows'ta Git Kurulumu

1. **Git for Windows İndirin:**
   - https://git-scm.com/download/win
   - İndirilen `.exe` dosyasını çalıştırın
   - Kurulum sırasında varsayılan ayarları kullanın

2. **PowerShell'i Yeniden Başlatın:**
   - Mevcut PowerShell penceresini kapatın
   - Yeni bir PowerShell penceresi açın

3. **Git Kurulumunu Kontrol Edin:**
   ```powershell
   git --version
   # Çıktı: git version 2.x.x
   ```

4. **Git Kullanıcı Bilgilerini Ayarlayın:**
   ```powershell
   git config --global user.name "Your Name"
   git config --global user.email "your_email@example.com"
   ```

5. **Repository'yi Kontrol Edin:**
   ```powershell
   cd C:\Users\issan\records_ai_v2
   git remote -v
   # Eğer remote yoksa:
   git remote add origin https://github.com/SanliData/records_ai.git
   ```

6. **Push İşlemi:**
   ```powershell
   git add .
   git commit -m "feat: Local changes from records_ai_v2"
   git push origin main
   ```

---

## Production Deployment

GitHub'a push işlemi tamamlandıktan sonra production'a deploy edebilirsiniz:

### PowerShell'de Deploy

```powershell
cd C:\Users\issan\records_ai_v2

# Deploy script'ini çalıştır
.\QUICK_DEPLOY.ps1

# VEYA manuel olarak:
gcloud run deploy records-ai-v2 `
  --source . `
  --platform managed `
  --region europe-west1 `
  --allow-unauthenticated `
  --port 8080
```

**Not:** `--source .` parametresi local dosyaları kullanır. GitHub'dan deploy etmek için Cloud Build trigger kurmanız gerekir.

---

## Hızlı Özet (Cloud Shell)

```bash
# 1. Cloud Shell'i aç
# 2. Repository'yi clone et
cd ~ && git clone https://github.com/SanliData/records_ai.git && cd records_ai

# 3. Local dosyaları yükle (Editor → Upload Files)
# 4. Dosyaları kopyala
cp -r ~/records_ai_v2/* .

# 5. Git işlemleri
git add .
git commit -m "feat: Local changes"
git push origin main
```

---

## Sorun Giderme

### "Permission denied" hatası
- GitHub Personal Access Token kullanın

### "Repository not found" hatası
- Repository URL'ini kontrol edin
- Repository'nin public veya erişiminizin olduğundan emin olun

### "Authentication failed" hatası
- Token oluşturun ve kullanın
- Veya SSH key kurulumu yapın

---

**Son Güncelleme:** 2026-01-13
