import numpy as np
import matplotlib.pyplot as plt

class StockAnalyzer:
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

    def calculate_ema(self, closing_prices, period=20):
        """EMA hesaplama."""
        ema = []
        alpha = 2 / (period + 1)

        # İlk 'period' günün EMA'sını basit ortalama olarak alıyoruz
        ema.append(np.mean(closing_prices[:period]))

        # Diğer EMA'lar, önceki EMA ile hesaplanır
        for i in range(period, len(closing_prices)):
            ema.append(alpha * closing_prices[i] + (1 - alpha) * ema[-1])

        return ema

    def plot_ema(self, dates, closing_prices, ema, period):
        """EMA grafiğini çizme."""
        plt.figure(figsize=(8,5)) 
        plt.plot(dates[len(dates)-len(ema):], closing_prices[len(dates)-len(ema):], label='Kapanış Fiyatı', color='blue', alpha=0.5)
        plt.plot(dates[len(dates)-len(ema):], ema, label=f'{period} Günlük EMA', color='purple', alpha=0.7)

        # Başlık ve etiketler
        plt.title(f'EMA {period} Grafiği')
        plt.xlabel('Tarih')
        plt.ylabel('Fiyat')
        plt.legend(loc='center left', bbox_to_anchor=(1.05, 0.5), frameon=False)
        plt.grid()
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    def analyze(self, period, plot_graph=True):
        """Veri çekme, analiz ve isteğe bağlı olarak grafiği çizme."""
        dates, closing_prices = self.fetch_data()
        if dates is None or closing_prices is None:
            return 0

        # EMA hesaplama
        ema = self.calculate_ema(closing_prices, period)

        # Sinyal hesaplama
        signals = []
        for i in range(period, len(closing_prices)):
            if closing_prices[i] > ema[i - period] and closing_prices[i - 1] > closing_prices[i]:  # EMA'nın üstündeyken aşağı yönlü hareket (satım)
                signals.append(-1)
            elif closing_prices[i] < ema[i - period] and closing_prices[i - 1] < closing_prices[i]:  # EMA'nın altındayken yukarı yönlü hareket (alım)
                signals.append(1)
            else:  # Diğer durumlar sinyal yok
                signals.append(0)

        # Grafiği oluştur
        if plot_graph:
            self.plot_ema(dates, closing_prices, ema, period)

        last_signal = signals[-1] if signals else None
        if last_signal == 1:
            return 1
        elif last_signal == -1:
            return -1
        else:
            return 0

        