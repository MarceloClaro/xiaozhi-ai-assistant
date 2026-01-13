# -*- coding: utf-8 -*-
"""
Módulo de exibição GUI - Implementado usando QML.
"""

import asyncio
import os
import signal
from abc import ABCMeta
from pathlib import Path
from typing import Callable, Optional

from PyQt5.QtCore import QObject, Qt, QTimer, QUrl
from PyQt5.QtGui import QCursor, QFont
from PyQt5.QtQuickWidgets import QQuickWidget
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QWidget

from src.display.base_display import BaseDisplay
from src.display.gui_display_model import GuiDisplayModel
from src.utils.resource_finder import find_assets_dir


# Criar metaclasse compatível
class CombinedMeta(type(QObject), ABCMeta):
    pass


class GuiDisplay(BaseDisplay, QObject, metaclass=CombinedMeta):
    """Classe de exibição GUI - Interface moderna baseada em QML"""

    # Definições de constantes
    EMOTION_EXTENSIONS = (".gif", ".png", ".jpg", ".jpeg", ".webp")
    DEFAULT_WINDOW_SIZE = (880, 560)
    MINIMUM_WINDOW_SIZE = (480, 360)
    DEFAULT_FONT_SIZE = 12
    QUIT_TIMEOUT_MS = 3000

    def __init__(self):
        super().__init__()
        QObject.__init__(self)

        # Componentes Qt
        self.app = None
        self.root = None
        self.qml_widget = None
        self.system_tray = None

        # Modelo de dados
        self.display_model = GuiDisplayModel()

        # Gerenciamento de expressões
        self._emotion_cache = {}
        self._last_emotion_name = None

        # Gerenciamento de estado
        self.auto_mode = False
        self._running = True
        self.current_status = ""
        self.is_connected = True

        # Estado de arrastamento da janela
        self._dragging = False
        self._drag_position = None

        # Mapa de funções de retorno de chamada
        self._callbacks = {
            "button_press": None,
            "button_release": None,
            "mode": None,
            "auto": None,
            "abort": None,
            "send_text": None,
        }

    # =========================================================================
    # API Pública - Retornos de chamada com atualizações
    # =========================================================================

    async def set_callbacks(
        self,
        press_callback: Optional[Callable] = None,
        release_callback: Optional[Callable] = None,
        mode_callback: Optional[Callable] = None,
        auto_callback: Optional[Callable] = None,
        abort_callback: Optional[Callable] = None,
        send_text_callback: Optional[Callable] = None,
    ):
        """
        Configura as funções de retorno de chamada.
        """
        self._callbacks.update(
            {
                "button_press": press_callback,
                "button_release": release_callback,
                "mode": mode_callback,
                "auto": auto_callback,
                "abort": abort_callback,
                "send_text": send_text_callback,
            }
        )

    async def update_status(self, status: str, connected: bool):
        """
        Atualiza o texto de estado e processa a lógica relacionada.
        """
        self.display_model.update_status(status, connected)

        # Rastrear mudanças de estado
        status_changed = status != self.current_status
        connected_changed = bool(connected) != self.is_connected

        if status_changed:
            self.current_status = status
        if connected_changed:
            self.is_connected = bool(connected)

        # Atualizar bandeja do sistema
        if (status_changed or connected_changed) and self.system_tray:
            self.system_tray.update_status(status, self.is_connected)

    async def update_text(self, text: str):
        """
        Atualiza o texto de TTS.
        """
        self.display_model.update_text(text)

    async def update_emotion(self, emotion_name: str):
        """
        Atualiza a exibição da expressão.
        """
        if emotion_name == self._last_emotion_name:
            return

        self._last_emotion_name = emotion_name
        asset_path = self._get_emotion_asset_path(emotion_name)

        # Converta o caminho do arquivo local para uma URL disponível para QML (file:///...),
        # Arquivos não-locais (como caracteres emoji) permanecem inalterados.
        def to_qml_url(p: str) -> str:
            if not p:
                return ""
            if p.startswith(("qrc:/", "file:")):
                return p
            # Apenas converta para URL de arquivo quando o caminho existe, evitando tratar emoji como caminho
            try:
                if os.path.exists(p):
                    return QUrl.fromLocalFile(p).toString()
            except Exception:
                pass
            return p

        url_or_text = to_qml_url(asset_path)
        self.display_model.update_emotion(url_or_text)

    async def update_button_status(self, text: str):
        """
        Atualiza o estado do botão.
        """
        if self.auto_mode:
            self.display_model.update_button_text(text)

    async def toggle_mode(self):
        """
        Alterna o modo de diálogo.
        """
        if self._callbacks["mode"]:
            self._on_mode_button_click()
            self.logger.debug("Alternando modo de diálogo via atalho de teclado")

    async def toggle_window_visibility(self):
        """
        Alterna a visibilidade da janela.
        """
        if not self.root:
            return

        if self.root.isVisible():
            self.logger.debug("Ocultando janela via atalho de teclado")
            self.root.hide()
        else:
            self.logger.debug("Exibindo janela via atalho de teclado")
            self._show_main_window()

    async def close(self):
        """
        Processamento de fechamento de janela.
        """
        self._running = False
        if self.system_tray:
            self.system_tray.hide()
        if self.root:
            self.root.close()

    # =========================================================================
    # Processo de inicialização
    # =========================================================================

    async def start(self):
        """
        Inicia a GUI.
        """
        try:
            self._configure_environment()
            self._create_main_window()
            self._load_qml()
            self._setup_interactions()
            await self._finalize_startup()
        except Exception as e:
            self.logger.error(f"Falha ao iniciar GUI: {e}", exc_info=True)
            raise

    def _configure_environment(self):
        """
        Configura o ambiente.
        """
        os.environ.setdefault("QT_LOGGING_RULES", "qt.qpa.fonts.debug=false")

        self.app = QApplication.instance()
        if self.app is None:
            raise RuntimeError(
                "QApplication não encontrado, certifique-se de estar em ambiente qasync"
            )

        self.app.setQuitOnLastWindowClosed(False)
        self.app.setFont(QFont("PingFang SC", self.DEFAULT_FONT_SIZE))

        self._setup_signal_handlers()
        self._setup_activation_handler()

    def _create_main_window(self):
        """
        Cria a janela principal.
        """
        self.root = QWidget()
        self.root.setWindowTitle("")
        self.root.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)

        # Calcule o tamanho da janela de acordo com a configuração
        window_size, is_fullscreen = self._calculate_window_size()
        self.root.resize(*window_size)

        # Configurar tamanho mínimo de janela
        self.root.setMinimumSize(*self.MINIMUM_WINDOW_SIZE)

        # Salve o estado de tela cheia, usar ao mostrar
        self._is_fullscreen = is_fullscreen

        self.root.closeEvent = self._closeEvent

    def _calculate_window_size(self) -> tuple:
        """
        Calcula o tamanho da janela. Retorna (largura, altura, tela_cheia)
        """
        try:
            from src.utils.config_manager import ConfigManager

            config_manager = ConfigManager.get_instance()
            window_size_mode = config_manager.get_config(
                "SYSTEM_OPTIONS.WINDOW_SIZE_MODE", "default"
            )

            # Obter tamanho da tela (área disponível, excluindo barra de tarefas)
            desktop = QApplication.desktop()
            screen_rect = desktop.availableGeometry()
            screen_width = screen_rect.width()
            screen_height = screen_rect.height()

            # Calcule o tamanho da janela de acordo com o modo
            if window_size_mode == "default":
                # Padrão: 50% da tela
                width = int(screen_width * 0.5)
                height = int(screen_height * 0.5)
                is_fullscreen = False
            elif window_size_mode == "screen_75":
                width = int(screen_width * 0.75)
                height = int(screen_height * 0.75)
                is_fullscreen = False
            elif window_size_mode == "screen_100":
                # 100% modo de tela cheia real
                width = screen_width
                height = screen_height
                is_fullscreen = True
            else:
                # Modo desconhecido: usa 50% por padrão
                width = int(screen_width * 0.5)
                height = int(screen_height * 0.5)
                is_fullscreen = False

            return ((width, height), is_fullscreen)

        except Exception as e:
            self.logger.error(f"Erro ao calcular tamanho da janela: {e}", exc_info=True)
            # Erro: retorna 50% da tela
            try:
                desktop = QApplication.desktop()
                screen_rect = desktop.availableGeometry()
                return (
                    (int(screen_rect.width() * 0.5), int(screen_rect.height() * 0.5)),
                    False,
                )
            except Exception:
                return (self.DEFAULT_WINDOW_SIZE, False)

    def _load_qml(self):
        """
        Carrega a interface QML.
        """
        self.qml_widget = QQuickWidget()
        self.qml_widget.setResizeMode(QQuickWidget.SizeRootObjectToView)
        self.qml_widget.setClearColor(Qt.white)

        # Registre o modelo de dados para o contexto QML
        qml_context = self.qml_widget.rootContext()
        qml_context.setContextProperty("displayModel", self.display_model)

        # Carregue o arquivo QML
        qml_file = Path(__file__).parent / "gui_display.qml"
        self.qml_widget.setSource(QUrl.fromLocalFile(str(qml_file)))

        # Configuração para o widget central da janela principal
        layout = QVBoxLayout(self.root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.qml_widget)

    def _setup_interactions(self):
        """
        Configura a interação (sinais, bandeja)
        """
        self._connect_qml_signals()

    async def _finalize_startup(self):
        """
        Conclui o processo de inicialização.
        """
        await self.update_emotion("neutral")

        # Decide o modo de exibição de acordo com a configuração
        if getattr(self, "_is_fullscreen", False):
            self.root.showFullScreen()
        else:
            self.root.show()

        self._setup_system_tray()

    # =========================================================================
    # Conexão de sinais
    # =========================================================================

    def _connect_qml_signals(self):
        """
        Conecta sinais QML aos slots do Python.
        """
        root_object = self.qml_widget.rootObject()
        if not root_object:
            self.logger.warning(
                "Objeto raiz QML não encontrado, não é possível configurar conexão de sinais"
            )
            return

        # Mapa de sinais de eventos de botão
        button_signals = {
            "manualButtonPressed": self._on_manual_button_press,
            "manualButtonReleased": self._on_manual_button_release,
            "autoButtonClicked": self._on_auto_button_click,
            "abortButtonClicked": self._on_abort_button_click,
            "modeButtonClicked": self._on_mode_button_click,
            "sendButtonClicked": self._on_send_button_click,
            "settingsButtonClicked": self._on_settings_button_click,
        }

        # Mapa de sinais de controle da barra de título
        titlebar_signals = {
            "titleMinimize": self._minimize_window,
            "titleClose": self._quit_application,
            "titleDragStart": self._on_title_drag_start,
            "titleDragMoveTo": self._on_title_drag_move,
            "titleDragEnd": self._on_title_drag_end,
        }

        # Conexão de sinais
        for signal_name, handler in {**button_signals, **titlebar_signals}.items():
            try:
                getattr(root_object, signal_name).connect(handler)
            except AttributeError:
                self.logger.debug(f"Sinal {signal_name} não existe (pode ser opcional)")

        self.logger.debug("Conexão de sinais QML configurada com sucesso")

    # =========================================================================
    # BotãoProcessando
    # =========================================================================

    def _on_manual_button_press(self):
        """
        Botão modo manual pressionado.
        """
        self._dispatch_callback("button_press")

    def _on_manual_button_release(self):
        """
        Botão modo manual liberado.
        """
        self._dispatch_callback("button_release")

    def _on_auto_button_click(self):
        """
        Clique no botão modo automático.
        """
        self._dispatch_callback("auto")

    def _on_abort_button_click(self):
        """
        Clique no botão abortar.
        """
        self._dispatch_callback("abort")

    def _on_mode_button_click(self):
        """
        Clique no botão alternar modo de diálogo.
        """
        if self._callbacks["mode"] and not self._callbacks["mode"]():
            return

        self.auto_mode = not self.auto_mode
        mode_text = "Diálogo automático" if self.auto_mode else "Diálogo manual"
        self.display_model.update_mode_text(mode_text)
        self.display_model.set_auto_mode(self.auto_mode)

    def _on_send_button_click(self, text: str):
        """
        Processa clique do botão de envio de texto.
        """
        text = text.strip()
        if not text or not self._callbacks["send_text"]:
            return

        try:
            task = asyncio.create_task(self._callbacks["send_text"](text))
            task.add_done_callback(
                lambda t: t.cancelled()
                or not t.exception()
                or self.logger.error(
                    f"Erro na tarefa de envio de texto: {t.exception()}", exc_info=True
                )
            )
        except Exception as e:
            self.logger.error(f"Erro ao enviar texto: {e}")

    def _on_settings_button_click(self):
        """
        Processa clique do botão de configurações.
        """
        try:
            from src.views.settings import SettingsWindow

            settings_window = SettingsWindow(self.root)
            settings_window.exec_()
        except Exception as e:
            self.logger.error(f"Erro ao abrir janela de configurações: {e}", exc_info=True)

    def _dispatch_callback(self, callback_name: str, *args):
        """
        Despachador genérico de retorno de chamada.
        """
        callback = self._callbacks.get(callback_name)
        if callback:
            callback(*args)

    # =========================================================================
    # Arrastamento de janela
    # =========================================================================

    def _on_title_drag_start(self, _x, _y):
        """
        Inicia o arrastamento da barra de título.
        """
        self._dragging = True
        self._drag_position = QCursor.pos() - self.root.pos()

    def _on_title_drag_move(self, _x, _y):
        """
        Movimento de arrastamento da barra de título.
        """
        if self._dragging and self._drag_position:
            self.root.move(QCursor.pos() - self._drag_position)

    def _on_title_drag_end(self):
        """
        Final do arrastamento da barra de título.
        """
        self._dragging = False
        self._drag_position = None

    # =========================================================================
    # Gerenciamento de expressões
    # =========================================================================

    def _get_emotion_asset_path(self, emotion_name: str) -> str:
        """
        Obtém o caminho do arquivo de ativo de expressão.
        """
        if emotion_name in self._emotion_cache:
            return self._emotion_cache[emotion_name]

        assets_dir = find_assets_dir()
        if not assets_dir:
            path = "😊"
        else:
            emotion_dir = assets_dir / "emojis"
            # Tenta encontrar arquivo de expressão, falha então volta para neutro
            path = (
                str(self._find_emotion_file(emotion_dir, emotion_name))
                or str(self._find_emotion_file(emotion_dir, "neutral"))
                or "😊"
            )

        self._emotion_cache[emotion_name] = path
        return path

    def _find_emotion_file(self, emotion_dir: Path, name: str) -> Optional[Path]:
        """
        Procura arquivo de expressão no diretório especificado.
        """
        for ext in self.EMOTION_EXTENSIONS:
            file_path = emotion_dir / f"{name}{ext}"
            if file_path.exists():
                return file_path
        return None

    # =========================================================================
    # Configuração
    # =========================================================================

    def _setup_signal_handlers(self):
        """
        Configura o manipulador de sinais (Ctrl+C)
        """
        try:
            signal.signal(
                signal.SIGINT,
                lambda *_: QTimer.singleShot(0, self._quit_application),
            )
        except Exception as e:
            self.logger.warning(
                f"Falha ao configurar manipulador de sinaisProcessando  Falha: {e}"
            )

    def _setup_activation_handler(self):
        """
        Configura o manipulador de ativação (macOS)
        """
        try:
            import platform

            if platform.system() != "Darwin":
                return

            self.app.applicationStateChanged.connect(self._on_application_state_changed)
            self.logger.debug(
                "Configurado manipulador de ativação (macOS)"
            )
        except Exception as e:
            self.logger.warning(f"Falha ao configurar manipulador de ativação: {e}")

    def _on_application_state_changed(self, state):
        """
        Processamento de mudança de estado de aplicação
        """
        if state == Qt.ApplicationActive and self.root and not self.root.isVisible():
            QTimer.singleShot(0, self._show_main_window)

    def _setup_system_tray(self):
        """
        Configura a bandeja do sistema.
        """
        if os.getenv("XIAOZHI_DISABLE_TRAY") == "1":
            self.logger.warning(
                "Bandeja do sistema desabilitada via variável de ambiente (XIAOZHI_DISABLE_TRAY=1)"
            )
            return

        try:
            from src.views.components.system_tray import SystemTray

            self.system_tray = SystemTray(self.root)

            # Conexão de sinais da bandeja (usando QTimer para garantir execução na thread principal)
            tray_signals = {
                "show_window_requested": self._show_main_window,
                "settings_requested": self._on_settings_button_click,
                "quit_requested": self._quit_application,
            }

            for signal_name, handler in tray_signals.items():
                getattr(self.system_tray, signal_name).connect(
                    lambda h=handler: QTimer.singleShot(0, h)
                )

        except Exception as e:
            self.logger.error(
                f"Erro ao inicializar componente de bandeja do sistema: {e}",
                exc_info=True,
            )

    # =========================================================================
    # Controle de janela
    # =========================================================================

    def _show_main_window(self):
        """
        Exibe a janela principal.
        """
        if not self.root:
            return

        if self.root.isMinimized():
            self.root.showNormal()
        if not self.root.isVisible():
            self.root.show()
        self.root.activateWindow()
        self.root.raise_()

    def _minimize_window(self):
        """
        Minimiza a janela.
        """
        if self.root:
            self.root.showMinimized()

    def _quit_application(self):
        """
        Encerra a aplicação.
        """
        self.logger.info("ComeçarAplicação...")
        self._running = False

        if self.system_tray:
            self.system_tray.hide()

        try:
            from src.application import Application

            app = Application.get_instance()
            if not app:
                QApplication.quit()
                return

            loop = asyncio.get_event_loop()
            if not loop.is_running():
                QApplication.quit()
                return

            # FechandoConfigurandoTimeout
            shutdown_task = asyncio.create_task(app.shutdown())

            def on_shutdown_complete(task):
                if not task.cancelled() and task.exception():
                    self.logger.error(f"Exceção ao encerrar aplicação: {task.exception()}")
                else:
                    self.logger.info("Aplicação encerrada normalmente")
                QApplication.quit()

            def force_quit():
                if not shutdown_task.done():
                    self.logger.warning("Timeout no encerramento, forçando saída")
                    shutdown_task.cancel()
                QApplication.quit()

            shutdown_task.add_done_callback(on_shutdown_complete)
            QTimer.singleShot(self.QUIT_TIMEOUT_MS, force_quit)

        except Exception as e:
            self.logger.error(f"Erro ao encerrar aplicação: {e}")
            QApplication.quit()

    def _closeEvent(self, event):
        """
        Processa evento de fechamento de janela.
        """
        # Se a bandeja do sistema estiver disponível, minimizar para bandeja
        if self.system_tray and (
            getattr(self.system_tray, "is_available", lambda: False)()
            or getattr(self.system_tray, "is_visible", lambda: False)()
        ):
            self.logger.info("Fechando janela: minimizando para bandeja")
            QTimer.singleShot(0, self.root.hide)
            event.ignore()
        else:
            QTimer.singleShot(0, self._quit_application)
            event.accept()
