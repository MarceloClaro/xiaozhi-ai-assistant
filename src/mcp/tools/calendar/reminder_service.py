"""
Serviço de lembretes de agendamento Pesquisardados Banco de dados Emde，paraTempo  Através deTTS.
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Optional

from src.utils.logging_config import get_logger

from .database import get_calendar_database

logger = get_logger(__name__)


class CalendarReminderService:
    """
    Serviço de lembretes de agendamento.
    """

    def __init__(self):
        self.db = get_calendar_database()
        self.is_running = False
        self._task: Optional[asyncio.Task] = None
        self.check_interval = 30  # Pesquisar（Segundos）

    def _get_application(self):
        """
        Carregandoaplicação.
        """
        try:
            from src.application import Application

            return Application.get_instance()
        except Exception as e:
            logger.warning(f"AppFalha: {e}")
            return None

    async def start(self):
        """
        Iniciando.
        """
        if self.is_running:
            logger.warning("JáEm")
            return

        self.is_running = True
        self._task = asyncio.create_task(self._reminder_loop())
        logger.info("Serviço de lembretes de agendamentoIniciando")

        # IniciandoNãode
        await self.reset_reminder_flags_for_future_events()

    async def stop(self):
        """
        Parar.
        """
        if not self.is_running:
            return

        self.is_running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None

        logger.info("Serviço de lembretes de agendamentoJáParar")

    async def _reminder_loop(self):
        """
        Pesquisar.
        """
        logger.info("ComeçarAgendamentoPesquisar")

        while self.is_running:
            try:
                await self._check_and_send_reminders()
                # de
                await self._cleanup_expired_reminders()
                await asyncio.sleep(self.check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Pesquisar: {e}", exc_info=True)
                await asyncio.sleep(self.check_interval)

    async def _check_and_send_reminders(self):
        """
        PesquisarEnviando.
        """
        try:
            now = datetime.now()

            # PesquisarNãoEnviandoTempoJáparade
            # AindaNenhum（ComeçarTempoEmTempoou  EmdeTempo）
            with self.db._get_connection() as conn:
                cursor = conn.execute(
                    """
                    SELECT * FROM events
                    WHERE reminder_sent = 0
                    AND reminder_time IS NOT NULL
                    AND reminder_time <= ?
                    AND start_time > ?
                    ORDER BY reminder_time
                """,
                    (now.isoformat(), (now - timedelta(hours=1)).isoformat()),
                )

                pending_reminders = cursor.fetchall()

            if not pending_reminders:
                return

            logger.info(f" {len(pending_reminders)} Enviandode")

            # Processando cada lembrete
            for reminder in pending_reminders:
                await self._send_reminder(dict(reminder))

        except Exception as e:
            logger.error(f"Falha ao verificar: {e}", exc_info=True)

    async def _send_reminder(self, event_data: dict):
        """
        Enviando um lembrete.
        """
        try:
            event_id = event_data["id"]
            title = event_data["title"]
            start_time = event_data["start_time"]
            description = event_data.get("description", "")
            category = event_data.get("category", "")

            # ComeçarTempo
            start_dt = datetime.fromisoformat(start_time)
            now = datetime.now()
            time_until = start_dt - now

            if time_until.total_seconds() > 0:
                hours = int(time_until.total_seconds() // 3600)
                minutes = int((time_until.total_seconds() % 3600) // 60)

                if hours > 0:
                    time_str = f"{hours}{minutes}"
                else:
                    time_str = f"{minutes}"
            else:
                time_str = "Agora"

            # Mensagem
            reminder_message = {
                "type": "calendar_reminder",
                "event": {
                    "id": event_id,
                    "title": title,
                    "start_time": start_time,
                    "description": description,
                    "category": category,
                    "time_until": time_str,
                },
                "message": self._format_reminder_text(
                    title, time_str, category, description
                ),
            }

            # Serializar para JSON String
            reminder_json = json.dumps(reminder_message, ensure_ascii=False)

            # Obter instância do App e chamar método TTS
            application = self._get_application()
            if application and hasattr(application, "_send_text_tts"):
                await application._send_text_tts(reminder_json)
                logger.info(f"Já Enviando lembrete: {title} ({time_str})")
            else:
                logger.warning(
                    "Não é possível enviar lembrete: instância do App ou método TTS não disponível"
                )

            # Marcar Já Enviando
            await self._mark_reminder_sent(event_id)

        except Exception as e:
            logger.error(f"Falha ao enviar: {e}", exc_info=True)

    def _format_reminder_text(
        self, title: str, time_str: str, category: str, description: str
    ) -> str:
        """
        FormatoConversão.
        """
        # Informação
        if time_str == "Agora":
            message = f"【{category}】Agendamento：{title} Começar"
        else:
            message = f"【{category}】Agendamento：{title} Em{time_str}Começar"

        # Informação
        if description:
            message += f"，：{description}"

        return message

    async def _mark_reminder_sent(self, event_id: str):
        """
        JáEnviando.
        """
        try:
            with self.db._get_connection() as conn:
                conn.execute(
                    """
                    UPDATE events
                    SET reminder_sent = 1, updated_at = ?
                    WHERE id = ?
                """,
                    (datetime.now().isoformat(), event_id),
                )
                conn.commit()

            logger.debug(f"JáparaJáEnviando: {event_id}")

        except Exception as e:
            logger.error(f"JáEnviandoFalha: {e}", exc_info=True)

    async def check_daily_events(self):
        """
        Pesquisar（EmprogramaIniciando）
        """
        try:
            now = datetime.now()
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            today_end = today_start + timedelta(days=1)

            with self.db._get_connection() as conn:
                cursor = conn.execute(
                    """
                    SELECT * FROM events
                    WHERE start_time >= ? AND start_time < ?
                    ORDER BY start_time
                """,
                    (today_start.isoformat(), today_end.isoformat()),
                )

                today_events = cursor.fetchall()

            if today_events:
                logger.info(f" {len(today_events)} Agendamento")

                # Agendamento
                summary_message = {
                    "type": "daily_schedule",
                    "date": today_start.strftime("%Y-%m-%d"),
                    "total_events": len(today_events),
                    "events": [dict(event) for event in today_events],
                    "message": self._format_daily_summary(today_events),
                }

                summary_json = json.dumps(summary_message, ensure_ascii=False)

                # AppEnviandoAgendamento
                application = self._get_application()
                if application and hasattr(application, "_send_text_tts"):
                    await application._send_text_tts(summary_json)
                    logger.info("JáEnviandoAgendamento")

            else:
                logger.info("Sem compromissos agendados hoje")

        except Exception as e:
            logger.error(f"PesquisarFalha: {e}", exc_info=True)

    def _format_daily_summary(self, events) -> str:
        """
        FormatoConversãoAgendamento.
        """
        if not events:
            return "NenhumAgendamento"

        summary = f"{len(events)}Agendamento："

        for i, event in enumerate(events, 1):
            start_dt = datetime.fromisoformat(event["start_time"])
            time_str = start_dt.strftime("%H:%M")
            summary += f" {i}.{time_str} {event['title']}"

            if i < len(events):
                summary += "，"

        return summary

    async def reset_reminder_flags_for_future_events(self):
        """
        Nãode（programa）
        """
        try:
            now = datetime.now()

            with self.db._get_connection() as conn:
                # Nãode
                cursor = conn.execute(
                    """
                    UPDATE events
                    SET reminder_sent = 0, updated_at = ?
                    WHERE start_time > ? AND reminder_sent = 1
                """,
                    (now.isoformat(), now.isoformat()),
                )

                reset_count = cursor.rowcount
                conn.commit()

            if reset_count > 0:
                logger.info(f"Já {reset_count} Nãode")

        except Exception as e:
            logger.error(f"Falha: {e}", exc_info=True)

    async def _cleanup_expired_reminders(self):
        """
        de（24de）
        """
        try:
            now = datetime.now()
            cleanup_threshold = now - timedelta(hours=24)

            with self.db._get_connection() as conn:
                cursor = conn.execute(
                    """
                    UPDATE events
                    SET reminder_sent = 1, updated_at = ?
                    WHERE start_time < ? AND reminder_sent = 0
                """,
                    (now.isoformat(), cleanup_threshold.isoformat()),
                )

                cleanup_count = cursor.rowcount
                conn.commit()

            if cleanup_count > 0:
                logger.info(f"Já {cleanup_count} de")

        except Exception as e:
            logger.error(f"Falha: {e}", exc_info=True)


# 
_reminder_service = None


def get_reminder_service() -> CalendarReminderService:
    """
    .
    """
    global _reminder_service
    if _reminder_service is None:
        _reminder_service = CalendarReminderService()
    return _reminder_service
