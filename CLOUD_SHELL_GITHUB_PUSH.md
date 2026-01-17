# Cloud Shell'den GitHub'a Push

## Adımlar

### 1. Google Cloud Shell'i Açın
1. [Google Cloud Console](https://console.cloud.google.com) → Cloud Shell açın (sağ üstte terminal ikonu)
2. Terminal hazır olduğunda devam edin

### 2. Dosyaları Cloud Shell'e Yükleyin

**Seçenek A: Cloud Shell Editor ile (Önerilen)**
1. Cloud Shell'de sağ üstteki **Editor** ikonuna tıklayın (kalem simgesi)
2. Sol panelde **File → Upload Files** seçin
3. Local'deki `C:\Users\issan\records_ai_v2` klasörünü ZIP olarak yükleyin
4. ZIP'i çıkarın: `unzip records_ai_v2.zip`

**Seçenek B: gcloud CLI ile (Alternatif)**
```bash
# Local'den Cloud Shell'e dosya yükleme (gcloud CLI gerekli)
gcloud cloud-shell scp --recurse local:* cloudshell:~/records_ai_v2
```

**Seçenek C: Cloud Shell Upload Butonu**
1. Cloud Shell terminalinde sağ üstteki **⋮** menüsü
2. **Upload file** seçin
3. Dosyaları tek tek veya ZIP olarak yükleyin

### 3. Cloud Shell'de Git Kurulumu Kontrol

```bash
# Git kontrol
git --version
# Çıktı: git version 2.x.x (genellikle önceden yüklüdür)

# Eğer yüklü değilse:
sudo apt-get update
sudo apt-get install -y git
```

### 4. Repository'yi Clone veya Initialize Edin

**Seçenek A: Mevcut Repository'yi Clone (Önerilen)**
```bash
cd ~
git clone https://github.com/SanliData/records_ai.git
cd records_ai
```

**Seçenek B: Mevcut Dosyaları Git Repository'sine Dönüştür**
```bash
cd ~/records_ai_v2  # Veya yüklediğiniz klasör
git init
git remote add origin https://github.com/SanliData/records_ai.git
git fetch origin
git branch -M main
```

### 5. Değişiklikleri Ekleyin ve Commit Edin

```bash
# Tüm değişiklikleri ekle
git add .

# Commit et
git commit -m "feat: Admin system, marketplace integration, multi-record detection, preview page, lyrics/sheet music integration"

# Veya daha detaylı:
git commit -m "feat: Major updates - Admin system with ednovitsky@archive.com and isanli058@gmail.com
- Multi-platform marketplace integration (Discogs, eBay, Etsy, Amazon)
- Multi-record detection with AI (Sherlock Holmes mode)
- Preview/confirmation page with label zoom
- Lyrics and sheet music auto-fetch integration
- Mobile-responsive design across all pages
- Updated live_book and tree documentation"
```

### 6. GitHub Authentication

**Personal Access Token ile (Önerilen)**
1. GitHub'da: Settings → Developer settings → Personal access tokens → Tokens (classic)
2. **Generate new token (classic)** tıklayın
3. Scopes: `repo` seçin
4. Token'ı kopyalayın

```bash
# Token ile push
git push https://YOUR_TOKEN@github.com/SanliData/records_ai.git main

# Veya remote'u token ile güncelle
git remote set-url origin https://YOUR_TOKEN@github.com/SanliData/records_ai.git
git push origin main
```

**SSH Key ile (Alternatif)**
```bash
# SSH key oluştur (eğer yoksa)
ssh-keygen -t ed25519 -C "your_email@example.com"

# Public key'i göster ve GitHub'a ekle
cat ~/.ssh/id_ed25519.pub
# GitHub: Settings → SSH and GPG keys → New SSH key

# Remote'u SSH ile güncelle
git remote set-url origin git@github.com:SanliData/records_ai.git
git push origin main
```

### 7. Push İşlemi

```bash
# Push et
git push origin main

# İlk push ise:
git push -u origin main
```

### 8. Başarı Kontrolü

```bash
# Remote repository kontrol
git remote -v

# Son commit kontrol
git log --oneline -5

# Status kontrol
git status
```

## Hızlı Push Komutları (Özet)

```bash
# 1. Cloud Shell'e geç
cd ~/records_ai_v2  # Veya clone edilen klasör

# 2. Git durumu kontrol
git status

# 3. Değişiklikleri ekle
git add .

# 4. Commit et
git commit -m "feat: Latest updates - admin, marketplace, multi-record detection, preview page"

# 5. Push et (Token gerekebilir)
git push origin main
```

## Sorun Giderme

### Git kullanıcı bilgileri ayarlama
```bash
git config --global user.name "Your Name"
git config --global user.email "your_email@example.com"
```

### Remote repository kontrolü
```bash
git remote -v
# Çıktı: origin  https://github.com/SanliData/records_ai.git (fetch)
#        origin  https://github.com/SanliData/records_ai.git (push)
```

### Merge conflict çözümü
```bash
# En son değişiklikleri çek
git pull origin main

# Conflict varsa düzelt, sonra:
git add .
git commit -m "fix: Resolve merge conflicts"
git push origin main
```

### Force push (DİKKATLİ KULLANIN)
```bash
# Sadece gerektiğinde ve eminseniz:
git push -f origin main
```

## Notlar

1. **Cloud Shell'in Git'i genellikle önceden yüklüdür**
2. **Personal Access Token kullanmak daha güvenlidir** (SSH yerine)
3. **Cloud Shell oturumu kapandığında dosyalar kalıcıdır** (`~/` dizininde)
4. **Büyük dosyalar için `.gitignore` kullanın** (database, logs, vb.)

## Kaynaklar

- GitHub Repository: https://github.com/SanliData/records_ai
- Cloud Shell Dokümantasyon: https://cloud.google.com/shell/docs
- Git Dokümantasyon: https://git-scm.com/doc
