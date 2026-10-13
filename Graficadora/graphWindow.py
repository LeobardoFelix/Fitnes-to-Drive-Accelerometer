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
    QVBoxLayout, QWidget,
)
from PyQt6.QtWidgets import QMessageBox

import TestWindow.SerialCommunication.SerialReader as SerialReader
from TestWindow.testsWindow import IMU_MODE, EOG_MODE, STATIC_MODE, MOVIL_MODE
import Graficadora.DataLogger as DL
from StyleGraphics.StylesGraphic import STYLE_SHEET, DARK_BG, PANEL_BG, BORDER, ACCENT_CYAN, \
ACCENT_RED, ACCENT_AMBER, ACCENT_BLUE, TEXT_PRIMARY, TEXT_MUTED, TEXT_LABEL, ACCENT_GREEN, ACCENT_YELLOW
BAUD_RATE = 9600
LINE_LENGTH = [0, 500]
class GraphWindow(QMainWindow):

    reconectar_solicitado = pyqtSignal()  # ← avisa al loop principal

    def __init__(self, puerto, topThreshold, bottomThreshold, thresholdMode, filterLength, dataMode, thresholdIMU, topFrame, bottomFrame):
        super().__init__()
        self.setWindowTitle("Monitor Serial")
        self.setMinimumSize(1020, 640)
        self.setStyleSheet(STYLE_SHEET)

        # ── Estado ────────────────────────────────────────────────────────────
        self.corriendo     = True
        self._reconectando = False
        self.limit         = 300
        self.average = 0.0
        self.datos         = deque(maxlen=500)
        self.promedios = deque(maxlen=500)
        self.queue         = queue.Queue()
        self.puerto = puerto
        self.thresholdMode      = thresholdMode
        self.dataMode = dataMode
        self.thresholdImu = thresholdIMU
        self.filterLength = filterLength
        self.topThreshold = topThreshold
        self.bottomThreshold = bottomThreshold
        #self.topEOG = topEOG
        #self.bottomEOG = bottomEOG

        if thresholdMode:
            self.umbralType = "Promedio"
            self.limit      = 0
        else:
            self.umbralType = "Limite"

        # Logger
        self.logger = DL.DataLogger(modo='continuo', limit=self.limit)

        # Comunicación Serial
        umbralMode = 1 if self.umbralType == "Promedio" else 0
        #self.SC = SerialReader.SerialReader(puerto, 9600, self.thresholdMode, umbralMode)
        self.SC = SerialReader.SerialReader(self.puerto, BAUD_RATE, self.filterLength, 
            self.thresholdMode, self.dataMode, self.thresholdImu, 
            self.topThreshold, self.bottomThreshold)
        
        try:
            self.SC.openConection()
        except Exception as e:
            # Marcar como reconexión para que closeEvent no llame sys.exit()
            self._reconectando = True
            
            msg = QMessageBox()
            msg.setStyleSheet(STYLE_SHEET)
            msg.setWindowTitle("Error de conexión")
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setText(f"No se pudo conectar al puerto <b>{puerto}</b>.")
            msg.setInformativeText(
                f"Verifica que el dispositivo esté conectado y que el puerto sea correcto.\n\n{e}"
            )
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.exec()
            self.reconectar_solicitado.emit()
            # Programar el cierre para después de que __init__ termine
            QTimer.singleShot(0, self.close)
            return

        # ── Layout raíz ───────────────────────────────────────────────────────
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(14, 14, 14, 14)
        main_layout.setSpacing(12)

        # Panel izquierdo (controles + log)
        left_panel = QVBoxLayout()
        left_panel.setSpacing(10)

        # Panel derecho (gráfica)
        right_panel = QVBoxLayout()
        right_panel.setSpacing(8)

        main_layout.addLayout(left_panel, stretch=0)
        main_layout.addWidget(make_separator(vertical=True))
        main_layout.addLayout(right_panel, stretch=1)

        # ── PANEL IZQUIERDO ───────────────────────────────────────────────────

        # Encabezado pequeño
        lbl_title = QLabel("MONITOR SERIAL")
        lbl_title.setObjectName("labelTitle")
        lbl_title.setFont(QFont("JetBrains Mono", 13, QFont.Weight.Bold))
        left_panel.addWidget(lbl_title)

        # Indicador de promedio
        self.label_promedio = QLabel("Promedio móvil: 0.00")
        self.label_promedio.setObjectName("labelPromedio")
        left_panel.addWidget(self.label_promedio)

        left_panel.addWidget(make_separator())

        # Botón reconectar
        btn_reconectar = QPushButton("⟳  Reconectar")
        btn_reconectar.setObjectName("btnReconectar")
        btn_reconectar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_reconectar.setToolTip("Cierra la sesión, resetea Arduino y reabre la configuración")
        btn_reconectar.clicked.connect(self.solicitar_reconexion)
        left_panel.addWidget(btn_reconectar)

        # ── Grupo: Señal ──────────────────────────────────────────────────────
        grp_signal = QGroupBox("Señal")
        sig_layout = QGridLayout(grp_signal)
        sig_layout.setSpacing(8)

        sig_layout.addWidget(QLabel("Límite:"), 0, 0)
        self.campo_texto = QLineEdit("300")
        self.campo_texto.setFixedWidth(80)
        sig_layout.addWidget(self.campo_texto, 0, 1)

        btn_enviar = QPushButton("Enviar")
        btn_enviar.setObjectName("btnEnviar")
        btn_enviar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_enviar.clicked.connect(self.enviar_manual)
        sig_layout.addWidget(btn_enviar, 0, 2)

        left_panel.addWidget(grp_signal)

        # ── Grupo: Muestreo ───────────────────────────────────────────────────
        grp_muestreo = QGroupBox("Muestreo")
        mues_layout  = QVBoxLayout(grp_muestreo)
        mues_layout.setSpacing(8)

        btn_row = QHBoxLayout()
        self.buttonStart  = QPushButton("▶ Iniciar")
        self.buttonFinish = QPushButton("■ Detener")
        self.buttonStart.setObjectName("btnStart")
        self.buttonFinish.setObjectName("btnStop")
        self.buttonStart.setCursor(Qt.CursorShape.PointingHandCursor)
        self.buttonFinish.setCursor(Qt.CursorShape.PointingHandCursor)
        self.buttonStart.clicked.connect(self.iniciar_muestreo)
        self.buttonFinish.clicked.connect(self.detener_muestreo)
        btn_row.addWidget(self.buttonStart)
        btn_row.addWidget(self.buttonFinish)
        mues_layout.addLayout(btn_row)

        self.modo_umbral_var = QCheckBox("Muestreo por Umbral")
        self.modo_umbral_var.stateChanged.connect(self.cambiar_modo)
        mues_layout.addWidget(self.modo_umbral_var)

        left_panel.addWidget(grp_muestreo)

        # ── Log ───────────────────────────────────────────────────────────────
        grp_log = QGroupBox("Log en Vivo")
        log_layout = QVBoxLayout(grp_log)
        log_layout.setContentsMargins(6, 6, 6, 6)

        self.area_log = QTextEdit()
        self.area_log.setReadOnly(True)
        self.area_log.setFixedWidth(200)
        self.area_log.setMinimumHeight(200)
        log_layout.addWidget(self.area_log)

        left_panel.addWidget(grp_log, stretch=1)
        left_panel.addStretch()

        # ── PANEL DERECHO: Gráfica ─────────────────────────────────────────────
        plt.style.use("dark_background")
        self.fig, self.ax = plt.subplots(figsize=(8, 5))
        self.fig.patch.set_facecolor(PANEL_BG)
        self.ax.set_facecolor(DARK_BG)
        self.ax.tick_params(colors=TEXT_MUTED, labelsize=9)
        for spine in self.ax.spines.values():
            spine.set_edgecolor(BORDER)
        self.ax.set_title("Señal Arduino", color=TEXT_LABEL,
                          fontsize=11, fontfamily="monospace", pad=10)
        self.ax.set_ylim(bottomFrame, topFrame)
        self.ax.set_xlim(0, 500)
        self.ax.grid(True, color=BORDER, linewidth=0.5, alpha=0.6)

        self.valueLine,                = self.ax.plot([], [], color=ACCENT_CYAN, linewidth=1.2, label="EOG")
        self.lineaPromedio, = self.ax.plot([], [], color=ACCENT_RED, linewidth=1.2, label="PROMEDIO EOG")
        if dataMode == IMU_MODE:
            self.imuLine, = self.ax.plot([], [], color=ACCENT_BLUE,  linestyle="--", linewidth=1.0, label="IMU Threshold")
        else:
            self.topEogLine, = self.ax.plot([], [], color=ACCENT_BLUE,  linestyle="--", linewidth=0.8, label="Top EOG Threshold")
            self.bottomEogLine, = self.ax.plot([], [], color=ACCENT_AMBER,  linestyle="--", linewidth=0.8, label="Bottom EOG Threshold")
        #self.linea_limite,         = self.ax.plot([], [], color=ACCENT_RED,   linestyle="--", linewidth=1.0, label="Límite")
        #self.linea_limite_azul,    = self.ax.plot([], [], color=ACCENT_BLUE,  linestyle="--", linewidth=0.8, label="+σ")
        #self.linea_limite_amarilla,= self.ax.plot([], [], color=ACCENT_AMBER, linestyle="--", linewidth=0.8, label="-σ")

        self.ax.legend(
            facecolor=PANEL_BG, edgecolor=BORDER,
            labelcolor=TEXT_LABEL, fontsize=9, loc="upper right"
        )

        self.canvas = FigureCanvas(self.fig)
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        right_panel.addWidget(self.canvas)

        # Barra de estado inferior
        status_bar = QHBoxLayout()
        self.lbl_status = QLabel(f"Puerto: {puerto}  ·  Baudrate: 9600  ·  Modo: {self.umbralType}")
        self.lbl_status.setObjectName("labelStatus")
        status_bar.addWidget(self.lbl_status)
        status_bar.addStretch()
        self.lbl_count = QLabel("Muestras: 0")
        self.lbl_count.setObjectName("labelStatus")
        status_bar.addWidget(self.lbl_count)
        right_panel.addLayout(status_bar)

        # ── Hilo serial y timers ───────────────────────────────────────────────
        self.hilo = threading.Thread(target=self.leer_serial, daemon=True)
        self.hilo.start()

        self.timer_ui = QTimer()
        self.timer_ui.timeout.connect(self.actualizar_ui)
        self.timer_ui.start(50)

        self.timer_plot = QTimer()
        self.timer_plot.timeout.connect(self.actualizar_grafica)
        self.timer_plot.start(100)
        self.contado = 0

    # ── Lógica (sin cambios respecto al original) ─────────────────────────────
    #Leer_serial se actualiza en un hilo
    def leer_serial(self):
        #Equivalente a SerialConsumer, lee constantemente el puerto serial con SerialCatcher (SerialReader)
        while self.corriendo:
            linea = self.SC.catchSerial()
            if linea:
                #try:
                #print(f"Len: {self.queue.qsize()}")
                partes  = linea.strip().split(',')
                if isNumeric(partes[0]):
                    valor   = float(partes[0])
                    promedio = float(partes[1]) if len(partes) > 1 else None
                    reaccion = float(partes[2]) if len(partes) > 2 else None
                    #promedioIMU = float(partes[3]) if len(partes) > 3 else None

                    item = (valor, promedio, reaccion)
                    #print(item)
                    self.queue.put(item=item)
                #print(f"Len: {self.queue.qsize()}")
                

    #actualizar_ui Se actualiza cada 50 ms en un timer
    def actualizar_ui(self):
        #Clasifica los valores leidos dentro de datos y promedios
        #Actualiza los valores mostrados en el log.
        #print(f"AU: {self.queue.empty()}")
        while not self.queue.empty():
             #aux = self.queue.get()
            valor, promedio, reaccion = self.queue.get()
            #print(f"VAL: {valor} Prom: {promedio} REACT: {reaccion}")
            if promedio is not None:
                self.average = promedio
                self.label_promedio.setText(f"Promedio móvil: {self.average:.2f}")

            self.datos.append(valor)
            self.promedios.append(promedio)
            #self.promedio_datosBth.append(promedioIMU * 1000)
            
            

            self.area_log.append(f"V: {str(valor)} M: {str(promedio)} R: {str(reaccion)}")
            # Limitar líneas del log
            doc = self.area_log.document()
            while doc.blockCount() > 200:
                cursor = self.area_log.textCursor()
                cursor.movePosition(cursor.MoveOperation.Start)
                cursor.select(cursor.SelectionType.LineUnderCursor)
                cursor.removeSelectedText()
                cursor.deleteChar()
            self.area_log.verticalScrollBar().setValue(
                self.area_log.verticalScrollBar().maximum()
            )

            if self.umbralType == "Promedio":
                self.logger.set_limit(self.average)
            else:
                self.logger.set_limit(self.limit)

            self.logger.registrar(valor)

        self.lbl_count.setText(f"Muestras: {len(self.datos)}")


    #actualizar_grafica Se actualiza cada 100ms en un timer
    def actualizar_grafica(self):
        #Actualiza las lineas
        if len(self.promedios) > 0:
            n = len(self.promedios)
            self.lineaPromedio.set_data(range(n), list(self.promedios))
        if len(self.datos) > 0:
            n = len(self.datos)
            self.valueLine.set_data(range(n), list(self.datos))

            if self.dataMode == IMU_MODE:
                currentThreshold = self.thresholdImu if self.thresholdMode == STATIC_MODE else self.thresholdImu+self.average
                self.imuLine.set_data(LINE_LENGTH, [currentThreshold, currentThreshold])
            else:
                currentTopThreshold = self.topThreshold if self.thresholdMode == STATIC_MODE else self.average+self.topThreshold
                currentBottomThreshold = self.bottomThreshold if self.thresholdMode == STATIC_MODE else self.average-self.bottomThreshold
                print(f"{str(currentTopThreshold)} {currentBottomThreshold}")
                self.topEogLine.set_data(LINE_LENGTH, [currentTopThreshold, currentTopThreshold])
                self.bottomEogLine.set_data(LINE_LENGTH, [currentBottomThreshold, currentBottomThreshold])

            #limite_actual = (
            #    self.average if self.umbralType == "Promedio" else self.limit
            #)
            #self.linea_limite.set_data(LINE_LENGTH, [limite_actual, limite_actual])

            """if self.umbralType == "Promedio":
                self.linea_limite_azul.set_data(
                    LINE_LENGTH,
                    [self.average + self.limit, self.average + self.limit]
                )
                self.linea_limite_amarilla.set_data(
                    LINE_LENGTH,
                    [self.average - self.limit, self.average - self.limit]
                )
            else:
                self.linea_limite_azul.set_data([], [])
                self.linea_limite_amarilla.set_data([], [])"""

            self.canvas.draw_idle()
        
        # if len(self.promedio_datosBth) > 0:
        #     n = len(self.promedio_datosBth)
        #     self.lineaPromedio_bth.set_data(range(n), list(self.promedio_datosBth))
        # if len(self.promedio_datosBth) > 0:
        #     n = len(self.promedio_datosBth)
        #     self.lineaPromedio_EOG.set_data(range(n), list(self.promedio_datosEOG))

    def enviar_manual(self):
        try:
            mensaje = self.campo_texto.text()
            self.limit = float(mensaje)
            self.logger.set_limit(self.limit)
            self.SC.sendSignal(mensaje + "\n")
        except ValueError:
            pass

    def iniciar_muestreo(self):
        self.logger.iniciar()

    def detener_muestreo(self):
        self.logger.detener()

    def cambiar_modo(self):
        modo = "umbral" if self.modo_umbral_var.isChecked() else "continuo"
        self.logger.set_modo(modo)

    def _cerrar_sesion(self, reset_arduino=False):
        """Detiene timers, hilo y conexión. Si reset_arduino=True, pulsa DTR."""
        self.corriendo = False
        if hasattr(self, 'timer_ui'):
            self.timer_ui.stop()
        if hasattr(self, 'timer_plot'):
            self.timer_plot.stop()
        if hasattr(self, 'logger'):
            self.logger.detener()
        if reset_arduino and hasattr(self, 'SC'):
            try:
                self.SC.ser.dtr = False
                time.sleep(0.1)
                self.SC.ser.dtr = True
                time.sleep(0.05)
            except Exception:
                pass
        if hasattr(self, 'SC'):
            self.SC.closeConection()

    def solicitar_reconexion(self):
        self._reconectando = True
        self._cerrar_sesion(reset_arduino=True)
        self.reconectar_solicitado.emit()
        self.close()

    def closeEvent(self, event):
        if not self._reconectando:
            self._cerrar_sesion(reset_arduino=False)
            event.accept()
            sys.exit()
        # Si es reconexión, _cerrar_sesion ya fue llamado; solo aceptar el cierre
        event.accept()

def isNumeric(num):
    try: 
        float(num)
        return True
    except Exception as e:
        return False
def make_separator(vertical=False):
    sep = QFrame()
    sep.setFrameShape(QFrame.Shape.VLine if vertical else QFrame.Shape.HLine)
    return sep