import pymysql
from Bollinger import BollingerBandsAnalyzer
from Ema import StockAnalyzer

def analyze_stocka(stock_code):
    """
    Verilen hisse kodu için analiz yapar ve sonucu döndürür.
    """
    try:
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='123456',
            db='hisse_senedi_db',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )

        sumOfSignals = 0

        # Bollinger Bands Analizi
        analyzer = BollingerBandsAnalyzer(connection, stock_code)
        signal = analyzer.analyze(plot_graph=False)  
        sumOfSignals += signal

        # EMA Analizleri
        stock_analyzer = StockAnalyzer(connection, stock_code)
        ema5_signal = stock_analyzer.analyze(5, plot_graph=False)  
        ema10_signal = stock_analyzer.analyze(10, plot_graph=False)
        ema25_signal = stock_analyzer.analyze(25, plot_graph=False)

        sumOfSignals += ema5_signal + ema10_signal + ema25_signal

        # Risk analizi sonucunu belirle
        if sumOfSignals > 2:
            return "Risk oranı düşük, hisse alınabilir."
        elif sumOfSignals > 0:
            return "Risk oranı orta, hisse alınabilir."
        elif sumOfSignals > -3:
            return "Risk oranı yüksek, hisse alınmamalı."
        else:
            return "Risk oranı çok yüksek, hisse alınmamalı."

    except Exception as e:
        return f"Hata oluştu: {e}"

    finally:
        connection.close()


