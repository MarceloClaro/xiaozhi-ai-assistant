"""MúsicaDispositivo.

MúsicadeInicializando、configuraçãoeMCP
"""

from typing import Any, Dict

from src.utils.logging_config import get_logger

from .music_player import get_music_player_instance

logger = get_logger(__name__)


class MusicToolsManager:
    """
    MúsicaDispositivo.
    """

    def __init__(self):
        """
        InicializandoMúsicaDispositivo.
        """
        self._initialized = False
        self._music_player = None
        logger.info("[MusicManager] MúsicaDispositivoInicializando")

    def init_tools(self, add_tool, PropertyList, Property, PropertyType):
        """
        InicializandoMúsica.
        """
        try:
            logger.info("[MusicManager] ComeçarMúsica")

            # MúsicaReproduçãoDispositivo
            self._music_player = get_music_player_instance()

            # Pesquisa  Reprodução
            self._register_search_and_play_tool(
                add_tool, PropertyList, Property, PropertyType
            )

            # Pausado
            self._register_pause_tool(add_tool, PropertyList)

            # Restaurando
            self._register_resume_tool(add_tool, PropertyList)

            # Parar
            self._register_stop_tool(add_tool, PropertyList)

            # Pulando para
            self._register_seek_tool(add_tool, PropertyList, Property, PropertyType)

            # 
            self._register_get_lyrics_tool(add_tool, PropertyList)

            # 
            self._register_get_local_playlist_tool(
                add_tool, PropertyList, Property, PropertyType
            )

            self._initialized = True
            logger.info("[MusicManager] MúsicaConcluído")

        except Exception as e:
            logger.error(f"[MusicManager] MúsicaFalha: {e}", exc_info=True)
            raise

    def _register_search_and_play_tool(
        self, add_tool, PropertyList, Property, PropertyType
    ):
        """
        Pesquisa  Reprodução.
        """

        async def search_and_play_wrapper(args: Dict[str, Any]) -> str:
            song_name = args.get("song_name", "")
            result = await self._music_player.search_and_play(song_name)
            return result.get("message", "PesquisaReproduçãoConcluído")

        search_props = PropertyList([Property("song_name", PropertyType.STRING)])

        add_tool(
            (
                "music_player.search_and_play",
                "Pesquisa  Reproduçãode。Em  PesquisaAutomáticoComeçarReprodução。"
                "SeJáMúsicaEmReprodução，AutomáticoPararMúsica  Reprodução。"
                "Reproduçãode，'Reproduçãode'、''。",
                search_props,
                search_and_play_wrapper,
            )
        )
        logger.debug("[MusicManager] PesquisaReproduçãoSucesso")

    def _register_pause_tool(self, add_tool, PropertyList):
        """
        Pausado.
        """

        async def pause_wrapper(args: Dict[str, Any]) -> str:
            result = await self._music_player.pause()
            return result.get("message", "JáPausado")

        add_tool(
            (
                "music_player.pause",
                "PausadoEmReproduçãodeMúsica。ImediatamentePararMúsicaReprodução，Posição。"
                " resume RestaurandoReprodução。"
                "：Não  Em TTS ，TTS AutomáticoPausadoMúsica。"
                "'Pausado'、'PausadoMúsica'、''Aguardar。",
                PropertyList(),
                pause_wrapper,
            )
        )
        logger.debug("[MusicManager] PausadoSucesso")

    def _register_resume_tool(self, add_tool, PropertyList):
        """
        Restaurando.
        """

        async def resume_wrapper(args: Dict[str, Any]) -> str:
            result = await self._music_player.resume()
            return result.get("message", "JáRestaurandoReprodução")

        add_tool(
            (
                "music_player.resume",
                "RestaurandoReproduçãoPausadodeMúsica。dePausadodePosiçãoContinuarReprodução。"
                "Música'JáPausado'Estado（Pausado）。"
                "SeMúsica TTS ，TTS FinalAutomáticoRestaurando，。",
                PropertyList(),
                resume_wrapper,
            )
        )
        logger.debug("[MusicManager] RestaurandoSucesso")

    def _register_stop_tool(self, add_tool, PropertyList):
        """
        Parar.
        """

        async def stop_wrapper(args: Dict[str, Any]) -> str:
            result = await self._music_player.stop()
            return result.get("message", "PararReproduçãoConcluído")

        add_tool(
            (
                "music_player.stop",
                "PararMúsicaReprodução。PararReproduçãoPosiçãopara。"
                "com pause（Pausado）de：stop FinalReprodução，pause Pausado。"
                "'PararMúsica'、'FechandoMúsica'、''AguardarFinalReproduçãode。",
                PropertyList(),
                stop_wrapper,
            )
        )
        logger.debug("[MusicManager] PararSucesso")

    def _register_seek_tool(self, add_tool, PropertyList, Property, PropertyType):
        """
        Pulando para.
        """

        async def seek_wrapper(args: Dict[str, Any]) -> str:
            position = args.get("position", 0)
            result = await self._music_player.seek(float(position))
            return result.get("message", "Pulando paraConcluído")

        seek_props = PropertyList(
            [Property("position", PropertyType.INTEGER, min_value=0)]
        )

        add_tool(
            (
                "music_player.seek",
                "Pulando paraparadePosição。position Parâmetro  BitsparaSegundos（de）。"
                "'para2'、'para'、'para'、'Pulando para30%'、'para30Segundos'Aguardar。"
                "：Se'30Segundos'，Posição，30Segundos。",
                seek_props,
                seek_wrapper,
            )
        )
        logger.debug("[MusicManager] Pulando paraSucesso")

    def _register_get_lyrics_tool(self, add_tool, PropertyList):
        """
        .
        """

        async def get_lyrics_wrapper(args: Dict[str, Any]) -> str:
            result = await self._music_player.get_lyrics()
            if result.get("status") == "success":
                lyrics = result.get("lyrics", [])
                return ":\n" + "\n".join(lyrics)
            else:
                return result.get("message", "Falha")

        add_tool(
            (
                "music_player.get_lyrics",
                "Reproduçãode。RetornoTempo。"
                "'de'、''、'de'Aguardar。",
                PropertyList(),
                get_lyrics_wrapper,
            )
        )
        logger.debug("[MusicManager] Sucesso")

    def _register_get_local_playlist_tool(
        self, add_tool, PropertyList, Property, PropertyType
    ):
        """
        .
        """

        async def get_local_playlist_wrapper(args: Dict[str, Any]) -> str:
            force_refresh = args.get("force_refresh", False)
            result = await self._music_player.get_local_playlist(force_refresh)

            if result.get("status") == "success":
                playlist = result.get("playlist", [])
                total_count = result.get("total_count", 0)

                if playlist:
                    playlist_text = f"Música ({total_count}):\n"
                    playlist_text += "\n".join(playlist)
                    return playlist_text
                else:
                    return "EmNenhumMúsicaArquivo"
            else:
                return result.get("message", "Falha")

        refresh_props = PropertyList(
            [Property("force_refresh", PropertyType.BOOLEAN, default_value=False)]
        )

        add_tool(
            (
                "music_player.get_local_playlist",
                "Música。Jáde。"
                "RetornoFormato：' - '，' - '。"
                "''、''、'Música'Aguardar。"
                "：ReproduçãoEmde，Usando search_and_play，"
                "' - '， search_and_play(song_name='') 。",
                refresh_props,
                get_local_playlist_wrapper,
            )
        )
        logger.debug("[MusicManager] Sucesso")

    def _format_time(self, seconds: float) -> str:
        """
        Segundos  Formato Conversão para mm:ss Formato.
        """
        minutes = int(seconds) // 60
        seconds = int(seconds) % 60
        return f"{minutes:02d}:{seconds:02d}"

    def is_initialized(self) -> bool:
        """
        PesquisarDispositivoInicializando.
        """
        return self._initialized


# Dispositivo
_music_tools_manager = None


def get_music_tools_manager() -> MusicToolsManager:
    """
    MúsicaDispositivo.
    """
    global _music_tools_manager
    if _music_tools_manager is None:
        _music_tools_manager = MusicToolsManager()
        logger.debug("[MusicManager] MúsicaDispositivo")
    return _music_tools_manager
