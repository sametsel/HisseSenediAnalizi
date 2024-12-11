import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import pymysql
from Bollinger import BollingerBandsAnalyzer
from Ema import StockAnalyzer
from main import analyze_stocka 
from VeriCekme import fetch_and_update_data
import threading
import time

# Analiz sonuçlarını global olarak saklama
analysis_result = None

def analyze_stock():
    """Kullanıcının seçtiği grafik türünü analiz eder ve sonucu kaydeder."""
    global analysis_result
    stock_code = entry.get().upper()
    selected_graph = graph_selection.get()

    try:
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='123456',
            db='hisse_senedi_db',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )

        if selected_graph == "Bollinger Bands":
            analyzer = BollingerBandsAnalyzer(connection, stock_code)
            analysis_result = analyzer.analyze()
        elif selected_graph == "EMA 5":
            analyzer = StockAnalyzer(connection, stock_code)
            analysis_result = analyzer.analyze(5)
        elif selected_graph == "EMA 10":
            analyzer = StockAnalyzer(connection, stock_code)
            analysis_result = analyzer.analyze(10)
        elif selected_graph == "EMA 25":
            analyzer = StockAnalyzer(connection, stock_code)
            analysis_result = analyzer.analyze(25)
        else:
            analysis_result = "Lütfen bir grafik türü seçin."
    except Exception as e:
        analysis_result = f"Hata: {str(e)}"
    finally:
        connection.close()

def show_analysis_result():
    """
    Analiz sonucunu kullanıcıya gösterir (grafik olmadan).
    """
    stock_code = entry.get().upper()
    if not stock_code:
        messagebox.showwarning("Uyarı", "Lütfen bir hisse kodu giriniz.")
        return

    try:
        # Analyze the stock
        result = analyze_stocka(stock_code)
        messagebox.showinfo("Analiz Sonucu", result)
    except Exception as e:
        messagebox.showerror("Hata", f"Bir hata oluştu: {e}")

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
            query = f"SELECT * FROM `{stock_code}` ORDER BY Date DESC"
            cursor.execute(query)
            data = cursor.fetchall()

            if data:
                for widget in tab1.winfo_children():
                    widget.destroy()  # Önceki içerikleri temizle

                # Treeview stilini tanımla ve arka plan rengini yeşil yap
                style = ttk.Style()
                style.configure("Custom.Treeview", background="lightgreen", fieldbackground="lightgreen", font=("Arial", 10))
                style.configure("Custom.Treeview.Heading", font=("Arial", 12, "bold"), foreground="black")

                # Treeview oluştur
                tree = ttk.Treeview(tab1, columns=('Date', 'Open', 'High', 'Low', 'Close', 'Volume'), 
                                    show='headings', height=20, style="Custom.Treeview")
                tree.heading('Date', text='Tarih')
                tree.heading('Open', text='Açılış')
                tree.heading('High', text='Yüksek')
                tree.heading('Low', text='Düşük')
                tree.heading('Close', text='Kapanış')
                tree.heading('Volume', text='Hacim')

                # Sütun genişliklerini ayarla
                tree.column('Date', width=70, anchor='center')
                tree.column('Open', width=50, anchor='center')
                tree.column('High', width=50, anchor='center')
                tree.column('Low', width=50, anchor='center')
                tree.column('Close', width=50, anchor='center')
                tree.column('Volume', width=50, anchor='center')

                for row in data:
                    tree.insert('', 'end', values=(row['Date'], row['Open'], row['High'], row['Low'], row['Close'], row['Volume']))

                # Kaydırma çubuğu ekle
                scrollbar = ttk.Scrollbar(tab1, orient='vertical', command=tree.yview)
                tree.configure(yscroll=scrollbar.set)

                # Treeview ve scrollbar'ı yerleştir
                tree.grid(row=0, column=0, sticky='nsew')
                scrollbar.grid(row=0, column=1, sticky='ns')

                # Sekme alanını küçült ve sağ üst köşeye yerleştir
                tab1.grid_columnconfigure(0, weight=2)
                tab1.grid_rowconfigure(0, weight=5)

                # Sekmeyi sağ üst köşeye taşı
                tab_control.pack_forget()
                tab_control.place(relx=0.70, rely=0.0, relwidth=0.30, relheight=0.40)
                
                tab_control.add(tab1, text='Veriler')
                tab_control.select(tab1)
            else:
                messagebox.showinfo("Bilgi", "Veritabanında veri bulunamadı.")
    except Exception as e:
        messagebox.showerror("Hata", str(e))
def update_data_with_loading():
    """
    Veritabanı güncelleme işlemini başlatır ve yükleme simgesi gösterir.
    """
    # Yükleme simgesi için ayrı bir pencere oluştur
    loading_window = tk.Toplevel(root)
    loading_window.title("Veriler Güncelleniyor")
    loading_window.geometry("300x100")
    loading_window.resizable(False, False)

    # Yükleme etiketi ve çubuğu
    progress_label = tk.Label(loading_window, text="Veriler güncelleniyor, lütfen bekleyin...", font=("Arial", 10))
    progress_label.pack(pady=10)

    progress_bar = ttk.Progressbar(loading_window, mode="indeterminate")
    progress_bar.pack(pady=10)
    progress_bar.start()

    def update_task():
        """
        Veritabanı güncelleme işlemini arka planda çalıştırır.
        """
        try:
            fetch_and_update_data(progress_callback=lambda msg: progress_label.config(text=msg))  # Veri çekme işlemi
        except Exception as e:
            messagebox.showerror("Hata", f"Bir hata oluştu: {str(e)}")
        finally:
            progress_bar.stop()  # Yükleme çubuğunu durdur
            loading_window.destroy()  # Yükleme penceresini kapat
            messagebox.showinfo("Başarılı", "Tüm veriler güncellendi.")  # Bilgi mesajı

    # İş parçacığında güncelleme işlemini başlat
    threading.Thread(target=update_task).start()
def clear_placeholder(event):
    """
    Kullanıcı combobox'a tıkladığında placeholder metnini temizler.
    """
    if entry.get() == "Hisse seçiniz veya giriniz":
        entry.set("")  # Placeholder'ı temizle
def update_combobox_values(event):
    """
    Kullanıcının yazdığı metne göre combobox içeriğini filtreler ve listeyi otomatik açar.
    """
    user_input = entry.get().lower()

    if user_input == "":
        # Eğer giriş boşsa, tüm listeyi geri yükle
        entry["values"] = hisse_listesi
    else:
        # Filtrelenmiş listeyi oluştur
        filtered_hisse_listesi = [hisse for hisse in hisse_listesi if user_input in hisse.lower()]
        entry["values"] = filtered_hisse_listesi

    # İmleç konumunu koru
    entry.icursor(len(user_input))

    # Listeyi aç ama odak kaymasını engelle
    if len(entry["values"]) > 0:  # Filtrelenmiş liste boş değilse
        entry.event_generate('<Down>')  # Listeyi aç

# Ana pencere
root = tk.Tk()
root.title("Hisse Analiz Aracı")
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Canvas üzerinde arka plan resmi
canvas = tk.Canvas(root, width=screen_width, height=screen_height)
canvas.pack(fill="both", expand=True)

try:
    image_path = "C:/Users/Samet  SEL/Downloads/HisseSenediAnalizi-main/HisseSenediAnalizi-main/a.webp"
    image = Image.open(image_path)
    background_image = ImageTk.PhotoImage(image.resize((screen_width, screen_height)))
    canvas.create_image(0, 0, image=background_image, anchor="nw")
    canvas.background_image = background_image
except Exception as e:
    print(f"Resim yüklenemedi: {e}")

# Kullanıcı giriş kısmı doğrudan Canvas üzerine yerleştirildi
canvas.create_text(screen_width // 2, 100, text="Hisse kodunu seçiniz veya giriniz:", font=("Arial", 12), fill="white")

# Hisse seçim/düzenleme için Combobox
hisse_listesi = [
    "AEFES", "AGHOL", "AKBNK", "AKSEN", "ALARK", "ALFAS", "ALTNY", "ARCLK", "ASELS", "ASTOR",
    "BERA", "BIMAS", "BINHO", "BJKAS", "CCOLA", "CWENE", "CIMSA", "CLEBI", "DOAS", "BRSAN",
    "DOHOL", "EGEEN", "ECILC", "ENERY", "ENKAI", "ENJSA", "EREGL", "FENER", "FROTO", "PEKGY",
    "GARAN", "GESAN", "GOLTS", "GUBRF", "HALKB", "HEKTS", "ISCTR", "ISMEN", "EKGYO", "CANTE",
    "KARSN", "KCAER", "KCHOL", "KLSER", "KONTR", "KONYA", "KOZAA", "TABGD", "BTCIM", "BRYAT",
    "KOZAL", "KRDMD", "KTLEV", "LMKDC", "MAVI", "MGROS", "MPARK", "OBAMS", "ODAS", "ARDYZ",  
    "OTKAR", "OYAKC", "PAPIL", "PETKM", "PGSUS", "REEDR", "RGYAS", "SMRTG", "ANSGR", "AGROT",
    "SAHOL", "SASA", "SISE", "SKBNK", "SOKM", "TAVHL", "TCELL", "THYAO", "TKFEN", "TMSN", 
    "TSKB", "TOASO", "TTKOM", "TTRAK", "TUKAS", "TUPRS", "TURSG", "ULKER", "EUPWR",
    "VAKBN", "VESTL", "VESBE", "YKBNK", "YEOTK", "ZOREN", "ADEL", "AKFGY", "AKFYE", "AKSA"
]

entry = ttk.Combobox(canvas, values=hisse_listesi, font=("Arial", 12))
entry.set("Hisse seçiniz veya giriniz")  # Varsayılan yazı
entry.bind("<Button-1>", clear_placeholder)
entry.bind("<KeyRelease>", update_combobox_values)
canvas.create_window(screen_width // 2, 130, window=entry)

# Grafik seçimi için dropdown
canvas.create_text(screen_width // 2, 160, text="Grafik Türü Seçin:", font=("Arial", 12), fill="white")
graph_selection = ttk.Combobox(canvas, values=["Bollinger Bands", "EMA 5", "EMA 10", "EMA 25"], state="readonly")
canvas.create_window(screen_width // 2, 190, window=graph_selection)
graph_selection.set("Bollinger Bands")

# Düğmeler
show_button = tk.Button(canvas, text="Göster", command=analyze_stock, bg="#4CAF50", fg="white", font=("Arial", 12))
canvas.create_window(screen_width // 2, 230, window=show_button)

show_data_button = tk.Button(canvas, text="Verileri Göster", command=show_stock_data, bg="#2196F3", fg="white", font=("Arial", 12))
canvas.create_window(screen_width // 2, 270, window=show_data_button)

show_result_button = tk.Button(canvas, text="Analiz Sonucunu Göster", command=show_analysis_result, bg="#FF9800", fg="white", font=("Arial", 12))
canvas.create_window(screen_width // 2, 310, window=show_result_button)

update_button = tk.Button(canvas, text="Verileri Güncelle", command=update_data_with_loading, bg="#2236F3", fg="white",font=("Arial", 12))
canvas.create_window(screen_width // 2, 350, window=update_button)

# Sekme oluştur ve Canvas üzerine ekle
tab_control = ttk.Notebook(canvas)
canvas.create_window(screen_width // 2, screen_height // 1.5, window=tab_control, anchor="n")

tab1 = ttk.Frame(tab_control)
tab_control.add(tab1, text='Veriler')
tab_control.hide(tab1)

root.mainloop() 

