from base_analyzer import BaseAnalyzer
import numpy as np

class BollingerBandsAnalyzer(BaseAnalyzer):
    def calculate_bollinger_bands(self, closing_prices, period=20):
        """Bollinger Bantları ve sinyalleri hesaplar."""
        sma20 = np.convolve(closing_prices, np.ones(period)/period, mode='valid')
        std_dev = [np.std(closing_prices[i-period:i]) for i in range(period, len(closing_prices)+1)]
        
        upper_band = sma20 + (np.array(std_dev) * 2)
        lower_band = sma20 - (np.array(std_dev) * 2)
        
        return sma20, upper_band, lower_band

    def plot_bollinger_bands(self, dates, closing_prices, sma20, upper_band, lower_band):
        fig, ax = self.create_base_figure(f'{self.table_name} - Bollinger Bantları')
        
        # Ana çizgiler
        ax.plot(dates[19:], closing_prices[19:], label='Kapanış Fiyatı', color='blue', alpha=0.5)
        ax.plot(dates[19:], sma20, label='20 Günlük SMA', color='orange', alpha=0.5)
        ax.plot(dates[19:], upper_band, label='Üst Bant', color='red', alpha=0.5)
        ax.plot(dates[19:], lower_band, label='Alt Bant', color='green', alpha=0.5)

        # Al/Sat sinyallerini hesapla
        buy_dates, buy_prices = [], []
        sell_dates, sell_prices = [], []
        
        for i in range(len(sma20)):
            idx = i + 19
            if closing_prices[idx] > sma20[i] and closing_prices[idx] < closing_prices[idx-1]:
                sell_dates.append(dates[idx])
                sell_prices.append(closing_prices[idx])
            elif closing_prices[idx] < sma20[i] and closing_prices[idx] > closing_prices[idx-1]:
                buy_dates.append(dates[idx])
                buy_prices.append(closing_prices[idx])

        self.add_signals_to_plot(ax, buy_dates, buy_prices, sell_dates, sell_prices)
        ax.legend(loc='upper left')
        fig.tight_layout()
        return fig

    def analyze(self, plot_graph=True):
        dates, closing_prices = self.fetch_data()
        if dates and closing_prices:
            sma20, upper_band, lower_band = self.calculate_bollinger_bands(closing_prices)
            
            if plot_graph:
                return self.plot_bollinger_bands(dates, closing_prices, sma20, upper_band, lower_band)

            # Son sinyal kontrolü
            if closing_prices[-1] > sma20[-1] and closing_prices[-1] < closing_prices[-2]:
                return -1
            elif closing_prices[-1] < sma20[-1] and closing_prices[-1] > closing_prices[-2]:
                return 1
            return 0
