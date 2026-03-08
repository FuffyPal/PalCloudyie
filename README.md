# ☁️ PalCloudy - OVH Cloud Management Panel

**PalCloudy**, OVHcloud ekosistemini (OVH, SoYouStart, Kimsufi) yönetmek için tasarlanmış, **Python tabanlı**, **GTK4/Libadwaita arayüzlü**, **modüler** ve **güvenli** bir yönetim panelidir.

## 🌟 Özellikler

### Faz 2 - Auth & Login UI ✅ (Tamamlandı)

- ✅ **Libadwaita 1.8.4** ile uyumlu GTK4 arayüzü
- ✅ **Fernet encryption** ile güvenli credential storage
- ✅ **Kaydedilmiş hesaplar** yönetimi
- ✅ **Responsive sidebar** navigation
- ✅ **Dark mode** otomatik adaptasyon
- ✅ **Background bağlantı testleri**
- ✅ **Modal dialog** ayarlar penceresı
- ✅ **Tam modüler** kod yapısı

### Planlanan Faz 3 - Dashboard & Server Management

- [ ] Sunucu listesi (API çağrıları)
- [ ] Server management (reboot, reinstall, vb.)
- [ ] Status göstergeleri
- [ ] Server monitoring

## 📋 Sistem Gereksinimleri

### OS & Runtime
- **Linux** (Fedora 43+ veya equivalent)
- **Python 3.10+**

### GUI Kütüphaneleri
- **GTK 4.0+**
- **Libadwaita 1.8.4+** (GNOME)
- **PyGObject 3.46+**

### Python Paketleri
```
ovh>=1.0.0
PyGObject>=3.46.0
PyGI>=1.0.3
aiohttp>=3.8.0
cryptography>=41.0.0
python-dotenv>=0.21.0
```

## 🚀 Hızlı Başlangıç

### 1. Kurulum

```bash
# Proje klonla
git clone https://github.com/yourusername/PalCloudy.git
cd PalCloudy

# Virtual environment oluştur
python3 -m venv venv
source venv/bin/activate

# Bağımlılıkları yükle
pip install -r requirements.txt
```

### 2. Uygulamayı Başlat

```bash
python main.py
```

**İlk açılışta**:
- Giriş sayfası (Login page) açılır
- OVH API anahtarlarını gir
- Hesap kaydedilir ve dashboard açılır

### 3. OVH API Anahtarlarını Elde Et

1. [OVHcloud](https://www.ovhcloud.com) hesabına gir
2. **Control Panel** → **Advanced** → **API**
3. **Create an application** butonuna tıkla
4. Application Key, Secret ve Consumer Key'i kopyala
5. PalCloudy login sayfasına yapıştır

**Detaylı rehber**: [API Anahtarları Rehberi](https://help.ovhcloud.com/csm/en-managing-tokens-and-permissions)

## 📁 Proje Yapısı

```
PalCloudy/
├── main.py                     # Entry point
├── app.py                      # Application lifecycle
├── requirements.txt            # Bağımlılıklar
├── README.md                   # Bu dosya
│
├── config/
│   ├── endpoints.py            # API endpoints tanımları
│   └── settings.py             # Kullanıcı tercihleri
│
├── core/
│   ├── factory.py              # OVH Client üretici
│   ├── auth_handler.py         # Credential yönetimi (Fernet encryption)
│   └── async_worker.py         # Asenkron işler
│
├── api/
│   ├── test_connection.py      # Bağlantı testi
│   ├── get_dedicated.py        # Sunucu listeleme
│   ├── post_reboot.py          # Reboot komutu
│   └── get_vps_status.py       # VPS durumu
│
├── ui/
│   ├── window.py               # Ana pencere (Adw.ApplicationWindow)
│   ├── login_page.py           # Login sayfası (Adw.Bin)
│   ├── dashboard.py            # Dashboard (kaydedilmiş hesaplar)
│   └── components/             # Özel widgetlar (Faz 3)
│
└── assets/                     # Logolar ve ikonlar
```

## 🔐 Güvenlik Mimarisi

### Credential Storage

Hesaplarınız **şifreli** olarak **yerel** diskte tutulur:

```
~/.config/palcloudy/
├── .master              (Master encryption key - 0o600)
└── credentials.enc      (Şifreli credentials - 0o600)
```

**Özellikler**:
- ✅ **Fernet encryption** (AES-128 + HMAC)
- ✅ **File permissions** (0o600 - sadece sen okuyabilir)
- ✅ **No network** (veriler asla internete gönderilmez)
- ✅ **Per-system master key** (sistem başına unique)

**Detaylı rehber**: [Kayıtlar Nerede?](../KAYITLAR_NEREDE_REHBERI.md)

## 🎨 Kullanıcı Arayüzü

### Libadwaita & GNOME HIG Uyumluluğu

- ✅ **Adw.NavigationSplitView** - Sidebar navigation
- ✅ **Adw.ViewStack** - Tab yönetimi
- ✅ **Adw.Toast** - Notifications
- ✅ **Dark mode** - Otomatik sistem teması
- ✅ **Responsive design** - Pencere resize desteği

### Ana Bileşenler

```
┌─────────────────────────────────────────┐
│ PalCloudy - OVH Cloud Management Panel  │
├──────────────┬────────────────────────┤
│ Hesaplar     │                        │
│              │                        │
│ 👤 Fluffy    │    Dashboard           │
│    Pal       │                        │
│              │   (Kaydedilmiş         │
│ 👤 Test      │    hesaplar listesi)   │
│              │                        │
│ ➕ Hesap     │                        │
│    Ekle      │                        │
│ ⚙️ Ayarlar   │                        │
└──────────────┴────────────────────────┘
```

## 🧪 Test Senaryoları

### Senaryo 1: İlk Kurulum
```
1. python main.py
2. Login sayfası açılır
3. OVH API anahtarlarını gir
4. "Bağlantıyı Test Et" - Başarılı ✅
5. "Giriş Yap" - Hesap kaydedilir
6. Dashboard açılır, hesap sidebar'da görülür
```

### Senaryo 2: Kaydedilmiş Hesapla Giriş
```
1. python main.py
2. Kaydedilmiş hesap varsa → Dashboard açılır
3. Sidebar'da "👤 Fluffy Pal" görülür
4. Hesaba tıklanırsa → Hesap seçilir (log çıkar)
```

### Senaryo 3: Yeni Hesap Ekleme
```
1. Dashboard'da "➕ Hesap Ekle" butonuna tıkla
2. Login sayfası (yeni pencere) açılır
3. Yeni hesap bilgileri gir
4. "✅ Giriş Yap" butonuna tıkla
5. Yeni hesap kaydedilir
6. Dashboard'a dön, sidebar'da yeni hesap görülür
```

### Senaryo 4: Ayarlar Dialog'u
```
1. Dashboard'da "⚙️ Ayarlar" butonuna tıkla
2. Modal dialog penceresi açılır
3. "Kapat" butonuyla dialog kapanır
4. Ana pencere etkinliğini yeniden alır
```

## 🛠️ Geliştirme

### Virtual Environment Aktivasyonu

```bash
source venv/bin/activate
```

### Uyumluluğu Kontrol Et

```bash
python check_compat.py

# Çıktı:
# 🔍 Libadwaita Uyumluluğu Kontrolü
# ✅ set_sidebar() mevcut
# ✅ set_content() mevcut
# ✅ Uyumluluğa göre yöntemler doğru
```

### Hata Ayıklama

```bash
python main.py

# Debug çıktıları:
# ============================================================
# 🚀 PalCloudy - OVH Cloud Management Panel
# ============================================================
# 🎨 GUI modu etkinleştiriliyor...
# ✅ Hesap yüklendi: Fluffy Pal
```

## 📚 Dokümantasyon

| Dosya | Açıklama |
|-------|----------|
| [KAYITLAR_NEREDE_REHBERI.md](../KAYITLAR_NEREDE_REHBERI.md) | Credential storage ve güvenlik |
| [GTK4_LIBADWAITA_HATA_REFERANSI.md](../GTK4_LIBADWAITA_HATA_REFERANSI.md) | Yaygın hatalar ve çözümleri |
| [FAZ_2_8_SIDEBAR_LAYOUT.md](../FAZ_2_8_SIDEBAR_LAYOUT.md) | Responsive sidebar tasarımı |
| [HIZLI_BASLANGIC.md](../HIZLI_BASLANGIC.md) | Kurulum ve başlama rehberi |

## 🔄 Geliştirme Fezları

### ✅ Faz 1: Core API Factory
- OVH Client factory
- 7 endpoint desteği
- Bağlantı testi
- Mock fallback

### ✅ Faz 2: Auth & Login UI
- Libadwaita giriş sayfası
- Fernet encryption ile credential storage
- Kaydedilmiş hesaplar listesi
- Modal dialog ayarlar
- Responsive sidebar
- Background bağlantı testleri

### 📌 Faz 3: Dashboard & Server Management
- Sunucu listesi API çağrıları
- Server management (reboot, reinstall)
- Status göstergeleri
- Monitoring dashboard

### 📌 Faz 4: Packaging
- Flatpak bundle
- MSYS2 Windows build
- Snap package

### 📌 Faz 5: Advanced Features
- Mobile responsiveness
- Advanced filtering & search
- Batch operations

## 🤝 Katkı

Hataları bildirmek veya özellik önerileri için:

1. **Issue** açın
2. **Pull request** gönderin
3. **Dokümantasyon** iyileştirmelerine katkıda bulunun

## 📄 Lisans

MIT License - Detaylar için [LICENSE](./LICENSE) dosyasına bakın

## 👨‍💻 Geliştirici

**PalCloudy Development Team**

- Modüler Python mimarisi
- GTK4/Libadwaita UI
- Fernet encryption güvenliği
- GNOME HIG uyumluluğu

## 🔗 Bağlantılar

- [OVHcloud API Dokümantasyonu](https://api.ovh.com/)
- [GTK4 Dokümantasyonu](https://docs.gtk.org/gtk4/)
- [Libadwaita Dokümantasyonu](https://gnome.pages.gitlab.gnome.org/libadwaita/)
- [PyGObject](https://pygobject.readthedocs.io/)

## 📞 Destek

Sorularınız veya sorunlarınız için:

1. [Issues](https://github.com/yourusername/PalCloudy/issues) açın
2. Dokümantasyonu kontrol edin
3. Pull request gönderin

---

**Versiyon**: 0.2.8 (Faz 2 - Tamamlandı)  
**Son Güncelleme**: 2026-03-08  
**Durum**: 🟢 Aktif Geliştirme  

---

**Happy Coding! 🚀**
