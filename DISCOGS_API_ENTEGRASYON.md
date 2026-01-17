# Discogs API Entegrasyonu - Dokümantasyon

## ✅ Tamamlanan Özellikler

### 1. Market Price Fetching
- Discogs marketplace'ten piyasa fiyatları çekiliyor
- En düşük, en yüksek ve medyan fiyatlar gösteriliyor
- Farklı para birimleri USD'ye dönüştürülüyor

### 2. Release Information
- Discogs'tan detaylı release bilgileri alınıyor
- Artist, label, year, format, tracklist bilgileri
- Release görselleri

### 3. Condition-Based Pricing
- Goldmine standard kondisyon çarpanları
- M (Mint) → %100
- NM (Near Mint) → %95
- VG+ (Very Good Plus) → %85
- VG (Very Good) → %70
- G+ (Good Plus) → %50
- G (Good) → %30
- P (Poor) → %10

### 4. User Estimate
- Kullanıcı manuel fiyat tahmini girebiliyor
- User estimate, kondisyon ile birlikte hesaplanıyor

---

## 🔌 API Endpoints

### 1. Market Prices
```
GET /vinyl/pricing/market-prices?artist={artist}&album={album}&catalog_number={catalog}&label={label}
```

**Response:**
```json
{
  "status": "ok",
  "prices": {
    "price_low": 15.50,
    "price_high": 89.99,
    "price_median": 45.00,
    "currency": "USD",
    "source": "discogs",
    "url": "https://www.discogs.com/release/123456",
    "sample_size": 12
  }
}
```

### 2. Estimate Value
```
GET /vinyl/pricing/estimate-value?artist={artist}&album={album}&condition={condition}&user_estimate={price}
```

**Response:**
```json
{
  "status": "ok",
  "estimate": {
    "estimated_value": 45.00,
    "condition_adjusted": 38.25,
    "market_range": {
      "low": 15.50,
      "high": 89.99,
      "median": 45.00
    },
    "calculation_method": "market_median",
    "condition": "VG+",
    "condition_multiplier": 0.85
  }
}
```

### 3. Release Info
```
GET /vinyl/pricing/release-info?artist={artist}&album={album}
```

**Response:**
```json
{
  "status": "ok",
  "release_info": {
    "release_id": "123456",
    "title": "The Wall",
    "artist": "Pink Floyd",
    "label": "Harvest",
    "year": 1979,
    "format": "LP",
    "genre": ["Rock"],
    "tracklist": [...],
    "images": [...],
    "url": "https://www.discogs.com/release/123456"
  }
}
```

### 4. Condition Multipliers (Reference)
```
GET /vinyl/pricing/condition-multipliers
```

**Response:**
```json
{
  "status": "ok",
  "multipliers": {
    "M": 1.0,
    "NM": 0.95,
    "VG+": 0.85,
    ...
  },
  "condition_codes": {
    "M": "Mint (100%)",
    ...
  }
}
```

---

## 🔑 Discogs API Token

Discogs API token'ı environment variable'dan alınıyor:

```bash
export DISCOGS_TOKEN="your_token_here"
```

Veya `.env` dosyasında:
```
DISCOGS_TOKEN=your_token_here
```

**Token Alma:**
1. https://www.discogs.com/settings/developers adresine gidin
2. "Generate new token" butonuna tıklayın
3. Token'ı kopyalayıp environment variable'a ekleyin

---

## 💻 Frontend Kullanımı

### Library Sayfasında Fiyat Çekme

```javascript
// Fetch market prices
async function fetchMarketPrices() {
    const artist = document.getElementById('editArtist').value;
    const album = document.getElementById('editAlbum').value;
    
    const response = await fetch(
        `${API_BASE}/vinyl/pricing/market-prices?artist=${artist}&album=${album}`,
        {
            headers: {
                'Authorization': `Bearer ${currentUser.token}`
            }
        }
    );
    
    const data = await response.json();
    const prices = data.prices;
    
    // Display prices
    // prices.price_low, prices.price_high, prices.price_median
}
```

### Estimate Value Hesaplama

```javascript
// Calculate estimated value with condition
async function calculateEstimate(artist, album, condition, userEstimate) {
    const params = new URLSearchParams({
        artist: artist,
        album: album,
        condition: condition
    });
    
    if (userEstimate) {
        params.append('user_estimate', userEstimate);
    }
    
    const response = await fetch(
        `${API_BASE}/vinyl/pricing/estimate-value?${params}`,
        {
            headers: {
                'Authorization': `Bearer ${currentUser.token}`
            }
        }
    );
    
    const data = await response.json();
    const estimate = data.estimate;
    
    // estimate.condition_adjusted = final estimated value
}
```

---

## 📊 Kondisyon Bazlı Fiyat Hesaplama

### Örnek:
- **Base Price (Median):** $50.00
- **Condition:** VG+ (Very Good Plus)
- **Multiplier:** 0.85
- **Estimated Value:** $50.00 × 0.85 = **$42.50**

### User Estimate ile:
- **User Estimate:** $100.00
- **Condition:** NM (Near Mint)
- **Multiplier:** 0.95
- **Estimated Value:** $100.00 × 0.95 = **$95.00**

---

## 🔧 Servis Özellikleri

### VinylPricingService

1. **get_market_prices()** - Market fiyatlarını çeker
2. **get_release_info()** - Release detaylarını çeker
3. **calculate_condition_price()** - Kondisyon bazlı fiyat hesaplar
4. **get_estimated_value()** - Nihai değer tahmini hesaplar

### Fallback Mekanizması

- Marketplace stats yoksa → Release listings denenir
- Release listings yoksa → Release details çekilir
- Hiçbiri yoksa → Empty pricing döner (kullanıcı manuel girebilir)

---

## ⚠️ Rate Limiting

Discogs API rate limiting:
- **60 requests/dakika** (unauthenticated)
- **1000 requests/dakika** (authenticated with token)

Servis otomatik olarak rate limiting'e uyar (sleep eklenir).

---

## 🧪 Test Etme

### Python'da Test:
```python
from backend.services.vinyl_pricing_service import vinyl_pricing_service

# Market prices
prices = vinyl_pricing_service.get_market_prices(
    artist="Pink Floyd",
    album="The Wall"
)
print(prices)

# Estimate value
estimate = vinyl_pricing_service.get_estimated_value(
    market_prices=prices,
    condition="VG+",
    user_estimate=None
)
print(estimate)
```

### Frontend'de Test:
1. Library sayfasına gidin
2. Bir kaydı düzenleyin (Edit)
3. "Fetch Market Prices from Discogs" butonuna tıklayın
4. Artist ve Album bilgileri varsa fiyatlar çekilecek

---

## 📝 Notlar

1. **Discogs Token:** Production'da environment variable olarak saklanmalı
2. **Currency Conversion:** Şu an yaklaşık dönüşüm kullanılıyor. Production'da gerçek exchange rate API kullanılabilir
3. **Caching:** Fiyatlar cache'lenebilir (sonraki versiyon)
4. **Error Handling:** API hatalarında graceful fallback var

---

**✅ Discogs API entegrasyonu tamamlandı ve hazır kullanıma sunuldu!**
