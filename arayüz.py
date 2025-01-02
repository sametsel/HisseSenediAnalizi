import sys
import traceback
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QPushButton, 
                            QVBoxLayout, QHBoxLayout, QComboBox, QLabel, 
                            QTableWidget, QTableWidgetItem, QTabWidget, QMessageBox,
                            QScrollArea, QHeaderView, QDockWidget, QGridLayout)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QTime
from PyQt5.QtGui import QImage, QPalette, QBrush
import pymysql
from Bollinger import BollingerBandsAnalyzer
from Ema import StockAnalyzer
from main import analyze_stocka
from VeriCekme import bist100_hisseleri, fetch_and_update_data, DB_CONFIG
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import os  

# Hisse listesi
hisse_listesi = bist100_hisseleri

class UpdateThread(QThread):
    finished = pyqtSignal(str)
    progress = pyqtSignal(str)

    def run(self):
        try:
            fetch_and_update_data(progress_callback=lambda msg: self.progress.emit(msg))
            self.finished.emit("Veriler başarıyla güncellendi!")
        except Exception as e:
            self.finished.emit(f"Hata: {str(e)}")

class StockTickerWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(350)
        self.setup_ui()
        self.setup_timers()
        self.update_prices()
        self.setEnabled(False)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        
        header = self.create_header()
        layout.addWidget(header)
        
        self.setup_scroll_area()
        layout.addWidget(self.scroll)

    def create_header(self):
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(5, 5, 5, 5)
        
        for title in ["Kod", "Son", "Değişim", "Hacim"]:
            label = QLabel(title)
            label.setStyleSheet("color: white; font-weight: bold; padding: 5px;")
            header_layout.addWidget(label, 1)
        
        header.setStyleSheet("background-color: rgb(30, 30, 30);")
        return header

    def setup_scroll_area(self):
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setStyleSheet("QScrollArea { border: none; background-color: rgb(30, 30, 30); }")
        
        self.content = QWidget()
        self.content.setStyleSheet("background-color: rgb(30, 30, 30);")
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setSpacing(1)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll.setWidget(self.content)

    def setup_timers(self):
        self.scroll_pos = 0
        self.scroll_speed = 3
        self.pause_duration = 1000
        self.is_paused = False
        self.last_pause = 0
        
        self.scroll_timer = QTimer(self)
        self.scroll_timer.timeout.connect(self.scroll_content)
        self.scroll_timer.start(15)
        
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_prices)
        self.update_timer.start(10000)

    def scroll_content(self):
        try:
            if not self.content_layout.count():
                return
            
            scrollbar = self.scroll.verticalScrollBar()
            max_scroll = scrollbar.maximum()
            
            if max_scroll == 0:
                return
            
            if self.is_paused:
                if QTime.currentTime().msecsSinceStartOfDay() - self.last_pause > self.pause_duration:
                    self.is_paused = False
                return
            
            self.scroll_pos += self.scroll_speed
            
            if self.scroll_pos % 30 == 0:
                self.is_paused = True
                self.last_pause = QTime.currentTime().msecsSinceStartOfDay()
                QTimer.singleShot(self.pause_duration, lambda: setattr(self, 'is_paused', False))
            
            if self.scroll_pos >= max_scroll:
                self.scroll_pos = 0
            
            scrollbar.setValue(int(self.scroll_pos))
            
        except Exception as e:
            print(f"Kaydırma hatası: {str(e)}")

    def update_prices(self):
        try:
            connection = pymysql.connect(**DB_CONFIG)
            self.clear_content()
            
            for stock in hisse_listesi:
                self.add_stock_widget(connection, stock)
            
        except Exception as e:
            print(f"Fiyat güncelleme hatası: {str(e)}")
        finally:
            if 'connection' in locals():
                connection.close()

    def clear_content(self):
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.scroll_pos = 0

    def add_stock_widget(self, connection, stock):
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"SELECT * FROM {stock} ORDER BY Date DESC LIMIT 2")
                data = cursor.fetchall()
                
                if len(data) >= 2:
                    current = float(data[0]['Close'])
                    previous = float(data[1]['Close'])
                    change = ((current - previous) / previous) * 100
                    volume = int(data[0]['Volume'])
                    
                    item = self.create_stock_item(stock, current, change, volume)
                    self.content_layout.addWidget(item)
        except Exception as e:
            print(f"Hisse ekleme hatası ({stock}): {str(e)}")

    def create_stock_item(self, stock, price, change, volume):
        item = QWidget()
        item.setFixedHeight(30)
        item_layout = QHBoxLayout(item)
        item_layout.setContentsMargins(5, 2, 5, 2)
        
        code = QLabel(stock)
        code.setStyleSheet("color: white; font-weight: bold;")
        
        price_label = QLabel(f"{price:.2f}")
        price_label.setStyleSheet("color: white;")
        
        color = "#00FF7F" if change > 0 else "#FF4444"
        arrow = "▲" if change > 0 else "▼"
        change_label = QLabel(f"{arrow} {abs(change):.2f}%")
        change_label.setStyleSheet(f"color: {color};")
        
        volume_label = QLabel(f"{volume:,}")
        volume_label.setStyleSheet("color: #888888;")
        
        item_layout.addWidget(code, 1)
        item_layout.addWidget(price_label, 1)
        item_layout.addWidget(change_label, 1)
        item_layout.addWidget(volume_label, 1)
        
        item.setStyleSheet("""
            QWidget {
                background-color: rgb(40, 40, 40);
                border-radius: 3px;
                margin: 1px;
            }
            QWidget:hover {
                background-color: rgb(45, 45, 45);
            }
        """)
        return item

class StockAnalyzerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hisse Analiz Aracı")
        
        self.setup_background()
        
        self.setStyleSheet("""
            QMainWindow {
                background: none;  /* transparent yerine none kullan */
            }
            QWidget {
                background-color: transparent;
            }
            QPushButton {
                background-color: rgba(95, 158, 160, 0.9);
                color: white;
                border: none;
                padding: 10px;
                border-radius: 15px;
                font-size: 12px;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: rgba(79, 142, 144, 0.9);
            }
            QComboBox {
                background-color: rgba(255, 255, 255, 0.9);
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 5px;
                min-width: 200px;
            }
            QLabel {
                color: white;
                font-size: 12px;
                font-weight: bold;
                background-color: rgba(0, 0, 0, 0.5);
                padding: 5px;
                border-radius: 5px;
            }
            QTableWidget {
                background-color: rgb(0, 0, 0);
                color: white;
                gridline-color: #3D3D3D;
            }
            QHeaderView::section {
                background-color: rgb(0, 0, 0);
                color: white;
                padding: 5px;
            }
            QTabWidget::pane {
                background-color: transparent;
                border: none;
            }
            QTabBar::tab {
                background-color: rgba(61, 61, 61, 0.7);
                color: white;
                padding: 8px 15px;
                margin: 2px;
                border-radius: 5px;
            }
            QTabBar::tab:selected {
                background-color: rgba(95, 158, 160, 0.7);
            }
        """)
        
        self.init_ui()

    def setup_background(self):
        """Arka plan resmini ayarla ve güncelle"""
        # Arka plan resmi yolu
        current_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(current_dir, '3.jpg')
        self.background_image = QImage(image_path)
        
        if not self.background_image.isNull():
            # Resmi ölçeklendir ve uygula
            scaled_image = self.background_image.scaled(
                self.size(),
                Qt.KeepAspectRatioByExpanding,
                Qt.SmoothTransformation
            )
            palette = self.palette()
            palette.setBrush(QPalette.Window, QBrush(scaled_image))
            self.setPalette(palette)
            self.setAttribute(Qt.WA_StyledBackground)
            self.setAutoFillBackground(True)
            
            # Pencere yeniden boyutlandırma olayını bağla
            self.resizeEvent = lambda event: self.setup_background()

    def init_ui(self):
        central_widget = QWidget()
        central_widget.setAttribute(Qt.WA_TranslucentBackground)
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)
        
        # Sol panel
        left_dock = QDockWidget("Kontrol Paneli", self)
        left_dock.setFixedWidth(250)
        left_dock.setWidget(self.create_control_panel())
        left_dock.setFeatures(QDockWidget.NoDockWidgetFeatures)
        self.addDockWidget(Qt.LeftDockWidgetArea, left_dock)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        layout.addWidget(self.tab_widget, stretch=1)
        
        # Sağ panel
        right_dock = QDockWidget("Canlı Fiyatlar", self)
        right_dock.setFixedWidth(350)
        right_dock.setWidget(StockTickerWidget())
        right_dock.setFeatures(QDockWidget.NoDockWidgetFeatures)
        self.addDockWidget(Qt.RightDockWidgetArea, right_dock)
        
        self.showMaximized()

    def create_control_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Hisse Seçimi
        stock_label = QLabel("Hisse Kodu:")
        self.stock_combo = QComboBox()
        self.stock_combo.addItems(hisse_listesi)
        self.stock_combo.setEditable(True)
        self.stock_combo.setInsertPolicy(QComboBox.NoInsert)
        
        # Grafik Seçimi
        graph_label = QLabel("Grafik Türü:")
        self.graph_combo = QComboBox()
        self.graph_combo.addItems(["Bollinger Bands", "EMA 5", "EMA 10", "EMA 25"])
        
        # Butonlar
        self.show_button = QPushButton("Göster")
        self.show_data_button = QPushButton("Verileri Göster")
        self.show_result_button = QPushButton("Analiz Sonucunu Göster")
        self.update_button = QPushButton("Verileri Güncelle")
        
        # Buton bağlantıları
        self.show_button.clicked.connect(self.analyze_stock)
        self.show_data_button.clicked.connect(self.show_stock_data)
        self.show_result_button.clicked.connect(self.show_analysis_result)
        self.update_button.clicked.connect(self.update_data)
        
        # Sol panel yerleşimi
        layout.addWidget(stock_label)
        layout.addWidget(self.stock_combo)
        layout.addWidget(graph_label)
        layout.addWidget(self.graph_combo)
        layout.addWidget(self.show_button)
        layout.addWidget(self.show_data_button)
        layout.addWidget(self.show_result_button)
        layout.addWidget(self.update_button)
        layout.addStretch()
        
        return panel

    def analyze_stock(self):
        stock_code = self.stock_combo.currentText().upper()
        selected_graph = self.graph_combo.currentText()
        
        try:
            connection = pymysql.connect(**DB_CONFIG)
            
            if selected_graph == "Bollinger Bands":
                analyzer = BollingerBandsAnalyzer(connection, stock_code)
                figure = analyzer.analyze(plot_graph=True)
            elif selected_graph.startswith("EMA"):
                period = int(selected_graph.split()[1])
                analyzer = StockAnalyzer(connection, stock_code)
                figure = analyzer.analyze(period, plot_graph=True)
                
            # Sadece grafiği göster
            self.show_graph(figure, stock_code, selected_graph)
            
        except Exception as e:
            msg = QMessageBox()
            msg.setWindowTitle("Hata")
            msg.setText(str(e))
            msg.setIcon(QMessageBox.Critical)
            msg.exec_()
        finally:
            if 'connection' in locals():
                connection.close()

    def show_stock_data(self):
        stock_code = self.stock_combo.currentText().upper()
        
        try:
            connection = pymysql.connect(**DB_CONFIG)
            
            with connection.cursor() as cursor:
                query = f"SELECT * FROM `{stock_code}` ORDER BY Date DESC"
                cursor.execute(query)
                data = cursor.fetchall()
                
                if data:
                    # Yeni tab oluştur
                    tab = QWidget()
                    tab.setStyleSheet("background-color: rgb(0, 0, 0);")
                    tab_layout = QHBoxLayout(tab)  
                    
                    # Tablo widget'ı - Sol taraf
                    table = QTableWidget()
                    table.setStyleSheet("""
                        QTableWidget {
                            background-color: rgb(0, 0, 0);
                            color: white;
                            gridline-color: #3D3D3D;
                        }
                        QHeaderView::section {
                            background-color: rgb(0, 0, 0);
                            color: white;
                            padding: 5px;
                        }
                    """)
                    
                    table.setEditTriggers(QTableWidget.NoEditTriggers)
                    table.setFocusPolicy(Qt.NoFocus)
                    table.setSelectionMode(QTableWidget.NoSelection)
                    
                    table.setColumnCount(6)
                    table.setHorizontalHeaderLabels(['TARİH', 'AÇILIŞ', 'YÜKSEK', 'DÜŞÜK', 'KAPANIŞ', 'HACİM'])
                    
                    # Verileri tabloya ekle
                    table.setRowCount(len(data))
                    for row, record in enumerate(data):
                        table.setItem(row, 0, QTableWidgetItem(str(record['Date'])))
                        table.setItem(row, 1, QTableWidgetItem(f"{float(record['Open']):.2f}"))
                        table.setItem(row, 2, QTableWidgetItem(f"{float(record['High']):.2f}"))
                        table.setItem(row, 3, QTableWidgetItem(f"{float(record['Low']):.2f}"))
                        table.setItem(row, 4, QTableWidgetItem(f"{float(record['Close']):.2f}"))
                        table.setItem(row, 5, QTableWidgetItem(f"{int(record['Volume']):,}"))
                    
                    # Detay bilgileri widget'ı - Sağ taraf
                    detail_group = QWidget()
                    detail_layout = QGridLayout(detail_group)
                    detail_group.setFixedWidth(250)  # Sabit genişlik
                    
                    # Son veriyi al ve detay bilgilerini hazırla
                    latest_data = data[0]
                    previous_data = data[1] if len(data) > 1 else latest_data
                    
                    current_price = float(latest_data['Close'])
                    previous_price = float(previous_data['Close'])
                    change = ((current_price - previous_price) / previous_price) * 100
                    
                    # Başlık
                    title = QLabel(f"{stock_code} Detay Bilgileri")
                    title.setStyleSheet("color: white; font-size: 14px; font-weight: bold; padding: 5px;")
                    detail_layout.addWidget(title, 0, 0, 1, 2)
                    
                    # 52 haftalık yüksek/düşük hesapla
                    high_52w = max([float(row['High']) for row in data[:252]])
                    low_52w = min([float(row['Low']) for row in data[:252]])
                    
                    # Detay bilgileri
                    labels = [
                        ("Son Fiyat:", f"{current_price:.2f} ₺"),
                        ("Günlük Değişim:", f"{'▲' if change >= 0 else '▼'} {abs(change):.2f}%", "#00FF7F" if change >= 0 else "#FF4444"),
                        ("Günlük Hacim:", f"{int(latest_data['Volume']):,}"),
                        ("52H En Yüksek:", f"{high_52w:.2f}"),
                        ("52H En Düşük:", f"{low_52w:.2f}"),
                        ("Günlük Aralık:", f"{float(latest_data['High']):.2f} - {float(latest_data['Low']):.2f}")
                    ]
                    
                    for i, label_info in enumerate(labels, 1):
                        label = QLabel(label_info[0])
                        value = QLabel(label_info[1])
                        label.setStyleSheet("color: #888888; font-size: 11px;")
                        
                        # Eğer renk bilgisi varsa (Günlük Değişim için) o rengi kullan, yoksa beyaz kullan
                        if len(label_info) > 2:
                            value.setStyleSheet(f"color: {label_info[2]}; font-size: 11px; font-weight: bold;")
                        else:
                            value.setStyleSheet("color: white; font-size: 11px; font-weight: bold;")
                        
                        detail_layout.addWidget(label, i, 0)
                        detail_layout.addWidget(value, i, 1)
                    
                    detail_group.setStyleSheet("""
                        QWidget {
                            background-color: rgb(20, 20, 20);
                            border-radius: 5px;
                            padding: 10px;
                            margin: 5px;
                        }
                    """)
                    
                    # Widget'ları ana layout'a ekle
                    tab_layout.addWidget(table, stretch=3)  
                    tab_layout.addWidget(detail_group, stretch=1)  
                    
                    # Tab'ı ekle
                    self.tab_widget.addTab(tab, f"{stock_code} Verileri")
                    self.tab_widget.setCurrentWidget(tab)
                    
                    self.adjust_table_columns(table)
                    
        except Exception as e:
            QMessageBox.critical(self, "Hata", str(e))
        finally:
            connection.close()

    def show_analysis_result(self):
        stock_code = self.stock_combo.currentText().upper()
        try:
            result = analyze_stocka(stock_code)
            msg = QMessageBox()
            msg.setWindowTitle("Analiz Sonucu")
            msg.setText(str(result))
            msg.setIcon(QMessageBox.Information)
            msg.exec_()
        except Exception as e:
            msg = QMessageBox()
            msg.setWindowTitle("Hata")
            msg.setText(str(e))
            msg.setIcon(QMessageBox.Critical)
            msg.exec_()

    def update_data(self):
        self.update_thread = UpdateThread()
        self.update_thread.finished.connect(self.update_finished)
        self.update_thread.progress.connect(self.update_progress)
        self.update_thread.start()
        self.update_button.setEnabled(False)

    def update_finished(self, message):
        self.update_button.setEnabled(True)
        msg = QMessageBox()
        msg.setWindowTitle("Güncelleme Durumu")
        msg.setText(message)
        msg.setIcon(QMessageBox.Information)
        msg.exec_()

    def update_progress(self, message):
        self.update_button.setText(message)
        
    def adjust_table_columns(self, table):
        """Tablo sütun genişliklerini ayarla"""
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)  # TARİH
        header.setSectionResizeMode(1, QHeaderView.Fixed)  # AÇILIŞ
        header.setSectionResizeMode(2, QHeaderView.Fixed)  # YÜKSEK
        header.setSectionResizeMode(3, QHeaderView.Fixed)  # DÜŞÜK
        header.setSectionResizeMode(4, QHeaderView.Fixed)  # KAPANIŞ
        header.setSectionResizeMode(5, QHeaderView.Fixed)  # HACİM
        

    def show_graph(self, figure, stock_code, graph_type):
        if figure:
            tab = QWidget()
            tab_layout = QVBoxLayout(tab)
            
            canvas = FigureCanvas(figure)
            
            toolbar = NavigationToolbar(canvas, tab)
            toolbar.setStyleSheet("""
                QToolBar {
                    background-color: rgba(45, 45, 45, 0.9);
                    border: none;
                    padding: 5px;
                }
                QToolButton {
                    background-color: rgba(95, 158, 160, 0.9);
                    color: white;
                    border: none;
                    border-radius: 3px;
                    padding: 5px;
                    margin: 1px;
                }
                QToolButton:hover {
                    background-color: rgba(79, 142, 144, 0.9);
                }
                /* Matplotlib ayarlar penceresi için stil */
                QDialog {
                    background-color: rgb(45, 45, 45);
                }
                QDialog QLabel {
                    color: white;
                    background: transparent;
                }
                QDialog QLineEdit {
                    background-color: rgb(60, 60, 60);
                    color: white;
                    border: 1px solid rgb(80, 80, 80);
                    padding: 5px;
                }
                QDialog QComboBox {
                    background-color: rgb(60, 60, 60);
                    color: white;
                    border: 1px solid rgb(80, 80, 80);
                }
                QDialog QPushButton {
                    background-color: rgba(95, 158, 160, 0.9);
                    color: white;
                    border: none;
                    padding: 5px 15px;
                    border-radius: 3px;
                }
                QDialog QPushButton:hover {
                    background-color: rgba(79, 142, 144, 0.9);
                }
                QDialog QCheckBox {
                    color: white;
                }
            """)
            
            # Widget'ları layout'a ekle
            tab_layout.addWidget(toolbar)
            tab_layout.addWidget(canvas)
            
            # Tab'ı ekle
            self.tab_widget.addTab(tab, f"{stock_code} - {graph_type}")
            self.tab_widget.setCurrentWidget(tab)

    def close_tab(self, index):
        """Seçilen sekmeyi kapat"""
        # İlk sekme değilse kapat 
        if index > -1:  
            self.tab_widget.removeTab(index)

    def resizeEvent(self, event):
        """Pencere boyutu değiştiğinde arka planı güncelle"""
        super().resizeEvent(event)
        self.setup_background()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = StockAnalyzerApp()
    sys.exit(app.exec_())

