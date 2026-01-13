# -*- coding: utf-8 -*-
"""
Janela - PyQtJanelade
SuportadoOperaçãoeqasync
"""

import asyncio
from typing import Optional

from PyQt5.QtCore import QTimer, pyqtSignal
from PyQt5.QtWidgets import QMainWindow, QWidget

from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class BaseWindow(QMainWindow):
    """
    Janelade，Suportado.
    """

    # 
    window_closed = pyqtSignal()
    status_updated = pyqtSignal(str)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.logger = get_logger(self.__class__.__name__)

        # 
        self._tasks = set()
        self._shutdown_event = asyncio.Event()

        # DispositivoUI（comOperação）
        self._update_timer = QTimer()
        self._update_timer.timeout.connect(self._on_timer_update)

        # InicializandoUI
        self._setup_ui()
        self._setup_connections()
        self._setup_styles()

        self.logger.debug(f"{self.__class__.__name__} Inicialização concluída")

    def _setup_ui(self):
        """ConfigurandoUI - """

    def _setup_connections(self):
        """ConfigurandoConectando - """

    def _setup_styles(self):
        """Configurando - """

    def _on_timer_update(self):
        """Dispositivo - """

    def start_update_timer(self, interval_ms: int = 1000):
        """
        Iniciando.
        """
        self._update_timer.start(interval_ms)
        self.logger.debug(f"Iniciando，: {interval_ms}ms")

    def stop_update_timer(self):
        """
        Parar.
        """
        self._update_timer.stop()
        self.logger.debug("Parar")

    def create_task(self, coro, name: str = None):
        """
        Criando.
        """
        task = asyncio.create_task(coro, name=name)
        self._tasks.add(task)

        def done_callback(t):
            self._tasks.discard(t)
            if not t.cancelled() and t.exception():
                self.logger.error(f"Exceção: {t.exception()}", exc_info=True)

        task.add_done_callback(done_callback)
        return task

    async def shutdown_async(self):
        """
        FechandoJanela.
        """
        self.logger.info("ComeçarFechandoJanela")

        # ConfigurandoFechando
        self._shutdown_event.set()

        # PararDispositivo
        self.stop_update_timer()

        # 
        for task in self._tasks.copy():
            if not task.done():
                task.cancel()

        # AguardandoConcluído
        if self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)

        self.logger.info("JanelaFechandoConcluído")

    def closeEvent(self, event):
        """
        JanelaFechando.
        """
        self.logger.info("JanelaFechando")

        # ConfigurandoFechando
        self._shutdown_event.set()

        # SeJanela，
        if hasattr(self, "device_activator") and self.device_activator:
            self.device_activator.cancel_activation()
            self.logger.info("JáEnviando")

        # Fechando
        self.window_closed.emit()

        # PararDispositivo
        self.stop_update_timer()

        # （）
        for task in self._tasks.copy():
            if not task.done():
                task.cancel()

        # Fechando
        event.accept()

        self.logger.info("JanelaFechandoProcessandoConcluído")

    def update_status(self, message: str):
        """
        estadomensagem.
        """
        self.status_updated.emit(message)
        self.logger.debug(f"Estado: {message}")

    def is_shutdown_requested(self) -> bool:
        """
        PesquisarFechando.
        """
        return self._shutdown_event.is_set()
