import yfinance as yf
import pymysql

# Güncel BIST 100 hisselerinin tam sembol listesi
bist100_hisseleri = [
    "AEFES", "AGHOL", "AKBNK", "AKSEN", "ALARK", "ALFAS", "ALTNY", "ARCLK", "ASELS", "ASTOR",
    "BERA", "BIMAS", "BINHO", "BJKAS", "CCOLA", "CWENE", "CIMSA", "CLEBI", "DOAS", "BRSAN",
    "DOHOL", "EGEEN", "ECILC", "ENERY", "ENKAI", "ENJSA", "EREGL", "FENER", "FROTO", "PEKGY",
    "GARAN", "GESAN", "GOLTS", "GUBRF", "HALKB", "HEKTS", "ISCTR", "ISMEN", "EKGYO", "CANTE",
    "KARSN", "KCAER", "KCHOL", "KLSER", "KONTR", "KONYA", "KOZAA", "TABGD", "BTCIM", "BRYAT",
    "KOZAL", "KRDMD", "KTLEV", "LMKDC", "MAVI", "MGROS", "MPARK", "OBAMS", "ODAS", "ARDYZ",  
    "OTKAR", "OYAKC", "PAPIL", "PETKM", "PGSUS", "REEDR", "RGYAS", "SMRTG", "ANSGR", "AGROT",
    "SAHOL", "SASA", "SISE", "SKBNK", "SOKM", "TAVHL", "TCELL", "THYAO", "TKFEN", "TMSN", 
    "TSKB", "TOASO", "TTKOM", "TTRAK", "TUKAS", "TUPRS", "TURSG", "ULKER", "EUPWR",
    "VAKBN", "VESTL", "VESBE", "YKBNK", "YEOTK", "ZOREN", "ADEL", "AKFGY", "AKFYE", "AKSA",   
]

# Veritabanı bağlantısı
connection = pymysql.connect(
    host='localhost',
    user='root',
    password='123456',
    db='hisse_senedi_db',
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

for hisse in bist100_hisseleri:
    # Hisse sembolünü tanımlayın
    ticker_symbol = hisse + ".IS"

    # Yfinance üzerinden veri çek
    ticker = yf.Ticker(ticker_symbol)
    historical_data = ticker.history(period="1y")  # Son 1 yılın verisini çek

    try:
        with connection.cursor() as cursor:
            # Veritabanına veri kaydetme
            for index, row in historical_data.iterrows():
                # Veriyi ekle veya var ise güncelle
                insert_query = f"""
                INSERT INTO `{hisse}` (Date, Open, High, Low, Close, Volume)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE 
                    Open = VALUES(Open), 
                    High = VALUES(High), 
                    Low = VALUES(Low), 
                    Close = VALUES(Close), 
                    Volume = VALUES(Volume)
                """
                cursor.execute(insert_query, (index.strftime('%Y-%m-%d'), row['Open'], row['High'], row['Low'], row['Close'], row['Volume']))
            connection.commit()
    except Exception as e:
        print(f"{hisse} için hata oluştu: {e}")
    finally:
        print(f"{hisse} için veri kaydedildi.")

# Bağlantıyı kapat
connection.close()
print("Tüm veriler kaydedildi.")
