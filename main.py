import pymysql
from Bollinger import BollingerBandsAnalyzer
from Ema import StockAnalyzer

connection = pymysql.connect(
    host='localhost',
    user='root',
    password='123456',
    db='hisse_senedi_db',
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

sumOfSignals = 0

try:
    stock_code = input("Hisse kodunu giriniz: ").upper()
    analyzer = BollingerBandsAnalyzer(connection, stock_code)
    sumOfSignals = sumOfSignals + analyzer.analyze()

    stock_analyzer = StockAnalyzer(connection, stock_code)
    sumOfSignals = sumOfSignals + stock_analyzer.analyze(5)
    sumOfSignals = sumOfSignals + stock_analyzer.analyze(10)
    sumOfSignals = sumOfSignals + stock_analyzer.analyze(25)

    if(sumOfSignals > 2):
        print("Risk oranı düşük, hisse alınabilir.")
    elif(sumOfSignals > 0):
        print("Risk oranı orta, hisse alınabilir")
    elif(sumOfSignals > -3):
        print("Risk oranı yüksek, hisse alınmamalı")
    else:
        print("Risk oranı çok yüksek, hisse alınmamalı")

finally:
    connection.close()


