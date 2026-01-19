# ADIM ADIM: COMMIT VE PUSH

## ✅ ADIM 1: Değişiklikleri Kontrol Et

```bash
git status
```

**Beklenen:** `backend/main.py` modified olarak görünmeli.

---

## ✅ ADIM 2: Değişiklikleri Stage'e Al

```bash
git add backend/main.py
```

---

## ✅ ADIM 3: Commit Yap

```bash
git commit -m "fix: wrap risky imports in try/except to prevent startup crashes

Production emergency fix:
- Wrap slowapi imports (rate limiting optional)
- Wrap error_handler import (exception handlers optional)
- Wrap db import (database init optional if DATABASE_URL missing)
- Wrap all router imports (individual routers optional)
- Add local run support for testing

App now boots even if optional features fail.
All failures are logged but do not prevent startup.

Fixes Cloud Run startup crash (revision 00060-92w)."
```

---

## ✅ ADIM 4: GitHub'a Push Et

```bash
git push origin main
```

---

## ✅ ADIM 5: Deploy İçin Hazır

Push başarılı olduktan sonra Cloud Run'a deploy edebiliriz.

---

**Not:** Bu komutları Git Bash veya Git CMD'de çalıştırın. PowerShell'de Git PATH'te olmayabilir.
