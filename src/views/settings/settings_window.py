import os
from pathlib import Path

from PyQt5.QtWidgets import (
    QDialog,
    QMessageBox,
    QPushButton,
    QTabWidget,
)

from src.utils.config_manager import ConfigManager
from src.utils.logging_config import get_logger
from src.views.settings.components.audio import AudioWidget
from src.views.settings.components.camera import CameraWidget
from src.views.settings.components.shortcuts_settings import ShortcutsSettingsWidget
from src.views.settings.components.system_options import SystemOptionsWidget
from src.views.settings.components.wake_word import WakeWordWidget


class SettingsWindow(QDialog):
    """
    ParâmetroconfiguraçãoJanela.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = get_logger(__name__)
        self.config_manager = ConfigManager.get_instance()

        # 
        self.system_options_tab = None
        self.wake_word_tab = None
        self.camera_tab = None
        self.audio_tab = None
        self.shortcuts_tab = None

        # UI
        self.ui_controls = {}

        # InicializandoUI
        self._setup_ui()
        self._connect_events()

    def _setup_ui(self):
        """
        ConfigurandoUI.
        """
        try:
            from PyQt5 import uic

            ui_path = Path(__file__).parent / "settings_window.ui"
            uic.loadUi(str(ui_path), self)

            # UIde
            self._get_ui_controls()

            # 
            self._add_component_tabs()

        except Exception as e:
            self.logger.error(f"ConfigurandoUIFalha: {e}", exc_info=True)
            raise

    def _add_component_tabs(self):
        """
        .
        """
        try:
            # TabWidget
            tab_widget = self.findChild(QTabWidget, "tabWidget")
            if not tab_widget:
                self.logger.error("NãoEncontradoTabWidget")
                return

            # Limpando（Se  de）
            tab_widget.clear()

            # 
            self.system_options_tab = SystemOptionsWidget()
            tab_widget.addTab(self.system_options_tab, "Sistema")
            self.system_options_tab.settings_changed.connect(self._on_settings_changed)

            # 
            self.wake_word_tab = WakeWordWidget()
            tab_widget.addTab(self.wake_word_tab, "Palavra-chave")
            self.wake_word_tab.settings_changed.connect(self._on_settings_changed)

            # 
            self.camera_tab = CameraWidget()
            tab_widget.addTab(self.camera_tab, "Câmera")
            self.camera_tab.settings_changed.connect(self._on_settings_changed)

            # ÁudioDispositivo
            self.audio_tab = AudioWidget()
            tab_widget.addTab(self.audio_tab, "Áudio")
            self.audio_tab.settings_changed.connect(self._on_settings_changed)

            # Configurando
            self.shortcuts_tab = ShortcutsSettingsWidget()
            tab_widget.addTab(self.shortcuts_tab, "Atalhos")
            self.shortcuts_tab.settings_changed.connect(self._on_settings_changed)

            self.logger.debug("Sucesso")

        except Exception as e:
            self.logger.error(f"Falha: {e}", exc_info=True)

    def _on_settings_changed(self):
        """
        Configurando.
        """
        # Emou

    def _get_ui_controls(self):
        """
        UI.
        """
        # de
        self.ui_controls.update(
            {
                "save_btn": self.findChild(QPushButton, "save_btn"),
                "cancel_btn": self.findChild(QPushButton, "cancel_btn"),
                "reset_btn": self.findChild(QPushButton, "reset_btn"),
            }
        )

        # Forçar campos de senha/token a ficarem visíveis para auditoria
        from PyQt5.QtWidgets import QLineEdit
        
        password_fields = [
            "websocket_token_edit",
            "mqtt_password_edit",
            "vl_api_key_edit"
        ]
        
        for field_name in password_fields:
            field = self.findChild(QLineEdit, field_name)
            if field:
                field.setEchoMode(QLineEdit.Normal)
                self.logger.info(f"✅ Campo '{field_name}' configurado como visível")

    def _connect_events(self):
        """
        ConectandoProcessando.
        """
        if self.ui_controls["save_btn"]:
            self.ui_controls["save_btn"].clicked.connect(self._on_save_clicked)

        if self.ui_controls["cancel_btn"]:
            self.ui_controls["cancel_btn"].clicked.connect(self.reject)

        if self.ui_controls["reset_btn"]:
            self.ui_controls["reset_btn"].clicked.connect(self._on_reset_clicked)

    # ConfiguraçãoAgoraProcessando，NãoEm  JanelaEmProcessando

    # NãodeOperação，AgoraProcessando

    def _on_save_clicked(self):
        """
        Salvando.
        """
        try:
            # Dados
            success = self._save_all_config()

            if success:
                # Sucesso
                reply = QMessageBox.question(
                    self,
                    "Sucesso",
                    "Configurações salvas!\n\nDeseja reiniciar a aplicação?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.Yes,
                )

                if reply == QMessageBox.Yes:
                    self._restart_application()
                else:
                    self.accept()
            else:
                QMessageBox.warning(self, "Erro", "ConfiguraçãoFalha，PesquisarEntradadeValor。")

        except Exception as e:
            self.logger.error(f"Falha: {e}", exc_info=True)
            QMessageBox.critical(self, "Erro", f"Erro: {str(e)}")

    def _save_all_config(self) -> bool:
        """
        Salvandoconfiguração.
        """
        try:
            # deDados
            all_config_data = {}

            # 
            if self.system_options_tab:
                system_config = self.system_options_tab.get_config_data()
                all_config_data.update(system_config)

            # 
            if self.wake_word_tab:
                wake_word_config = self.wake_word_tab.get_config_data()
                all_config_data.update(wake_word_config)
                # Arquivo
                self.wake_word_tab.save_keywords()

            # 
            if self.camera_tab:
                camera_config = self.camera_tab.get_config_data()
                all_config_data.update(camera_config)

            # ÁudioDispositivo
            if self.audio_tab:
                audio_config = self.audio_tab.get_config_data()
                all_config_data.update(audio_config)

            # 
            if self.shortcuts_tab:
                # de
                self.shortcuts_tab.apply_settings()

            # 
            for config_path, value in all_config_data.items():
                self.config_manager.update_config(config_path, value)

            self.logger.info("Sucesso")
            return True

        except Exception as e:
            self.logger.error(f": {e}", exc_info=True)
            return False

    def _on_reset_clicked(self):
        """
        .
        """
        reply = QMessageBox.question(
            self,
            "",
            "paraValor？\ndeConfigurando。",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            self._reset_to_defaults()

    def _reset_to_defaults(self):
        """
        paraValor.
        """
        try:
            # paraValor
            if self.system_options_tab:
                self.system_options_tab.reset_to_defaults()

            if self.wake_word_tab:
                self.wake_word_tab.reset_to_defaults()

            if self.camera_tab:
                self.camera_tab.reset_to_defaults()

            if self.audio_tab:
                self.audio_tab.reset_to_defaults()

            if self.shortcuts_tab:
                self.shortcuts_tab.reset_to_defaults()

            self.logger.info("Configurações resetadas para padrão")

        except Exception as e:
            self.logger.error(f"Falha: {e}", exc_info=True)
            QMessageBox.critical(self, "Erro", f"Erro: {str(e)}")

    def _restart_application(self):
        """
        Reiniciar a aplicação.
        """
        try:
            self.logger.info("SelecionandoAplicação")

            # FechandoConfigurandoJanela
            self.accept()

            # 
            self._direct_restart()

        except Exception as e:
            self.logger.error(f"AplicaçãoFalha: {e}", exc_info=True)
            QMessageBox.warning(
                self, "Falha", "AutomáticoFalha，Configuração。"
            )

    def _direct_restart(self):
        """
        programa.
        """
        try:
            import sys

            from PyQt5.QtWidgets import QApplication

            # deCaminhoeParâmetro
            python = sys.executable
            script = sys.argv[0]
            args = sys.argv[1:]

            self.logger.info(f"Comando: {python} {script} {' '.join(args)}")

            # FechandoApp
            QApplication.quit()

            # Iniciando
            if getattr(sys, "frozen", False):
                # 
                os.execv(sys.executable, [sys.executable] + args)
            else:
                # 
                os.execv(python, [python, script] + args)

        except Exception as e:
            self.logger.error(f"Falha: {e}", exc_info=True)

    def closeEvent(self, event):
        """
        Janela sendo fechada.
        """
        self.logger.debug("Janela de configurações fechando")
        super().closeEvent(event)
