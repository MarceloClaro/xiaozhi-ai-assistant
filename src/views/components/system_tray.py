"""
sistema sistema、eestado.
"""

from typing import Optional

from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtGui import QBrush, QColor, QIcon, QPainter, QPixmap
from PyQt5.QtWidgets import QAction, QMenu, QSystemTrayIcon, QWidget

from src.utils.logging_config import get_logger


class SystemTray(QObject):
    """
    sistema.
    """

    # 
    show_window_requested = pyqtSignal()
    settings_requested = pyqtSignal()
    quit_requested = pyqtSignal()

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.logger = get_logger("SystemTray")
        self.parent_widget = parent

        # 
        self.tray_icon = None
        self.tray_menu = None

        # Estado
        self.current_status = ""
        self.is_connected = True

        # Inicializando
        self._setup_tray()

    def _setup_tray(self):
        """
        Configurandosistema.
        """
        try:
            # PesquisarSuportado
            if not QSystemTrayIcon.isSystemTrayAvailable():
                self.logger.warning("NãoSuportado")
                return

            # 
            self._create_tray_menu()

            # Ícone da bandeja do sistema（Não QWidget para，JanelaPeríodo， macOS /Fechando）
            self.tray_icon = QSystemTrayIcon()
            self.tray_icon.setContextMenu(self.tray_menu)

            # EmConfigurandoBits， QSystemTrayIcon::setVisible: No Icon set Aviso
            try:
                # UsandoparaBits
                pixmap = QPixmap(16, 16)
                pixmap.fill(QColor(0, 0, 0, 0))
                painter = QPainter(pixmap)
                painter.setRenderHint(QPainter.Antialiasing)
                painter.setBrush(QBrush(QColor(0, 180, 0)))
                painter.setPen(QColor(0, 0, 0, 0))
                painter.drawEllipse(2, 2, 12, 12)
                painter.end()
                self.tray_icon.setIcon(QIcon(pixmap))
            except Exception:
                pass

            # Conexãode
            self.tray_icon.activated.connect(self._on_tray_activated)

            # Configurando（EmVezes，para）
            try:
                from PyQt5.QtCore import QTimer

                QTimer.singleShot(0, lambda: self.update_status("", connected=True))
            except Exception:
                self.update_status("", connected=True)

            # Ícone da bandeja do sistema
            self.tray_icon.show()
            self.logger.info("Ícone da bandeja do sistemaInicializando")

        except Exception as e:
            self.logger.error(f"InicializandoÍcone da bandeja do sistemaFalha: {e}", exc_info=True)

    def _create_tray_menu(self):
        """
        Criando.
        """
        self.tray_menu = QMenu()

        # Janela
        show_action = QAction("Janela", self.parent_widget)
        show_action.triggered.connect(self._on_show_window)
        self.tray_menu.addAction(show_action)

        # 
        self.tray_menu.addSeparator()

        # Configurando
        settings_action = QAction("Parâmetro", self.parent_widget)
        settings_action.triggered.connect(self._on_settings)
        self.tray_menu.addAction(settings_action)

        # 
        self.tray_menu.addSeparator()

        # 
        quit_action = QAction("", self.parent_widget)
        quit_action.triggered.connect(self._on_quit)
        self.tray_menu.addAction(quit_action)

    def _on_tray_activated(self, reason):
        """
        Processando.
        """
        if reason == QSystemTrayIcon.Trigger:  # 
            self.show_window_requested.emit()

    def _on_show_window(self):
        """
        ProcessandoJanela.
        """
        self.show_window_requested.emit()

    def _on_settings(self):
        """
        ProcessandoConfigurando.
        """
        self.settings_requested.emit()

    def _on_quit(self):
        """
        ProcessandoSaindo.
        """
        self.quit_requested.emit()

    def update_status(self, status: str, connected: bool = True):
        """estado.

        Args:
            status: estado
            connected: Conectandoestado
        """
        if not self.tray_icon:
            return

        self.current_status = status
        self.is_connected = connected

        try:
            icon_color = self._get_status_color(status, connected)

            # de
            pixmap = QPixmap(16, 16)
            pixmap.fill(QColor(0, 0, 0, 0))  # 

            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setBrush(QBrush(icon_color))
            painter.setPen(QColor(0, 0, 0, 0))  # 
            painter.drawEllipse(2, 2, 12, 12)
            painter.end()

            # Configurando
            self.tray_icon.setIcon(QIcon(pixmap))

            # Configurando
            tooltip = f"AI - {status}"
            self.tray_icon.setToolTip(tooltip)

        except Exception as e:
            self.logger.error(f"Ícone da bandeja do sistemaFalha: {e}")

    def _get_status_color(self, status: str, connected: bool) -> QColor:
        """estadoRetornode.

        Args:
            status: estado
            connected: Conectandoestado

        Returns:
            QColor: de
        """
        if not connected:
            return QColor(128, 128, 128)  #  - NãoConexão

        if "Erro" in status:
            return QColor(255, 0, 0)  #  - ErroEstado
        elif "Em" in status:
            return QColor(255, 200, 0)  #  - EmEstado
        elif "Em" in status:
            return QColor(0, 120, 255)  #  - EmEstado
        else:
            return QColor(0, 180, 0)  #  - /IniciandoEstado

    def show_message(
        self,
        title: str,
        message: str,
        icon_type=QSystemTrayIcon.Information,
        duration: int = 2000,
    ):
        """Notificandomensagem.

        Args:
            title: Notificando
            message: Notificando
            icon_type: Tipo
            duration: Tempo(Milissegundos)
        """
        if self.tray_icon and self.tray_icon.isVisible():
            self.tray_icon.showMessage(title, message, icon_type, duration)

    def hide(self):
        """
        .
        """
        if self.tray_icon:
            self.tray_icon.hide()

    def is_visible(self) -> bool:
        """
        Pesquisar.
        """
        return self.tray_icon and self.tray_icon.isVisible()

    def is_available(self) -> bool:
        """
        Pesquisarsistema.
        """
        return QSystemTrayIcon.isSystemTrayAvailable()
