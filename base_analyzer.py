import numpy as np
from matplotlib.figure import Figure

class BaseAnalyzer:
    def __init__(self, connection, table_name):
        self.connection = connection
        self.table_name = table_name

    def fetch_data(self):
        """Veritabanından hisse verilerini çekme."""
        cursor = self.connection.cursor()
        query = f"SELECT Date, Close FROM {self.table_name} ORDER BY Date ASC"
        cursor.execute(query)
        data = cursor.fetchall()

        if not data:
            print(f"{self.table_name} için veri bulunamadı.")
            return None, None

        dates = [row['Date'] for row in data]
        closing_prices = [row['Close'] for row in data]
        return dates, closing_prices

    def create_base_figure(self, title):
        """Temel grafik oluşturma"""
        fig = Figure(figsize=(10, 6))
        ax = fig.add_subplot(111)
        ax.set_title(title)
        ax.set_xlabel('Tarih')
        ax.set_ylabel('Fiyat')
        ax.grid(True, alpha=0.3)
        return fig, ax

    def add_signals_to_plot(self, ax, buy_dates, buy_prices, sell_dates, sell_prices):
        """Al/Sat sinyallerini grafiğe ekle"""
        if buy_dates:
            ax.scatter(buy_dates, buy_prices, marker='^', color='lime', s=100, 
                      label='Al Sinyali', zorder=5)
        
        if sell_dates:
            ax.scatter(sell_dates, sell_prices, marker='v', color='red', s=100, 
                      label='Sat Sinyali', zorder=5) 