# ✅ DOĞRU YERDEYİZ - Şimdi IAM Ekleme

## Görünen Sayfa:
"Permissions for records-ai-v2" ✅

## ŞİMDİ YAPILACAKLAR:

### 1️⃣ "Add principal" butonuna tıklayın
Sağ panelde mavi "Add principal" butonunu görüyorsunuz. Tıklayın.

### 2️⃣ Principal ekleyin:
**New principals** alanına yazın:
```
allUsers
```

### 3️⃣ Role seçin:
**Select a role** dropdown'ından seçin:
```
Cloud Run Invoker
```

### 4️⃣ Save butonuna tıklayın

### 5️⃣ Onay mesajı:
"Allow unauthenticated invocations?" sorusu çıkarsa:
- **"Allow"** butonuna tıklayın

### 6️⃣ Tamamlandı!
Artık listede `allUsers` görünecek ve servise herkes erişebilecek.

## Sonra Test Edin:
```
https://records-ai-v2-969278596906.europe-west1.run.app/ui/index.html
```



