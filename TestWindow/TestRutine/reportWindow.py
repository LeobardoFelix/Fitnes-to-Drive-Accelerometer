from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

from PyQt6.QtWidgets import (
    QHBoxLayout, QPushButton, QStyledItemDelegate,
    QVBoxLayout, QDialog, QTableWidget, QTableWidgetItem
)
from PyQt6.QtCore import Qt


COLUMN_WIDTH = 100
class ReportWindow(QDialog):
    def __init__(self, reactionLog):
        super().__init__()
        self.reactionLog = reactionLog
        headers = ["no_round", "ts_start_round", "ts_end_round", "delta_ts", "reaction"]
        self.resize(len(headers) * (COLUMN_WIDTH+7), (len(reactionLog))*55)
        self.isLastLogSaved = True
        self.hasEnded = False
        layout = QVBoxLayout()
        mainTable = QTableWidget()
        
        mainTable.setColumnCount(len(headers))
        mainTable.setRowCount(len(self.reactionLog))
        mainTable.setHorizontalHeaderLabels(headers)
        
        delegate = AlignDelegate(mainTable)
        mainTable.setItemDelegateForColumn(len(headers), delegate)
        self.checks = []
        for i in range(mainTable.rowCount()):
            mainTable.setColumnWidth(i, COLUMN_WIDTH)
        for i, log in enumerate(self.reactionLog):

            for j, content in enumerate(log):
                if 0 < j and j < 4:
                    content = round(content, 3)
                label = QTableWidgetItem(str(content))
                label.setTextAlignment(Qt.AlignmentFlag.AlignHCenter)
                #label.setTextAlig(Qt.AlignmentFlag.AlignHCenter)
                mainTable.setItem(i, j, label)
        layout.addWidget(mainTable)
        btnLayout = QHBoxLayout()
        self.saveBtn = QPushButton("SAVE")
        self.rerunBtn = QPushButton("RERUN")
        btnLayout.addWidget(self.saveBtn)
        btnLayout.addWidget(self.rerunBtn)
        self.saveBtn.clicked.connect(self.saveLog)
        self.rerunBtn.clicked.connect(self.reDoLog)
        layout.addLayout(btnLayout)
        self.setLayout(layout)

    def saveLog(self):
        self.isLastLogSaved = True
        self.hasEnded = True
        self.close()

    def reDoLog(self):
        self.isLastLogSaved = False
        self.hasEnded = True
        self.close()

class AlignDelegate(QStyledItemDelegate):
    def initStyleOption(self, option, index):
        super(AlignDelegate, self).initStyleOption(option, index)
        option.displayAlignment = Qt.AlignmentFlag.AlignHCenter


#TestWindow/TestRutine/reportWindow.py
"""app = QApplication(sys.argv)
app.setStyle("Fusion")
pruebaLog = [[0,6693.7325156,6698.7338546,5.001339000000371,0],
[1,6702.771452,6703.835072,1.0636199999999008,1],
[2,6710.8934594,6715.8945745,5.001115099999879,0],
[3,6723.947009,6725.2070988,1.2600897999991503,1]]
reportWindow = ReportWindow(pruebaLog)
reportWindow.show()

app.exec()"""