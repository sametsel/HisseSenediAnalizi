import numpy as np
import matplotlib.pyplot as plt

class BollingerBandsAnalyzer:
    def __init__(self, connection, table_name):
        self.connection = connection
        self.table_name = table_name

    def fetch_data(self):
        """Veritabanından verileri çeker."""
        cursor = self.connection.cursor()
        query = f"SELECT Date, Close FROM {self.table_name} ORDER BY Date ASC"
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()
        
        if not data:
            print(f"{self.table_name} için veri bulunamadı.")
            return None, None
        
        dates = [row['Date'] for row in data]
        closing_prices = [row['Close'] for row in data]
        return dates, closing_prices

    def calculate_bollinger_bands(self, closing_prices, period=20):
        """Bollinger Bantları ve sinyalleri hesaplar."""
        sma20, std_dev, upper_band, lower_band, signals = [], [], [], [], []
        
        for i in range(period - 1, len(closing_prices)):
            sma20.append(np.mean(closing_prices[i - period + 1:i + 1]))
            std_dev.append(np.std(closing_prices[i - period + 1:i + 1]))
        
        for i in range(len(sma20)):
            upper_band.append(sma20[i] + (std_dev[i] * 2))
            lower_band.append(sma20[i] - (std_dev[i] * 2))
            
            # Alım ve satım sinyalleri
            if closing_prices[i + period - 1] > sma20[i] and closing_prices[i + period - 1] < closing_prices[i + period - 2]:
                signals.append(-1)  # Satım sinyali
            elif closing_prices[i + period - 1] < sma20[i] and closing_prices[i + period - 1] > closing_prices[i + period - 2]:
                signals.append(1)  # Alım sinyali
            else:
                signals.append(0)
        
        return sma20, upper_band, lower_band, signals

    def plot_bollinger_bands(self, dates, closing_prices, sma20, upper_band, lower_band, signals):
        """Bollinger Bantlarını ve sinyalleri grafik olarak gösterir."""
        plt.figure(figsize=(14, 7))
        plt.plot(dates[19:], closing_prices[19:], label='Close Price', color='blue', alpha=0.5)
        plt.plot(dates[19:], sma20, label='20 Day SMA', color='orange', alpha=0.5)
        plt.plot(dates[19:], upper_band, label='Upper Band', color='red', alpha=0.5)
        plt.plot(dates[19:], lower_band, label='Lower Band', color='green', alpha=0.5)

        # Sinyalleri grafikte işaretleme
        for i in range(len(signals)):
            if signals[i] == 1:  # Al sinyali
                plt.scatter(dates[i + 19], closing_prices[i + 19], marker='^', color='green', s=100, label='Buy Signal' if i == 0 else "")
            elif signals[i] == -1:  # Sat sinyali
                plt.scatter(dates[i + 19], closing_prices[i + 19], marker='v', color='red', s=100, label='Sell Signal' if i == 0 else "")
        
        plt.title(f'Bollinger Bands for {self.table_name}')
        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.legend()
        plt.grid()
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    signal = 0

    def analyze(self):
        """Veri çekme, hesaplama ve grafik işlemlerini başlatır."""
        dates, closing_prices = self.fetch_data()
        if dates and closing_prices:
            sma20, upper_band, lower_band, signals = self.calculate_bollinger_bands(closing_prices)

            # Grafik çizdirme
            self.plot_bollinger_bands(dates, closing_prices, sma20, upper_band, lower_band, signals)

            last_signal = signals[-1] if signals else None
            if last_signal == 1:
                return 1
            elif last_signal == -1:
                return -1
            else:
                return 0
                
            
            