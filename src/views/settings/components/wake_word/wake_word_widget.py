from pathlib import Path

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import (
    QCheckBox,
    QFileDialog,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QWidget,
)

from src.utils.config_manager import ConfigManager
from src.utils.logging_config import get_logger
from src.utils.resource_finder import get_project_root, resource_finder

# Banco de dados
try:
    from pypinyin import Style, lazy_pinyin

    PYPINYIN_AVAILABLE = True
except ImportError:
    PYPINYIN_AVAILABLE = False


class WakeWordWidget(QWidget):
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

        # （）
        self.initials = [
            "b",
            "p",
            "m",
            "f",
            "d",
            "t",
            "n",
            "l",
            "g",
            "k",
            "h",
            "j",
            "q",
            "x",
            "zh",
            "ch",
            "sh",
            "r",
            "z",
            "c",
            "s",
            "y",
            "w",
        ]

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

            ui_path = Path(__file__).parent / "wake_word_widget.ui"
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
                "use_wake_word_check": self.findChild(QCheckBox, "use_wake_word_check"),
                "model_path_edit": self.findChild(QLineEdit, "model_path_edit"),
                "model_path_btn": self.findChild(QPushButton, "model_path_btn"),
                "wake_words_edit": self.findChild(QTextEdit, "wake_words_edit"),
            }
        )

    def _connect_events(self):
        """
        ConectandoProcessando.
        """
        if self.ui_controls["use_wake_word_check"]:
            self.ui_controls["use_wake_word_check"].toggled.connect(
                self.settings_changed.emit
            )

        if self.ui_controls["model_path_edit"]:
            self.ui_controls["model_path_edit"].textChanged.connect(
                self.settings_changed.emit
            )

        if self.ui_controls["model_path_btn"]:
            self.ui_controls["model_path_btn"].clicked.connect(
                self._on_model_path_browse
            )

        if self.ui_controls["wake_words_edit"]:
            self.ui_controls["wake_words_edit"].textChanged.connect(
                self.settings_changed.emit
            )

    def _load_config_values(self):
        """
        deconfiguraçãoarquivoCarregandoValorparaUI.
        """
        try:
            # 
            use_wake_word = self.config_manager.get_config(
                "WAKE_WORD_OPTIONS.USE_WAKE_WORD", False
            )
            if self.ui_controls["use_wake_word_check"]:
                self.ui_controls["use_wake_word_check"].setChecked(use_wake_word)

            model_path = self.config_manager.get_config(
                "WAKE_WORD_OPTIONS.MODEL_PATH", ""
            )
            self._set_text_value("model_path_edit", model_path)

            # de keywords.txt Arquivo
            wake_words_text = self._load_keywords_from_file()
            if self.ui_controls["wake_words_edit"]:
                self.ui_controls["wake_words_edit"].setPlainText(wake_words_text)

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

    def _on_model_path_browse(self):
        """
        ModeloCaminho.
        """
        try:
            current_path = self._get_text_value("model_path_edit")
            if not current_path:
                # Usandoresource_finderPesquisarmodelsDiretório
                models_dir = resource_finder.find_models_dir()
                if models_dir:
                    current_path = str(models_dir)
                else:
                    # Se  Nãopara，UsandoDiretório  demodels
                    project_root = resource_finder.get_project_root()
                    current_path = str(project_root / "models")

            selected_path = QFileDialog.getExistingDirectory(
                self, "SelecionandoModeloDiretório", current_path
            )

            if selected_path:
                # paraCaminho（Se）
                relative_path = self._convert_to_relative_path(selected_path)
                self._set_text_value("model_path_edit", relative_path)
                self.logger.info(
                    f"JáSelecionandoModeloCaminho: {selected_path}，para: {relative_path}"
)
        except Exception as e:
            self.logger.error(f"Erro ao selecionar: {e}", exc_info=True)
            QMessageBox.warning(self, "Erro", f"Erro: {str(e)}")

    def _convert_to_relative_path(self, model_path: str) -> str:
        """
        CaminhoparaDiretóriodeCaminho（SeEm）.
        """
        try:
            import os

            # Diretório
            project_root = get_project_root()

            # PesquisarEm（EmWindows）
            if os.name == "nt":  # Windows
                model_path_drive = os.path.splitdrive(model_path)[0]
                project_root_drive = os.path.splitdrive(str(project_root))[0]

                # SeEm，Caminho
                if model_path_drive.lower() == project_root_drive.lower():
                    relative_path = os.path.relpath(model_path, project_root)
                    return relative_path
                else:
                    # NãoEm，UsandoCaminho
                    return model_path
            else:
                # Windows，Caminho
                try:
                    relative_path = os.path.relpath(model_path, project_root)
                    # CaminhoNão".."+os.sepUsandoCaminho
                    if not relative_path.startswith(
                        ".." + os.sep
                    ) and not relative_path.startswith("/"):
                        return relative_path
                    else:
                        # CaminhoPesquisar，UsandoCaminho
                        return model_path
                except ValueError:
                    # Incapaz deCaminho（Não），UsandoCaminho
                    return model_path
        except Exception as e:
            self.logger.warning(f"Caminho，UsandoOriginalCaminho: {e}")
            return model_path

    def _load_keywords_from_file(self) -> str:
        """
        de keywords.txt arquivoCarregando，Em.
        """
        try:
            # deModeloCaminho
            model_path = self.config_manager.get_config(
                "WAKE_WORD_OPTIONS.MODEL_PATH", "models"
            )

            # Usando resource_finder Pesquisar（e）
            model_dir = resource_finder.find_directory(model_path)

            if model_dir is None:
                self.logger.warning(f"ModeloDiretórioNãoExiste: {model_path}")
                return ""

            keywords_file = model_dir / "keywords.txt"

            if not keywords_file.exists():
                self.logger.warning(f"Arquivo de palavras-chave não existe: {keywords_file}")
                return ""

            keywords = []
            with open(keywords_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and "@" in line and not line.startswith("#"):
                        # @deEm
                        chinese_part = line.split("@", 1)[1].strip()
                        keywords.append(chinese_part)

            return "\n".join(keywords)

        except Exception as e:
            self.logger.error(f"Erro ao carregar arquivo: {e}")
            return ""

    def _split_pinyin(self, pinyin: str) -> list:
        """.

        : "xiǎo" -> ["x", "iǎo"]       "mǐ" -> ["m", "ǐ"]
        """
        if not pinyin:
            return []

        # ComprimentoTentativaCorrespondência（zh, ch, sh）
        for initial in sorted(self.initials, key=len, reverse=True):
            if pinyin.startswith(initial):
                final = pinyin[len(initial) :]
                if final:
                    return [initial, final]
                else:
                    return [initial]

        # Nenhum（）
        return [pinyin]

    def _chinese_to_keyword_format(self, chinese_text: str) -> str:
        """EmparakeywordFormato.

        Args:
            chinese_text: Em，""

        Returns:
            keywordFormato，"x iǎo m ǐ x iǎo m ǐ @"
        """
        if not PYPINYIN_AVAILABLE:
            self.logger.error("pypinyin Banco de dados Não，Incapaz deAutomático")
            return f"# Falha（pypinyin） - {chinese_text}"

        try:
            # para
            pinyin_list = lazy_pinyin(chinese_text, style=Style.TONE)

            # 
            split_parts = []
            for pinyin in pinyin_list:
                parts = self._split_pinyin(pinyin)
                split_parts.extend(parts)

            # 
            pinyin_str = " ".join(split_parts)
            keyword_line = f"{pinyin_str} @{chinese_text}"

            return keyword_line

        except Exception as e:
            self.logger.error(f"Falha: {e}")
            return f"# Falha - {chinese_text}"

    def _save_keywords_to_file(self, keywords_text: str):
        """
        Salvandopara keywords.txt arquivo，AutomáticoEmparaFormato.
        """
        try:
            # Pesquisarpypinyin
            if not PYPINYIN_AVAILABLE:
                QMessageBox.warning(
                    self,
                    "",
                    "Automático pypinyin Banco de dados\n\n"
                    ": pip install pypinyin",
                )
                return

            # deModeloCaminho
            model_path = self.config_manager.get_config(
                "WAKE_WORD_OPTIONS.MODEL_PATH", "models"
            )

            # Usando resource_finder Pesquisar（e）
            model_dir = resource_finder.find_directory(model_path)

            if model_dir is None:
                self.logger.error(f"ModeloDiretórioNãoExiste: {model_path}")
                QMessageBox.warning(
                    self,
                    "Erro",
                    f"ModeloDiretórioNãoExiste: {model_path}\ndeModeloCaminho。",
                )
                return

            keywords_file = model_dir / "keywords.txt"

            # ProcessandoEntradade（Em）
            lines = [line.strip() for line in keywords_text.split("\n") if line.strip()]

            processed_lines = []
            for chinese_text in lines:
                # AutomáticoparaFormato
                keyword_line = self._chinese_to_keyword_format(chinese_text)
                processed_lines.append(keyword_line)

            # Arquivo
            with open(keywords_file, "w", encoding="utf-8") as f:
                f.write("\n".join(processed_lines) + "\n")

            self.logger.info(
                f"Sucesso {len(processed_lines)} para {keywords_file}")
            QMessageBox.information(
                self,
                "Sucesso",
                f"Sucesso {len(processed_lines)} palavras-chave carregadas\n\n"
                f"Formato automático aplicado",
            )

        except Exception as e:
            self.logger.error(f"Erro ao carregar arquivo: {e}")
            QMessageBox.warning(self, "Erro", f"Falha: {str(e)}")

    def get_config_data(self) -> dict:
        """
        configuraçãodados.
        """
        config_data = {}

        try:
            # 
            if self.ui_controls["use_wake_word_check"]:
                use_wake_word = self.ui_controls["use_wake_word_check"].isChecked()
                config_data["WAKE_WORD_OPTIONS.USE_WAKE_WORD"] = use_wake_word

            model_path = self._get_text_value("model_path_edit")
            if model_path:
                # paraCaminho（Se）
                relative_path = self._convert_to_relative_path(model_path)
                config_data["WAKE_WORD_OPTIONS.MODEL_PATH"] = relative_path

        except Exception as e:
            self.logger.error(f"DadosFalha: {e}", exc_info=True)

        return config_data

    def save_keywords(self):
        """
        Salvandoparaarquivo.
        """
        if self.ui_controls["wake_words_edit"]:
            wake_words_text = self.ui_controls["wake_words_edit"].toPlainText().strip()
            self._save_keywords_to_file(wake_words_text)

    def reset_to_defaults(self):
        """
        paraValor.
        """
        try:
            # 
            default_config = ConfigManager.DEFAULT_CONFIG

            # 
            wake_word_config = default_config["WAKE_WORD_OPTIONS"]
            if self.ui_controls["use_wake_word_check"]:
                self.ui_controls["use_wake_word_check"].setChecked(
                    wake_word_config["USE_WAKE_WORD"]
                )

            self._set_text_value("model_path_edit", wake_word_config["MODEL_PATH"])

            if self.ui_controls["wake_words_edit"]:
                # Usandode
                default_keywords = self._get_default_keywords()
                self.ui_controls["wake_words_edit"].setPlainText(default_keywords)

            self.logger.info("JáparaValor")

        except Exception as e:
            self.logger.error(f"Falha: {e}", exc_info=True)

    def _get_default_keywords(self) -> str:
        """
        ，RetornoEm.
        """
        default_keywords = [
            "",
            "",
            "",
            "",
            "",
            "",
        ]
        return "\n".join(default_keywords)
