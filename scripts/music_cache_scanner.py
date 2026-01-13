#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MúsicaDispositivo cache/musicDiretórioEmdeMúsicaArquivo，Dados，.

: pip install mutagen
"""

import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

try:
    from mutagen import File as MutagenFile
    from mutagen.id3 import ID3NoHeaderError
except ImportError:
    print("Erro:  mutagen Banco de dados")
    print(": pip install mutagen")
    sys.exit(1)

# Diretório
PROJECT_ROOT = Path(__file__).parent.parent


class MusicMetadata:
    """
    Música  Dados.
    """

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.filename = file_path.name
        self.file_id = file_path.stem  # Arquivo，ID
        self.file_size = file_path.stat().st_size
        self.creation_time = datetime.fromtimestamp(file_path.stat().st_ctime)
        self.modification_time = datetime.fromtimestamp(file_path.stat().st_mtime)

        # deArquivode  Dados
        self.title = None
        self.artist = None
        self.album = None
        self.genre = None
        self.year = None
        self.duration = None  # Segundos
        self.bitrate = None
        self.sample_rate = None

        # Arquivo（）
        self.file_hash = self._calculate_hash()

    def _calculate_hash(self) -> str:
        """
        ArquivoMD5Valor（1MBArquivo）
        """
        try:
            hash_md5 = hashlib.md5()
            with open(self.file_path, "rb") as f:
                # 1MB
                chunk = f.read(1024 * 1024)
                hash_md5.update(chunk)
            return hash_md5.hexdigest()[:16]  # 16Bits
        except Exception:
            return "unknown"

    def extract_metadata(self) -> bool:
        """
        MúsicaArquivo  Dados.
        """
        try:
            audio_file = MutagenFile(self.file_path)
            if audio_file is None:
                return False

            # Informação
            if hasattr(audio_file, "info"):
                self.duration = getattr(audio_file.info, "length", None)
                self.bitrate = getattr(audio_file.info, "bitrate", None)
                self.sample_rate = getattr(audio_file.info, "sample_rate", None)

            # ID3Informação
            tags = audio_file.tags if audio_file.tags else {}

            # 
            self.title = self._get_tag_value(tags, ["TIT2", "TITLE", "\xa9nam"])

            # 
            self.artist = self._get_tag_value(tags, ["TPE1", "ARTIST", "\xa9ART"])

            # 
            self.album = self._get_tag_value(tags, ["TALB", "ALBUM", "\xa9alb"])

            # 
            self.genre = self._get_tag_value(tags, ["TCON", "GENRE", "\xa9gen"])

            # 
            year_raw = self._get_tag_value(tags, ["TDRC", "DATE", "YEAR", "\xa9day"])
            if year_raw:
                # 
                year_str = str(year_raw)
                if year_str.isdigit():
                    self.year = int(year_str)
                else:
                    # TentativadeDataCaracteres  Em
                    import re

                    year_match = re.search(r"(\d{4})", year_str)
                    if year_match:
                        self.year = int(year_match.group(1))

            return True

        except ID3NoHeaderError:
            # NenhumID3，Não  Erro
            return True
        except Exception as e:
            print(f"DadosFalha {self.filename}: {e}")
            return False

    def _get_tag_value(self, tags: dict, tag_names: List[str]) -> Optional[str]:
        """
        dedeEmValor.
        """
        for tag_name in tag_names:
            if tag_name in tags:
                value = tags[tag_name]
                if isinstance(value, list) and value:
                    return str(value[0])
                elif value:
                    return str(value)
        return None

    def format_duration(self) -> str:
        """
        Formato Conversão Reprodução.
        """
        if self.duration is None:
            return "Não"

        minutes = int(self.duration) // 60
        seconds = int(self.duration) % 60
        return f"{minutes:02d}:{seconds:02d}"

    def format_file_size(self) -> str:
        """
        Formato Conversão ArquivoTamanho.
        """
        size = self.file_size
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"

    def to_dict(self) -> Dict:
        """
        paraFormato.
        """
        return {
            "file_id": self.file_id,
            "filename": self.filename,
            "title": self.title,
            "artist": self.artist,
            "album": self.album,
            "genre": self.genre,
            "year": self.year,
            "duration": self.duration,
            "duration_formatted": self.format_duration(),
            "bitrate": self.bitrate,
            "sample_rate": self.sample_rate,
            "file_size": self.file_size,
            "file_size_formatted": self.format_file_size(),
            "file_hash": self.file_hash,
            "creation_time": self.creation_time.isoformat(),
            "modification_time": self.modification_time.isoformat(),
        }


class MusicCacheScanner:
    """
    MúsicaDispositivo.
    """

    def __init__(self, cache_dir: Path = None):
        self.cache_dir = cache_dir or PROJECT_ROOT / "cache" / "music"
        self.playlist: List[MusicMetadata] = []
        self.scan_stats = {
            "total_files": 0,
            "success_count": 0,
            "error_count": 0,
            "total_duration": 0,
            "total_size": 0,
        }

    def scan_cache(self) -> bool:
        """
        Diretório.
        """
        print(f"🎵 ComeçarMúsicaDiretório: {self.cache_dir}")

        if not self.cache_dir.exists():
            print(f"❌ DiretórioNãoExiste: {self.cache_dir}")
            return False

        # PesquisarMúsicaArquivo
        music_files = []
        for pattern in ["*.mp3", "*.m4a", "*.flac", "*.wav", "*.ogg"]:
            music_files.extend(self.cache_dir.glob(pattern))

        if not music_files:
            print("📁 DiretórioEmNenhumEncontradoMúsicaArquivo")
            return False

        self.scan_stats["total_files"] = len(music_files)
        print(f"📊 Encontrado {len(music_files)} MúsicaArquivo")

        # Arquivo
        for i, file_path in enumerate(music_files, 1):
            print(f"🔍 [{i}/{len(music_files)}] : {file_path.name}")

            try:
                metadata = MusicMetadata(file_path)

                if metadata.extract_metadata():
                    self.playlist.append(metadata)
                    self.scan_stats["success_count"] += 1

                    # 
                    if metadata.duration:
                        self.scan_stats["total_duration"] += metadata.duration
                    self.scan_stats["total_size"] += metadata.file_size

                    # Informação
                    display_title = metadata.title or "Não"
                    display_artist = metadata.artist or "Não"
                    print(
                        f"   ✅ {display_title} - {display_artist} ({metadata.format_duration()})"
                    )
                else:
                    self.scan_stats["error_count"] += 1
                    print("   ❌ DadosFalha")

            except Exception as e:
                self.scan_stats["error_count"] += 1
                print(f"   ❌ ProcessandoFalha: {e}")

        return True

    def remove_duplicates(self):
        """
        deMúsicaArquivo（Valor）
        """
        seen_hashes = set()
        unique_playlist = []
        duplicates = []

        for metadata in self.playlist:
            if metadata.file_hash in seen_hashes:
                duplicates.append(metadata)
            else:
                seen_hashes.add(metadata.file_hash)
                unique_playlist.append(metadata)

        if duplicates:
            print(f"🔄  {len(duplicates)} Arquivo:")
            for dup in duplicates:
                print(f"   - {dup.filename}")

        self.playlist = unique_playlist

    def sort_playlist(self, sort_by: str = "artist"):
        """
        .
        """
        sort_functions = {
            "artist": lambda x: (
                x.artist or "Unknown",
                x.album or "Unknown",
                x.title or "Unknown",
            ),
            "title": lambda x: x.title or "Unknown",
            "album": lambda x: (x.album or "Unknown", x.artist or "Unknown"),
            "duration": lambda x: x.duration or 0,
            "file_size": lambda x: x.file_size,
            "creation_time": lambda x: x.creation_time,
        }

        if sort_by in sort_functions:
            self.playlist.sort(key=sort_functions[sort_by])
            print(f"📋 Já {sort_by} ")

    def print_statistics(self):
        """
        Informação.
        """
        stats = self.scan_stats
        print("\n📊 :")
        print(f"   Arquivo: {stats['total_files']}")
        print(f"   SucessoProcessando: {stats['success_count']}")
        print(f"   ProcessandoFalha: {stats['error_count']}")
        print(f"   Sucesso: {stats['success_count']/stats['total_files']*100:.1f}%")

        # 
        total_hours = stats["total_duration"] // 3600
        total_minutes = (stats["total_duration"] % 3600) // 60
        print(f"   Reprodução: {total_hours}{total_minutes}")

        # Tamanho
        total_size_mb = stats["total_size"] / (1024 * 1024)
        print(f"   ArquivoTamanho: {total_size_mb:.1f} MB")

        # Informação
        if stats["success_count"] > 0:
            avg_duration = stats["total_duration"] / stats["success_count"]
            avg_size = stats["total_size"] / stats["success_count"]
            print(f"   : {int(avg_duration//60)}:{int(avg_duration%60):02d}")
            print(f"   Tamanho: {avg_size/(1024*1024):.1f} MB")

    def print_playlist(self, limit: int = None):
        """
        .
        """
        print(f"\n🎵 Música ( {len(self.playlist)} )")
        print("=" * 80)

        for i, metadata in enumerate(
            self.playlist[:limit] if limit else self.playlist, 1
        ):
            title = metadata.title or "Não"
            artist = metadata.artist or "Não"
            album = metadata.album or "Não"
            duration = metadata.format_duration()

            print(f"{i:3d}. {title}")
            print(f"     : {artist}")
            print(f"     : {album}")
            print(f"     : {duration} | ArquivoID: {metadata.file_id}")
            print()

        if limit and len(self.playlist) > limit:
            print(f"... Ainda {len(self.playlist) - limit} ")

    def export_playlist(self, output_file: Path = None, format: str = "json"):
        """
        .
        """
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = PROJECT_ROOT / f"local_playlist_{timestamp}.{format}"

        try:
            if format == "json":
                playlist_data = {
                    "metadata": {
                        "generated_at": datetime.now().isoformat(),
                        "cache_directory": str(self.cache_dir),
                        "total_songs": len(self.playlist),
                        "statistics": self.scan_stats,
                    },
                    "playlist": [metadata.to_dict() for metadata in self.playlist],
                }

                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(playlist_data, f, ensure_ascii=False, indent=2)

            elif format == "m3u":
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write("#EXTM3U\n")
                    for metadata in self.playlist:
                        title = metadata.title or metadata.filename
                        artist = metadata.artist or "Unknown Artist"
                        duration = int(metadata.duration) if metadata.duration else -1

                        f.write(f"#EXTINF:{duration},{artist} - {title}\n")
                        f.write(f"{metadata.file_path}\n")

            print(f"📄 Jápara: {output_file}")
            return output_file

        except Exception as e:
            print(f"❌ Falha: {e}")
            return None

    def search_songs(self, query: str) -> List[MusicMetadata]:
        """
        Pesquisa.
        """
        query = query.lower()
        results = []

        for metadata in self.playlist:
            # Em、、EmPesquisa
            searchable_text = " ".join(
                filter(
                    None,
                    [
                        metadata.title,
                        metadata.artist,
                        metadata.album,
                        metadata.filename,
                    ],
                )
            ).lower()

            if query in searchable_text:
                results.append(metadata)

        return results

    def get_artists(self) -> Dict[str, List[MusicMetadata]]:
        """
        .
        """
        artists = {}
        for metadata in self.playlist:
            artist = metadata.artist or "Não"
            if artist not in artists:
                artists[artist] = []
            artists[artist].append(metadata)
        return artists

    def get_albums(self) -> Dict[str, List[MusicMetadata]]:
        """
        .
        """
        albums = {}
        for metadata in self.playlist:
            album_key = (
                f"{metadata.album or 'Não'} - {metadata.artist or 'Não'}"
            )
            if album_key not in albums:
                albums[album_key] = []
            albums[album_key].append(metadata)
        return albums


def main():
    """
    .
    """
    print("🎵 MúsicaDispositivo")
    print("=" * 50)

    # Dispositivo
    scanner = MusicCacheScanner()

    # 
    if not scanner.scan_cache():
        return

    # Arquivo
    scanner.remove_duplicates()

    # 
    scanner.sort_playlist("artist")

    # Informação
    scanner.print_statistics()

    # （Limitado a20）
    scanner.print_playlist(limit=20)

    # 
    while True:
        print("\n" + "=" * 50)
        print("SelecionandoOperação:")
        print("1. ")
        print("2. ")
        print("3. ")
        print("4. Pesquisa")
        print("5.  (JSON)")
        print("6.  (M3U)")
        print("7. Novamente")
        print("0. ")

        choice = input("\n  Selecionando (0-7): ").strip()

        if choice == "0":
            break
        elif choice == "1":
            scanner.print_playlist()
        elif choice == "2":
            artists = scanner.get_artists()
            for artist, songs in artists.items():
                print(f"\n🎤 {artist} ({len(songs)} )")
                for song in songs:
                    title = song.title or song.filename
                    print(f"   - {title} ({song.format_duration()})")
        elif choice == "3":
            albums = scanner.get_albums()
            for album, songs in albums.items():
                print(f"\n💿 {album} ({len(songs)} )")
                for song in songs:
                    title = song.title or song.filename
                    print(f"   - {title} ({song.format_duration()})")
        elif choice == "4":
            query = input("EntradaPesquisa: ").strip()
            if query:
                results = scanner.search_songs(query)
                if results:
                    print(f"\n🔍 Encontrado {len(results)} :")
                    for i, song in enumerate(results, 1):
                        title = song.title or song.filename
                        artist = song.artist or "Não"
                        print(f"   {i}. {title} - {artist} ({song.format_duration()})")
                else:
                    print("🔍 NenhumEncontradoCorrespondênciade")
        elif choice == "5":
            scanner.export_playlist(format="json")
        elif choice == "6":
            scanner.export_playlist(format="m3u")
        elif choice == "7":
            print(":")
            print("1. ")
            print("2. ")
            print("3. ")
            print("4. ")
            print("5. ArquivoTamanho")
            print("6. Tempo")

            sort_choice = input("Selecionando (1-6): ").strip()
            sort_map = {
                "1": "artist",
                "2": "title",
                "3": "album",
                "4": "duration",
                "5": "file_size",
                "6": "creation_time",
            }

            if sort_choice in sort_map:
                scanner.sort_playlist(sort_map[sort_choice])
                print("✅ Concluído")
        else:
            print("❌ Selecionando")

    print("\n👋 !")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Em，")
    except Exception as e:
        print(f"\n❌ Exceção: {e}")
        import traceback

        traceback.print_exc()
