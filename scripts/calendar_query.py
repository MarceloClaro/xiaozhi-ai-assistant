#!/usr/bin/env python3
"""
AgendamentoPesquisar PesquisareAgendamento.
"""

import argparse
import asyncio
import sys
from datetime import datetime, timedelta
from pathlib import Path

from src.mcp.tools.calendar import get_calendar_manager
from src.utils.logging_config import get_logger

# DiretórioparaPythonCaminho - Emsrc
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

logger = get_logger(__name__)


class CalendarQueryScript:
    """
    AgendamentoPesquisar.
    """

    def __init__(self):
        self.manager = get_calendar_manager()

    def format_event_display(self, event, show_details=True):
        """
        FormatoConversão.
        """
        start_dt = datetime.fromisoformat(event.start_time)
        end_dt = datetime.fromisoformat(event.end_time)

        # Informação
        time_str = f"{start_dt.strftime('%m/%d %H:%M')} - {end_dt.strftime('%H:%M')}"
        basic_info = f"📅 {time_str} | 【{event.category}】{event.title}"

        if not show_details:
            return basic_info

        # Informação
        details = []
        if event.description:
            details.append(f"   📝 : {event.description}")

        # Informação
        if event.reminder_minutes > 0:
            details.append(f"   ⏰ : {event.reminder_minutes}")
            if hasattr(event, "reminder_sent") and event.reminder_sent:
                details.append("   ✅ Estado: JáEnviando")
            else:
                details.append("   ⏳ Estado: Enviando")

        # Tempo
        now = datetime.now()
        time_diff = start_dt - now
        if time_diff.total_seconds() > 0:
            days = time_diff.days
            hours = int(time_diff.seconds // 3600)
            minutes = int((time_diff.seconds % 3600) // 60)

            time_until_parts = []
            if days > 0:
                time_until_parts.append(f"{days}")
            if hours > 0:
                time_until_parts.append(f"{hours}")
            if minutes > 0:
                time_until_parts.append(f"{minutes}")

            if time_until_parts:
                details.append(f"   🕐 Começar: {' '.join(time_until_parts)}")
            else:
                details.append("   🕐 Começar: Começar")
        elif start_dt <= now <= end_dt:
            details.append("   🔴 Estado: EmEm")
        else:
            details.append("   ✅ Estado: JáFinal")

        if details:
            return basic_info + "\n" + "\n".join(details)
        return basic_info

    async def query_today(self):
        """
        PesquisarAgendamento.
        """
        print("📅 Agendamento")
        print("=" * 50)

        now = datetime.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)

        events = self.manager.get_events(
            start_date=today_start.isoformat(), end_date=today_end.isoformat()
        )

        if not events:
            print("🎉 NenhumAgendamento")
            return

        print(f"📊  {len(events)} Agendamento:\n")
        for i, event in enumerate(events, 1):
            print(f"{i}. {self.format_event_display(event)}")
            if i < len(events):
                print()

    async def query_tomorrow(self):
        """
        PesquisarAgendamento.
        """
        print("📅 Agendamento")
        print("=" * 50)

        now = datetime.now()
        tomorrow_start = (now + timedelta(days=1)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        tomorrow_end = tomorrow_start + timedelta(days=1)

        events = self.manager.get_events(
            start_date=tomorrow_start.isoformat(), end_date=tomorrow_end.isoformat()
        )

        if not events:
            print("🎉 NenhumAgendamento")
            return

        print(f"📊  {len(events)} Agendamento:\n")
        for i, event in enumerate(events, 1):
            print(f"{i}. {self.format_event_display(event)}")
            if i < len(events):
                print()

    async def query_week(self):
        """
        PesquisarAgendamento.
        """
        print("📅 Agendamento")
        print("=" * 50)

        now = datetime.now()
        # 
        days_since_monday = now.weekday()
        week_start = (now - timedelta(days=days_since_monday)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        week_end = week_start + timedelta(days=7)

        events = self.manager.get_events(
            start_date=week_start.isoformat(), end_date=week_end.isoformat()
        )

        if not events:
            print("🎉 NenhumAgendamento")
            return

        print(f"📊  {len(events)} Agendamento:\n")

        # Data
        events_by_date = {}
        for event in events:
            event_date = datetime.fromisoformat(event.start_time).date()
            if event_date not in events_by_date:
                events_by_date[event_date] = []
            events_by_date[event_date].append(event)

        for date in sorted(events_by_date.keys()):
            weekday = ["", "", "", "", "", "", ""][
                date.weekday()
            ]
            print(f"📆 {date.strftime('%m%d')} ({weekday})")
            print("-" * 30)

            for event in events_by_date[date]:
                print(f"  {self.format_event_display(event, show_details=False)}")
            print()

    async def query_upcoming(self, hours=24):
        """
        Pesquisarpara  deAgendamento.
        """
        print(f"📅 Não {hours} deAgendamento")
        print("=" * 50)

        now = datetime.now()
        end_time = now + timedelta(hours=hours)

        events = self.manager.get_events(
            start_date=now.isoformat(), end_date=end_time.isoformat()
        )

        if not events:
            print(f"🎉 Não {hours} NenhumAgendamento")
            return

        print(f"📊  {len(events)} Agendamento:\n")
        for i, event in enumerate(events, 1):
            print(f"{i}. {self.format_event_display(event)}")
            if i < len(events):
                print()

    async def query_by_category(self, category=None):
        """
        PesquisarAgendamento.
        """
        if category:
            print(f"📅 【{category}】deAgendamento")
            print("=" * 50)

            events = self.manager.get_events(category=category)

            if not events:
                print(f"🎉 【{category}】NenhumAgendamento")
                return

            print(f"📊  {len(events)} Agendamento:\n")
            for i, event in enumerate(events, 1):
                print(f"{i}. {self.format_event_display(event)}")
                if i < len(events):
                    print()
        else:
            print("📅 ")
            print("=" * 50)

            categories = self.manager.get_categories()

            if not categories:
                print("🎉 ")
                return

            print("📊 :")
            for i, cat in enumerate(categories, 1):
                # de
                events = self.manager.get_events(category=cat)
                print(f"{i}. 【{cat}】- {len(events)} Agendamento")

    async def query_all(self):
        """
        PesquisarAgendamento.
        """
        print("📅 Agendamento")
        print("=" * 50)

        events = self.manager.get_events()

        if not events:
            print("🎉 Agendamento")
            return

        print(f"📊  {len(events)} Agendamento:\n")

        # Tempo
        now = datetime.now()
        past_events = []
        current_events = []
        future_events = []

        for event in events:
            start_dt = datetime.fromisoformat(event.start_time)
            end_dt = datetime.fromisoformat(event.end_time)

            if end_dt < now:
                past_events.append(event)
            elif start_dt <= now <= end_dt:
                current_events.append(event)
            else:
                future_events.append(event)

        # Emde
        if current_events:
            print("🔴 EmEm:")
            for event in current_events:
                print(f"  {self.format_event_display(event, show_details=False)}")
            print()

        # Não
        if future_events:
            print("⏳ para:")
            for event in future_events[:5]:  # 5
                print(f"  {self.format_event_display(event, show_details=False)}")
            if len(future_events) > 5:
                print(f"  ... Ainda {len(future_events) - 5} Agendamento")
            print()

        # de
        if past_events:
            recent_past = sorted(past_events, key=lambda e: e.start_time, reverse=True)[
                :3
            ]
            print("✅ Concluído:")
            for event in recent_past:
                print(f"  {self.format_event_display(event, show_details=False)}")
            if len(past_events) > 3:
                print(f"  ... Ainda {len(past_events) - 3} JáConcluídodeAgendamento")

    async def search_events(self, keyword):
        """
        PesquisaAgendamento.
        """
        print(f"🔍 Pesquisa '{keyword}' deAgendamento")
        print("=" * 50)

        all_events = self.manager.get_events()
        matched_events = []

        for event in all_events:
            if (
                keyword.lower() in event.title.lower()
                or keyword.lower() in event.description.lower()
                or keyword.lower() in event.category.lower()
            ):
                matched_events.append(event)

        if not matched_events:
            print(f"🎉 NenhumEncontrado '{keyword}' deAgendamento")
            return

        print(f"📊 Encontrado {len(matched_events)} CorrespondênciadeAgendamento:\n")
        for i, event in enumerate(matched_events, 1):
            print(f"{i}. {self.format_event_display(event)}")
            if i < len(matched_events):
                print()


async def main():
    """
    .
    """
    parser = argparse.ArgumentParser(description="AgendamentoPesquisar")
    parser.add_argument(
        "command",
        nargs="?",
        default="today",
        choices=["today", "tomorrow", "week", "upcoming", "category", "all", "search"],
        help="Tipo",
    )
    parser.add_argument("--hours", type=int, default=24, help="upcomingde")
    parser.add_argument("--category", type=str, help="Nome")
    parser.add_argument("--keyword", type=str, help="Pesquisa")

    args = parser.parse_args()

    script = CalendarQueryScript()

    try:
        if args.command == "today":
            await script.query_today()
        elif args.command == "tomorrow":
            await script.query_tomorrow()
        elif args.command == "week":
            await script.query_week()
        elif args.command == "upcoming":
            await script.query_upcoming(args.hours)
        elif args.command == "category":
            await script.query_by_category(args.category)
        elif args.command == "all":
            await script.query_all()
        elif args.command == "search":
            if not args.keyword:
                print("❌ Pesquisa，Usando --keyword Parâmetro")
                return
            await script.search_events(args.keyword)

        print("\n" + "=" * 50)
        print("💡 Usando:")
        print("  python scripts/calendar_query.py today      # PesquisarAgendamento")
        print("  python scripts/calendar_query.py tomorrow   # PesquisarAgendamento")
        print("  python scripts/calendar_query.py week       # PesquisarAgendamento")
        print(
            "  python scripts/calendar_query.py upcoming --hours 48  # PesquisarNão48"
        )
        print(
            "  python scripts/calendar_query.py category --category   # Pesquisar"
        )
        print("  python scripts/calendar_query.py all        # PesquisarAgendamento")
        print("  python scripts/calendar_query.py search --keyword   # PesquisaAgendamento")

    except Exception as e:
        logger.error(f"PesquisarAgendamentoFalha: {e}", exc_info=True)
        print(f"❌ Falha: {e}")


if __name__ == "__main__":
    asyncio.run(main())
