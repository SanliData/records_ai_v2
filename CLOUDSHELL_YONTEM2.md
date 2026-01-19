# Cloud Shell Terminal Çalışmıyorsa - Alternatif Yöntem

## 🎯 Yöntem: Cloud Shell Editor ile Script Çalıştırma

Cloud Shell terminaline yazamıyorsanız, Editor üzerinden script oluşturup çalıştırabilirsiniz.

---

## ADIM 1: Script'i Cloud Shell Editor'e Yükleme

1. **Local'de `push_to_github.sh` dosyası oluşturuldu** ✅

2. **Cloud Shell Editor'de:**
   - Sol panelde `File` → `New File`
   - Dosya adı: `push_to_github.sh`
   - İçeriğini yapıştırın (local'deki `push_to_github.sh` dosyasının içeriği)

   VEYA

   - `File` → `Upload Files`
   - Local'deki `push_to_github.sh` dosyasını yükleyin

---

## ADIM 2: Script'i Çalıştırılabilir Yapma

Cloud Shell Editor'de script'i açtıktan sonra:

1. **Terminal sekmesine geçin** (Editor'ün altında)
2. Şu komutu yazın (eğer yazabiliyorsanız):
   ```bash
   chmod +x push_to_github.sh
   bash push_to_github.sh
   ```

---

## Yöntem 2: Direkt Local'den GitHub'a Push (Git Kurulumu)

Terminal yazamıyorsanız, **Git'i Windows'a kurup local'den push edebilirsiniz**.

### Git Kurulumu (Windows)

1. **Git for Windows İndirin:**
   - https://git-scm.com/download/win
   - `.exe` dosyasını çalıştırın ve "Next" ile kurun

2. **Kurulum sonrası PowerShell'i yeniden başlatın**

3. **Git Kontrol:**
   ```powershell
   git --version
   ```

4. **Repository'yi Kontrol Et:**
   ```powershell
   cd C:\Users\issan\records_ai_v2
   git remote -v
   ```

5. **Push İşlemi:**
   ```powershell
   git add .
   git commit -m "feat: Major revision - local changes"
   git push origin main
   ```

---

## Yöntem 3: Cloud Build ile Otomatik Deploy

Cloud Shell yerine, **local'den direkt Cloud Run'a deploy** edebilirsiniz (GitHub'a push olmadan):

```powershell
cd C:\Users\issan\records_ai_v2
.\QUICK_DEPLOY.ps1
```

Bu yöntem:
- ✅ Local dosyaları kullanır
- ✅ GitHub'a push gerekmez
- ✅ Direkt production'a deploy eder

---

## 🎯 Hangi Yöntemi Seçmeli?

1. **Cloud Shell Terminal çalışıyorsa:** Script'i terminal'de çalıştırın
2. **Cloud Shell Terminal çalışmıyorsa:** 
   - Git kurup local'den push edin (Yöntem 2)
   - VEYA direkt local'den deploy edin (Yöntem 3)

---

**En kolay çözüm:** Git kurulumu yapıp local'den push etmek veya direkt `QUICK_DEPLOY.ps1` ile deploy etmek.
