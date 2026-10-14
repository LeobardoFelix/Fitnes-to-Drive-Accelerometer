import queue
import sys
import threading
from collections import deque
import matplotlib
matplotlib.use("QtAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

import time
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QCheckBox, QFrame, QGridLayout,
    QGroupBox, QHBoxLayout, QLabel, QLineEdit, QMainWindow,
    QPushButton, QSizePolicy, QTextEdit,
    QVBoxLayout, QWidget, QDialog
)
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import QObject, pyqtSignal

import TestWindow.SerialCommunication.SerialReader as SerialReader
from TestWindow.testsWindow import IMU_MODE, EOG_MODE, STATIC_MODE, MOVIL_MODE
import Graficadora.DataLogger as DL
from StyleGraphics.StylesGraphic import STYLE_SHEET, DARK_BG, PANEL_BG, BORDER, ACCENT_CYAN, \
ACCENT_RED, ACCENT_AMBER, ACCENT_BLUE, TEXT_PRIMARY, TEXT_MUTED, TEXT_LABEL, ACCENT_GREEN, ACCENT_YELLOW

class ReportWindow(QDialog):
    def __init__(self, reactionLog):
        self.reactionLog = reactionLog
        gridLayout = QGridLayout()
        