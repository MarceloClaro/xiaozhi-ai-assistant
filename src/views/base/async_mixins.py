# -*- coding: utf-8 -*-
"""
OperaçãodeMixin QtcomOperaçãode.
"""

import asyncio

from PyQt5.QtCore import QObject, pyqtSignal

from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class AsyncMixin:
    """
    OperaçãoMixin.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._async_tasks = set()
        self.logger = get_logger(self.__class__.__name__)

    def run_async(self, coro, callback=None, error_callback=None):
        """
        EmQtEm.
        """
        task = asyncio.create_task(coro)
        self._async_tasks.add(task)

        def done_callback(future):
            self._async_tasks.discard(future)
            try:
                result = future.result()
                if callback:
                    callback(result)
            except Exception as e:
                self.logger.error(f"Falha: {e}", exc_info=True)
                if error_callback:
                    error_callback(e)

        task.add_done_callback(done_callback)
        return task

    async def cleanup_async_tasks(self):
        """
        .
        """
        if self._async_tasks:
            for task in self._async_tasks.copy():
                if not task.done():
                    task.cancel()

            await asyncio.gather(*self._async_tasks, return_exceptions=True)
            self._async_tasks.clear()


class AsyncSignalEmitter(QObject):
    """
    Dispositivo.
    """

    # 
    data_ready = pyqtSignal(object)
    error_occurred = pyqtSignal(str)
    progress_updated = pyqtSignal(int)
    status_changed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.logger = get_logger(self.__class__.__name__)

    def emit_data(self, data):
        """
        dados.
        """
        self.data_ready.emit(data)

    def emit_error(self, error_message: str):
        """
        erro.
        """
        self.error_occurred.emit(error_message)

    def emit_progress(self, progress: int):
        """
        .
        """
        self.progress_updated.emit(progress)

    def emit_status(self, status: str):
        """
        estado.
        """
        self.status_changed.emit(status)
