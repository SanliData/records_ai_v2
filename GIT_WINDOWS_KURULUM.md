# Git Windows Kurulum Rehberi
## Local Git Kurulumu - Adım Adım

### 📍 Durum
- Windows'ta Git kurulu değil
- Local'den GitHub'a push etmek için Git gerekli

---

## ADIM ADIM KURULUM

### ADIM 1: Git for Windows İndirin

1. **Tarayıcıda şu linki açın:**
   ```
   https://git-scm.com/download/win
   ```
   
2. **Otomatik indirme başlayacak** - `.exe` dosyası indirilecek
   - Dosya adı: `Git-2.x.x-64-bit.exe` (veya benzer)

---

### ADIM 2: Git'i Kurun

1. **İndirilen `.exe` dosyasını çalıştırın**
   - İndirilenler klasöründe `Git-2.x.x-64-bit.exe` dosyasını bulun
   - Çift tıklayarak çalıştırın

2. **Kurulum penceresi açılacak:**
   - **"Next"** butonuna tıklayın (birden fazla kez)
   - **Varsayılan ayarları koruyun** (genellikle en iyisi)
   - Önemli ekranlarda:

   **"Select Components":**
   - ✅ Git Bash Here
   - ✅ Git GUI Here
   - ✅ Associate .git* configuration files with the default text editor
   - ✅ Associate .sh files to be run with Bash
   - **"Next"** tıklayın

   **"Choosing the default editor":**
   - Varsayılan: "Use Visual Studio Code as Git's default editor" (veya başka bir editör)
   - VEYA: "Use Notepad++" seçebilirsiniz
   - **"Next"** tıklayın

   **"Adjusting your PATH environment":**
   - ✅ "Git from the command line and also from 3rd-party software" (ÖNERİLEN)
   - **"Next"** tıklayın

   **"Choosing HTTPS transport backend":**
   - ✅ "Use the OpenSSL library" (varsayılan)
   - **"Next"** tıklayın

   **"Configuring the line ending conversions":**
   - ✅ "Checkout Windows-style, commit Unix-style line endings" (varsayılan)
   - **"Next"** tıklayın

   **"Configuring the terminal emulator":**
   - ✅ "Use Windows' default console window" (varsayılan)
   - **"Next"** tıklayın

   **"Configuring extra options":**
   - ✅ "Enable file system caching"
   - ✅ "Enable Git Credential Manager"
   - **"Next"** tıklayın

   **"Installing":**
   - Kurulum başlayacak
   - **"Finish"** butonuna tıklayın

---

### ADIM 3: PowerShell'i Yeniden Başlatın

**ÖNEMLİ:** Kurulumdan sonra PowerShell'i kapatıp yeniden açın!

1. **Mevcut PowerShell penceresini kapatın**
2. **Yeni bir PowerShell penceresi açın**

---

### ADIM 4: Git Kurulumunu Kontrol Edin

Yeni PowerShell penceresinde:

```powershell
git --version
```

**Beklenen çıktı:**
```
git version 2.x.x.windows.x
```

Eğer hata alırsanız, PowerShell'i tekrar yeniden başlatın.

---

### ADIM 5: Git Kullanıcı Bilgilerini Ayarlayın

```powershell
# Adınızı ayarlayın
git config --global user.name "Your Name"

# Email adresinizi ayarlayın
git config --global user.email "your_email@example.com"
```

**Örnek:**
```powershell
git config --global user.name "Isanli"
git config --global user.email "ednovitsky@novitskyarchive.com"
```

---

### ADIM 6: Repository'yi Kontrol Edin

```powershell
cd C:\Users\issan\records_ai_v2

# Git durumunu kontrol et
git status

# Remote repository'yi kontrol et
git remote -v
```

Eğer remote yoksa:
```powershell
git remote add origin https://github.com/SanliData/records_ai.git
```

---

## ✅ Kurulum Tamamlandı!

Artık local'den GitHub'a push edebilirsiniz:

```powershell
cd C:\Users\issan\records_ai_v2

git add .
git commit -m "feat: Local changes"
git push origin main
```

---

## 🆘 Sorun Giderme

### Problem: "git: command not found"
**Çözüm:** 
- PowerShell'i kapatıp yeniden açın
- Sistem PATH'inin doğru ayarlandığından emin olun

### Problem: "fatal: not a git repository"
**Çözüm:**
```powershell
cd C:\Users\issan\records_ai_v2
git init
git remote add origin https://github.com/SanliData/records_ai.git
```

### Problem: "Permission denied" (push sırasında)
**Çözüm:**
- GitHub Personal Access Token kullanın
- VEYA SSH key kurun

---

**Son Güncelleme:** 2026-01-18
