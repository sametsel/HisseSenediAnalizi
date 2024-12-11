import yfinance as yf
import pymysql

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

def fetch_and_update_data(progress_callback=None):
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

    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='123456',
        db='hisse_senedi_db',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

    try:
        for i, hisse in enumerate(bist100_hisseleri):
            try:
                ticker_symbol = hisse + ".IS"
                ticker = yf.Ticker(ticker_symbol)
                historical_data = ticker.history(period="1y")

                with connection.cursor() as cursor:
                    # Tabloyu kontrol et ve yoksa oluştur
                    create_table_if_not_exists(cursor, hisse)

                    for index, row in historical_data.iterrows():
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

                if progress_callback:
                    progress_callback(f"{hisse} güncelleniyor ({i+1}/{len(bist100_hisseleri)})")

            except Exception as e:
                # Hata mesajı ama diğer hisseler için devam et
                print(f"Hata oluştu: {hisse} için veri güncellenemedi. {str(e)}")
                if progress_callback:
                    progress_callback(f"{hisse} için hata oluştu, atlanıyor...")

    finally:
        connection.close()
        if progress_callback:
            progress_callback("Veritabanı güncellemesi tamamlandı.")


