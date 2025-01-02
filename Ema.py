from base_analyzer import BaseAnalyzer
import numpy as np

class StockAnalyzer(BaseAnalyzer):
    def calculate_ema(self, closing_prices, period=20):
        """EMA hesaplama."""
        alpha = 2 / (period + 1)
        ema = [np.mean(closing_prices[:period])]
        
        for price in closing_prices[period:]:
            ema.append(alpha * price + (1 - alpha) * ema[-1])
            
        return ema

    def plot_ema(self, dates, closing_prices, ema, period):
        fig, ax = self.create_base_figure(f'{self.table_name} - EMA {period} Grafiği')
        
        start_idx = len(dates) - len(ema)
        ax.plot(dates[start_idx:], closing_prices[start_idx:], 
                label='Kapanış Fiyatı', color='blue', alpha=0.5)
        ax.plot(dates[start_idx:], ema, 
                label=f'{period} Günlük EMA', color='purple', alpha=0.7)

        # Al/Sat sinyallerini hesapla
        buy_dates, buy_prices = [], []
        sell_dates, sell_prices = [], []
        
        for i in range(period, len(closing_prices)):
            if closing_prices[i] > ema[i - period] and closing_prices[i - 1] > closing_prices[i]:
                sell_dates.append(dates[i])
                sell_prices.append(closing_prices[i])
            elif closing_prices[i] < ema[i - period] and closing_prices[i - 1] < closing_prices[i]:
                buy_dates.append(dates[i])
                buy_prices.append(closing_prices[i])

        self.add_signals_to_plot(ax, buy_dates, buy_prices, sell_dates, sell_prices)
        ax.legend(loc='upper left')
        fig.tight_layout()
        return fig

    def analyze(self, period, plot_graph=True):
        dates, closing_prices = self.fetch_data()
        if dates is None or closing_prices is None:
            return 0

        ema = self.calculate_ema(closing_prices, period)

        if plot_graph:
            return self.plot_ema(dates, closing_prices, ema, period)

        # Son sinyal kontrolü
        if closing_prices[-1] > ema[-1] and closing_prices[-2] > closing_prices[-1]:
            return -1
        elif closing_prices[-1] < ema[-1] and closing_prices[-2] < closing_prices[-1]:
            return 1
        return 0

        