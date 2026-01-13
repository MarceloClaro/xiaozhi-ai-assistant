"""
AgendamentoSQLitedados Banco de dados Operação.
"""

import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Dict, List, Optional

from src.utils.logging_config import get_logger
from src.utils.resource_finder import get_user_data_dir

logger = get_logger(__name__)


def _get_database_file_path() -> str:
    """
    dados Banco de dados arquivoCaminho，EmDiretórioEm.
    """
    data_dir = get_user_data_dir()
    database_file = str(data_dir / "calendar.db")
    logger.debug(f"UsandoDados Banco de dados ArquivoCaminho: {database_file}")
    return database_file


# Dados Banco de dados ArquivoCaminho - Usando
DATABASE_FILE = _get_database_file_path()


class CalendarDatabase:
    """
    Agendamentodados Banco de dados Operação.
    """

    def __init__(self):
        self.db_file = DATABASE_FILE
        self._ensure_database()

    def _ensure_database(self):
        """
        dados Banco de dados eExiste.
        """
        os.makedirs(os.path.dirname(self.db_file), exist_ok=True)

        with self._get_connection() as conn:
            # 
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS events (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT NOT NULL,
                    description TEXT DEFAULT '',
                    category TEXT DEFAULT '',
                    reminder_minutes INTEGER DEFAULT 15,
                    reminder_time TEXT,
                    reminder_sent BOOLEAN DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """
            )

            # 
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL
                )
            """
            )

            # 
            default_categories = ["", "", "", "", ""]
            for category in default_categories:
                conn.execute(
                    "INSERT OR IGNORE INTO categories (name) VALUES (?)", (category,)
                )

            conn.commit()

            # Pesquisar（DadosBanco de dados）
            self._upgrade_database(conn)

            logger.info("Dados Banco de dados Inicialização concluída")

    @contextmanager
    def _get_connection(self):
        """
        dados Banco de dados ConectandodeDispositivo.
        """
        conn = None
        try:
            conn = sqlite3.connect(self.db_file)
            conn.row_factory = sqlite3.Row  # 
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Dados Banco de dados OperaçãoFalha: {e}")
            raise
        finally:
            if conn:
                conn.close()

    def add_event(self, event_data: Dict[str, Any]) -> bool:
        """
        .
        """
        try:
            with self._get_connection() as conn:
                # PesquisarTempo
                if self._has_conflict(conn, event_data):
                    return False

                conn.execute(
                    """
                    INSERT INTO events (
                        id, title, start_time, end_time, description,
                        category, reminder_minutes, reminder_time, reminder_sent,
                        created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        event_data["id"],
                        event_data["title"],
                        event_data["start_time"],
                        event_data["end_time"],
                        event_data["description"],
                        event_data["category"],
                        event_data["reminder_minutes"],
                        event_data.get("reminder_time"),
                        event_data.get("reminder_sent", False),
                        event_data["created_at"],
                        event_data["updated_at"],
                    ),
                )
                conn.commit()
                logger.info(f"Sucesso: {event_data['title']}")
                return True
        except Exception as e:
            logger.error(f"Falha: {e}")
            return False

    def get_events(
        self, start_date: str = None, end_date: str = None, category: str = None
    ) -> List[Dict[str, Any]]:
        """
        .
        """
        try:
            with self._get_connection() as conn:
                query = "SELECT * FROM events WHERE 1=1"
                params = []

                if start_date:
                    query += " AND start_time >= ?"
                    params.append(start_date)

                if end_date:
                    query += " AND start_time <= ?"
                    params.append(end_date)

                if category:
                    query += " AND category = ?"
                    params.append(category)

                query += " ORDER BY start_time"

                cursor = conn.execute(query, params)
                rows = cursor.fetchall()

                events = []
                for row in rows:
                    events.append(dict(row))

                return events
        except Exception as e:
            logger.error(f"Falha: {e}")
            return []

    def update_event(self, event_id: str, **kwargs) -> bool:
        """
        .
        """
        try:
            with self._get_connection() as conn:
                # Pesquisar
                set_clauses = []
                params = []

                for key, value in kwargs.items():
                    if key in [
                        "title",
                        "start_time",
                        "end_time",
                        "description",
                        "category",
                        "reminder_minutes",
                    ]:
                        set_clauses.append(f"{key} = ?")
                        params.append(value)

                if not set_clauses:
                    return False

                # Tempo
                set_clauses.append("updated_at = ?")
                params.append(datetime.now().isoformat())
                params.append(event_id)

                query = f"UPDATE events SET {', '.join(set_clauses)} WHERE id = ?"

                cursor = conn.execute(query, params)
                conn.commit()

                if cursor.rowcount > 0:
                    logger.info(f"Sucesso: {event_id}")
                    return True
                else:
                    logger.warning(f"NãoExiste: {event_id}")
                    return False
        except Exception as e:
            logger.error(f"Falha: {e}")
            return False

    def delete_event(self, event_id: str) -> bool:
        """
        Deletando.
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.execute("DELETE FROM events WHERE id = ?", (event_id,))
                conn.commit()

                if cursor.rowcount > 0:
                    logger.info(f"DeletandoSucesso: {event_id}")
                    return True
                else:
                    logger.warning(f"NãoExiste: {event_id}")
                    return False
        except Exception as e:
            logger.error(f"DeletandoFalha: {e}")
            return False

    def delete_events_batch(
        self,
        start_date: str = None,
        end_date: str = None,
        category: str = None,
        delete_all: bool = False,
    ) -> Dict[str, Any]:
        """Deletando.

        Args:
            start_date: IniciandoData，ISOFormato
            end_date: FinalData，ISOFormato
            category: 
            delete_all: Deletando

        Returns:
            Deletandode
        """
        try:
            with self._get_connection() as conn:
                if delete_all:
                    # Deletando
                    cursor = conn.execute("SELECT COUNT(*) FROM events")
                    total_count = cursor.fetchone()[0]

                    if total_count == 0:
                        return {
                            "success": True,
                            "deleted_count": 0,
                            "message": "NenhumDeletando",
                        }

                    cursor = conn.execute("DELETE FROM events")
                    conn.commit()

                    logger.info(
                        f"DeletandoSucesso，Deletando {total_count} "
                    )
                    return {
                        "success": True,
                        "deleted_count": total_count,
                        "message": f"SucessoDeletando {total_count} ",
                    }

                else:
                    # Deletando
                    # Pesquisarde
                    query = "SELECT id, title FROM events WHERE 1=1"
                    params = []

                    if start_date:
                        query += " AND start_time >= ?"
                        params.append(start_date)

                    if end_date:
                        query += " AND start_time <= ?"
                        params.append(end_date)

                    if category:
                        query += " AND category = ?"
                        params.append(category)

                    cursor = conn.execute(query, params)
                    events_to_delete = cursor.fetchall()

                    if not events_to_delete:
                        return {
                            "success": True,
                            "deleted_count": 0,
                            "message": "NenhumdeDeletando",
                        }

                    # Deletando
                    delete_query = "DELETE FROM events WHERE 1=1"
                    delete_params = []

                    if start_date:
                        delete_query += " AND start_time >= ?"
                        delete_params.append(start_date)

                    if end_date:
                        delete_query += " AND start_time <= ?"
                        delete_params.append(end_date)

                    if category:
                        delete_query += " AND category = ?"
                        delete_params.append(category)

                    cursor = conn.execute(delete_query, delete_params)
                    deleted_count = cursor.rowcount
                    conn.commit()

                    # Registrar títulos de eventos deletados
                    deleted_titles = [event[1] for event in events_to_delete]
                    logger.info(
                        f"Deletar eventos em lote bem-sucedido, total deletado {deleted_count} eventos: "
                        f"{', '.join(deleted_titles[:3])}"
                        f"{'...' if len(deleted_titles) > 3 else ''}"
                    )

                    return {
                        "success": True,
                        "deleted_count": deleted_count,
                        "deleted_titles": deleted_titles,
                        "message": f"Sucesso ao deletar {deleted_count} eventos",
                    }

        except Exception as e:
            logger.error(f"DeletandoFalha: {e}")
            return {
                "success": False,
                "deleted_count": 0,
                "message": f"DeletandoFalha: {str(e)}",
            }

    def get_event_by_id(self, event_id: str) -> Optional[Dict[str, Any]]:
        """
        ID.
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.execute("SELECT * FROM events WHERE id = ?", (event_id,))
                row = cursor.fetchone()

                if row:
                    return dict(row)
                return None
        except Exception as e:
            logger.error(f"Falha: {e}")
            return None

    def get_categories(self) -> List[str]:
        """
        .
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.execute("SELECT name FROM categories ORDER BY name")
                rows = cursor.fetchall()
                return [row[0] for row in rows]
        except Exception as e:
            logger.error(f"Falha: {e}")
            return [""]

    def add_category(self, category_name: str) -> bool:
        """
        .
        """
        try:
            with self._get_connection() as conn:
                conn.execute(
                    "INSERT OR IGNORE INTO categories (name) VALUES (?)",
                    (category_name,),
                )
                conn.commit()
                logger.info(f"Sucesso: {category_name}")
                return True
        except Exception as e:
            logger.error(f"Falha: {e}")
            return False

    def delete_category(self, category_name: str) -> bool:
        """
        Deletando（SeNenhumUsando）
        """
        try:
            with self._get_connection() as conn:
                # PesquisarUsando
                cursor = conn.execute(
                    "SELECT COUNT(*) FROM events WHERE category = ?", (category_name,)
                )
                count = cursor.fetchone()[0]

                if count > 0:
                    logger.warning(
                        f" '{category_name}' EmUsandoEm，Incapaz deDeletando"
                    )
                    return False

                cursor = conn.execute(
                    "DELETE FROM categories WHERE name = ?", (category_name,)
                )
                conn.commit()

                if cursor.rowcount > 0:
                    logger.info(f"DeletandoSucesso: {category_name}")
                    return True
                else:
                    logger.warning(f"NãoExiste: {category_name}")
                    return False
        except Exception as e:
            logger.error(f"DeletandoFalha: {e}")
            return False

    def _has_conflict(
        self, conn: sqlite3.Connection, event_data: Dict[str, Any]
    ) -> bool:
        """
        PesquisarTempo.
        """
        cursor = conn.execute(
            """
            SELECT title FROM events
            WHERE id != ? AND (
                (start_time < ? AND end_time > ?) OR
                (start_time < ? AND end_time > ?)
            )
        """,
            (
                event_data["id"],
                event_data["end_time"],
                event_data["start_time"],
                event_data["start_time"],
                event_data["end_time"],
            ),
        )

        conflicting_events = cursor.fetchall()

        if conflicting_events:
            for event in conflicting_events:
                logger.warning(f"Tempo: com '{event[0]}' ")
            return True

        return False

    def get_statistics(self) -> Dict[str, Any]:
        """
        Informação.
        """
        try:
            with self._get_connection() as conn:
                # 
                cursor = conn.execute("SELECT COUNT(*) FROM events")
                total_events = cursor.fetchone()[0]

                # 
                cursor = conn.execute(
                    """
                    SELECT category, COUNT(*)
                    FROM events
                    GROUP BY category
                    ORDER BY COUNT(*) DESC
                """
                )
                category_stats = dict(cursor.fetchall())

                # de
                today = datetime.now().strftime("%Y-%m-%d")
                cursor = conn.execute(
                    """
                    SELECT COUNT(*) FROM events
                    WHERE date(start_time) = ?
                """,
                    (today,),
                )
                today_events = cursor.fetchone()[0]

                return {
                    "total_events": total_events,
                    "category_stats": category_stats,
                    "today_events": today_events,
                }
        except Exception as e:
            logger.error(f"InformaçãoFalha: {e}")
            return {}

    def migrate_from_json(self, json_file_path: str) -> bool:
        """
        deJSONarquivodados.
        """
        try:
            import json

            if not os.path.exists(json_file_path):
                logger.info("JSONArquivoNãoExiste，")
                return True

            with open(json_file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            events_data = data.get("events", [])
            categories_data = data.get("categories", [])

            with self._get_connection() as conn:
                # 
                for category in categories_data:
                    conn.execute(
                        "INSERT OR IGNORE INTO categories (name) VALUES (?)",
                        (category,),
                    )

                # 
                for event_data in events_data:
                    conn.execute(
                        """
                        INSERT OR REPLACE INTO events (
                            id, title, start_time, end_time, description,
                            category, reminder_minutes, created_at, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                        (
                            event_data["id"],
                            event_data["title"],
                            event_data["start_time"],
                            event_data["end_time"],
                            event_data.get("description", ""),
                            event_data.get("category", ""),
                            event_data.get("reminder_minutes", 15),
                            event_data.get("created_at", datetime.now().isoformat()),
                            event_data.get("updated_at", datetime.now().isoformat()),
                        ),
                    )

                conn.commit()
                logger.info(
                    f"Sucesso {len(events_data)} e {len(categories_data)} "
                )
                return True

        except Exception as e:
            logger.error(f"DadosFalha: {e}")
            return False

    def _upgrade_database(self, conn: sqlite3.Connection):
        """
        dadosBanco de dados.
        """
        try:
            # PesquisarExiste
            cursor = conn.execute("PRAGMA table_info(events)")
            columns = [col[1] for col in cursor.fetchall()]

            # reminder_time
            if "reminder_time" not in columns:
                conn.execute("ALTER TABLE events ADD COLUMN reminder_time TEXT")
                logger.info("Járeminder_time")

            # reminder_sent
            if "reminder_sent" not in columns:
                conn.execute(
                    "ALTER TABLE events ADD COLUMN reminder_sent BOOLEAN DEFAULT 0"
                )
                logger.info("Járeminder_sent")

            # paraConfigurandoreminder_time
            cursor = conn.execute(
                "SELECT id, start_time, reminder_minutes "
                "FROM events WHERE reminder_time IS NULL"
            )
            events_to_update = cursor.fetchall()

            for event in events_to_update:
                event_id, start_time, reminder_minutes = event
                try:
                    from datetime import timedelta

                    start_dt = datetime.fromisoformat(start_time)
                    reminder_dt = start_dt - timedelta(minutes=reminder_minutes)

                    conn.execute(
                        "UPDATE events SET reminder_time = ? WHERE id = ?",
                        (reminder_dt.isoformat(), event_id),
                    )
                except Exception as e:
                    logger.warning(f"{event_id}deTempoFalha: {e}")

            if events_to_update:
                logger.info(
                    f"Jápara{len(events_to_update)}ConfigurandoTempo"
                )

            conn.commit()

        except Exception as e:
            logger.error(f"DadosBanco de dadosFalha: {e}", exc_info=True)


# DadosBanco de dados
_calendar_db = None


def get_calendar_database() -> CalendarDatabase:
    """
    dadosBanco de dados.
    """
    global _calendar_db
    if _calendar_db is None:
        _calendar_db = CalendarDatabase()
    return _calendar_db
