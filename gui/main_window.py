import asyncio
from PySide6.QtWidgets import QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QHeaderView
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QColor
from engine.binance_ws import BinanceWS
from engine.analyzer import PriceAnalyzer
from utils.logger import log_to_csv

class WorkerThread(QThread):
    price_updated = Signal(dict)

    def __init__(self, groups, threshold):
        super().__init__()
        all_symbols = []
        for group_data in groups:
            all_symbols.extend(group_data["pairs"])
        self.symbols = groups
        self.engine = BinanceWS(all_symbols)
        self.analyzer = PriceAnalyzer(groups=groups, threshold=threshold)

    async def handle_update(self, data):
        results = await self.analyzer.process_update(data)
        
        if results:
            for res in results:
                log_entry = res.copy()
                if 'dirrection' in log_entry:
                    log_entry['direction'] = log_entry.pop('dirrection')
                
                log_to_csv(log_entry)
        
        self.price_updated.emit({"data": data, "analysis": results})

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.engine.start(callback=self.handle_update))

class MainWindow(QMainWindow):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.setWindowTitle("CryptoStreamAnalyzer v1.0")
        self.resize(800, 500)
        self.setStyleSheet("background-color: #121212; color: white;") # Темна тема

        self.setup_ui()

        self.worker = WorkerThread(
            groups=self.config['monitored_groups'],
            threshold=self.config['settings']['global_threshold_percent']
        )
        self.worker.price_updated.connect(self.update_table)
        self.worker.start()

    def setup_ui(self):
        layout = QVBoxLayout()
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Symbol", "Bid Price", "Ask Price", "Spread Analysis"])

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        self.table.setStyleSheet("gridline-color: #333; border: none;")
        
        container = QWidget()
        container.setLayout(layout)
        layout.addWidget(self.table)
        self.setCentralWidget(container)

    def update_table(self, payload):
        data = payload['data']
        analysis = payload['analysis']
        symbol = data['symbol']

        items = self.table.findItems(symbol, Qt.MatchExactly)
        if items:
            row = items[0].row()
        else:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(symbol))

        self.table.setItem(row, 1, QTableWidgetItem(str(data['bid'])))
        self.table.setItem(row, 2, QTableWidgetItem(str(data['ask'])))

        if analysis:
            for res in analysis:
                if symbol in res['pair']:
                    msg = f"{res['diff_percent']}% diff"
                    item = QTableWidgetItem(msg)
                    
                    global_limit = self.config['settings']['global_threshold_percent']
                    if res['diff_percent'] >= global_limit:
                        item.setForeground(QColor("#FF5555"))
                    
                    self.table.setItem(row, 3, item)
