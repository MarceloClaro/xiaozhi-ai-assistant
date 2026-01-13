from pathlib import Path

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QCheckBox, QComboBox, QLineEdit, QWidget

from src.utils.config_manager import ConfigManager
from src.utils.logging_config import get_logger


class SystemOptionsWidget(QWidget):
    """
    sistemaConfigurando.
    """

    # 
    settings_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = get_logger(__name__)
        self.config_manager = ConfigManager.get_instance()

        # UI
        self.ui_controls = {}

        # InicializandoUI
        self._setup_ui()
        self._connect_events()
        self._load_config_values()

    def _setup_ui(self):
        """
        ConfigurandoUI.
        """
        try:
            from PyQt5 import uic

            ui_path = Path(__file__).parent / "system_options_widget.ui"
            uic.loadUi(str(ui_path), self)

            # UI
            self._get_ui_controls()

        except Exception as e:
            self.logger.error(f"ConfigurandoUIFalha: {e}", exc_info=True)
            raise

    def _get_ui_controls(self):
        """
        UI.
        """
        # 
        self.ui_controls.update(
            {
                "client_id_edit": self.findChild(QLineEdit, "client_id_edit"),
                "device_id_edit": self.findChild(QLineEdit, "device_id_edit"),
                "ota_url_edit": self.findChild(QLineEdit, "ota_url_edit"),
                "websocket_url_edit": self.findChild(QLineEdit, "websocket_url_edit"),
                "websocket_token_edit": self.findChild(
                    QLineEdit, "websocket_token_edit"
                ),
                "authorization_url_edit": self.findChild(
                    QLineEdit, "authorization_url_edit"
                ),
                "activation_version_combo": self.findChild(
                    QComboBox, "activation_version_combo"
                ),
                "window_size_combo": self.findChild(QComboBox, "window_size_combo"),
            }
        )

        # MQTT
        self.ui_controls.update(
            {
                "mqtt_endpoint_edit": self.findChild(QLineEdit, "mqtt_endpoint_edit"),
                "mqtt_client_id_edit": self.findChild(QLineEdit, "mqtt_client_id_edit"),
                "mqtt_username_edit": self.findChild(QLineEdit, "mqtt_username_edit"),
                "mqtt_password_edit": self.findChild(QLineEdit, "mqtt_password_edit"),
                "mqtt_publish_topic_edit": self.findChild(
                    QLineEdit, "mqtt_publish_topic_edit"
                ),
                "mqtt_subscribe_topic_edit": self.findChild(
                    QLineEdit, "mqtt_subscribe_topic_edit"
                ),
            }
        )

        # Forçar campos de senha/token a ficarem visíveis para auditoria
        password_fields = {
            "websocket_token_edit": self.findChild(QLineEdit, "websocket_token_edit"),
            "mqtt_password_edit": self.ui_controls.get("mqtt_password_edit")
        }
        
        for field_name, field in password_fields.items():
            if field:
                field.setEchoMode(QLineEdit.Normal)
                self.logger.info(f"✅ Campo '{field_name}' forçado como visível")

        # AEC
        self.ui_controls.update(
            {
                "aec_enabled_check": self.findChild(QCheckBox, "aec_enabled_check"),
            }
        )

    def _connect_events(self):
        """
        ConectandoProcessando.
        """
        # paraEntradaConexão
        for control in self.ui_controls.values():
            if isinstance(control, QLineEdit):
                control.textChanged.connect(self.settings_changed.emit)
            elif isinstance(control, QComboBox):
                control.currentTextChanged.connect(self.settings_changed.emit)
            elif isinstance(control, QCheckBox):
                control.stateChanged.connect(self.settings_changed.emit)

    def _load_config_values(self):
        """
        deconfiguraçãoarquivoCarregandoValorparaUI.
        """
        try:
            # 
            client_id = self.config_manager.get_config("SYSTEM_OPTIONS.CLIENT_ID", "")
            self._set_text_value("client_id_edit", client_id)

            device_id = self.config_manager.get_config("SYSTEM_OPTIONS.DEVICE_ID", "")
            self._set_text_value("device_id_edit", device_id)

            ota_url = self.config_manager.get_config(
                "SYSTEM_OPTIONS.NETWORK.OTA_VERSION_URL", ""
            )
            self._set_text_value("ota_url_edit", ota_url)

            websocket_url = self.config_manager.get_config(
                "SYSTEM_OPTIONS.NETWORK.WEBSOCKET_URL", ""
            )
            self._set_text_value("websocket_url_edit", websocket_url)

            websocket_token = self.config_manager.get_config(
                "SYSTEM_OPTIONS.NETWORK.WEBSOCKET_ACCESS_TOKEN", ""
            )
            self._set_text_value("websocket_token_edit", websocket_token)

            auth_url = self.config_manager.get_config(
                "SYSTEM_OPTIONS.NETWORK.AUTHORIZATION_URL", ""
            )
            self._set_text_value("authorization_url_edit", auth_url)

            # Versão
            activation_version = self.config_manager.get_config(
                "SYSTEM_OPTIONS.NETWORK.ACTIVATION_VERSION", "v1"
            )
            if self.ui_controls["activation_version_combo"]:
                combo = self.ui_controls["activation_version_combo"]
                combo.setCurrentText(activation_version)

            # JanelaTamanhoModo
            window_size_mode = self.config_manager.get_config(
                "SYSTEM_OPTIONS.WINDOW_SIZE_MODE", "default"
            )
            if self.ui_controls["window_size_combo"]:
                # Valorpara（ = 50%）
                mode_to_text = {
                    "default": "",
                    "screen_75": "75%",
                    "screen_100": "100%",
                }
                combo = self.ui_controls["window_size_combo"]
                combo.setCurrentText(mode_to_text.get(window_size_mode, ""))

            # MQTT
            mqtt_info = self.config_manager.get_config(
                "SYSTEM_OPTIONS.NETWORK.MQTT_INFO", {}
            )
            if mqtt_info:
                self._set_text_value(
                    "mqtt_endpoint_edit", mqtt_info.get("endpoint", "")
                )
                self._set_text_value(
                    "mqtt_client_id_edit", mqtt_info.get("client_id", "")
                )
                self._set_text_value(
                    "mqtt_username_edit", mqtt_info.get("username", "")
                )
                self._set_text_value(
                    "mqtt_password_edit", mqtt_info.get("password", "")
                )
                self._set_text_value(
                    "mqtt_publish_topic_edit", mqtt_info.get("publish_topic", "")
                )
                self._set_text_value(
                    "mqtt_subscribe_topic_edit", mqtt_info.get("subscribe_topic", "")
                )

            # AEC
            aec_enabled = self.config_manager.get_config("AEC_OPTIONS.ENABLED", True)
            self._set_check_value("aec_enabled_check", aec_enabled)

        except Exception as e:
            self.logger.error(f"ValorFalha: {e}", exc_info=True)

    def _set_text_value(self, control_name: str, value: str):
        """
        ConfigurandodeValor.
        """
        control = self.ui_controls.get(control_name)
        if control and hasattr(control, "setText"):
            control.setText(str(value) if value is not None else "")

    def _get_text_value(self, control_name: str) -> str:
        """
        deValor.
        """
        control = self.ui_controls.get(control_name)
        if control and hasattr(control, "text"):
            return control.text().strip()
        return ""

    def _set_check_value(self, control_name: str, value: bool):
        """
        ConfigurandodeValor.
        """
        control = self.ui_controls.get(control_name)
        if control and hasattr(control, "setChecked"):
            control.setChecked(bool(value))

    def _get_check_value(self, control_name: str) -> bool:
        """
        deValor.
        """
        control = self.ui_controls.get(control_name)
        if control and hasattr(control, "isChecked"):
            return control.isChecked()
        return False

    def get_config_data(self) -> dict:
        """
        configuraçãodados.
        """
        config_data = {}

        try:
            # IDeDispositivoID
            client_id = self._get_text_value("client_id_edit")
            if client_id:
                config_data["SYSTEM_OPTIONS.CLIENT_ID"] = client_id

            device_id = self._get_text_value("device_id_edit")
            if device_id:
                config_data["SYSTEM_OPTIONS.DEVICE_ID"] = device_id

            #  - 
            ota_url = self._get_text_value("ota_url_edit")
            if ota_url:
                config_data["SYSTEM_OPTIONS.NETWORK.OTA_VERSION_URL"] = ota_url

            websocket_url = self._get_text_value("websocket_url_edit")
            if websocket_url:
                config_data["SYSTEM_OPTIONS.NETWORK.WEBSOCKET_URL"] = websocket_url

            websocket_token = self._get_text_value("websocket_token_edit")
            if websocket_token:
                config_data["SYSTEM_OPTIONS.NETWORK.WEBSOCKET_ACCESS_TOKEN"] = (
                    websocket_token
                )

            authorization_url = self._get_text_value("authorization_url_edit")
            if authorization_url:
                config_data["SYSTEM_OPTIONS.NETWORK.AUTHORIZATION_URL"] = (
                    authorization_url
                )

            # Versão
            if self.ui_controls["activation_version_combo"]:
                activation_version = self.ui_controls[
                    "activation_version_combo"
                ].currentText()
                config_data["SYSTEM_OPTIONS.NETWORK.ACTIVATION_VERSION"] = (
                    activation_version
                )

            # JanelaTamanhoModo
            if self.ui_controls["window_size_combo"]:
                # paraValor（ = 50%）
                text_to_mode = {
                    "": "default",
                    "75%": "screen_75",
                    "100%": "screen_100",
                }
                window_size_text = self.ui_controls["window_size_combo"].currentText()
                window_size_mode = text_to_mode.get(window_size_text, "default")
                config_data["SYSTEM_OPTIONS.WINDOW_SIZE_MODE"] = window_size_mode

            # MQTT
            mqtt_config = {}
            mqtt_endpoint = self._get_text_value("mqtt_endpoint_edit")
            if mqtt_endpoint:
                mqtt_config["endpoint"] = mqtt_endpoint

            mqtt_client_id = self._get_text_value("mqtt_client_id_edit")
            if mqtt_client_id:
                mqtt_config["client_id"] = mqtt_client_id

            mqtt_username = self._get_text_value("mqtt_username_edit")
            if mqtt_username:
                mqtt_config["username"] = mqtt_username

            mqtt_password = self._get_text_value("mqtt_password_edit")
            if mqtt_password:
                mqtt_config["password"] = mqtt_password

            mqtt_publish_topic = self._get_text_value("mqtt_publish_topic_edit")
            if mqtt_publish_topic:
                mqtt_config["publish_topic"] = mqtt_publish_topic

            mqtt_subscribe_topic = self._get_text_value("mqtt_subscribe_topic_edit")
            if mqtt_subscribe_topic:
                mqtt_config["subscribe_topic"] = mqtt_subscribe_topic

            if mqtt_config:
                # deMQTT
                existing_mqtt = self.config_manager.get_config(
                    "SYSTEM_OPTIONS.NETWORK.MQTT_INFO", {}
                )
                existing_mqtt.update(mqtt_config)
                config_data["SYSTEM_OPTIONS.NETWORK.MQTT_INFO"] = existing_mqtt

            # AEC
            aec_enabled = self._get_check_value("aec_enabled_check")
            config_data["AEC_OPTIONS.ENABLED"] = aec_enabled

        except Exception as e:
            self.logger.error(f"DadosFalha: {e}", exc_info=True)

        return config_data

    def reset_to_defaults(self):
        """
        paraValor.
        """
        try:
            # 
            default_config = ConfigManager.DEFAULT_CONFIG

            # 
            self._set_text_value(
                "ota_url_edit",
                default_config["SYSTEM_OPTIONS"]["NETWORK"]["OTA_VERSION_URL"],
            )
            self._set_text_value("websocket_url_edit", "")
            self._set_text_value("websocket_token_edit", "")
            self._set_text_value(
                "authorization_url_edit",
                default_config["SYSTEM_OPTIONS"]["NETWORK"]["AUTHORIZATION_URL"],
            )

            if self.ui_controls["activation_version_combo"]:
                self.ui_controls["activation_version_combo"].setCurrentText(
                    default_config["SYSTEM_OPTIONS"]["NETWORK"]["ACTIVATION_VERSION"]
                )

            # LimpandoMQTT
            self._set_text_value("mqtt_endpoint_edit", "")
            self._set_text_value("mqtt_client_id_edit", "")
            self._set_text_value("mqtt_username_edit", "")
            self._set_text_value("mqtt_password_edit", "")
            self._set_text_value("mqtt_publish_topic_edit", "")
            self._set_text_value("mqtt_subscribe_topic_edit", "")

            # AECValor
            default_aec = default_config.get("AEC_OPTIONS", {})
            self._set_check_value(
                "aec_enabled_check", default_aec.get("ENABLED", False)
            )

            self.logger.info("JáparaValor")

        except Exception as e:
            self.logger.error(f"Falha: {e}", exc_info=True)
