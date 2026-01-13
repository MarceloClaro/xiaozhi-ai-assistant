"""
Widget para configurar modelo de IA (remoto vs. local com fallback).
"""

from typing import Optional

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QRadioButton,
    QButtonGroup,
    QCheckBox,
    QPushButton,
    QLabel,
    QComboBox,
    QSpinBox,
)

from src.utils.config_manager import ConfigManager
from src.utils.logging_config import get_logger
from src.utils.ai_model_manager import get_model_manager, AIModelType

logger = get_logger(__name__)


class AIModelWidget(QWidget):
    """Widget para configurar modelo de IA."""
    
    model_changed = pyqtSignal(str)  # Emite tipo de modelo
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = ConfigManager.get_instance()
        self.model_manager = get_model_manager()
        
        self.init_ui()
        self.load_settings()
    
    def init_ui(self):
        """Inicializa UI."""
        layout = QVBoxLayout()
        
        # Grupo: Modo de Modelo
        model_group = QGroupBox("Modo de Modelo de IA")
        model_layout = QVBoxLayout()
        
        self.model_button_group = QButtonGroup()
        
        # Opção 1: Remoto
        self.radio_remote = QRadioButton("🌐 API Remota (Padrão)")
        self.radio_remote.setToolTip(
            "Usa API remota via WebSocket\n"
            "Requer conexão com internet"
        )
        self.model_button_group.addButton(self.radio_remote, 0)
        model_layout.addWidget(self.radio_remote)
        
        # Opção 2: Local
        self.radio_local = QRadioButton("💾 Modelo Local (Deepseek 1.5B)")
        self.radio_local.setToolTip(
            "Usa modelo Deepseek local\n"
            "Não requer conexão, mas é mais lento"
        )
        self.radio_local.setEnabled(self.model_manager.local_model_available)
        self.model_button_group.addButton(self.radio_local, 1)
        model_layout.addWidget(self.radio_local)
        
        # Informação de disponibilidade
        if self.model_manager.local_model_available:
            status_text = f"✅ Encontrado: {self.model_manager.local_model_path}"
        else:
            status_text = "❌ Não encontrado"
        
        self.label_local_status = QLabel(f"Status do modelo local: {status_text}")
        self.label_local_status.setStyleSheet("color: gray; font-size: 10px;")
        model_layout.addWidget(self.label_local_status)
        
        model_group.setLayout(model_layout)
        layout.addWidget(model_group)
        
        # Grupo: Fallback automático
        fallback_group = QGroupBox("Fallback Automático")
        fallback_layout = QVBoxLayout()
        
        self.check_fallback = QCheckBox("Habilitar fallback automático")
        self.check_fallback.setToolTip(
            "Se API remota falhar, tenta modelo local automaticamente"
        )
        fallback_layout.addWidget(self.check_fallback)
        
        fallback_options_layout = QHBoxLayout()
        fallback_options_layout.addSpacing(20)
        
        # Ordem de tentativa
        self.label_order = QLabel("Tentar primeiro:")
        self.combo_order = QComboBox()
        self.combo_order.addItem("API Remota", "remote")
        self.combo_order.addItem("Modelo Local", "local")
        
        fallback_options_layout.addWidget(self.label_order)
        fallback_options_layout.addWidget(self.combo_order)
        fallback_options_layout.addStretch()
        
        fallback_layout.addLayout(fallback_options_layout)
        
        fallback_group.setLayout(fallback_layout)
        layout.addWidget(fallback_group)
        
        # Grupo: Timeouts
        timeout_group = QGroupBox("Configurações de Timeout (segundos)")
        timeout_layout = QHBoxLayout()
        
        timeout_layout.addWidget(QLabel("API Remota:"))
        self.spin_remote_timeout = QSpinBox()
        self.spin_remote_timeout.setMinimum(5)
        self.spin_remote_timeout.setMaximum(60)
        self.spin_remote_timeout.setValue(20)
        timeout_layout.addWidget(self.spin_remote_timeout)
        
        timeout_layout.addSpacing(20)
        
        timeout_layout.addWidget(QLabel("Modelo Local:"))
        self.spin_local_timeout = QSpinBox()
        self.spin_local_timeout.setMinimum(5)
        self.spin_local_timeout.setMaximum(120)
        self.spin_local_timeout.setValue(30)
        timeout_layout.addWidget(self.spin_local_timeout)
        
        timeout_layout.addStretch()
        timeout_group.setLayout(timeout_layout)
        layout.addWidget(timeout_group)
        
        # Botões de ação
        button_layout = QHBoxLayout()
        
        self.btn_test_remote = QPushButton("🧪 Testar API Remota")
        self.btn_test_remote.clicked.connect(self.test_remote)
        button_layout.addWidget(self.btn_test_remote)
        
        self.btn_test_local = QPushButton("🧪 Testar Modelo Local")
        self.btn_test_local.clicked.connect(self.test_local)
        self.btn_test_local.setEnabled(self.model_manager.local_model_available)
        button_layout.addWidget(self.btn_test_local)
        
        self.btn_save = QPushButton("💾 Salvar Configurações")
        self.btn_save.clicked.connect(self.save_settings)
        button_layout.addWidget(self.btn_save)
        
        layout.addLayout(button_layout)
        
        # Informações de status
        self.label_status = QLabel("")
        self.label_status.setStyleSheet("color: blue; font-size: 10px;")
        layout.addWidget(self.label_status)
        
        layout.addStretch()
        self.setLayout(layout)
        
        # Conexões
        self.radio_remote.toggled.connect(self.on_model_changed)
        self.radio_local.toggled.connect(self.on_model_changed)
    
    def load_settings(self):
        """Carrega configurações salvas."""
        use_local = self.config.get_config("AI_MODEL.USE_LOCAL", False)
        
        if use_local and self.model_manager.local_model_available:
            self.radio_local.setChecked(True)
        else:
            self.radio_remote.setChecked(True)
        
        fallback_enabled = self.config.get_config("AI_MODEL.FALLBACK_ENABLED", True)
        self.check_fallback.setChecked(fallback_enabled)
        
        prefer_local = self.config.get_config("AI_MODEL.PREFER_LOCAL", False)
        if prefer_local:
            self.combo_order.setCurrentIndex(1)
        else:
            self.combo_order.setCurrentIndex(0)
        
        remote_timeout = self.config.get_config("AI_MODEL.TIMEOUT_REMOTE", 20)
        self.spin_remote_timeout.setValue(remote_timeout)
        
        local_timeout = self.config.get_config("AI_MODEL.TIMEOUT_LOCAL", 30)
        self.spin_local_timeout.setValue(local_timeout)
        
        self.update_status()
    
    def on_model_changed(self, checked):
        """Chamado quando modelo é alterado."""
        if checked:
            current = self.radio_local.isChecked()
            model_type = "local" if current else "remote"
            self.model_changed.emit(model_type)
            self.update_status()
    
    def update_status(self):
        """Atualiza rótulo de status."""
        status = self.model_manager.get_status()
        current = status["current_model"]
        remote_ok = "✅" if status["remote_api_available"] else "❌"
        local_ok = "✅" if status["local_model_available"] else "❌"
        
        text = (
            f"Status: {remote_ok} API Remota | {local_ok} Modelo Local | "
            f"Atual: {current}"
        )
        self.label_status.setText(text)
    
    def test_remote(self):
        """Testa API remota."""
        logger.info("Testando API remota...")
        self.label_status.setText("⏳ Testando API remota...")
        
        # Aqui você poderia fazer um teste real
        if self.model_manager.remote_api_available:
            self.label_status.setText("✅ API remota está disponível!")
            logger.info("✅ API remota funcional")
        else:
            self.label_status.setText("❌ API remota não está disponível")
            logger.error("❌ API remota indisponível")
    
    def test_local(self):
        """Testa modelo local."""
        logger.info("Testando modelo local...")
        self.label_status.setText("⏳ Testando modelo local...")
        
        if self.model_manager.local_model_available:
            self.label_status.setText("✅ Modelo local está disponível!")
            logger.info("✅ Modelo local funcional")
        else:
            self.label_status.setText("❌ Modelo local não está disponível")
            logger.error("❌ Modelo local indisponível")
    
    def save_settings(self):
        """Salva configurações."""
        use_local = self.radio_local.isChecked()
        fallback_enabled = self.check_fallback.isChecked()
        prefer_local = self.combo_order.currentData() == "local"
        remote_timeout = self.spin_remote_timeout.value()
        local_timeout = self.spin_local_timeout.value()
        
        try:
            self.config.set_config("AI_MODEL.USE_LOCAL", use_local)
            self.config.set_config("AI_MODEL.FALLBACK_ENABLED", fallback_enabled)
            self.config.set_config("AI_MODEL.PREFER_LOCAL", prefer_local)
            self.config.set_config("AI_MODEL.TIMEOUT_REMOTE", remote_timeout)
            self.config.set_config("AI_MODEL.TIMEOUT_LOCAL", local_timeout)
            
            self.config.save_config()
            logger.info("✅ Configurações de modelo salvas")
            self.label_status.setText("✅ Configurações salvas com sucesso!")
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar: {e}")
            self.label_status.setText(f"❌ Erro ao salvar: {e}")
