import sys
import os
import errno
from serial.tools import list_ports 

import matplotlib
matplotlib.use("QtAgg")
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication, QCheckBox, QComboBox, QDialog, QFrame, QGridLayout,
    QGroupBox, QHBoxLayout, QLabel, QLineEdit, QMainWindow,
    QPushButton, QScrollBar, QSizePolicy, QSlider, QTextEdit,
    QVBoxLayout, QWidget,
)
from StyleGraphics.StylesGraphic import STYLE_SHEET
from TestWindow.testsWindow import IMU_MODE, EOG_MODE, STATIC_MODE, MOVIL_MODE
GRAPH_WINDOW_MODE = 0
PRUEBAS_WINDOW_MODE = 1
ERROR_INVALID_NAME = 123


class configurationWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Monitor Serial — Configuración")
        self.setMinimumWidth(480)
        self.setStyleSheet(STYLE_SHEET)

        self.puerto   = None
        self.topThreshold     = None
        self.bottomThreshold     = None
        self.thresholdMode   = None
        self.promAmo  = None

        root_layout = QVBoxLayout(self)
        root_layout.setSpacing(0)
        root_layout.setContentsMargins(28, 24, 28, 24)

        # Encabezado
        header = QVBoxLayout()
        header.setSpacing(2)
        lbl_title = QLabel("MONITOR SERIAL")
        lbl_title.setObjectName("labelTitle")
        lbl_sub   = QLabel("CONFIGURACIÓN DE CONEXIÓN")
        lbl_sub.setObjectName("labelSubtitle")
        header.addWidget(lbl_title)
        header.addWidget(lbl_sub)
        root_layout.addLayout(header)
        root_layout.addSpacing(20)
        root_layout.addWidget(make_separator())
        root_layout.addSpacing(20)

        # Formulario
        form = QGridLayout()
        form.setHorizontalSpacing(16)
        form.setVerticalSpacing(14)

        def row(label_text, widget, r):
            lbl = QLabel(label_text)
            form.addWidget(lbl, r, 0, Qt.AlignmentFlag.AlignRight)
            form.addWidget(widget, r, 1)

        self.campo_com = QComboBox()
        puertos = list_ports.comports()
        for puerto in puertos: 
            self.campo_com.addItem(puerto.device)
        row("Puerto COM", self.campo_com, 0)
        self.windowsBox = QComboBox()
        self.windowsBox.addItems(["Graficadora", "Ventana de pruebas"])
        row("Ventana: ", self.windowsBox, 1)
        self.imuThreshLine = QLineEdit("2.0")
        row("Threshold IMU: ", self.imuThreshLine, 2)
        self.campo_max = QLineEdit("1000")
        row("TOP THRESHOLD EOG", self.campo_max, 3)
        self.campo_min = QLineEdit("0")
        row("BOTTOM THRESHOLD EOG", self.campo_min, 4)

        self.topFrameLine = QLineEdit("1000")
        row("TOP FRAME", self.topFrameLine, 5)
        self.bottomFrameLine = QLineEdit("0")
        row("BOTTOM FRAME", self.bottomFrameLine, 6)

        self.currentDir = "."
        self.directoryLine = QLineEdit(self.currentDir)
        row("SAVE DIRECTORY", self.directoryLine, 7)

        root_layout.addLayout(form)
        root_layout.addSpacing(18)

        # Promedio móvil
        grp_prom = QGroupBox("Promedio Móvil")
        prom_layout = QVBoxLayout(grp_prom)
        prom_layout.setSpacing(10)

        #Checks layout
        check_layout = QHBoxLayout()
        self.checkUmbral = QCheckBox("Static Threshold")
        self.checkUmbral.toggled.connect(self.changeThresholdCheckText)
        check_layout.addWidget(self.checkUmbral)
        self.checkDataMode = QCheckBox("EOG")
        self.checkDataMode.toggled.connect(self.changeDataCheckText)
        check_layout.addWidget(self.checkDataMode)
        prom_layout.addLayout(check_layout)

        slider_row = QHBoxLayout()
        lbl_slider = QLabel("Ventana:")
        lbl_slider.setFixedWidth(70)
        self.filterLenSlider = QSlider(Qt.Orientation.Horizontal)
        self.filterLenSlider.setRange(1, 500)
        self.filterLenSlider.setValue(50)
        self.lbl_prom_val = QLabel("50")
        self.lbl_prom_val.setFixedWidth(36)
        self.lbl_prom_val.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.filterLenSlider.valueChanged.connect(
            lambda v: self.lbl_prom_val.setText(str(v))
        )
        slider_row.addWidget(lbl_slider)
        slider_row.addWidget(self.filterLenSlider)
        slider_row.addWidget(self.lbl_prom_val)
        prom_layout.addLayout(slider_row)

        root_layout.addWidget(grp_prom)
        root_layout.addSpacing(24)

        # Botón conectar
        btn = QPushButton("CONECTAR")
        btn.setObjectName("btnConectar")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(self.conectar)
        root_layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignHCenter)

    def changeThresholdCheckText(self):
        if self.checkUmbral.isChecked():
            self.checkUmbral.setText("Movil Threshold")
        else:
            self.checkUmbral.setText("Static Threshold")

    def changeDataCheckText(self):
        if self.checkDataMode.isChecked():
            self.checkDataMode.setText("IMU")
        else:
            self.checkDataMode.setText("EOG")

    def conectar(self):
        self.puerto  = self.campo_com.currentText()
        self.topThreshold    = int(self.campo_max.text())
        self.bottomThreshold    = int(self.campo_min.text())
        self.thresholdMode  = MOVIL_MODE if self.checkUmbral.isChecked() else STATIC_MODE
        self.filterLength = self.filterLenSlider.value()
        self.dataMode =  IMU_MODE if self.checkDataMode.isChecked() else EOG_MODE
        self.windowMode = GRAPH_WINDOW_MODE if self.windowsBox.currentText() == "Graficadora" else PRUEBAS_WINDOW_MODE
        self.imuThreshold = float(self.imuThreshLine.text())
        self.topFrame = float(self.topFrameLine.text())
        self.bottomFrame = float(self.bottomFrameLine.text())
        self.currentDir = self.directoryLine.text()
        if not is_pathname_valid(self.currentDir):
            self.currentDir = "./NewFolder"

        self.accept()

    def iniciar(self):
        if self.exec() == QDialog.DialogCode.Accepted:
            return self.puerto, self.topThreshold, self.bottomThreshold, self.thresholdMode, \
         self.filterLength, self.dataMode, self.windowMode, self.imuThreshold, self.topFrame, \
            self.bottomFrame, self.currentDir
        return [None] * 11

def make_separator(vertical=False):
    sep = QFrame()
    sep.setFrameShape(QFrame.Shape.VLine if vertical else QFrame.Shape.HLine)
    return sep
def is_pathname_valid(pathname: str) -> bool:
    '''
    `True` if the passed pathname is a valid pathname for the current OS;
    `False` otherwise.
    '''
    # If this pathname is either not a string or is but is empty, this pathname
    # is invalid.
    try:
        if not isinstance(pathname, str) or not pathname:
            return False

        # Strip this pathname's Windows-specific drive specifier (e.g., `C:\`)
        # if any. Since Windows prohibits path components from containing `:`
        # characters, failing to strip this `:`-suffixed prefix would
        # erroneously invalidate all valid absolute Windows pathnames.
        _, pathname = os.path.splitdrive(pathname)

        # Directory guaranteed to exist. If the current OS is Windows, this is
        # the drive to which Windows was installed (e.g., the "%HOMEDRIVE%"
        # environment variable); else, the typical root directory.
        root_dirname = os.environ.get('HOMEDRIVE', 'C:') \
            if sys.platform == 'win32' else os.path.sep
        assert os.path.isdir(root_dirname)   # ...Murphy and her ironclad Law

        # Append a path separator to this directory if needed.
        root_dirname = root_dirname.rstrip(os.path.sep) + os.path.sep

        # Test whether each path component split from this pathname is valid or
        # not, ignoring non-existent and non-readable path components.
        for pathname_part in pathname.split(os.path.sep):
            try:
                os.lstat(root_dirname + pathname_part)
            # If an OS-specific exception is raised, its error code
            # indicates whether this pathname is valid or not. Unless this
            # is the case, this exception implies an ignorable kernel or
            # filesystem complaint (e.g., path not found or inaccessible).
            #
            # Only the following exceptions indicate invalid pathnames:
            #
            # * Instances of the Windows-specific "WindowsError" class
            #   defining the "winerror" attribute whose value is
            #   "ERROR_INVALID_NAME". Under Windows, "winerror" is more
            #   fine-grained and hence useful than the generic "errno"
            #   attribute. When a too-long pathname is passed, for example,
            #   "errno" is "ENOENT" (i.e., no such file or directory) rather
            #   than "ENAMETOOLONG" (i.e., file name too long).
            # * Instances of the cross-platform "OSError" class defining the
            #   generic "errno" attribute whose value is either:
            #   * Under most POSIX-compatible OSes, "ENAMETOOLONG".
            #   * Under some edge-case OSes (e.g., SunOS, *BSD), "ERANGE".
            except OSError as exc:
                if hasattr(exc, 'winerror'):
                    if exc.winerror == ERROR_INVALID_NAME:
                        return False
                elif exc.errno in {errno.ENAMETOOLONG, errno.ERANGE}:
                    return False
    # If a "TypeError" exception was raised, it almost certainly has the
    # error message "embedded NUL character" indicating an invalid pathname.
    except TypeError as exc:
        return False
    # If no exception was raised, all path components and hence this
    # pathname itself are valid. (Praise be to the curmudgeonly python.)
    else:
        return True