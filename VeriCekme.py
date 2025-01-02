import yfinance as yf
import pymysql

# Veritabanı konfigürasyonu
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'db': 'hisse_senedi_db',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

def create_table_if_not_exists(cursor, table_name):
    """
    Belirtilen tablo yoksa oluşturur.
    """
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS `{table_name}` (
        Date DATE NOT NULL,
        Open FLOAT,
        High FLOAT,
        Low FLOAT,
        Close FLOAT,
        Volume BIGINT,
        PRIMARY KEY (Date)
    ) ENGINE=InnoDB;
    """
    cursor.execute(create_table_query)

def get_all_stocks():
    """Veritabanındaki tüm hisseleri getirir."""
    try:
        connection = pymysql.connect(**DB_CONFIG)
        with connection.cursor() as cursor:
            # Tüm tabloları getir
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            # Tablo isimlerini liste olarak döndür
            return [list(table.values())[0] for table in tables]
    except Exception as e:
        print(f"Hisse listesi alınırken hata: {e}")
        return []
    finally:
        if 'connection' in locals():
            connection.close()

def get_stock_data(stock_code, limit=None):
    """Belirli bir hissenin verilerini getirir."""
    try:
        connection = pymysql.connect(**DB_CONFIG)
        with connection.cursor() as cursor:
            query = f"SELECT * FROM `{stock_code}` ORDER BY Date DESC"
            if limit:
                query += f" LIMIT {limit}"
            cursor.execute(query)
            return cursor.fetchall()
    except Exception as e:
        print(f"{stock_code} verileri alınırken hata: {e}")
        return []
    finally:
        if 'connection' in locals():
            connection.close()

def get_last_price(stock_code):
    """Bir hissenin son kapanış fiyatını ve değişimini getirir."""
    try:
        connection = pymysql.connect(**DB_CONFIG)
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM `{stock_code}` ORDER BY Date DESC LIMIT 2")
            data = cursor.fetchall()
            if len(data) >= 2:
                current = float(data[0]['Close'])
                previous = float(data[1]['Close'])
                change = ((current - previous) / previous) * 100
                return {
                    'price': current,
                    'change': change,
                    'direction': 'up' if change > 0 else 'down'
                }
            return None
    except Exception as e:
        print(f"{stock_code} son fiyat alınırken hata: {e}")
        return None
    finally:
        if 'connection' in locals():
            connection.close()

def fetch_and_update_data(progress_callback=None):
    """Tüm hisselerin verilerini günceller."""
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
        "VAKBN", "VESTL", "VESBE", "YKBNK", "YEOTK", "ZOREN", "ADEL", "AKFGY", "AKFYE", "AKSA", "GSRAY",
    ]

    connection = pymysql.connect(**DB_CONFIG)

    try:
        for i, hisse in enumerate(bist100_hisseleri):
            try:
                # Spor kulüpleri için özel durum kontrolü
                if hisse in ["GSRAY", "BJKAS", "FENER"]:
                    ticker_symbol = f"{hisse}.IS"
                    # Tablo adını küçük harfe çevir
                    table_name = hisse.lower()
                else:
                    ticker_symbol = f"{hisse}.IS"
                    table_name = hisse

                ticker = yf.Ticker(ticker_symbol)
                historical_data = ticker.history(period="1y")

                with connection.cursor() as cursor:
                    create_table_if_not_exists(cursor, table_name)  # table_name kullan
                    
                    for index, row in historical_data.iterrows():
                        insert_query = f"""
                        INSERT INTO `{table_name}` (Date, Open, High, Low, Close, Volume)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE 
                            Open = VALUES(Open), 
                            High = VALUES(High), 
                            Low = VALUES(Low), 
                            Close = VALUES(Close), 
                            Volume = VALUES(Volume)
                        """
                        cursor.execute(insert_query, (
                            index.strftime('%Y-%m-%d'), 
                            row['Open'], 
                            row['High'], 
                            row['Low'], 
                            row['Close'], 
                            row['Volume']
                        ))
                    connection.commit()

                if progress_callback:
                    progress_callback(f"{hisse} güncelleniyor ({i+1}/{len(bist100_hisseleri)})")

            except Exception as e:
                print(f"Hata oluştu: {hisse} için veri güncellenemedi. {str(e)}")
                if progress_callback:
                    progress_callback(f"{hisse} için hata oluştu, atlanıyor...")

    finally:
        connection.close()
        if progress_callback:
            progress_callback("Veritabanı güncellemesi tamamlandı.")

# Hisse listesini dışa aktar
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
    "VAKBN", "VESTL", "VESBE", "YKBNK", "YEOTK", "ZOREN", "ADEL", "AKFGY", "AKFYE", "AKSA" ,"GSRAY",
]


