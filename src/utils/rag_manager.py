"""
Gerenciador de RAG (Retrieval-Augmented Generation) Local.
- Suporta até 8000 chunks de 2000 caracteres cada
- Embeddings locais com sentence-transformers
- Armazenamento em SQLite com busca vetorial
- Histórico expandido de conversas
- Resumo de reuniões/áudio capturado
"""

import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
from src.utils.logging_config import get_logger

logger = get_logger(__name__)

# Importar sentence_transformers opcionalmente com proteção
EMBEDDING_AVAILABLE = False


def _safe_import_sentence_transformers():
    """Tentar importar sentence_transformers com tratamento seguro."""
    global EMBEDDING_AVAILABLE
    try:
        import importlib.util

        spec = importlib.util.find_spec("sentence_transformers")
        if spec is not None:
            from sentence_transformers import SentenceTransformer
            EMBEDDING_AVAILABLE = True
            return SentenceTransformer
        else:
            logger.warning("sentence-transformers não instalado")
            EMBEDDING_AVAILABLE = False
            return None
    except Exception:
        logger.warning("Não foi possível carregar sentence-transformers")
        EMBEDDING_AVAILABLE = False
        return None


# Tentar importar SentenceTransformer de forma segura
SentenceTransformer = _safe_import_sentence_transformers()


class RagManager:
    """Gerenciador de RAG local com suporte a chunks e busca vetorial."""

    MAX_CHUNKS = 8000
    MAX_CHUNK_SIZE = 2000
    EMBEDDING_MODEL = "distiluse-base-multilingual-cased-v2"  # Leve, multilíngue
    DB_PATH = "data/rag_database.db"

    def __init__(self):
        """Inicializar gerenciador RAG."""
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)

        self.db_path = self.data_dir / self.DB_PATH.split("/")[1]
        self.chunks: dict[str, dict] = {}
        self.conversation_history: list[dict] = []
        self.meeting_transcripts: list[dict] = []

        # Embedding model
        self.embedding_model = None
        if EMBEDDING_AVAILABLE:
            self._load_embedding_model()

        # Inicializar banco de dados
        self._init_database()

        logger.info("RAG Manager inicializado")

    def _load_embedding_model(self):
        """Carregar modelo de embeddings (async)."""
        try:
            if SentenceTransformer is None:
                logger.warning("SentenceTransformer não disponível")
                return
            self.embedding_model = SentenceTransformer(self.EMBEDDING_MODEL)
            logger.info("Modelo de embeddings carregado")
        except Exception as e:
            logger.error("Erro ao carregar modelo: %s", e)
            self.embedding_model = None

    def _init_database(self):
        """Inicializar banco de dados SQLite para armazenamento de chunks."""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            # Tabela de chunks
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS chunks (
                    id TEXT PRIMARY KEY,
                    text TEXT NOT NULL,
                    metadata TEXT,
                    embedding BLOB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    source TEXT
                )
                """
            )

            # Tabela de histórico de conversas
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS conversation_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_input TEXT,
                    assistant_response TEXT,
                    context_chunks TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            # Tabela de transcrições de reuniões
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS meeting_transcripts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT,
                    transcript TEXT,
                    summary TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    duration_seconds INTEGER
                )
                """
            )

            # Índices para busca rápida
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_source ON chunks(source)")
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_created ON chunks(created_at)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_conv_timestamp ON conversation_history(timestamp)"
            )

            conn.commit()
            conn.close()
            logger.info("Banco de dados RAG inicializado em %s", self.db_path)
        except Exception as e:
            logger.error("Erro ao inicializar banco RAG: %s", e)

    async def add_chunk(
        self, text: str, metadata: dict = None, source: str = "user"
    ) -> str:
        """
        Adicionar novo chunk à base de conhecimento.

        Args:
            text: Texto do chunk (até 2000 caracteres)
            metadata: Metadados adicionais
            source: Fonte do chunk (user, transcript, web, etc)

        Returns:
            ID do chunk criado
        """
        if len(text) > self.MAX_CHUNK_SIZE:
            logger.warning(
                "Chunk truncado: %d > %d caracteres",
                len(text),
                self.MAX_CHUNK_SIZE,
            )
            text = text[: self.MAX_CHUNK_SIZE]

        chunk_id = f"chunk_{len(self.chunks)}_{datetime.now().timestamp()}"
        embedding = None

        # Gerar embedding se model disponível
        if self.embedding_model:
            try:
                embedding = self.embedding_model.encode(text)
            except Exception as e:
                logger.warning("Erro ao gerar embedding: %s", e)

        chunk_data = {
            "text": text,
            "metadata": metadata or {},
            "embedding": embedding,
            "source": source,
            "created_at": datetime.now().isoformat(),
        }

        self.chunks[chunk_id] = chunk_data

        # Persistir no banco
        self._save_chunk_to_db(chunk_id, chunk_data)

        logger.debug("Chunk adicionado: %s (%d caracteres)", chunk_id, len(text))
        return chunk_id

    def _save_chunk_to_db(self, chunk_id: str, chunk_data: dict):
        """Salvar chunk no banco de dados."""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            embedding_blob = None
            if chunk_data["embedding"] is not None:
                embedding_blob = np.array(chunk_data["embedding"]).tobytes()

            cursor.execute(
                """
                INSERT OR REPLACE INTO chunks (id, text, metadata, embedding, source)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    chunk_id,
                    chunk_data["text"],
                    json.dumps(chunk_data["metadata"]),
                    embedding_blob,
                    chunk_data["source"],
                ),
            )

            conn.commit()
            conn.close()
        except Exception as e:
            logger.error("Erro ao salvar chunk no DB: %s", e)

    async def retrieve_chunks(
        self, query: str, top_k: int = 5, use_embedding: bool = True
    ) -> list[dict]:
        """
        Recuperar chunks mais relevantes baseado na query.

        Args:
            query: Consulta do usuário
            top_k: Número de chunks a recuperar
            use_embedding: Usar busca vetorial se disponível

        Returns:
            Lista dos chunks mais relevantes
        """
        if not self.chunks:
            logger.debug("Base de chunks vazia")
            return []

        retrieved = []

        if use_embedding and self.embedding_model:
            try:
                query_embedding = self.embedding_model.encode(query)
                similarities = {}

                for chunk_id, chunk_data in self.chunks.items():
                    if chunk_data["embedding"] is not None:
                        similarity = np.dot(
                            query_embedding, chunk_data["embedding"]
                        ) / (
                            np.linalg.norm(query_embedding)
                            * np.linalg.norm(chunk_data["embedding"])
                        )
                        similarities[chunk_id] = similarity

                # Ordenar por similaridade
                sorted_chunks = sorted(
                    similarities.items(), key=lambda x: x[1], reverse=True
                )[:top_k]

                retrieved = [
                    {
                        "id": chunk_id,
                        **self.chunks[chunk_id],
                        "similarity": float(score),
                    }
                    for chunk_id, score in sorted_chunks
                ]

                logger.debug("Recuperados %d chunks por embedding", len(retrieved))
            except Exception as e:
                logger.warning("Erro em busca vetorial, usando fallback: %s", e)
                retrieved = list(self.chunks.values())[:top_k]
        else:
            # Fallback: retornar chunks mais recentes
            recent = sorted(
                self.chunks.items(),
                key=lambda x: x[1]["created_at"],
                reverse=True,
            )[:top_k]
            retrieved = [{"id": cid, **cdata} for cid, cdata in recent]

        return retrieved

    async def add_conversation_turn(
        self,
        user_input: str,
        assistant_response: str,
        context_chunks: list[str] = None,
    ):
        """
        Adicionar turno de conversa ao histórico expandido.

        Args:
            user_input: Input do usuário
            assistant_response: Resposta do assistente
            context_chunks: IDs dos chunks usados como contexto
        """
        turn = {
            "id": len(self.conversation_history),
            "user_input": user_input,
            "assistant_response": assistant_response,
            "context_chunks": context_chunks or [],
            "timestamp": datetime.now().isoformat(),
        }

        self.conversation_history.append(turn)

        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO conversation_history
                (user_input, assistant_response, context_chunks)
                VALUES (?, ?, ?)
                """,
                (user_input, assistant_response, json.dumps(context_chunks or [])),
            )

            conn.commit()
            conn.close()
        except Exception as e:
            logger.error("Erro ao salvar conversa: %s", e)

        logger.debug(
            "Conversa adicionada: %d turnos no histórico",
            len(self.conversation_history),
        )

    def get_conversation_context(self, window_size: int = 10) -> str:
        """
        Obter contexto de conversa expandido (últimas N turnos).

        Args:
            window_size: Número de últimos turnos a incluir

        Returns:
            String formatada com histórico de conversa
        """
        recent_turns = self.conversation_history[-window_size:]
        context = "=== HISTÓRICO DE CONVERSA RECENTE ===\n\n"

        for turn in recent_turns:
            context += f"👤 Usuário: {turn['user_input']}\n"
            context += f"🤖 Assistente: {turn['assistant_response']}\n"
            context += f"⏰ {turn['timestamp']}\n\n"

        return context

    async def add_meeting_transcript(
        self,
        title: str,
        transcript: str,
        duration_seconds: int = 0,
    ) -> str:
        """
        Adicionar transcrição de reunião/áudio capturado.

        Args:
            title: Título da reunião
            transcript: Transcrição completa
            duration_seconds: Duração em segundos

        Returns:
            ID da reunião
        """
        # Quebrar transcrição em chunks de 2000 caracteres
        chunks_ids = []
        for i in range(0, len(transcript), self.MAX_CHUNK_SIZE):
            chunk_text = transcript[i : i + self.MAX_CHUNK_SIZE]
            chunk_id = await self.add_chunk(
                chunk_text,
                metadata={"meeting": title, "part": i // self.MAX_CHUNK_SIZE},
                source="meeting_transcript",
            )
            chunks_ids.append(chunk_id)

        # Gerar resumo automático
        summary = await self._generate_summary(transcript)

        meeting = {
            "title": title,
            "transcript": transcript,
            "summary": summary,
            "timestamp": datetime.now().isoformat(),
            "duration_seconds": duration_seconds,
            "chunk_ids": chunks_ids,
        }

        self.meeting_transcripts.append(meeting)

        # Persistir no banco
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO meeting_transcripts
                (title, transcript, summary, duration_seconds)
                VALUES (?, ?, ?, ?)
                """,
                (title, transcript, summary, duration_seconds),
            )

            conn.commit()
            conn.close()
        except Exception as e:
            logger.error("Erro ao salvar reunião: %s", e)

        logger.info(
            "Reunião adicionada: %s (%d chunks, resumido em %d palavras)",
            title,
            len(chunks_ids),
            len(summary.split()),
        )

        return title

    async def _generate_summary(self, text: str, max_length: int = 500) -> str:
        """
        Gerar resumo de texto usando heurísticas simples.
        (Em produção, usar Ollama com llava para melhor qualidade)

        Args:
            text: Texto a resumir
            max_length: Tamanho máximo do resumo

        Returns:
            Resumo do texto
        """
        sentences = text.split(".")
        if len(sentences) <= 3:
            return text

        # Estratégia simples: pegar primeiras e últimas sentenças
        summary_sentences = (
            sentences[:2] + ["..."] + sentences[-2:]
        )  # TODO: usar Ollama para melhor resumo
        summary = ".".join(summary_sentences).strip()

        if len(summary) > max_length:
            summary = summary[:max_length] + "..."

        return summary

    async def search_meetings(self, query: str) -> list[dict]:
        """
        Buscar reuniões por query.

        Args:
            query: Query de busca

        Returns:
            Lista de reuniões relevantes
        """
        retrieved_chunks = await self.retrieve_chunks(query, top_k=10)

        # Encontrar reuniões correspondentes
        meeting_ids = set()
        for chunk in retrieved_chunks:
            if chunk.get("source") == "meeting_transcript":
                meeting_title = chunk.get("metadata", {}).get("meeting")
                if meeting_title:
                    meeting_ids.add(meeting_title)

        # Retornar dados das reuniões
        results = [m for m in self.meeting_transcripts if m["title"] in meeting_ids]
        logger.debug("Encontradas %d reuniões para query: %s", len(results), query)

        return results

    def cleanup_old_data(self, days: int = 30):
        """
        Limpar dados antigos (mais de N dias).

        Args:
            days: Número de dias a manter
        """
        cutoff_date = datetime.now() - timedelta(days=days)

        # Limpar chunks antigos
        removed_chunks = 0
        for chunk_id in list(self.chunks.keys()):
            created_at = datetime.fromisoformat(self.chunks[chunk_id]["created_at"])
            if created_at < cutoff_date:
                del self.chunks[chunk_id]
                removed_chunks += 1

        # Limpar histórico antigo do DB
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            cursor.execute(
                """
                DELETE FROM conversation_history
                WHERE timestamp < datetime('now', ? || ' days')
                """,
                (f"-{days}",),
            )

            conn.commit()
            conn.close()
        except Exception as e:
            logger.error("Erro ao limpar dados antigos: %s", e)

        logger.info("Limpeza: removidos %d chunks antigos", removed_chunks)

    def get_stats(self) -> dict:
        """Obter estatísticas do RAG."""
        return {
            "total_chunks": len(self.chunks),
            "max_chunks": self.MAX_CHUNKS,
            "conversation_turns": len(self.conversation_history),
            "meetings": len(self.meeting_transcripts),
            "embedding_enabled": self.embedding_model is not None,
            "db_path": str(self.db_path),
        }
