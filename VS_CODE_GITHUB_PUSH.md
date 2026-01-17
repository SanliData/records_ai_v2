# VS Code ile GitHub'a Push

## Adımlar

### 1. VS Code'u Açın
1. VS Code'u açın
2. **File → Open Folder** ile `C:\Users\issan\records_ai_v2` klasörünü açın

### 2. Source Control Paneli
1. Sol taraftaki **Source Control** ikonuna tıklayın (Ctrl+Shift+G)
2. Veya sol üstteki **View → Source Control** menüsünden

### 3. Repository Kontrolü
VS Code otomatik olarak Git repository'sini algılamalı. Eğer algılamazsa:

**A. Git Repository'sini Initialize Edin:**
```bash
# VS Code terminalde (Ctrl+`) veya PowerShell'de:
cd C:\Users\issan\records_ai_v2
git init
```

**B. Remote Repository Ekleyin:**
VS Code terminalinde:
```bash
git remote add origin https://github.com/SanliData/records_ai.git
```

Veya mevcut remote'u kontrol edin:
```bash
git remote -v
```

### 4. Değişiklikleri Stage Edin (Add)
1. Source Control panelinde **"Changes"** altında tüm değişiklikler görünür
2. Her dosyanın yanındaki **"+"** ikonuna tıklayarak stage edin
3. VEYA üstteki **"Stage All Changes"** (✓) butonuna tıklayın

### 5. Commit Mesajı ve Commit
1. Üst kısımdaki **Message** kutusuna commit mesajı yazın:
   ```
   feat: Admin system, marketplace integration, multi-record detection, preview page
   ```
   
   Veya daha detaylı:
   ```
   feat: Major updates - Admin system, marketplace, multi-record detection
   - Admin system with ednovitsky@archive.com and isanli058@gmail.com
   - Multi-platform marketplace (Discogs, eBay, Etsy, Amazon)
   - Multi-record detection with AI (Sherlock Holmes mode)
   - Preview/confirmation page with label zoom
   - Lyrics and sheet music auto-fetch integration
   - Mobile-responsive design
   - Updated live_book and tree documentation
   ```

2. **"✓ Commit"** butonuna tıklayın (veya Ctrl+Enter)

### 6. GitHub Authentication

**A. Personal Access Token Oluşturun:**
1. GitHub'a gidin: https://github.com
2. Sağ üstteki profil ikonu → **Settings**
3. Sol menüden **Developer settings**
4. **Personal access tokens → Tokens (classic)**
5. **Generate new token (classic)**
6. **Note**: "VS Code Push" yazın
7. **Expiration**: İstediğiniz süreyi seçin
8. **Scopes**: `repo` seçin (tüm alt seçenekleri otomatik seçilir)
9. **Generate token** tıklayın
10. Token'ı **kopyalayın** (bir daha gösterilmez!)

### 7. Push İşlemi

**Yöntem 1: VS Code Source Control Panelinden (Önerilen)**
1. Source Control panelinde üstteki **"..."** (üç nokta) menüsüne tıklayın
2. **Push** seçin
3. İlk push'ta authentication sorulacak:
   - **Username**: GitHub kullanıcı adınız
   - **Password**: Personal Access Token'ınız (gerçek şifre değil!)

**Yöntem 2: VS Code Terminal'den**
Terminal'de (Ctrl+`):
```bash
git push origin main
```

İlk push'ta GitHub credentials sorulacak:
- **Username**: GitHub kullanıcı adınız
- **Password**: Personal Access Token

**Yöntem 3: Remote URL'yi Token ile Güncelleyin**
```bash
git remote set-url origin https://YOUR_TOKEN@github.com/SanliData/records_ai.git
git push origin main
```

### 8. VS Code Git Ayarları

**Git Kullanıcı Bilgileri:**
VS Code terminalinde:
```bash
git config --global user.name "Your Name"
git config --global user.email "your_email@example.com"
```

Veya VS Code Settings'ten:
1. Ctrl+, (Settings)
2. Arama: "git user"
3. `git.enabled` ve `git.path` ayarlarını kontrol edin

### 9. Başarı Kontrolü

**VS Code'da:**
- Source Control panelinde "No changes" görünmeli
- Alt durum çubuğunda branch adı görünmeli

**GitHub'da:**
1. https://github.com/SanliData/records_ai adresine gidin
2. Son commit'i kontrol edin
3. Dosyaların güncellendiğini kontrol edin

## VS Code Git Kısayolları

- **Ctrl+Shift+G**: Source Control panelini aç/kapat
- **Ctrl+Enter**: Commit
- **Ctrl+`**: Terminal aç/kapat
- **Ctrl+,**: Settings

## Sorun Giderme

### Git komutu bulunamıyor
VS Code Settings'te:
1. Ctrl+, → arama: "git path"
2. `git.path` ayarını kontrol edin
3. Veya Git'i PATH'e ekleyin

### Authentication hatası
1. Personal Access Token'ı kontrol edin
2. Token'ın `repo` scope'una sahip olduğundan emin olun
3. Token'ın expire olmadığını kontrol edin

### Remote repository bulunamadı
```bash
git remote -v
# Çıktı yoksa:
git remote add origin https://github.com/SanliData/records_ai.git
```

### Branch ismi farklıysa
```bash
# Mevcut branch'i kontrol
git branch

# main branch'ine geç veya oluştur
git checkout -b main

# Push et
git push -u origin main
```

### .gitignore ile ilgili
`.gitignore` dosyasında yoksa ekleyin:
- `*.db` (database dosyaları)
- `*.json` (key dosyaları hariç)
- `__pycache__/`
- `.venv/`
- `storage/`
- `uploads/`

## Hızlı Checklist

- [ ] VS Code'da proje klasörü açık
- [ ] Source Control panelinde değişiklikler görünüyor
- [ ] Tüm değişiklikler stage edildi (✓)
- [ ] Commit mesajı yazıldı
- [ ] Commit yapıldı
- [ ] GitHub Personal Access Token hazır
- [ ] Remote repository doğru (origin)
- [ ] Push işlemi tamamlandı
- [ ] GitHub'da değişiklikler görünüyor

## Kaynaklar

- GitHub Repository: https://github.com/SanliData/records_ai
- VS Code Git Dokümantasyon: https://code.visualstudio.com/docs/sourcecontrol/overview
- GitHub Personal Access Tokens: https://github.com/settings/tokens
