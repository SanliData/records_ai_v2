# Adım Adım GitHub'a Push ve Deployment Rehberi

## 📍 Mevcut Durum
- ✅ Cloud Shell'de bulunuyorsunuz
- ✅ Repository clone edildi: `~/records_ai`

---

## ADIM 1: Local Dosyaları Cloud Shell'e Yükleme

### 🔹 Seçenek A: Cloud Shell Editor (ÖNERİLEN - Kolay)

1. **Cloud Shell'de sağ üstteki Editor ikonuna tıklayın** (kalem simgesi 🔧)
   
2. **Sol panelde:**
   - `File` → `Upload Files...` tıklayın

3. **Local bilgisayarınızda (Windows PowerShell'de):**
   ```powershell
   # records_ai_v2 klasörünü ZIP yapın
   cd C:\Users\issan\records_ai_v2
   Compress-Archive -Path * -DestinationPath records_ai_v2.zip
   ```
   
4. **Cloud Shell Editor'de:**
   - `records_ai_v2.zip` dosyasını seçin ve yükleyin
   
5. **Cloud Shell Terminal'de:**
   ```bash
   # ZIP dosyasını çıkar
   unzip records_ai_v2.zip
   ```

### 🔹 Seçenek B: gcloud SCP (Alternatif)

**Local PowerShell'de (Windows):**
```powershell
cd C:\Users\issan\records_ai_v2

# Cloud Shell'e dosya yükle
gcloud cloud-shell scp --recurse * cloudshell:~/records_ai_v2/
```

---

## ADIM 2: Dosyaları Repository'ye Kopyalama

Cloud Shell Terminal'de çalıştırın:

```bash
# 1. Repository dizinine git
cd ~/records_ai

# 2. Dosyaların yüklendiğini kontrol et
ls ~/records_ai_v2

# 3. Dosyaları repository'ye kopyala
cp -r ~/records_ai_v2/* .

# 4. .git klasörünü koru (varsa)
# (cp komutu .git'i de kopyalayabilir, kontrol edin)
```

---

## ADIM 3: Git Durumunu Kontrol Etme

Cloud Shell Terminal'de:

```bash
# Repository dizininde olduğunuzdan emin olun
cd ~/records_ai

# Git durumunu kontrol et
git status
```

**Beklenen çıktı:** Değişen dosyaların listesi görünür.

---

## ADIM 4: Değişiklikleri Stage'e Ekleme

Cloud Shell Terminal'de:

```bash
# Tüm değişiklikleri ekle
git add .

# Kontrol et
git status
```

**Beklenen:** Dosyalar "Changes to be committed" altında görünür.

---

## ADIM 5: Commit Oluşturma

Cloud Shell Terminal'de:

```bash
# Commit mesajı ile commit oluştur
git commit -m "feat: Local changes from records_ai_v2 - $(date +'%Y-%m-%d %H:%M')"
```

**VEYA manuel mesaj:**

```bash
git commit -m "feat: Local changes from records_ai_v2"
```

**Beklenen çıktı:**
```
[main xxxxxxx] feat: Local changes from records_ai_v2
 X files changed, Y insertions(+), Z deletions(-)
```

---

## ADIM 6: GitHub'a Push Etme

### 🔹 İlk Deneme (Normal Push)

Cloud Shell Terminal'de:

```bash
git push origin main
```

### 🔹 Eğer Authentication Hatası Alırsanız:

#### Yöntem 1: Personal Access Token ile Push

1. **GitHub'da Token oluşturun:**
   - https://github.com/settings/tokens
   - "Generate new token (classic)"
   - Scopes: `repo` seçin
   - Token'ı kopyalayın

2. **Cloud Shell'de token ile push:**
   ```bash
   git push https://YOUR_TOKEN@github.com/SanliData/records_ai.git main
   ```

#### Yöntem 2: Remote URL'i Token ile Güncelle

```bash
# Token'ı remote URL'e ekle
git remote set-url origin https://YOUR_TOKEN@github.com/SanliData/records_ai.git

# Normal push yap
git push origin main
```

**Başarılı Push Beklenen Çıktı:**
```
Enumerating objects: X, done.
Counting objects: 100% (X/X), done.
Delta compression using up to X threads
Compressing objects: 100% (X/X), done.
Writing objects: 100% (X/X), done.
To https://github.com/SanliData/records_ai.git
   xxxxxx..xxxxxx  main -> main
```

---

## ADIM 7: Push Sonrası Kontrol

Cloud Shell Terminal'de:

```bash
# Son commit'i kontrol et
git log --oneline -3

# Remote durumu kontrol et
git remote -v

# GitHub'da görüntüle
echo "GitHub Repository: https://github.com/SanliData/records_ai"
```

**GitHub'da kontrol edin:**
- https://github.com/SanliData/records_ai
- Son commit'iniz görünmeli

---

## ADIM 8: Production Deployment (Push Sonrası)

### 🔹 Local PowerShell'den Deploy

**Windows PowerShell'de:**

```powershell
# Proje dizinine git
cd C:\Users\issan\records_ai_v2

# Deployment script'ini çalıştır
.\QUICK_DEPLOY.ps1
```

**VEYA manuel olarak:**

```powershell
# Google Cloud projesini ayarla
gcloud config set project records-ai

# Cloud Run'a deploy et
gcloud run deploy records-ai-v2 `
  --source . `
  --platform managed `
  --region europe-west1 `
  --allow-unauthenticated `
  --port 8080
```

---

## ✅ Kontrol Listesi

- [ ] ADIM 1: Local dosyalar Cloud Shell'e yüklendi
- [ ] ADIM 2: Dosyalar repository'ye kopyalandı
- [ ] ADIM 3: `git status` ile durum kontrol edildi
- [ ] ADIM 4: `git add .` ile dosyalar eklendi
- [ ] ADIM 5: `git commit` ile commit oluşturuldu
- [ ] ADIM 6: `git push origin main` ile GitHub'a push edildi
- [ ] ADIM 7: GitHub'da değişiklikler kontrol edildi
- [ ] ADIM 8: Production deployment yapıldı

---

## 🆘 Sorun Giderme

### Problem: "Permission denied" hatası
**Çözüm:** Personal Access Token kullanın (ADIM 6 - Yöntem 1)

### Problem: "Repository not found" hatası
**Çözüm:** 
```bash
# Remote URL'i kontrol et
git remote -v

# Düzelt (eğer gerekirse)
git remote set-url origin https://github.com/SanliData/records_ai.git
```

### Problem: "Nothing to commit" mesajı
**Çözüm:** Dosyalar zaten commit edilmiş. `git status` ile kontrol edin.

### Problem: "remote origin already exists" hatası
**Çözüm:**
```bash
# Remote'u kontrol et
git remote -v

# Güncelle
git remote set-url origin https://github.com/SanliData/records_ai.git
```

---

## 📝 Hızlı Komut Özeti (Cloud Shell'de)

```bash
# 1. Repository'ye git
cd ~/records_ai

# 2. Dosyaları kopyala (dosyalar ~/records_ai_v2'de varsa)
cp -r ~/records_ai_v2/* .

# 3. Git işlemleri
git status
git add .
git commit -m "feat: Local changes from records_ai_v2"
git push origin main
```

---

**Son Güncelleme:** 2026-01-13
