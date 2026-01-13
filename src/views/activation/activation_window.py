# -*- coding: utf-8 -*-
"""
dispositivoativaçãoJanela ativação、dispositivoInformaçãoeativação.
"""

from pathlib import Path
from typing import Optional

from PyQt5.QtCore import QSize, Qt, QUrl, pyqtSignal
from PyQt5.QtGui import QPainterPath, QRegion
from PyQt5.QtQuickWidgets import QQuickWidget
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QWidget

from src.core.system_initializer import SystemInitializer
from src.utils.device_activator import DeviceActivator
from src.utils.logging_config import get_logger

from ..base.async_mixins import AsyncMixin, AsyncSignalEmitter
from ..base.base_window import BaseWindow
from .activation_model import ActivationModel

logger = get_logger(__name__)


class ActivationWindow(BaseWindow, AsyncMixin):
    """
    dispositivoativaçãoJanela.
    """

    # 
    activation_completed = pyqtSignal(bool)  # Concluído
    window_closed = pyqtSignal()  # JanelaFechando

    def __init__(
        self,
        system_initializer: Optional[SystemInitializer] = None,
        parent: Optional = None,
    ):
        # QML - Emsuper().__init__
        self.qml_widget = None
        self.activation_model = ActivationModel()

        super().__init__(parent)

        # 
        self.system_initializer = system_initializer
        self.device_activator: Optional[DeviceActivator] = None

        # Estado
        self.current_stage = None
        self.activation_data = None
        self.is_activated = False
        self.initialization_started = False
        self.status_message = ""

        # Dispositivo
        self.signal_emitter = AsyncSignalEmitter()
        self._setup_signal_connections()

        # Janela
        self.drag_position = None

        # IniciandoInicializando（Aguardar）
        self.start_update_timer(100)  # 100ms  ComeçarInicializando

    def _setup_ui(self):
        """
        ConfigurandoUI.
        """
        # ConfigurandoJanela
        # DispositivoTipoWayland
        import os

        is_wayland = (
            os.environ.get("WAYLAND_DISPLAY")
            or os.environ.get("XDG_SESSION_TYPE") == "wayland"
        )

        if is_wayland:
            # Wayland：NãoUsandoWindowStaysOnTopHint（NãoSuportado）
            self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
            self.logger.info("paraWayland，UsandoJanela")
        else:
            # X11：Usando
            self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
            self.logger.info("paraX11，UsandoJanela")

        self.setAttribute(Qt.WA_TranslucentBackground)

        # Em  widget
        central_widget = QWidget()
        central_widget.setStyleSheet("background: transparent;")
        self.setCentralWidget(central_widget)

        # 
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)

        # QML widget
        self.qml_widget = QQuickWidget()
        self.qml_widget.setResizeMode(QQuickWidget.SizeRootObjectToView)

        # EmX11UsandoWA_AlwaysStackOnTop（WaylandNãoSuportado）
        if not is_wayland:
            self.qml_widget.setAttribute(Qt.WA_AlwaysStackOnTop)

        self.qml_widget.setClearColor(Qt.transparent)

        # DadosModeloparaQML
        qml_context = self.qml_widget.rootContext()
        qml_context.setContextProperty("activationModel", self.activation_model)

        # QMLArquivo
        qml_file = Path(__file__).parent / "activation_window.qml"
        self.qml_widget.setSource(QUrl.fromLocalFile(str(qml_file)))

        # PesquisarQMLSucesso
        if self.qml_widget.status() == QQuickWidget.Error:
            self.logger.error("QMLFalha，Motivo：")
            for error in self.qml_widget.errors():
                self.logger.error(f"  - {error.toString()}")

            # EmWayland，SeQMLFalha，UsandoCLIModo
            if is_wayland:
                self.logger.warning("WaylandQMLFalha，UsandoCLIModo")
                self.logger.info("UsandoComando: python main.py --mode cli")

        # para
        layout.addWidget(self.qml_widget)

        # Configurando
        self._setup_adaptive_size()

        # ConfigurandoConexão，QML
        self._setup_qml_connections()

    def _setup_adaptive_size(self):
        """
        ConfigurandoJanela.
        """
        # 
        screen = QApplication.primaryScreen()
        screen_size = screen.size()
        screen_width = screen_size.width()
        screen_height = screen_size.height()

        self.logger.info(f"para: {screen_width}x{screen_height}")

        # SelecionandodeJanelaTamanho
        if screen_width <= 480 or screen_height <= 320:
            #  (3.5480x320)
            window_width, window_height = 450, 250
            self.setMinimumSize(QSize(450, 250))
            self._apply_compact_styles()
        elif screen_width <= 800 or screen_height <= 480:
            #  (7800x480)
            window_width, window_height = 480, 280
            self.setMinimumSize(QSize(480, 280))
            self._apply_small_screen_styles()
        elif screen_width <= 1024 or screen_height <= 600:
            # EmAguardar
            window_width, window_height = 520, 300
            self.setMinimumSize(QSize(520, 300))
        else:
            #  (PCDispositivo)
            window_width, window_height = 550, 320
            self.setMinimumSize(QSize(550, 320))

        # JanelaNão
        max_width = min(window_width, screen_width - 50)
        max_height = min(window_height, screen_height - 50)

        self.resize(max_width, max_height)

        # Em
        self.move((screen_width - max_width) // 2, (screen_height - max_height) // 2)

        self.logger.info(f"ConfigurandoJanela: {max_width}x{max_height}")

    def _apply_compact_styles(self):
        """aplicação - """
        # Tamanho
        self.setStyleSheet(
            """
            QLabel { font-size: 10px; }
            QPushButton { font-size: 10px; padding: 4px 8px; }
            QTextEdit { font-size: 8px; }
        """
        )

    def _apply_small_screen_styles(self):
        """
        aplicação.
        """
        # Tamanho
        self.setStyleSheet(
            """
            QLabel { font-size: 11px; }
            QPushButton { font-size: 11px; padding: 6px 10px; }
            QTextEdit { font-size: 9px; }
        """
        )

    def _setup_connections(self):
        """
        ConfigurandoConectando.
        """
        # ConexãoDadosModelo
        self.activation_model.copyCodeClicked.connect(self._on_copy_code_clicked)
        self.activation_model.retryClicked.connect(self._on_retry_clicked)
        self.activation_model.closeClicked.connect(self.close)

        self.logger.debug("ConexãoConfigurandoConcluído")

    def _setup_qml_connections(self):
        """
        ConfigurandoQMLConectando.
        """
        # ConexãoQMLparaPython
        if self.qml_widget and self.qml_widget.rootObject():
            root_object = self.qml_widget.rootObject()
            root_object.copyCodeClicked.connect(self._on_copy_code_clicked)
            root_object.retryClicked.connect(self._on_retry_clicked)
            root_object.closeClicked.connect(self.close)
            self.logger.debug("QMLConexãoConfigurandoConcluído")
        else:
            self.logger.warning("QMLNãoEncontrado，Incapaz deConfigurandoConexão")

    def _setup_signal_connections(self):
        """
        ConfigurandoConectando.
        """
        self.signal_emitter.status_changed.connect(self._on_status_changed)
        self.signal_emitter.error_occurred.connect(self._on_error_occurred)
        self.signal_emitter.data_ready.connect(self._on_data_ready)

    def _on_timer_update(self):
        """Dispositivo - IniciandoInicializando"""
        if not self.initialization_started:
            self.initialization_started = True
            self.stop_update_timer()  # PararDispositivo

            # EmInicializandoDispositivoIniciandoInicializando
            if self.system_initializer is not None:
                # AgoraEm，
                try:
                    self.create_task(self._start_initialization(), "initialization")
                except RuntimeError as e:
                    self.logger.error(f"InicializandoFalha: {e}")
                    # SeAinda  Falha，Vezes
                    self.start_update_timer(500)
            else:
                self.logger.info("InicializandoDispositivo，AutomáticoInicializando")

    async def _start_initialization(self):
        """
        IniciandosistemaInicializando.
        """
        try:
            # SeJáSystemInitializer，Usando
            if self.system_initializer:
                self._update_device_info()
                await self._start_activation_process()
            else:
                # entãodeInicializando
                self.system_initializer = SystemInitializer()

                # Inicializando
                init_result = await self.system_initializer.run_initialization()

                if init_result.get("success", False):
                    self._update_device_info()

                    # EstadoMensagem
                    self.status_message = init_result.get("status_message", "")
                    if self.status_message:
                        self.signal_emitter.emit_status(self.status_message)

                    # Pesquisar
                    if init_result.get("need_activation_ui", True):
                        await self._start_activation_process()
                    else:
                        # ，Concluído
                        self.is_activated = True
                        self.activation_completed.emit(True)
                else:
                    error_msg = init_result.get("error", "InicializandoFalha")
                    self.signal_emitter.emit_error(error_msg)

        except Exception as e:
            self.logger.error(f"InicializandoExceção: {e}", exc_info=True)
            self.signal_emitter.emit_error(f"InicializandoExceção: {e}")

    def _update_device_info(self):
        """
        dispositivoInformação.
        """
        if (
            not self.system_initializer
            or not self.system_initializer.device_fingerprint
        ):
            return

        device_fp = self.system_initializer.device_fingerprint

        # 
        serial_number = device_fp.get_serial_number()
        self.activation_model.serialNumber = serial_number if serial_number else "--"

        # MAC
        mac_address = device_fp.get_mac_address_from_efuse()
        self.activation_model.macAddress = mac_address if mac_address else "--"

        # Estado
        activation_status = self.system_initializer.get_activation_status()
        local_activated = activation_status.get("local_activated", False)
        server_activated = activation_status.get("server_activated", False)
        status_consistent = activation_status.get("status_consistent", True)

        # Estado
        self.is_activated = local_activated

        if not status_consistent:
            self.activation_model.set_status_inconsistent(
                local_activated, server_activated
            )
        else:
            if local_activated:
                self.activation_model.set_status_activated()
            else:
                self.activation_model.set_status_not_activated()

        # Inicializando
        self.activation_model.reset_activation_code()

    async def _start_activation_process(self):
        """
        Iniciandoativação.
        """
        try:
            # Dados
            activation_data = self.system_initializer.get_activation_data()

            if not activation_data:
                self.signal_emitter.emit_error("NãoparaDados，PesquisarConexão")
                return

            self.activation_data = activation_data

            # Informação
            self._show_activation_info(activation_data)

            # InicializandoDispositivoDispositivo
            config_manager = self.system_initializer.get_config_manager()
            self.device_activator = DeviceActivator(config_manager)

            # Começar
            self.signal_emitter.emit_status("ComeçarDispositivo...")
            activation_success = await self.device_activator.process_activation(
                activation_data
            )

            # PesquisarparaJanelaFechando
            if self.is_shutdown_requested():
                self.signal_emitter.emit_status("Já")
                return

            if activation_success:
                self.signal_emitter.emit_status("DispositivoSucesso！")
                self._on_activation_success()
            else:
                self.signal_emitter.emit_status("DispositivoFalha")
                self.signal_emitter.emit_error("DispositivoFalha，Tentar novamente")

        except Exception as e:
            self.logger.error(f"Exceção: {e}", exc_info=True)
            self.signal_emitter.emit_error(f"Exceção: {e}")

    def _show_activation_info(self, activation_data: dict):
        """
        ativaçãoInformação.
        """
        code = activation_data.get("code", "------")

        # DispositivoInformaçãoEmde
        self.activation_model.update_activation_code(code)

        # InformaçãoJáEmUI，Log
        self.logger.info(f"Validando: {code}")

    def _on_activation_success(self):
        """
        ativaçãosucessoProcessando.
        """
        # Estado
        self.activation_model.set_status_activated()

        # Concluído
        self.activation_completed.emit(True)
        self.is_activated = True

    def _on_status_changed(self, status: str):
        """
        estadoConversãoProcessando.
        """
        self.update_status(status)

    def _on_error_occurred(self, error_message: str):
        """
        erroProcessando.
        """
        self.logger.error(f"Erro: {error_message}")
        self.update_status(f"Erro: {error_message}")

    def _on_data_ready(self, data):
        """
        dadosProcessando - dispositivoInformação.
        """
        self.logger.debug(f"paraDados: {data}")
        if isinstance(data, dict):
            serial = data.get("serial_number")
            mac = data.get("mac_address")
            if serial or mac:
                self.logger.info(f"Através deDispositivoInformação: SN={serial}, MAC={mac}")
                self.activation_model.update_device_info(
                    serial_number=serial, mac_address=mac
                )

    def _on_retry_clicked(self):
        """
        Pulando paraativação - Abrindoativação.
        """
        self.logger.info("Pulando para")

        # deEmURL  Abrindo
        try:
            from src.utils.common_utils import open_url
            from src.utils.config_manager import ConfigManager

            config = ConfigManager.get_instance()
            ota_url = config.get_config("SYSTEM_OPTIONS.NETWORK.AUTHORIZATION_URL", "")
            if ota_url:
                open_url(ota_url)
                self.update_status("JáAbrindo，EmDispositivoEmEntradaValidando")
            else:
                self.logger.error("NãoURL")
                self.update_status("Erro: NãoURL")
        except Exception as e:
            self.logger.error(f"AbrindoFalha: {e}")
            self.update_status(f"AbrindoFalha: {e}")

    def _on_copy_code_clicked(self):
        """
        Validando.
        """
        if self.activation_data:
            code = self.activation_data.get("code", "")
            if code:
                clipboard = QApplication.clipboard()
                clipboard.setText(code)
                self.update_status(f"Validando  Jápara: {code}")
        else:
            # deModelo
            code = self.activation_model.activationCode
            if code and code != "--":
                clipboard = QApplication.clipboard()
                clipboard.setText(code)
                self.update_status(f"Validando  Jápara: {code}")

    def update_status(self, message: str):
        """
        estadoInformação.
        """
        self.logger.info(message)

        # Se  Estado，
        if hasattr(self, "status_label"):
            self.status_label.setText(message)

    def get_activation_result(self) -> dict:
        """
        ativação.
        """
        device_fingerprint = None
        config_manager = None

        if self.system_initializer:
            device_fingerprint = self.system_initializer.device_fingerprint
            config_manager = self.system_initializer.config_manager

        return {
            "is_activated": self.is_activated,
            "device_fingerprint": device_fingerprint,
            "config_manager": config_manager,
        }

    async def shutdown_async(self):
        """
        Fechando.
        """
        self.logger.info("EmFechandoJanela...")

        # （Se  Em）
        if self.device_activator:
            self.device_activator.cancel_activation()
            self.logger.info("JáEnviando")

        # 
        await self.cleanup_async_tasks()

        # Fechando
        await super().shutdown_async()

    def mousePressEvent(self, event):
        """
         - Janela.
        """
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        """
         - Janela.
        """
        if event.buttons() == Qt.LeftButton and self.drag_position:
            self.move(event.globalPos() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        """
        .
        """
        self.drag_position = None

    def _apply_native_rounded_corners(self):
        """
        aplicaçãoArredondadoJanela.
        """
        try:
            # Janela
            width = self.width()
            height = self.height()

            # ArredondadoCaminho
            radius = 16  # ArredondadoRaio
            path = QPainterPath()
            path.addRoundedRect(0, 0, width, height, radius, radius)

            # AppparaJanela
            region = QRegion(path.toFillPolygon().toPolygon())
            self.setMask(region)

            self.logger.info(
                f"JáAppArredondadoJanela: {width}x{height}, ArredondadoRaio: {radius}px"
)
        except Exception as e:
            self.logger.error(f"AppArredondadoFalha: {e}")

    def resizeEvent(self, event):
        super().resizeEvent(event)

    def closeEvent(self, event):
        """
        JanelaFechandoProcessando.
        """
        self.logger.info("JanelaFechando")
        self.window_closed.emit()
        event.accept()
