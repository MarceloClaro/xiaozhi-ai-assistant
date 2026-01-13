import threading
import time
from pathlib import Path

import numpy as np
import sounddevice as sd
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import (
    QComboBox,
    QLabel,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QWidget,
)

from src.utils.config_manager import ConfigManager
from src.utils.logging_config import get_logger


class AudioWidget(QWidget):
    """
    áudiodispositivoConfigurando.
    """

    # 
    settings_changed = pyqtSignal()
    status_message = pyqtSignal(str)
    reset_input_ui = pyqtSignal()
    reset_output_ui = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = get_logger(__name__)
        self.config_manager = ConfigManager.get_instance()

        # UI
        self.ui_controls = {}

        # DispositivoDados
        self.input_devices = []
        self.output_devices = []

        # Estado
        self.testing_input = False
        self.testing_output = False

        # InicializandoUI
        self._setup_ui()
        self._connect_events()
        self._scan_devices()
        self._load_config_values()

        # ConexãoUI
        try:
            self.status_message.connect(self._on_status_message)
            self.reset_input_ui.connect(self._reset_input_test_ui)
            self.reset_output_ui.connect(self._reset_output_test_ui)
        except Exception:
            pass

    def _setup_ui(self):
        """
        ConfigurandoUI.
        """
        try:
            from PyQt5 import uic

            ui_path = Path(__file__).parent / "audio_widget.ui"
            uic.loadUi(str(ui_path), self)

            # UI
            self._get_ui_controls()

        except Exception as e:
            self.logger.error(f"ConfigurandoÁudioUIFalha: {e}", exc_info=True)
            raise

    def _get_ui_controls(self):
        """
        UI.
        """
        self.ui_controls.update(
            {
                "input_device_combo": self.findChild(QComboBox, "input_device_combo"),
                "output_device_combo": self.findChild(QComboBox, "output_device_combo"),
                "input_info_label": self.findChild(QLabel, "input_info_label"),
                "output_info_label": self.findChild(QLabel, "output_info_label"),
                "test_input_btn": self.findChild(QPushButton, "test_input_btn"),
                "test_output_btn": self.findChild(QPushButton, "test_output_btn"),
                "scan_devices_btn": self.findChild(QPushButton, "scan_devices_btn"),
                "status_text": self.findChild(QTextEdit, "status_text"),
            }
        )

    def _connect_events(self):
        """
        ConectandoProcessando.
        """
        # DispositivoSelecionando
        if self.ui_controls["input_device_combo"]:
            self.ui_controls["input_device_combo"].currentTextChanged.connect(
                self._on_input_device_changed
            )

        if self.ui_controls["output_device_combo"]:
            self.ui_controls["output_device_combo"].currentTextChanged.connect(
                self._on_output_device_changed
            )

        # 
        if self.ui_controls["test_input_btn"]:
            self.ui_controls["test_input_btn"].clicked.connect(self._test_input_device)

        if self.ui_controls["test_output_btn"]:
            self.ui_controls["test_output_btn"].clicked.connect(
                self._test_output_device
            )

        if self.ui_controls["scan_devices_btn"]:
            self.ui_controls["scan_devices_btn"].clicked.connect(self._scan_devices)

    def _on_input_device_changed(self):
        """
        Entradadispositivo.
        """
        self.settings_changed.emit()
        self._update_device_info()

    def _on_output_device_changed(self):
        """
        Saídadispositivo.
        """
        self.settings_changed.emit()
        self._update_device_info()

    def _update_device_info(self):
        """
        dispositivoInformação.
        """
        try:
            # EntradaDispositivoInformação
            input_device_id = self.ui_controls["input_device_combo"].currentData()
            if input_device_id is not None:
                input_device = next(
                    (d for d in self.input_devices if d["id"] == input_device_id), None
                )
                if input_device:
                    info_text = f"Taxa de amostragem: {int(input_device['sample_rate'])}Hz, : {input_device['channels']}"
                    self.ui_controls["input_info_label"].setText(info_text)
                else:
                    self.ui_controls["input_info_label"].setText(
                        "DispositivoInformaçãoFalha"
                    )
            else:
                self.ui_controls["input_info_label"].setText(
                    "NãoSelecionandoDispositivo"
                )

            # SaídaDispositivoInformação
            output_device_id = self.ui_controls["output_device_combo"].currentData()
            if output_device_id is not None:
                output_device = next(
                    (d for d in self.output_devices if d["id"] == output_device_id),
                    None,
                )
                if output_device:
                    info_text = f"Taxa de amostragem: {int(output_device['sample_rate'])}Hz, : {output_device['channels']}"
                    self.ui_controls["output_info_label"].setText(info_text)
                else:
                    self.ui_controls["output_info_label"].setText(
                        "DispositivoInformaçãoFalha"
                    )
            else:
                self.ui_controls["output_info_label"].setText(
                    "NãoSelecionandoDispositivo"
                )

        except Exception as e:
            self.logger.error(f"DispositivoInformaçãoFalha: {e}", exc_info=True)

    def _scan_devices(self):
        """
        áudiodispositivo.
        """
        try:
            self._append_status("EmÁudioDispositivo...")

            # LimpandoDispositivo
            self.input_devices.clear()
            self.output_devices.clear()

            # Dispositivo
            default_input = sd.default.device[0] if sd.default.device else None
            default_output = sd.default.device[1] if sd.default.device else None

            # Dispositivo
            devices = sd.query_devices()
            for i, dev_info in enumerate(devices):
                device_name = dev_info["name"]

                # EntradaDispositivo
                if dev_info["max_input_channels"] > 0:
                    default_mark = " ()" if i == default_input else ""
                    self.input_devices.append(
                        {
                            "id": i,
                            "name": device_name + default_mark,
                            "raw_name": device_name,
                            "channels": dev_info["max_input_channels"],
                            "sample_rate": dev_info["default_samplerate"],
                        }
                    )

                # SaídaDispositivo
                if dev_info["max_output_channels"] > 0:
                    default_mark = " ()" if i == default_output else ""
                    self.output_devices.append(
                        {
                            "id": i,
                            "name": device_name + default_mark,
                            "raw_name": device_name,
                            "channels": dev_info["max_output_channels"],
                            "sample_rate": dev_info["default_samplerate"],
                        }
                    )

            # 
            self._update_device_combos()

            # AutomáticoSelecionandoDispositivo
            self._select_default_devices()

            self._append_status(
                f"Concluído: Encontrado {len(self.input_devices)} EntradaDispositivo, {len(self.output_devices)} SaídaDispositivo"
            )

        except Exception as e:
            self.logger.error(f"ÁudioDispositivoFalha: {e}", exc_info=True)
            self._append_status(f"DispositivoFalha: {str(e)}")

    def _update_device_combos(self):
        """
        dispositivo.
        """
        try:
            # Selecionando
            current_input = self.ui_controls["input_device_combo"].currentData()
            current_output = self.ui_controls["output_device_combo"].currentData()

            # Limpando  NovamenteEntradaDispositivo
            self.ui_controls["input_device_combo"].clear()
            for device in self.input_devices:
                self.ui_controls["input_device_combo"].addItem(
                    device["name"], device["id"]
                )

            # Limpando  NovamenteSaídaDispositivo
            self.ui_controls["output_device_combo"].clear()
            for device in self.output_devices:
                self.ui_controls["output_device_combo"].addItem(
                    device["name"], device["id"]
                )

            # TentativaRestaurandodeSelecionando
            if current_input is not None:
                index = self.ui_controls["input_device_combo"].findData(current_input)
                if index >= 0:
                    self.ui_controls["input_device_combo"].setCurrentIndex(index)

            if current_output is not None:
                index = self.ui_controls["output_device_combo"].findData(current_output)
                if index >= 0:
                    self.ui_controls["output_device_combo"].setCurrentIndex(index)

        except Exception as e:
            self.logger.error(f"DispositivoFalha: {e}", exc_info=True)

    def _select_default_devices(self):
        """
        AutomáticoSelecionandodispositivo（comaudio_codec.pyde）。
        """
        try:
            # SelecionandoEmdeDispositivo，SeNenhumentãoSelecionandoDispositivo
            config_input_id = self.config_manager.get_config(
                "AUDIO_DEVICES.input_device_id"
            )
            config_output_id = self.config_manager.get_config(
                "AUDIO_DEVICES.output_device_id"
            )

            # SelecionandoEntradaDispositivo
            if config_input_id is not None:
                # UsandoEmdeDispositivo
                index = self.ui_controls["input_device_combo"].findData(config_input_id)
                if index >= 0:
                    self.ui_controls["input_device_combo"].setCurrentIndex(index)
            else:
                # AutomáticoSelecionandoEntradaDispositivo（""de）
                for i in range(self.ui_controls["input_device_combo"].count()):
                    if "" in self.ui_controls["input_device_combo"].itemText(i):
                        self.ui_controls["input_device_combo"].setCurrentIndex(i)
                        break

            # SelecionandoSaídaDispositivo
            if config_output_id is not None:
                # UsandoEmdeDispositivo
                index = self.ui_controls["output_device_combo"].findData(
                    config_output_id
                )
                if index >= 0:
                    self.ui_controls["output_device_combo"].setCurrentIndex(index)
            else:
                # AutomáticoSelecionandoSaídaDispositivo（""de）
                for i in range(self.ui_controls["output_device_combo"].count()):
                    if "" in self.ui_controls["output_device_combo"].itemText(i):
                        self.ui_controls["output_device_combo"].setCurrentIndex(i)
                        break

            # DispositivoInformação
            self._update_device_info()

        except Exception as e:
            self.logger.error(f"SelecionandoDispositivoFalha: {e}", exc_info=True)

    def _test_input_device(self):
        """
        Entradadispositivo.
        """
        if self.testing_input:
            return

        try:
            device_id = self.ui_controls["input_device_combo"].currentData()
            if device_id is None:
                QMessageBox.warning(self, "", "SelecionandoEntradaDispositivo")
                return

            self.testing_input = True
            self.ui_controls["test_input_btn"].setEnabled(False)
            self.ui_controls["test_input_btn"].setText("Em...")

            # EmEm
            test_thread = threading.Thread(
                target=self._do_input_test, args=(device_id,)
            )
            test_thread.daemon = True
            test_thread.start()

        except Exception as e:
            self.logger.error(f"EntradaDispositivoFalha: {e}", exc_info=True)
            self._append_status(f"EntradaDispositivoFalha: {str(e)}")
            self._reset_input_test_ui()

    def _do_input_test(self, device_id):
        """
        Entradadispositivo.
        """
        try:
            # DispositivoInformaçãoeTaxa de amostragem
            input_device = next(
                (d for d in self.input_devices if d["id"] == device_id), None
            )
            if not input_device:
                self._append_status_threadsafe("Erro: Incapaz deDispositivoInformação")
                return

            sample_rate = int(input_device["sample_rate"])
            duration = 3  # 3Segundos

            self._append_status_threadsafe(
                f"Começar (Dispositivo: {device_id}, Taxa de amostragem: {sample_rate}Hz)"
            )
            self._append_status_threadsafe("，: 1、2、3...")

            # 
            for i in range(3, 0, -1):
                self._append_status_threadsafe(f"{i}Segundos  Começar...")
                time.sleep(1)

            self._append_status_threadsafe("Em，... (3Segundos)")

            # 
            recording = sd.rec(
                int(duration * sample_rate),
                samplerate=sample_rate,
                channels=1,
                device=device_id,
                dtype=np.float32,
            )
            sd.wait()

            self._append_status_threadsafe("Concluído，Em...")

            # 
            max_amplitude = np.max(np.abs(recording))
            rms = np.sqrt(np.mean(recording**2))

            # 
            frame_length = int(0.1 * sample_rate)  # 100msQuadros
            frames = []
            for i in range(0, len(recording) - frame_length, frame_length):
                frame_rms = np.sqrt(np.mean(recording[i : i + frame_length] ** 2))
                frames.append(frame_rms)

            active_frames = sum(1 for f in frames if f > 0.01)  # Quadros
            activity_ratio = active_frames / len(frames) if frames else 0

            # 
            if max_amplitude < 0.001:
                self._append_status_threadsafe("[Falha] NãoparaÁudio")
                self._append_status_threadsafe(
                    "Pesquisar: 1) Conexão 2)  3) "
                )
            elif max_amplitude > 0.8:
                self._append_status_threadsafe("[Aviso] Áudio")
                self._append_status_threadsafe("ouConfigurando")
            elif activity_ratio < 0.1:
                self._append_status_threadsafe("[Aviso] paraÁudio")
                self._append_status_threadsafe(
                    "，ouPesquisar"
                )
            else:
                self._append_status_threadsafe("[Sucesso] Através de")
                self._append_status_threadsafe(
                    f"Dados: Máximo={max_amplitude:.1%}, ={rms:.1%}, ={activity_ratio:.1%}"
                )
                self._append_status_threadsafe("")

        except Exception as e:
            self.logger.error(f"Falha: {e}", exc_info=True)
            self._append_status_threadsafe(f"[Erro] Falha: {str(e)}")
            if "Permission denied" in str(e) or "access" in str(e).lower():
                self._append_status_threadsafe(
                    "，PesquisarConfigurando"
                )
        finally:
            # UIEstado（）
            self._reset_input_ui_threadsafe()

    def _test_output_device(self):
        """
        Saídadispositivo.
        """
        if self.testing_output:
            return

        try:
            device_id = self.ui_controls["output_device_combo"].currentData()
            if device_id is None:
                QMessageBox.warning(self, "", "SelecionandoSaídaDispositivo")
                return

            self.testing_output = True
            self.ui_controls["test_output_btn"].setEnabled(False)
            self.ui_controls["test_output_btn"].setText("ReproduçãoEm...")

            # EmEm
            test_thread = threading.Thread(
                target=self._do_output_test, args=(device_id,)
            )
            test_thread.daemon = True
            test_thread.start()

        except Exception as e:
            self.logger.error(f"SaídaDispositivoFalha: {e}", exc_info=True)
            self._append_status(f"SaídaDispositivoFalha: {str(e)}")
            self._reset_output_test_ui()

    def _do_output_test(self, device_id):
        """
        Saídadispositivo.
        """
        try:
            # DispositivoInformaçãoeTaxa de amostragem
            output_device = next(
                (d for d in self.output_devices if d["id"] == device_id), None
            )
            if not output_device:
                self._append_status_threadsafe("Erro: Incapaz deDispositivoInformação")
                return

            sample_rate = int(output_device["sample_rate"])
            duration = 2.0  # Reprodução
            frequency = 440  # 440Hz A

            self._append_status_threadsafe(
                f"ComeçarReprodução (Dispositivo: {device_id}, Taxa de amostragem: {sample_rate}Hz)"
            )
            self._append_status_threadsafe(
                "/Dispositivo，Reprodução..."
            )

            # 
            for i in range(3, 0, -1):
                self._append_status_threadsafe(f"{i}Segundos  ComeçarReprodução...")
                time.sleep(1)

            self._append_status_threadsafe(
                f"EmReprodução {frequency}Hz  ({duration}Segundos)..."
            )

            # Áudio ()
            t = np.linspace(0, duration, int(sample_rate * duration))
            # ，
            fade_samples = int(0.1 * sample_rate)  # 0.1Segundos
            audio = 0.3 * np.sin(2 * np.pi * frequency * t)

            # App
            audio[:fade_samples] *= np.linspace(0, 1, fade_samples)
            audio[-fade_samples:] *= np.linspace(1, 0, fade_samples)

            # ReproduçãoÁudio
            sd.play(audio, samplerate=sample_rate, device=device_id)
            sd.wait()

            self._append_status_threadsafe("ReproduçãoConcluído")
            self._append_status_threadsafe(
                ": Se  parade，Dispositivo/"
            )
            self._append_status_threadsafe(
                "Separa，PesquisarConfigurandoouSelecionandoSaídaDispositivo"
            )

        except Exception as e:
            self.logger.error(f"ReproduçãoFalha: {e}", exc_info=True)
            self._append_status_threadsafe(f"[Erro] ReproduçãoFalha: {str(e)}")
        finally:
            # UIEstado（）
            self._reset_output_ui_threadsafe()

    def _reset_input_test_ui(self):
        """
        EntradaUIestado.
        """
        self.testing_input = False
        self.ui_controls["test_input_btn"].setEnabled(True)
        self.ui_controls["test_input_btn"].setText("")

    def _reset_input_ui_threadsafe(self):
        try:
            self.reset_input_ui.emit()
        except Exception as e:
            self.logger.error(f"threadEntradaUIFalha: {e}")

    def _reset_output_test_ui(self):
        """
        SaídaUIestado.
        """
        self.testing_output = False
        self.ui_controls["test_output_btn"].setEnabled(True)
        self.ui_controls["test_output_btn"].setText("Reprodução")

    def _reset_output_ui_threadsafe(self):
        try:
            self.reset_output_ui.emit()
        except Exception as e:
            self.logger.error(f"threadSaídaUIFalha: {e}")

    def _append_status(self, message):
        """
        estadoInformação.
        """
        try:
            if self.ui_controls["status_text"]:
                current_time = time.strftime("%H:%M:%S")
                formatted_message = f"[{current_time}] {message}"
                self.ui_controls["status_text"].append(formatted_message)
                # para
                self.ui_controls["status_text"].verticalScrollBar().setValue(
                    self.ui_controls["status_text"].verticalScrollBar().maximum()
                )
        except Exception as e:
            self.logger.error(f"EstadoInformaçãoFalha: {e}", exc_info=True)

    def _append_status_threadsafe(self, message):
        """
        estadopara QTextEdit（Através de）。
        """
        try:
            if not self.ui_controls.get("status_text"):
                return
            current_time = time.strftime("%H:%M:%S")
            formatted_message = f"[{current_time}] {message}"
            self.status_message.emit(formatted_message)
        except Exception as e:
            self.logger.error(f"EstadoFalha: {e}", exc_info=True)

    def _on_status_message(self, formatted_message: str):
        try:
            if not self.ui_controls.get("status_text"):
                return
            self.ui_controls["status_text"].append(formatted_message)
            # para
            self.ui_controls["status_text"].verticalScrollBar().setValue(
                self.ui_controls["status_text"].verticalScrollBar().maximum()
            )
        except Exception as e:
            self.logger.error(f"EstadoFalha: {e}")

    def _load_config_values(self):
        """
        deconfiguraçãoarquivoCarregandoValorparaUI.
        """
        try:
            # ÁudioDispositivo
            audio_config = self.config_manager.get_config("AUDIO_DEVICES", {})

            # ConfigurandoEntradaDispositivo
            input_device_id = audio_config.get("input_device_id")
            if input_device_id is not None:
                index = self.ui_controls["input_device_combo"].findData(input_device_id)
                if index >= 0:
                    self.ui_controls["input_device_combo"].setCurrentIndex(index)

            # ConfigurandoSaídaDispositivo
            output_device_id = audio_config.get("output_device_id")
            if output_device_id is not None:
                index = self.ui_controls["output_device_combo"].findData(
                    output_device_id
                )
                if index >= 0:
                    self.ui_controls["output_device_combo"].setCurrentIndex(index)

            # DispositivoInformaçãoEmDispositivoSelecionandoAutomático，Configurando

        except Exception as e:
            self.logger.error(f"ÁudioDispositivoValorFalha: {e}", exc_info=True)

    def get_config_data(self) -> dict:
        """
        configuraçãodados.
        """
        config_data = {}

        try:
            audio_config = {}

            # EntradaDispositivoConfiguração
            input_device_id = self.ui_controls["input_device_combo"].currentData()
            if input_device_id is not None:
                audio_config["input_device_id"] = input_device_id
                audio_config["input_device_name"] = self.ui_controls[
                    "input_device_combo"
                ].currentText()

            # SaídaDispositivoConfiguração
            output_device_id = self.ui_controls["output_device_combo"].currentData()
            if output_device_id is not None:
                audio_config["output_device_id"] = output_device_id
                audio_config["output_device_name"] = self.ui_controls[
                    "output_device_combo"
                ].currentText()

            # DispositivodeTaxa de amostragemeCanaisInformação  DispositivoAutomático，NãoConfiguração
            # DispositivodeTaxa de amostragemeCanaisUsando
            input_device = next(
                (d for d in self.input_devices if d["id"] == input_device_id), None
            )
            if input_device:
                audio_config["input_sample_rate"] = int(input_device["sample_rate"])
                audio_config["input_channels"] = min(input_device["channels"], 8)

            output_device = next(
                (d for d in self.output_devices if d["id"] == output_device_id), None
            )
            if output_device:
                audio_config["output_sample_rate"] = int(output_device["sample_rate"])
                audio_config["output_channels"] = min(output_device["channels"], 8)

            if audio_config:
                config_data["AUDIO_DEVICES"] = audio_config

        except Exception as e:
            self.logger.error(f"ÁudioDispositivoDadosFalha: {e}", exc_info=True)

        return config_data

    def reset_to_defaults(self):
        """
        paraValor.
        """
        try:
            # NovamenteDispositivo
            self._scan_devices()

            # DispositivoTaxa de amostragemInformaçãoAutomático，Configurando

            # LimpandoEstado
            if self.ui_controls["status_text"]:
                self.ui_controls["status_text"].clear()

            self._append_status("JáparaConfigurando")
            self.logger.info("ÁudioDispositivoJáparaValor")

        except Exception as e:
            self.logger.error(f"ÁudioDispositivoFalha: {e}", exc_info=True)
