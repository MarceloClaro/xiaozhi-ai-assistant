"""
AgendamentoMCP paraMCPservidorde.
"""

import json
from datetime import datetime, timedelta
from typing import Any, Dict

from src.utils.logging_config import get_logger

from .manager import get_calendar_manager
from .models import CalendarEvent

logger = get_logger(__name__)


async def create_event(args: Dict[str, Any]) -> str:
    """
    CriandoAgendamento.
    """
    try:
        title = args["title"]
        start_time = args["start_time"]
        end_time = args.get("end_time")
        description = args.get("description", "")
        category = args.get("category", "")
        reminder_minutes = args.get("reminder_minutes", 15)

        # SeNenhumFinalTempo，Configurando
        if not end_time:
            start_dt = datetime.fromisoformat(start_time)

            # ConfigurandoNão  de
            if category in ["", "", ""]:
                # Tempo：5
                end_dt = start_dt + timedelta(minutes=5)
            elif category in ["", ""]:
                # ：1
                end_dt = start_dt + timedelta(hours=1)
            elif (
                "" in title.lower()
                or "" in title.lower()
                or "" in title.lower()
            ):
                # ：Tempo
                end_dt = start_dt + timedelta(minutes=5)
            else:
                # ：30
                end_dt = start_dt + timedelta(minutes=30)

            end_time = end_dt.isoformat()

        # ValidandoTempoFormato
        datetime.fromisoformat(start_time)
        datetime.fromisoformat(end_time)

        # 
        event = CalendarEvent(
            title=title,
            start_time=start_time,
            end_time=end_time,
            description=description,
            category=category,
            reminder_minutes=reminder_minutes,
        )

        manager = get_calendar_manager()
        if manager.add_event(event):
            return json.dumps(
                {
                    "success": True,
                    "message": "AgendamentoSucesso",
                    "event_id": event.id,
                    "event": event.to_dict(),
                },
                ensure_ascii=False,
            )
        else:
            return json.dumps(
                {"success": False, "message": "AgendamentoFalha，ExisteTempo"},
                ensure_ascii=False,
            )

    except Exception as e:
        logger.error(f"AgendamentoFalha: {e}")
        return json.dumps(
            {"success": False, "message": f"AgendamentoFalha: {str(e)}"}, ensure_ascii=False
        )


async def get_events_by_date(args: Dict[str, Any]) -> str:
    """
    DataPesquisarAgendamento.
    """
    try:
        date_type = args.get("date_type", "today")  # today, tomorrow, week, month
        category = args.get("category")

        now = datetime.now()

        if date_type == "today":
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=1)
        elif date_type == "tomorrow":
            start_date = (now + timedelta(days=1)).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            end_date = start_date + timedelta(days=1)
        elif date_type == "week":
            # 
            days_since_monday = now.weekday()
            start_date = (now - timedelta(days=days_since_monday)).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            end_date = start_date + timedelta(days=7)
        elif date_type == "month":
            # 
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if now.month == 12:
                end_date = start_date.replace(year=now.year + 1, month=1)
            else:
                end_date = start_date.replace(month=now.month + 1)
        else:
            # Data
            start_date = (
                datetime.fromisoformat(args["start_date"])
                if args.get("start_date")
                else None
            )
            end_date = (
                datetime.fromisoformat(args["end_date"])
                if args.get("end_date")
                else None
            )

        manager = get_calendar_manager()
        events = manager.get_events(
            start_date=start_date.isoformat() if start_date else None,
            end_date=end_date.isoformat() if end_date else None,
            category=category,
        )

        # FormatoConversãoSaída
        events_data = []
        for event in events:
            event_dict = event.to_dict()
            # ConversãoTempo
            start_dt = datetime.fromisoformat(event.start_time)
            end_dt = datetime.fromisoformat(event.end_time)
            event_dict["display_time"] = (
                f"{start_dt.strftime('%m/%d %H:%M')} - {end_dt.strftime('%H:%M')}"
            )
            events_data.append(event_dict)

        return json.dumps(
            {
                "success": True,
                "date_type": date_type,
                "total_events": len(events_data),
                "events": events_data,
            },
            ensure_ascii=False,
            indent=2,
        )

    except Exception as e:
        logger.error(f"PesquisarAgendamentoFalha: {e}")
        return json.dumps(
            {"success": False, "message": f"PesquisarAgendamentoFalha: {str(e)}"}, ensure_ascii=False
        )


async def update_event(args: Dict[str, Any]) -> str:
    """
    Agendamento.
    """
    try:
        event_id = args["event_id"]

        # 
        update_fields = {}
        for field in [
            "title",
            "start_time",
            "end_time",
            "description",
            "category",
            "reminder_minutes",
        ]:
            if field in args:
                update_fields[field] = args[field]

        if not update_fields:
            return json.dumps(
                {"success": False, "message": "Nenhumde"},
                ensure_ascii=False,
            )

        manager = get_calendar_manager()
        if manager.update_event(event_id, **update_fields):
            return json.dumps(
                {
                    "success": True,
                    "message": "AgendamentoSucesso",
                    "updated_fields": list(update_fields.keys()),
                },
                ensure_ascii=False,
            )
        else:
            return json.dumps(
                {"success": False, "message": "AgendamentoFalha，NãoExiste"},
                ensure_ascii=False,
            )

    except Exception as e:
        logger.error(f"AgendamentoFalha: {e}")
        return json.dumps(
            {"success": False, "message": f"AgendamentoFalha: {str(e)}"}, ensure_ascii=False
        )


async def delete_event(args: Dict[str, Any]) -> str:
    """
    DeletandoAgendamento.
    """
    try:
        event_id = args["event_id"]

        manager = get_calendar_manager()
        if manager.delete_event(event_id):
            return json.dumps(
                {"success": True, "message": "AgendamentoDeletandoSucesso"}, ensure_ascii=False
            )
        else:
            return json.dumps(
                {"success": False, "message": "AgendamentoDeletandoFalha，NãoExiste"},
                ensure_ascii=False,
            )

    except Exception as e:
        logger.error(f"DeletandoAgendamentoFalha: {e}")
        return json.dumps(
            {"success": False, "message": f"DeletandoAgendamentoFalha: {str(e)}"}, ensure_ascii=False
        )


async def delete_events_batch(args: Dict[str, Any]) -> str:
    """
    DeletandoAgendamento.
    """
    try:
        start_date = args.get("start_date")
        end_date = args.get("end_date")
        category = args.get("category")
        delete_all = args.get("delete_all", False)
        date_type = args.get("date_type")

        # Processandodate_typeParâmetro（get_events_by_date）
        if date_type and not (start_date and end_date):
            now = datetime.now()

            if date_type == "today":
                start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
                end_date = start_date + timedelta(days=1)
            elif date_type == "tomorrow":
                start_date = (now + timedelta(days=1)).replace(
                    hour=0, minute=0, second=0, microsecond=0
                )
                end_date = start_date + timedelta(days=1)
            elif date_type == "week":
                # 
                days_since_monday = now.weekday()
                start_date = (now - timedelta(days=days_since_monday)).replace(
                    hour=0, minute=0, second=0, microsecond=0
                )
                end_date = start_date + timedelta(days=7)
            elif date_type == "month":
                # 
                start_date = now.replace(
                    day=1, hour=0, minute=0, second=0, microsecond=0
                )
                if now.month == 12:
                    end_date = start_date.replace(year=now.year + 1, month=1)
                else:
                    end_date = start_date.replace(month=now.month + 1)

            # paraISOFormatoCaracteres
            if isinstance(start_date, datetime):
                start_date = start_date.isoformat()
            if isinstance(end_date, datetime):
                end_date = end_date.isoformat()

        manager = get_calendar_manager()
        result = manager.delete_events_batch(
            start_date=start_date,
            end_date=end_date,
            category=category,
            delete_all=delete_all,
        )

        return json.dumps(result, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"DeletandoAgendamentoFalha: {e}")
        return json.dumps(
            {"success": False, "message": f"DeletandoAgendamentoFalha: {str(e)}"},
            ensure_ascii=False,
        )


async def get_categories(args: Dict[str, Any]) -> str:
    """
    Agendamento.
    """
    try:
        manager = get_calendar_manager()
        categories = manager.get_categories()

        return json.dumps(
            {"success": True, "categories": categories}, ensure_ascii=False
        )

    except Exception as e:
        logger.error(f"Falha: {e}")
        return json.dumps(
            {"success": False, "message": f"Falha: {str(e)}"}, ensure_ascii=False
        )


async def get_upcoming_events(args: Dict[str, Any]) -> str:
    """
    para  deAgendamento（Não24）
    """
    try:
        hours = args.get("hours", 24)  # Não24

        now = datetime.now()
        end_time = now + timedelta(hours=hours)

        manager = get_calendar_manager()
        events = manager.get_events(
            start_date=now.isoformat(), end_date=end_time.isoformat()
        )

        # Tempo
        upcoming_events = []
        for event in events:
            event_dict = event.to_dict()
            start_dt = datetime.fromisoformat(event.start_time)

            # ComeçardeTempo
            time_until = start_dt - now
            if time_until.total_seconds() > 0:
                hours_until = int(time_until.total_seconds() // 3600)
                minutes_until = int((time_until.total_seconds() % 3600) // 60)

                if hours_until > 0:
                    time_display = f"{hours_until}{minutes_until}"
                else:
                    time_display = f"{minutes_until}"

                event_dict["time_until"] = time_display
                event_dict["time_until_minutes"] = int(time_until.total_seconds() // 60)
                upcoming_events.append(event_dict)

        return json.dumps(
            {
                "success": True,
                "query_hours": hours,
                "total_events": len(upcoming_events),
                "events": upcoming_events,
            },
            ensure_ascii=False,
            indent=2,
        )

    except Exception as e:
        logger.error(f"para  deAgendamentoFalha: {e}")
        return json.dumps(
            {"success": False, "message": f"para  deAgendamentoFalha: {str(e)}"},
            ensure_ascii=False,
        )
