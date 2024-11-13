from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk, messagebox
import yfinance as yf
import pandas as pd
import pymysql
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt


# Tkinter teması ve stil ayarları
def setup_style(root):
    style = ttk.Style(root)
    root.configure(bg='#2d2d2d')
    style.theme_use("clam")  # "clam" teması modern bir görünüm sağlar
    style.configure("TLabel", background="#2d2d2d", foreground="white", font=("Arial", 12))
    style.configure("TEntry", font=("Arial", 12))
    style.configure("TButton", font=("Arial", 12), background="#4caf50", foreground="white")
    style.configure("Treeview", rowheight=40)
    style.configure("Treeview.Heading", font=("Arial", 12, "bold"))
    style.configure("Treeview", font=("Arial", 12))


def show_data(ticker_symbol, data_frame):
    # Veriyi çekme
    ticker = yf.Ticker(ticker_symbol)
    data = ticker.history(period="1y")
    stock_name = ticker.info.get("longName", ticker_symbol)  # Hisse adını alma, yoksa sembolü kullan

    # MySQL bağlantısı oluşturma
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='123456',
        db='hisse_senedi_db',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

    # MySQL tablosu oluşturma
    create_table_query = """
    CREATE TABLE IF NOT EXISTS stock_data (
        id INT AUTO_INCREMENT PRIMARY KEY,
        hisse_adi VARCHAR(255),
        tarih DATE,
        acilis FLOAT,
        kapanis FLOAT,
        yuksek FLOAT,
        dusuk FLOAT,
        hacim BIGINT
    )
    """
    with connection.cursor() as cursor:
        cursor.execute(create_table_query)
        connection.commit()

    # Veriyi MySQL tablosuna kaydetme
    with connection.cursor() as cursor:
        for index, row in data.iterrows():
            insert_query = """
            INSERT INTO stock_data (hisse_adi, tarih, acilis, kapanis, yuksek, dusuk, hacim)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (stock_name, index.strftime('%Y-%m-%d'), row['Open'], row['Close'], row['High'], row['Low'], row['Volume']))
        connection.commit()

    connection.close()

    # Verileri gösterme işlemleri
    for widget in data_frame.winfo_children():
        widget.destroy()

    # Hisse adını göster
    ttk.Label(data_frame, text=f'Hisse Adı: {stock_name}', style="TLabel").pack(pady=10)

    tree = ttk.Treeview(data_frame)
    tree["columns"] = ["Tarih", "Açılış", "Kapanış", "Yüksek", "Düşük", "Hacim"]
    tree["show"] = "headings"
    for column in tree["columns"]:
        tree.heading(column, text=column)
        tree.column(column, width=150)
    for index, row in data.iterrows():
        tree.insert("", "end", values=(index.strftime('%Y-%m-%d'), row['Open'], row['Close'], row['High'], row['Low'], row['Volume']))
    tree.pack(fill=tk.BOTH, expand=True)


# Ana program
def main():
    root = tk.Tk()
    root.title("Hisse Senedi Verileri")
    root.geometry("800x600")  # Pencere boyutunu 800x600 olarak ayarla

    setup_style(root)

    tab_control = ttk.Notebook(root)
    tab1 = ttk.Frame(tab_control)
    tab2 = ttk.Frame(tab_control)
    tab_control.add(tab1, text='Ana Sayfa')
    tab_control.add(tab2, text='Veri Tablosu')
    tab_control.pack(expand=1, fill='both')

    ttk.Label(tab1, text='Hisse Senedi Ticker:', style="TLabel").pack(pady=10)
    ticker_entry = ttk.Entry(tab1, style="TEntry")
    ticker_entry.pack(pady=10)

    ttk.Button(tab1, text='Verileri Göster', command=lambda: show_data(ticker_entry.get(), tab2)).pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    main()
