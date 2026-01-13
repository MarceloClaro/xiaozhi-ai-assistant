"""Dispositivo.

deCriando、、eestadoPesquisar
"""

import asyncio
import json
from asyncio import Task
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class TimerService:
    """
    Dispositivo，.
    """

    def __init__(self):
        # UsandodeDispositivo， timer_id，Valor TimerTask 
        self._timers: Dict[int, "TimerTask"] = {}
        self._next_timer_id = 0
        # Usando _timers e _next_timer_id de，
        self._lock = asyncio.Lock()
        self.DEFAULT_DELAY = 5  # Segundos

    async def start_countdown(
        self, command: str, delay: int = None, description: str = ""
    ) -> Dict[str, Any]:
        """Iniciando.

        Args:
            command: deMCP (JSONFormatoCaracteres，nameearguments)
            delay: Tempo（Segundos），para5Segundos
            description: 

        Returns:
            Dict[str, Any]: Informaçãode
        """
        if delay is None:
            delay = self.DEFAULT_DELAY

        # ValidandoTempo
        try:
            delay = int(delay)
            if delay <= 0:
                logger.warning(
                    f"deTempo {delay} ，UsandoValor {self.DEFAULT_DELAY} Segundos")
                delay = self.DEFAULT_DELAY
        except (ValueError, TypeError):
            logger.warning(
                f"deTempo '{delay}' ，UsandoValor {self.DEFAULT_DELAY} Segundos")
            delay = self.DEFAULT_DELAY

        # ValidandoComandoFormato
        try:
            json.loads(command)
        except json.JSONDecodeError:
            logger.error(f"IniciandoFalha：ComandoFormatoErro，Incapaz deAnalisandoJSON: {command}")
            return {
                "success": False,
                "message": f"ComandoFormatoErro，Incapaz deAnalisandoJSON: {command}",
            }

        # 
        loop = asyncio.get_running_loop()

        async with self._lock:
            timer_id = self._next_timer_id
            self._next_timer_id += 1

            # 
            timer_task = TimerTask(
                timer_id=timer_id,
                command=command,
                delay=delay,
                description=description,
                service=self,
            )

            # 
            task = loop.create_task(timer_task.run())
            timer_task.task = task

            self._timers[timer_id] = timer_task

        logger.info(f"Iniciando {timer_id}，Em {delay} SegundosComando: {command}")

        return {
            "success": True,
            "message": f" {timer_id} Iniciando，Em {delay} Segundos",
            "timer_id": timer_id,
            "delay": delay,
            "command": command,
            "description": description,
            "start_time": datetime.now().isoformat(),
            "estimated_execution_time": (
                datetime.now() + timedelta(seconds=delay)
            ).isoformat(),
        }

    async def cancel_countdown(self, timer_id: int) -> Dict[str, Any]:
        """de.

        Args:
            timer_id: deDispositivoID

        Returns:
            Dict[str, Any]: 
        """
        try:
            timer_id = int(timer_id)
        except (ValueError, TypeError):
            logger.error(f"Falha：de timer_id {timer_id}")
            return {"success": False, "message": f"de timer_id: {timer_id}"}

        async with self._lock:
            if timer_id in self._timers:
                timer_task = self._timers.pop(timer_id)
                if timer_task.task:
                    timer_task.task.cancel()

                logger.info(f" {timer_id} JáSucesso")
                return {
                    "success": True,
                    "message": f" {timer_id} Já",
                    "timer_id": timer_id,
                    "cancelled_at": datetime.now().isoformat(),
                }
            else:
                logger.warning(f"TentativaNãoExisteouJáConcluídode {timer_id}")
                return {
                    "success": False,
                    "message": f"NãoparaIDpara {timer_id} de",
                    "timer_id": timer_id,
                }

    async def get_active_timers(self) -> Dict[str, Any]:
        """deestado.

        Returns:
            Dict[str, Any]: Dispositivo
        """
        async with self._lock:
            active_timers = []
            current_time = datetime.now()

            for timer_id, timer_task in self._timers.items():
                remaining_time = timer_task.get_remaining_time()
                if remaining_time > 0:
                    active_timers.append(
                        {
                            "timer_id": timer_id,
                            "command": timer_task.command,
                            "description": timer_task.description,
                            "delay": timer_task.delay,
                            "remaining_seconds": remaining_time,
                            "start_time": timer_task.start_time.isoformat(),
                            "estimated_execution_time": timer_task.execution_time.isoformat(),
                            "progress": timer_task.get_progress(),
                        }
                    )

            return {
                "success": True,
                "total_active_timers": len(active_timers),
                "timers": active_timers,
                "current_time": current_time.isoformat(),
            }

    async def cleanup_timer(self, timer_id: int):
        """
        deDispositivoEmJáconcluídodeDispositivo.
        """
        async with self._lock:
            if timer_id in self._timers:
                del self._timers[timer_id]
                logger.debug(f"JáConcluídode {timer_id}")

    async def cleanup_all(self):
        """
        （aplicaçãoFechando）
        """
        logger.info("Em...")
        async with self._lock:
            active_timer_ids = list(self._timers.keys())
            for timer_id in active_timer_ids:
                if timer_id in self._timers:
                    timer_task = self._timers.pop(timer_id)
                    if timer_task.task:
                        timer_task.task.cancel()
                    logger.info(f"Já {timer_id}")
        logger.info("Concluído")


class TimerTask:
    """
    .
    """

    def __init__(
        self,
        timer_id: int,
        command: str,
        delay: int,
        description: str,
        service: TimerService,
    ):
        self.timer_id = timer_id
        self.command = command
        self.delay = delay
        self.description = description
        self.service = service
        self.start_time = datetime.now()
        self.execution_time = self.start_time + timedelta(seconds=delay)
        self.task: Optional[Task] = None

    async def run(self):
        """
        .
        """
        try:
            # AguardandoTempo
            await asyncio.sleep(self.delay)

            # Comando
            await self._execute_command()

        except asyncio.CancelledError:
            logger.info(f" {self.timer_id} ")
        except Exception as e:
            logger.error(f" {self.timer_id} Em: {e}", exc_info=True)
        finally:
            # 
            await self.service.cleanup_timer(self.timer_id)

    async def _execute_command(self):
        """
        Final  deComando.
        """
        logger.info(f" {self.timer_id} Final，MCP: {self.command}")

        try:
            # AnalisandoMCPComando
            command_dict = json.loads(self.command)

            # ValidandoComandoFormato（MCPFormato）
            if "name" not in command_dict or "arguments" not in command_dict:
                raise ValueError("MCPComandoFormatoerro， 'name' e 'arguments' ")

            tool_name = command_dict["name"]
            arguments = command_dict["arguments"]

            # MCPDispositivo
            from src.mcp.mcp_server import McpServer

            mcp_server = McpServer.get_instance()

            # Pesquisar
            tool = None
            for t in mcp_server.tools:
                if t.name == tool_name:
                    tool = t
                    break

            if not tool:
                raise ValueError(f"MCPNãoExiste: {tool_name}")

            # MCP
            result = await tool.call(arguments)

            # Analisando
            result_data = json.loads(result)
            is_success = not result_data.get("isError", False)

            if is_success:
                logger.info(
                    f" {self.timer_id} MCPSucesso，: {tool_name}")
                await self._notify_execution_result(True, f"Já {tool_name}")
            else:
                error_text = result_data.get("content", [{}])[0].get("text", "Não  Erro")
                logger.error(f" {self.timer_id} MCPFalha: {error_text}")
                await self._notify_execution_result(False, error_text)

        except json.JSONDecodeError:
            error_msg = f" {self.timer_id}: MCPComandoFormatoErro，Incapaz deAnalisandoJSON"
            logger.error(error_msg)
            await self._notify_execution_result(False, error_msg)
        except Exception as e:
            error_msg = f" {self.timer_id} MCP: {e}"
            logger.error(error_msg, exc_info=True)
            await self._notify_execution_result(False, error_msg)

    async def _notify_execution_result(self, success: bool, result: Any):
        """
        Notificando（Através deTTS）
        """
        try:
            from src.application import Application

            app = Application.get_instance()
            if success:
                message = f" {self.timer_id} Concluído"
                if self.description:
                    message = f"{self.description}Concluído"
            else:
                message = f" {self.timer_id} Falha"
                if self.description:
                    message = f"{self.description}Falha"

            print("：", message)
            await app._send_text_tts(message)
        except Exception as e:
            logger.warning(f"NotificandoFalha: {e}")

    def get_remaining_time(self) -> float:
        """
        Tempo（Segundos）
        """
        now = datetime.now()
        remaining = (self.execution_time - now).total_seconds()
        return max(0, remaining)

    def get_progress(self) -> float:
        """
        （0-1de）
        """
        elapsed = (datetime.now() - self.start_time).total_seconds()
        return min(1.0, elapsed / self.delay)


# 
_timer_service = None


def get_timer_service() -> TimerService:
    """
    Dispositivo.
    """
    global _timer_service
    if _timer_service is None:
        _timer_service = TimerService()
        logger.debug("Dispositivo")
    return _timer_service
