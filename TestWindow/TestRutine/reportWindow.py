import queue
import sys
import threading
from collections import deque
import matplotlib
matplotlib.use("QtAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

from PyQt6.QtWidgets import (
    QCheckBox, QFrame, QDialogButtonBox,
    QGroupBox, QHBoxLayout, QLabel, 
    QPushButton, QSizePolicy, QStyledItemDelegate,
    QVBoxLayout, QDialog, QApplication, QTableWidget, QTableWidgetItem
)
from PyQt6.QtCore import Qt


COLUMN_WIDTH = 100
class ReportWindow(QDialog):
    def __init__(self, reactionLog):
        super().__init__()
        self.reactionLog = reactionLog
        headers = ["no_round", "ts_start_round", "ts_end_round", "delta_ts", "reaction"]
        self.resize(len(headers) * (COLUMN_WIDTH+7), (len(reactionLog))*55)
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
                #mainTable.
            """checkMark = QTableWidgetItem()
            checkMark.setTextAlignment(Qt.AlignmentFlag.AlignHCenter)
            checkMark.setCheckState(Qt.CheckState.Unchecked)
            self.checks.append(checkMark)
            mainTable.setItem(i, j+1, checkMark)
            #mainTable.setCellWidget(i, j+1, checkMark)"""
        layout.addWidget(mainTable)
        saveBtn = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Discard)
        saveBtn.accepted.connect(self.saveLog)
        saveBtn.rejected.connect(self.reDoLog)
        layout.addWidget(saveBtn)
        self.setLayout(layout)

    def saveLog(self):
        pass

    def reDoLog(self):
        pass

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