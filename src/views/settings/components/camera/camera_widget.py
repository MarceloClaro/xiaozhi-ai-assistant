from pathlib import Path

import cv2
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from src.utils.config_manager import ConfigManager
from src.utils.logging_config import get_logger


class CameraWidget(QWidget):
    """
    Configurando.
    """

    # 
    settings_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = get_logger(__name__)
        self.config_manager = ConfigManager.get_instance()

        # UI
        self.ui_controls = {}

        # 
        self.camera = None
        self.preview_timer = QTimer()
        self.preview_timer.timeout.connect(self._update_preview_frame)
        self.is_previewing = False

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

            ui_path = Path(__file__).parent / "camera_widget.ui"
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
        self.ui_controls.update(
            {
                "camera_index_spin": self.findChild(QSpinBox, "camera_index_spin"),
                "frame_width_spin": self.findChild(QSpinBox, "frame_width_spin"),
                "frame_height_spin": self.findChild(QSpinBox, "frame_height_spin"),
                "fps_spin": self.findChild(QSpinBox, "fps_spin"),
                "local_vl_url_edit": self.findChild(QLineEdit, "local_vl_url_edit"),
                "vl_api_key_edit": self.findChild(QLineEdit, "vl_api_key_edit"),
                "models_edit": self.findChild(QLineEdit, "models_edit"),
                "scan_camera_btn": self.findChild(QPushButton, "scan_camera_btn"),
                # 
                "preview_label": self.findChild(QLabel, "preview_label"),
                "start_preview_btn": self.findChild(QPushButton, "start_preview_btn"),
                "stop_preview_btn": self.findChild(QPushButton, "stop_preview_btn"),
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
            elif isinstance(control, QSpinBox):
                if control == self.ui_controls.get("camera_index_spin"):
                    # Conversão，Automático
                    control.valueChanged.connect(self._on_camera_index_changed)
                else:
                    control.valueChanged.connect(self.settings_changed.emit)
            elif isinstance(control, QPushButton):
                continue

        # 
        if self.ui_controls["scan_camera_btn"]:
            self.ui_controls["scan_camera_btn"].clicked.connect(self._on_scan_camera)

        # 
        if self.ui_controls["start_preview_btn"]:
            self.ui_controls["start_preview_btn"].clicked.connect(self._start_preview)

        if self.ui_controls["stop_preview_btn"]:
            self.ui_controls["stop_preview_btn"].clicked.connect(self._stop_preview)

    def _load_config_values(self):
        """
        deconfiguraçãoarquivoCarregandoValorparaUI.
        """
        try:
            # 
            camera_config = self.config_manager.get_config("CAMERA", {})
            self._set_spin_value(
                "camera_index_spin", camera_config.get("camera_index", 0)
            )
            self._set_spin_value(
                "frame_width_spin", camera_config.get("frame_width", 640)
            )
            self._set_spin_value(
                "frame_height_spin", camera_config.get("frame_height", 480)
            )
            self._set_spin_value("fps_spin", camera_config.get("fps", 30))
            self._set_text_value(
                "local_vl_url_edit", camera_config.get("Local_VL_url", "")
            )
            self._set_text_value("vl_api_key_edit", camera_config.get("VLapi_key", ""))
            self._set_text_value("models_edit", camera_config.get("models", ""))

        except Exception as e:
            self.logger.error(f"ValorFalha: {e}", exc_info=True)

    def _set_text_value(self, control_name: str, value: str):
        """
        ConfigurandodeValor.
        """
        control = self.ui_controls.get(control_name)
        if control and hasattr(control, "setText"):
            control.setText(str(value) if value is not None else "")

    def _set_spin_value(self, control_name: str, value: int):
        """
        ConfigurandodeValor.
        """
        control = self.ui_controls.get(control_name)
        if control and hasattr(control, "setValue"):
            control.setValue(int(value) if value is not None else 0)

    def _get_text_value(self, control_name: str) -> str:
        """
        deValor.
        """
        control = self.ui_controls.get(control_name)
        if control and hasattr(control, "text"):
            return control.text().strip()
        return ""

    def _get_spin_value(self, control_name: str) -> int:
        """
        deValor.
        """
        control = self.ui_controls.get(control_name)
        if control and hasattr(control, "value"):
            return control.value()
        return 0

    def _on_scan_camera(self):
        """
        .
        """
        try:
            # Parar（）
            was_previewing = self.is_previewing
            if self.is_previewing:
                self._stop_preview()

            # 
            available_cameras = self._scan_available_cameras()

            if not available_cameras:
                QMessageBox.information(
                    self,
                    "",
                    "NãoparadeDispositivo。\n"
                    "Nenhuma câmera conectada",
                )
                return

            # Se，Usando
            if len(available_cameras) == 1:
                camera = available_cameras[0]
                self._apply_camera_settings(camera)
                QMessageBox.information(
                    self,
                    "ConfigurandoConcluído",
                    f"para1，JáAutomáticoConfigurando:\n"
                    f": {camera[0]}, : {camera[1]}x{camera[2]}",
                )
            else:
                # Selecionando
                selected_camera = self._show_camera_selection_dialog(available_cameras)
                if selected_camera:
                    self._apply_camera_settings(selected_camera)
                    QMessageBox.information(
                        self,
                        "ConfigurandoConcluído",
                        f"JáConfigurando:\n"
                        f": {selected_camera[0]}, : {selected_camera[1]}x{selected_camera[2]}",
                    )

            # RestaurandoEstado
            if was_previewing:
                QTimer.singleShot(500, self._start_preview)

        except Exception as e:
            self.logger.error(f"Falha: {e}", exc_info=True)
            QMessageBox.warning(self, "Erro", f"Erro: {str(e)}")

    def _scan_available_cameras(self, max_devices: int = 5):
        """
        dedispositivo.
        """
        available_cameras = []

        try:
            for i in range(max_devices):
                try:
                    # TentativaAbrindo
                    cap = cv2.VideoCapture(i)

                    if cap.isOpened():
                        # TentativaQuadros  Validando
                        ret, _ = cap.read()
                        if ret:
                            # 
                            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                            available_cameras.append((i, width, height))

                            self.logger.info(f"para {i}: {width}x{height}")

                    cap.release()

                except Exception as e:
                    self.logger.debug(f" {i} : {e}")
                    continue

        except Exception as e:
            self.logger.error(f": {e}", exc_info=True)

        return available_cameras

    def _show_camera_selection_dialog(self, available_cameras):
        """
        Selecionando.
        """
        try:
            dialog = QDialog(self)
            dialog.setWindowTitle("Selecionando")
            dialog.setFixedSize(400, 300)

            layout = QVBoxLayout(dialog)

            # 
            title_label = QLabel(
                f"para {len(available_cameras)} ，Selecionando:"
            )
            title_label.setStyleSheet("font-weight: bold; margin-bottom: 10px;")
            layout.addWidget(title_label)

            # 
            camera_list = QListWidget()
            for idx, width, height in available_cameras:
                item_text = f" {idx}:  {width}x{height}"
                item = QListWidgetItem(item_text)
                item.setData(Qt.UserRole, (idx, width, height))  # Dados
                camera_list.addItem(item)

            # Selecionando
            if camera_list.count() > 0:
                camera_list.setCurrentRow(0)

            layout.addWidget(camera_list)

            # 
            button_box = QDialogButtonBox(
                QDialogButtonBox.Ok | QDialogButtonBox.Cancel, Qt.Horizontal
            )
            button_box.accepted.connect(dialog.accept)
            button_box.rejected.connect(dialog.reject)
            layout.addWidget(button_box)

            # 
            if dialog.exec_() == QDialog.Accepted:
                current_item = camera_list.currentItem()
                if current_item:
                    return current_item.data(Qt.UserRole)

            return None

        except Exception as e:
            self.logger.error(f"SelecionandoFalha: {e}", exc_info=True)
            return None

    def _apply_camera_settings(self, camera_data):
        """
        aplicaçãoConfigurando.
        """
        try:
            idx, width, height = camera_data
            self._set_spin_value("camera_index_spin", idx)
            self._set_spin_value("frame_width_spin", width)
            self._set_spin_value("frame_height_spin", height)

            self.logger.info(f"AppConfigurando: {idx}, {width}x{height}")

        except Exception as e:
            self.logger.error(f"AppConfigurandoFalha: {e}", exc_info=True)

    def get_config_data(self) -> dict:
        """
        configuraçãodados.
        """
        config_data = {}

        try:
            # 
            camera_config = {}
            camera_config["camera_index"] = self._get_spin_value("camera_index_spin")
            camera_config["frame_width"] = self._get_spin_value("frame_width_spin")
            camera_config["frame_height"] = self._get_spin_value("frame_height_spin")
            camera_config["fps"] = self._get_spin_value("fps_spin")

            local_vl_url = self._get_text_value("local_vl_url_edit")
            if local_vl_url:
                camera_config["Local_VL_url"] = local_vl_url

            vl_api_key = self._get_text_value("vl_api_key_edit")
            if vl_api_key:
                camera_config["VLapi_key"] = vl_api_key

            models = self._get_text_value("models_edit")
            if models:
                camera_config["models"] = models

            # de
            existing_camera = self.config_manager.get_config("CAMERA", {})
            existing_camera.update(camera_config)
            config_data["CAMERA"] = existing_camera

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
            camera_config = default_config["CAMERA"]
            self._set_spin_value("camera_index_spin", camera_config["camera_index"])
            self._set_spin_value("frame_width_spin", camera_config["frame_width"])
            self._set_spin_value("frame_height_spin", camera_config["frame_height"])
            self._set_spin_value("fps_spin", camera_config["fps"])
            self._set_text_value("local_vl_url_edit", camera_config["Local_VL_url"])
            self._set_text_value("vl_api_key_edit", camera_config["VLapi_key"])
            self._set_text_value("models_edit", camera_config["models"])

            self.logger.info("JáparaValor")

        except Exception as e:
            self.logger.error(f"Falha: {e}", exc_info=True)

    def _on_camera_index_changed(self):
        """
        ConversãoProcessando.
        """
        try:
            # Configurando
            self.settings_changed.emit()

            # SeEm，
            if self.is_previewing:
                self._restart_preview()

        except Exception as e:
            self.logger.error(f"ProcessandoConversãoFalha: {e}", exc_info=True)

    def _start_preview(self):
        """
        Iniciando.
        """
        try:
            if self.is_previewing:
                self._stop_preview()

            # Parâmetro
            camera_index = self._get_spin_value("camera_index_spin")
            width = self._get_spin_value("frame_width_spin")
            height = self._get_spin_value("frame_height_spin")
            fps = self._get_spin_value("fps_spin")

            # Inicializando
            self.camera = cv2.VideoCapture(camera_index)

            if not self.camera.isOpened():
                self._show_preview_error(f"Incapaz deAbrindo {camera_index}")
                return

            # ConfigurandoParâmetro
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            self.camera.set(cv2.CAP_PROP_FPS, fps)

            # Validando
            ret, _ = self.camera.read()
            if not ret:
                self._show_preview_error("Incapaz de")
                self.camera.release()
                self.camera = None
                return

            # Começar
            self.is_previewing = True
            self.preview_timer.start(max(1, int(1000 / fps)))

            # Estado
            self._update_preview_buttons(True)

            self.logger.info(f"Começar {camera_index}")

        except Exception as e:
            self.logger.error(f"IniciandoFalha: {e}", exc_info=True)
            self._show_preview_error(f"IniciandoErro: {str(e)}")
            self._cleanup_camera()

    def _stop_preview(self):
        """
        Parar.
        """
        try:
            if not self.is_previewing:
                return

            # PararDispositivo
            self.preview_timer.stop()
            self.is_previewing = False

            # 
            self._cleanup_camera()

            # Limpando
            if self.ui_controls["preview_label"]:
                self.ui_controls["preview_label"].setText(
                    "\nComeçarPesquisar"
                )
                self.ui_controls["preview_label"].setPixmap(QPixmap())

            # Estado
            self._update_preview_buttons(False)

            self.logger.info("Parar")

        except Exception as e:
            self.logger.error(f"PararFalha: {e}", exc_info=True)

    def _restart_preview(self):
        """
        （Parâmetro）.
        """
        if self.is_previewing:
            self._stop_preview()
            # ，Fonte
            QTimer.singleShot(100, self._start_preview)

    def _update_preview_frame(self):
        """
        Quadros.
        """
        try:
            if not self.camera or not self.camera.isOpened():
                return

            ret, frame = self.camera.read()
            if not ret:
                self._show_preview_error("Incapaz de")
                return

            #  BGR -> RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Quadros
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w

            # paraQImage
            qt_image = QImage(
                rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888
            )

            # paraTamanho
            if self.ui_controls["preview_label"]:
                label_size = self.ui_controls["preview_label"].size()
                scaled_image = qt_image.scaled(
                    label_size, Qt.KeepAspectRatio, Qt.SmoothTransformation
                )

                # paraQPixmap
                pixmap = QPixmap.fromImage(scaled_image)
                self.ui_controls["preview_label"].setPixmap(pixmap)

        except Exception as e:
            self.logger.error(f"QuadrosFalha: {e}", exc_info=True)
            self._show_preview_error(f": {str(e)}")

    def _update_preview_buttons(self, is_previewing: bool):
        """
        estado.
        """
        try:
            if self.ui_controls["start_preview_btn"]:
                self.ui_controls["start_preview_btn"].setEnabled(not is_previewing)

            if self.ui_controls["stop_preview_btn"]:
                self.ui_controls["stop_preview_btn"].setEnabled(is_previewing)

        except Exception as e:
            self.logger.error(f"EstadoFalha: {e}", exc_info=True)

    def _show_preview_error(self, message: str):
        """
        EmerroInformação.
        """
        try:
            if self.ui_controls["preview_label"]:
                self.ui_controls["preview_label"].setText(f"Erro:\n{message}")
                self.ui_controls["preview_label"].setPixmap(QPixmap())
        except Exception as e:
            self.logger.error(f"ErroFalha: {e}", exc_info=True)

    def _cleanup_camera(self):
        """
        Fonte.
        """
        try:
            if self.camera:
                self.camera.release()
                self.camera = None
        except Exception as e:
            self.logger.error(f"FonteFalha: {e}", exc_info=True)

    def closeEvent(self, event):
        """
        FechandoFonte.
        """
        try:
            self._stop_preview()
        except Exception as e:
            self.logger.error(f"FechandoFalha: {e}", exc_info=True)
        super().closeEvent(event)
