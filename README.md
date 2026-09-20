# Hisse Senedi Analizi

Python ile BIST hisse senetleri için teknik analiz yapan masaüstü uygulama. EMA, Bollinger Bantları ve sinyal birleştirmesi ile risk değerlendirmesi sunar.

## Özellikler

- BIST-100 verisi çekme ve MySQL’e kaydetme
- **EMA** analizi (5 / 10 / 25)
- **Bollinger Bantları** analizi
- Sinyallerin birleştirilmesi ile risk yorumu
- **PyQt5** arayüzü ve grafik gösterimi (Matplotlib)

## Teknolojiler

- Python 3
- PyQt5
- PyMySQL
- Matplotlib

## Kurulum

```bash
git clone https://github.com/sametsel/HisseSenediAnalizi.git
cd HisseSenediAnalizi
pip install pymysql PyQt5 matplotlib
```

MySQL’de `hisse_senedi_db` veritabanını oluşturun. Bağlantı bilgilerini ortam değişkenleriyle verin:

```bash
# Windows (PowerShell)
$env:DB_HOST="localhost"
$env:DB_USER="root"
$env:DB_PASSWORD="sifreniz"
$env:DB_NAME="hisse_senedi_db"

# Linux / macOS
export DB_HOST=localhost
export DB_USER=root
export DB_PASSWORD=sifreniz
export DB_NAME=hisse_senedi_db
```

## Çalıştırma

```bash
python arayüz.py
```

## Proje yapısı

| Dosya | Açıklama |
|-------|----------|
| `arayüz.py` | PyQt5 ana arayüz |
| `main.py` | Analiz orkestrasyonu |
| `Ema.py` | EMA analizi |
| `Bollinger.py` | Bollinger Bantları |
| `VeriCekme.py` | Veri çekme ve DB yapılandırması |
| `base_analyzer.py` | Ortak analiz tabanı |

## Not

Bu proje eğitim amaçlıdır; yatırım tavsiyesi değildir.
