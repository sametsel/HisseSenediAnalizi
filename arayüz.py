import tkinter as tk
from tkinter import messagebox, ttk
import pymysql
from Bollinger import BollingerBandsAnalyzer
from Ema import StockAnalyzer

def analyze_stock():
    stock_code = entry.get().upper()
    sumOfSignals = 0

    try:
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='123456',
            db='hisse_senedi_db',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )

        analyzer = BollingerBandsAnalyzer(connection, stock_code)
        sumOfSignals += analyzer.analyze()

        stock_analyzer = StockAnalyzer(connection, stock_code)
        sumOfSignals += stock_analyzer.analyze(5)
        sumOfSignals += stock_analyzer.analyze(10)
        sumOfSignals += stock_analyzer.analyze(25)

        if sumOfSignals > 2:
            result = "Risk oranı düşük, hisse alınabilir."
        elif sumOfSignals > 0:
            result = "Risk oranı orta, hisse alınabilir"
        elif sumOfSignals > -3:
            result = "Risk oranı yüksek, hisse alınmamalı"
        else:
            result = "Risk oranı çok yüksek, hisse alınmamalı"

        messagebox.showinfo("Sonuç", result)
    except Exception as e:
        messagebox.showerror("Hata", str(e))
    finally:
        connection.close()

def show_stock_data():
    stock_code = entry.get().upper()

    try:
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='123456',
            db='hisse_senedi_db',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )

        with connection.cursor() as cursor:
            query = f"SELECT * FROM {stock_code} ORDER BY Date DESC"
            cursor.execute(query)
            data = cursor.fetchall()

            if data:
                # Yeni bir sekme oluştur
                tab_control = ttk.Notebook(root)
                tab_control.pack(expand=1, fill='both')

                tab1 = ttk.Frame(tab_control)
                tab_control.add(tab1, text='Veriler')

                tree = ttk.Treeview(tab1, columns=('Date', 'Open', 'High', 'Low', 'Close', 'Volume'), show='headings')
                tree.heading('Date', text='Tarih')
                tree.heading('Open', text='Açılış')
                tree.heading('High', text='Yüksek')
                tree.heading('Low', text='Düşük')
                tree.heading('Close', text='Kapanış')
                tree.heading('Volume', text='Hacim')

                for row in data:
                    tree.insert('', 'end', values=(row['Date'], row['Open'], row['High'], row['Low'], row['Close'], row['Volume']))

                # Kaydırma çubuğu ekle
                scrollbar = ttk.Scrollbar(tab1, orient='vertical', command=tree.yview)
                tree.configure(yscroll=scrollbar.set)
                scrollbar.pack(side='right', fill='y')
                tree.pack(expand=True, fill='both')
            else:
                messagebox.showinfo("Bilgi", "Veritabanında veri bulunamadı.")
    except Exception as e:
        messagebox.showerror("Hata", str(e))
    finally:
        connection.close()

root = tk.Tk()
root.title("Hisse Analiz Aracı")
root.geometry("800x600")  # Arayüz boyutunu ayarla

frame = tk.Frame(root, padx=20, pady=20)
frame.pack(padx=10, pady=10)

tk.Label(frame, text="Hisse kodunu giriniz:").grid(row=0, column=0, pady=10)
entry = tk.Entry(frame)
entry.grid(row=0, column=1, pady=10)

tk.Button(frame, text="Analiz Et", command=analyze_stock).grid(row=1, columnspan=2, pady=20)
tk.Button(frame, text="Verileri Göster", command=show_stock_data).grid(row=2, columnspan=2, pady=20)

root.mainloop()
