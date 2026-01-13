# -*- coding: utf-8 -*-
"""
GUI JaneladadosModelo -  QML dados.
"""

from PyQt5.QtCore import QObject, pyqtProperty, pyqtSignal


class GuiDisplayModel(QObject):
    """
    GUI JaneladedadosModelo， Python e QML dedados.
    """

    # Conversão
    statusTextChanged = pyqtSignal()
    emotionPathChanged = pyqtSignal()
    ttsTextChanged = pyqtSignal()
    buttonTextChanged = pyqtSignal()
    modeTextChanged = pyqtSignal()
    autoModeChanged = pyqtSignal()

    # Operação
    manualButtonPressed = pyqtSignal()
    manualButtonReleased = pyqtSignal()
    autoButtonClicked = pyqtSignal()
    abortButtonClicked = pyqtSignal()
    modeButtonClicked = pyqtSignal()
    sendButtonClicked = pyqtSignal(str)  # Entradade
    settingsButtonClicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        # 
        self._status_text = "Estado: NãoConexão"
        self._emotion_path = ""  # FonteCaminho（GIF/）ou emoji Caracteres
        self._tts_text = ""
        self._button_text = "Começar"  # AutomáticoModo
        self._mode_text = ""  # Modo
        self._auto_mode = False  # AutomáticoModo
        self._is_connected = False

    # Estado
    @pyqtProperty(str, notify=statusTextChanged)
    def statusText(self):
        return self._status_text

    @statusText.setter
    def statusText(self, value):
        if self._status_text != value:
            self._status_text = value
            self.statusTextChanged.emit()

    # Caminho
    @pyqtProperty(str, notify=emotionPathChanged)
    def emotionPath(self):
        return self._emotion_path

    @emotionPath.setter
    def emotionPath(self, value):
        if self._emotion_path != value:
            self._emotion_path = value
            self.emotionPathChanged.emit()

    # TTS 
    @pyqtProperty(str, notify=ttsTextChanged)
    def ttsText(self):
        return self._tts_text

    @ttsText.setter
    def ttsText(self, value):
        if self._tts_text != value:
            self._tts_text = value
            self.ttsTextChanged.emit()

    # AutomáticoModo
    @pyqtProperty(str, notify=buttonTextChanged)
    def buttonText(self):
        return self._button_text

    @buttonText.setter
    def buttonText(self, value):
        if self._button_text != value:
            self._button_text = value
            self.buttonTextChanged.emit()

    # Modo
    @pyqtProperty(str, notify=modeTextChanged)
    def modeText(self):
        return self._mode_text

    @modeText.setter
    def modeText(self, value):
        if self._mode_text != value:
            self._mode_text = value
            self.modeTextChanged.emit()

    # AutomáticoModo
    @pyqtProperty(bool, notify=autoModeChanged)
    def autoMode(self):
        return self._auto_mode

    @autoMode.setter
    def autoMode(self, value):
        if self._auto_mode != value:
            self._auto_mode = value
            self.autoModeChanged.emit()

    # 
    def update_status(self, status: str, connected: bool):
        """
        estadoeConectandoestado.
        """
        self.statusText = f"Estado: {status}"
        self._is_connected = connected

    def update_text(self, text: str):
        """
         TTS .
        """
        self.ttsText = text

    def update_emotion(self, emotion_path: str):
        """
        Caminho.
        """
        self.emotionPath = emotion_path

    def update_button_text(self, text: str):
        """
        Automáticomodo.
        """
        self.buttonText = text

    def update_mode_text(self, text: str):
        """
        modo.
        """
        self.modeText = text

    def set_auto_mode(self, is_auto: bool):
        """
        ConfigurandoAutomáticomodo.
        """
        self.autoMode = is_auto
        if is_auto:
            self.modeText = "Automático"
        else:
            self.modeText = "Modo manual"
