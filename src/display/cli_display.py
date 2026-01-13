import asyncio
import logging
import os
import shutil
import sys
import termios
import tty
from collections import deque
from typing import Callable, Optional

from src.display.base_display import BaseDisplay


class CliDisplay(BaseDisplay):
    def __init__(self):
        super().__init__()
        self.running = True
        self._use_ansi = sys.stdout.isatty()
        self._loop = None
        self._last_drawn_rows = 0

        # Dados（）
        self._dash_status = ""
        self._dash_connected = False
        self._dash_text = ""
        self._dash_emotion = ""
        # ：（ + Entrada）
        # Entrada（ + Entrada），EmEntradade
        self._input_area_lines = 3
        self._dashboard_lines = 8  # （Altura）

        # /（Em TTY ）
        self._ansi = {
            "reset": "\x1b[0m",
            "bold": "\x1b[1m",
            "dim": "\x1b[2m",
            "blue": "\x1b[34m",
            "cyan": "\x1b[36m",
            "green": "\x1b[32m",
            "yellow": "\x1b[33m",
            "magenta": "\x1b[35m",
        }

        # 
        self.auto_callback = None
        self.abort_callback = None
        self.send_text_callback = None
        self.mode_callback = None

        # FilaProcessandoComando
        self.command_queue = asyncio.Queue()

        # Log（Em CLI ，Nãopara）
        self._log_lines: deque[str] = deque(maxlen=6)
        self._install_log_handler()

    async def set_callbacks(
        self,
        press_callback: Optional[Callable] = None,
        release_callback: Optional[Callable] = None,
        mode_callback: Optional[Callable] = None,
        auto_callback: Optional[Callable] = None,
        abort_callback: Optional[Callable] = None,
        send_text_callback: Optional[Callable] = None,
    ):
        """
        Configurando.
        """
        self.auto_callback = auto_callback
        self.abort_callback = abort_callback
        self.send_text_callback = send_text_callback
        self.mode_callback = mode_callback

    async def update_button_status(self, text: str):
        """
        estado.
        """
        # Conversão：Estado  EmEm
        self._dash_text = text
        await self._render_dashboard()

    async def update_status(self, status: str, connected: bool):
        """
        estado（，Não）。
        """
        self._dash_status = status
        self._dash_connected = bool(connected)
        await self._render_dashboard()

    async def update_text(self, text: str):
        """
        （，Não）。
        """
        if text and text.strip():
            self._dash_text = text.strip()
            await self._render_dashboard()

    async def update_emotion(self, emotion_name: str):
        """
        （，Não）。
        """
        self._dash_emotion = emotion_name
        await self._render_dashboard()

    async def start(self):
        """
        IniciandoCLI.
        """
        self._loop = asyncio.get_running_loop()
        await self._init_screen()

        # IniciandoComandoProcessando
        command_task = asyncio.create_task(self._command_processor())
        input_task = asyncio.create_task(self._keyboard_input_loop())

        try:
            await asyncio.gather(command_task, input_task)
        except KeyboardInterrupt:
            await self.close()

    async def _command_processor(self):
        """
        ComandoProcessandoDispositivo.
        """
        while self.running:
            try:
                command = await asyncio.wait_for(self.command_queue.get(), timeout=1.0)
                if asyncio.iscoroutinefunction(command):
                    await command()
                else:
                    command()
            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"ComandoProcessandoErro: {e}")

    async def _keyboard_input_loop(self):
        """
        Entrada.
        """
        try:
            while self.running:
                # EmTTY，EntradaEntrada
                if self._use_ansi:
                    await self._render_input_area()
                    # Entrada（），Entrada，EmCaracteres
                    cmd = await asyncio.to_thread(self._read_line_raw)
                    # Entrada（deEm）
                    self._clear_input_area()
                    await self._render_dashboard()
                else:
                    cmd = await asyncio.to_thread(input)
                await self._handle_command(cmd.lower().strip())
        except asyncio.CancelledError:
            pass

    # ===== Logpara =====
    def _install_log_handler(self) -> None:
        class _DisplayLogHandler(logging.Handler):
            def __init__(self, display: "CliDisplay"):
                super().__init__()
                self.display = display

            def emit(self, record: logging.LogRecord) -> None:
                try:
                    msg = self.format(record)
                    self.display._log_lines.append(msg)
                    loop = self.display._loop
                    if loop and self.display._use_ansi:
                        loop.call_soon_threadsafe(
                            lambda: asyncio.create_task(
                                self.display._render_dashboard()
                            )
                        )
                except Exception:
                    pass

        root = logging.getLogger()
        #  stdout/stderr deProcessandoDispositivo，
        for h in list(root.handlers):
            if isinstance(h, logging.StreamHandler) and getattr(h, "stream", None) in (
                sys.stdout,
                sys.stderr,
            ):
                root.removeHandler(h)

        handler = _DisplayLogHandler(self)
        handler.setLevel(logging.WARNING)
        handler.setFormatter(
            logging.Formatter(
                fmt="%(asctime)s [%(name)s] - %(levelname)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
        root.addHandler(handler)

    async def _handle_command(self, cmd: str):
        """
        ProcessandoComando.
        """
        if cmd == "q":
            await self.close()
        elif cmd == "h":
            self._print_help()
        elif cmd == "r":
            if self.auto_callback:
                await self.command_queue.put(self.auto_callback)
        elif cmd == "x":
            if self.abort_callback:
                await self.command_queue.put(self.abort_callback)
        else:
            if self.send_text_callback:
                await self.send_text_callback(cmd)

    async def close(self):
        """
        FechandoCLI.
        """
        self.running = False
        print("\n Está fechandoApp...\n")

    def _print_help(self):
        """
        Informação，。
        """
        help_text = "r: Começar/Parar | x:  | q:  | h:  | : Enviando"
        self._dash_text = help_text

    async def _init_screen(self):
        """
        Inicializando（ + Entrada）。
        """
        if self._use_ansi:
            # para
            sys.stdout.write("\x1b[2J\x1b[H")
            sys.stdout.flush()

        # Vezes
        await self._render_dashboard(full=True)
        await self._render_input_area()

    def _goto(self, row: int, col: int = 1):
        sys.stdout.write(f"\x1b[{max(1,row)};{max(1,col)}H")

    def _term_size(self):
        try:
            size = shutil.get_terminal_size(fallback=(80, 24))
            return size.columns, size.lines
        except Exception:
            return 80, 24

    # ====== OriginalEntrada（Raw mode）Suportado，Em ======
    def _read_line_raw(self) -> str:
        """
        UsandoOriginalmodo：Fechando、Caracteres， Através deCaracteres（Em）Deletando。
        """
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            buffer: list[str] = []
            while True:
                ch = os.read(fd, 4)  # 4Bytes，UTF-8Em
                if not ch:
                    break
                try:
                    s = ch.decode("utf-8")
                except UnicodeDecodeError:
                    # NãoUTF-8，Continuarpara
                    while True:
                        ch += os.read(fd, 1)
                        try:
                            s = ch.decode("utf-8")
                            break
                        except UnicodeDecodeError:
                            continue

                if s in ("\r", "\n"):
                    # ：，FinalEntrada
                    sys.stdout.write("\r\n")
                    sys.stdout.flush()
                    break
                elif s in ("\x7f", "\b"):
                    # ：Deletando Unicode Caracteres
                    if buffer:
                        buffer.pop()
                    # ，EmCaracteres
                    self._redraw_input_line("".join(buffer))
                elif s == "\x03":  # Ctrl+C
                    raise KeyboardInterrupt
                else:
                    buffer.append(s)
                    self._redraw_input_line("".join(buffer))

            return "".join(buffer)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    def _redraw_input_line(self, content: str) -> None:
        """
        LimpandoEntrada，Em  Deletando。
        """
        cols, rows = self._term_size()
        separator_row = max(1, rows - self._input_area_lines + 1)
        first_input_row = min(rows, separator_row + 1)
        prompt = "Entrada: " if not self._use_ansi else "\x1b[1m\x1b[36mEntrada:\x1b[0m "
        self._goto(first_input_row, 1)
        sys.stdout.write("\x1b[2K")
        visible = content
        # 
        max_len = max(1, cols - len("Entrada: ") - 1)
        if len(visible) > max_len:
            visible = visible[-max_len:]
        sys.stdout.write(f"{prompt}{visible}")
        sys.stdout.flush()

    async def _render_dashboard(self, full: bool = False):
        """
        Em，NãoEntrada。
        """

        # Truncado，
        def trunc(s: str, limit: int = 80) -> str:
            return s if len(s) <= limit else s[: limit - 1] + "…"

        lines = [
            f"Estado: {trunc(self._dash_status)}",
            f"Conexão: {'JáConexão' if self._dash_connected else 'NãoConexão'}",
            f": {trunc(self._dash_emotion)}",
            f": {trunc(self._dash_text)}",
        ]

        if not self._use_ansi:
            # Conversão：Estado
            print(f"\r{lines[0]}        ", end="", flush=True)
            return

        cols, rows = self._term_size()

        #  =  - Entrada
        usable_rows = max(5, rows - self._input_area_lines)

        # 
        def style(s: str, *names: str) -> str:
            if not self._use_ansi:
                return s
            prefix = "".join(self._ansi.get(n, "") for n in names)
            return f"{prefix}{s}{self._ansi['reset']}"

        title = style("  AI  ", "bold", "cyan")
        # e
        top_bar = "┌" + ("─" * (max(2, cols - 2))) + "┐"
        title_line = "│" + title.center(max(2, cols - 2)) + "│"
        sep_line = "├" + ("─" * (max(2, cols - 2))) + "┤"
        bottom_bar = "└" + ("─" * (max(2, cols - 2))) + "┘"

        # （de4）
        body_rows = max(1, usable_rows - 4)
        body = []
        for i in range(body_rows):
            text = lines[i] if i < len(lines) else ""
            text = style(text, "green") if i == 0 else text
            body.append("│" + text.ljust(max(2, cols - 2))[: max(2, cols - 2)] + "│")

        # Posição
        sys.stdout.write("\x1b7")

        # EmLimpandoQuadrosde，“”
        total_rows = 4 + body_rows  #  +  + 
        rows_to_clear = max(self._last_drawn_rows, total_rows)
        for i in range(rows_to_clear):
            self._goto(1 + i, 1)
            sys.stdout.write("\x1b[2K")

        # 
        self._goto(1, 1)
        sys.stdout.write("\x1b[2K" + top_bar[:cols])
        self._goto(2, 1)
        sys.stdout.write("\x1b[2K" + title_line[:cols])
        self._goto(3, 1)
        sys.stdout.write("\x1b[2K" + sep_line[:cols])

        # 
        for idx in range(body_rows):
            self._goto(4 + idx, 1)
            sys.stdout.write("\x1b[2K")
            sys.stdout.write(body[idx][:cols])

        # 
        self._goto(4 + body_rows, 1)
        sys.stdout.write("\x1b[2K" + bottom_bar[:cols])

        # RestaurandoPosição
        sys.stdout.write("\x1b8")
        sys.stdout.flush()

        # VezesAltura
        self._last_drawn_rows = total_rows

    def _clear_input_area(self):
        if not self._use_ansi:
            return
        cols, rows = self._term_size()
        separator_row = max(1, rows - self._input_area_lines + 1)
        first_input_row = min(rows, separator_row + 1)
        second_input_row = min(rows, separator_row + 2)
        # VezesLimpandoeEntrada，EmCaracteres
        for r in [separator_row, first_input_row, second_input_row]:
            self._goto(r, 1)
            sys.stdout.write("\x1b[2K")
        sys.stdout.flush()

    async def _render_input_area(self):
        if not self._use_ansi:
            return
        cols, rows = self._term_size()
        separator_row = max(1, rows - self._input_area_lines + 1)
        first_input_row = min(rows, separator_row + 1)
        second_input_row = min(rows, separator_row + 2)

        # 
        sys.stdout.write("\x1b7")
        # 
        self._goto(separator_row, 1)
        sys.stdout.write("\x1b[2K")
        sys.stdout.write("═" * max(1, cols))

        # Entrada（Limpando）
        self._goto(first_input_row, 1)
        sys.stdout.write("\x1b[2K")
        prompt = "Entrada: " if not self._use_ansi else "\x1b[1m\x1b[36mEntrada:\x1b[0m "
        sys.stdout.write(prompt)

        # 
        self._goto(second_input_row, 1)
        sys.stdout.write("\x1b[2K")
        sys.stdout.flush()

        # Restaurandopara，paraEntradaPosição input Usando
        sys.stdout.write("\x1b8")
        self._goto(first_input_row, 1)
        sys.stdout.write(prompt)
        sys.stdout.flush()

    async def toggle_mode(self):
        """
        CLImodo  demodo（Operação）
        """
        self.logger.debug("CLIModoNãoSuportadoModo")

    async def toggle_window_visibility(self):
        """
        CLImodo  deJanela（Operação）
        """
        self.logger.debug("CLIModoNãoSuportadoJanela")
