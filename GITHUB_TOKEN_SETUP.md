# 🔑 GitHub Token Kurulumu

## ❌ Mevcut Token Çalışmıyor
Token geçersiz veya süresi dolmuş. Yeni token oluşturun.

---

## ✅ Yeni Token Oluşturma

### 1. GitHub'a Git
- https://github.com/settings/tokens
- Veya: GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)

### 2. "Generate new token" → "Generate new token (classic)"

### 3. Ayarlar:
- **Note**: `records_ai_v2_push` (açıklama)
- **Expiration**: `90 days` veya `No expiration` (production için)
- **Scopes**: Şunları seçin:
  - ✅ `repo` (Full control of private repositories)

### 4. "Generate token" → Token'ı kopyalayın (bir daha gösterilmeyecek!)

---

## 🚀 Token ile Push

### Yöntem 1: URL'de Token (Hızlı)
```bash
git push https://YENI_TOKEN@github.com/SanliData/records_ai_v2.git main
```

### Yöntem 2: Credential Helper (Önerilen)
```bash
# Token'ı kaydet
git config --global credential.helper store

# Push yap
git push origin main
# Username: SanliData
# Password: YENI_TOKEN (token'ı buraya yapıştır)
```

### Yöntem 3: Remote URL Güncelle
```bash
# Remote URL'i token ile güncelle
git remote set-url origin https://YENI_TOKEN@github.com/SanliData/records_ai_v2.git

# Normal push
git push origin main
```

---

## 📝 Notlar
- Token'ı güvenli tutun (şifre gibi)
- Token'ı commit/push yapmayın
- Token süresi dolduğunda yeniden oluşturun

---

## 🔄 Şu An Yapılacaklar
1. Yeni token oluştur (yukarıdaki adımlar)
2. Token'ı kopyala
3. Push komutunu çalıştır:
   ```bash
   git push https://YENI_TOKEN@github.com/SanliData/records_ai_v2.git main
   ```
