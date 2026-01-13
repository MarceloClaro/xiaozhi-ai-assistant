#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Automático.

：
1. EntradaEmAutomáticopara
2. （+）
3. ValidandotokenEmtokens.txtEm
4. Automáticokeywords.txtFormato
"""

import sys
from pathlib import Path

try:
    from pypinyin import Style, lazy_pinyin
except ImportError:
    print("❌ : pypinyin")
    print(": pip install pypinyin")
    sys.exit(1)


class KeywordGenerator:
    def __init__(self, model_dir: Path):
        """InicializandoDispositivo.

        Args:
            model_dir: ModeloDiretórioCaminho（tokens.txtekeywords.txt）
        """
        self.model_dir = Path(model_dir)
        self.tokens_file = self.model_dir / "tokens.txt"
        self.keywords_file = self.model_dir / "keywords.txt"

        # Jádetokens
        self.available_tokens = self._load_tokens()

        # （de）
        self.initials = [
            "b",
            "p",
            "m",
            "f",
            "d",
            "t",
            "n",
            "l",
            "g",
            "k",
            "h",
            "j",
            "q",
            "x",
            "zh",
            "ch",
            "sh",
            "r",
            "z",
            "c",
            "s",
            "y",
            "w",
        ]

    def _load_tokens(self) -> set:
        """
        tokens.txtEmdetoken.
        """
        if not self.tokens_file.exists():
            print(f"⚠️  Aviso: tokensArquivoNãoExiste: {self.tokens_file}")
            return set()

        tokens = set()
        with open(self.tokens_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    # Formato: "token id" ou "token"
                    parts = line.split()
                    if parts:
                        tokens.add(parts[0])

        print(f"✅  {len(tokens)} tokens")
        return tokens

    def _split_pinyin(self, pinyin: str) -> list:
        """.

        : "xiǎo" -> ["x", "iǎo"]       "mǐ" -> ["m", "ǐ"]       "ài" -> ["ài"]  ()
        """
        if not pinyin:
            return []

        # ComprimentoTentativaCorrespondência（zh, ch, sh）
        for initial in sorted(self.initials, key=len, reverse=True):
            if pinyin.startswith(initial):
                final = pinyin[len(initial) :]
                if final:
                    return [initial, final]
                else:
                    return [initial]

        # Nenhum（）
        return [pinyin]

    def chinese_to_keyword_format(self, chinese_text: str) -> str:
        """EmparakeywordFormato.

        Args:
            chinese_text: Em，""

        Returns:
            keywordFormato，"x iǎo m ǐ x iǎo m ǐ @"
        """
        # para
        pinyin_list = lazy_pinyin(chinese_text, style=Style.TONE)

        # 
        split_parts = []
        missing_tokens = []

        for pinyin in pinyin_list:
            parts = self._split_pinyin(pinyin)

            # Validando  partEmtokensEm
            for part in parts:
                if part not in self.available_tokens:
                    missing_tokens.append(part)
                split_parts.append(part)

        # 
        pinyin_str = " ".join(split_parts)
        keyword_line = f"{pinyin_str} @{chinese_text}"

        # Sedetoken，para  Aviso
        if missing_tokens:
            print(
                f"⚠️  Aviso: tokenNãoEmtokens.txtEm: {', '.join(set(missing_tokens))}"
            )
            print(f"   deIncapaz de")

        return keyword_line

    def add_keyword(self, chinese_text: str, append: bool = True) -> bool:
        """parakeywords.txt.

        Args:
            chinese_text: Em
            append: （True）ou（False）

        Returns:
            Sucesso
        """
        try:
            # keywordFormato
            keyword_line = self.chinese_to_keyword_format(chinese_text)

            # PesquisarJáExiste
            if self.keywords_file.exists():
                with open(self.keywords_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    if f"@{chinese_text}" in content:
                        print(f"⚠️   '{chinese_text}' JáExiste")
                        return False

            # Arquivo
            mode = "a" if append else "w"
            with open(self.keywords_file, mode, encoding="utf-8") as f:
                f.write(keyword_line + "\n")

            print(f"✅ Sucesso: {keyword_line}")
            return True

        except Exception as e:
            print(f"❌ Falha: {e}")
            return False

    def batch_add_keywords(self, chinese_texts: list, overwrite: bool = False):
        """.

        Args:
            chinese_texts: Em
            overwrite: Arquivo
        """
        if overwrite:
            print("⚠️  keywords.txt")

        success_count = 0
        for text in chinese_texts:
            text = text.strip()
            if not text:
                continue

            if self.add_keyword(text, append=not overwrite):
                success_count += 1

            # 
            overwrite = False

        print(f"\n📊 Concluído: Sucesso {success_count}/{len(chinese_texts)} ")

    def list_keywords(self):
        """
        .
        """
        if not self.keywords_file.exists():
            print("⚠️  keywords.txt NãoExiste")
            return

        print(f"\n📄  ({self.keywords_file}):")
        print("-" * 60)

        with open(self.keywords_file, "r", encoding="utf-8") as f:
            for i, line in enumerate(f, 1):
                line = line.strip()
                if line and not line.startswith("#"):
                    # Em
                    if "@" in line:
                        pinyin_part, chinese_part = line.split("@", 1)
                        print(
                            f"{i}. {chinese_part.strip():15s} -> {pinyin_part.strip()}"
                        )
                    else:
                        print(f"{i}. {line}")

        print("-" * 60)


def main():
    """
    .
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="Automático",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
:
  # 
  python keyword_generator.py -a ""

  # 
  python keyword_generator.py -b "" "" ""

  # deArquivo（Em）
  python keyword_generator.py -f keywords_input.txt

  # 
  python keyword_generator.py -l

  # （NãoArquivo）
  python keyword_generator.py -t ""
        """,
    )

    parser.add_argument(
        "-m", "--model-dir", default="models", help="ModeloDiretórioCaminho（: models）"
    )

    parser.add_argument("-a", "--add", help="（Em）")

    parser.add_argument(
        "-b", "--batch", nargs="+", help="（Em，）"
    )

    parser.add_argument("-f", "--file", help="deArquivo（Em）")

    parser.add_argument("-l", "--list", action="store_true", help="")

    parser.add_argument("-t", "--test", help="（NãoArquivo）")

    parser.add_argument(
        "--overwrite", action="store_true", help="Modo（Limpando）"
    )

    args = parser.parse_args()

    # ModeloDiretório
    if Path(args.model_dir).is_absolute():
        model_dir = Path(args.model_dir)
    else:
        # Caminho：Diretório
        script_dir = Path(__file__).parent
        project_root = script_dir.parent
        model_dir = project_root / args.model_dir

    if not model_dir.exists():
        print(f"❌ ModeloDiretórioNãoExiste: {model_dir}")
        sys.exit(1)

    print(f"🔧 UsandoModeloDiretório: {model_dir}")

    # Dispositivo
    generator = KeywordGenerator(model_dir)

    # Operação
    if args.test:
        # Modo
        print(f"\n🧪 :")
        keyword_line = generator.chinese_to_keyword_format(args.test)
        print(f"   Entrada: {args.test}")
        print(f"   Saída: {keyword_line}")

    elif args.add:
        # 
        generator.add_keyword(args.add)

    elif args.batch:
        # 
        generator.batch_add_keywords(args.batch, overwrite=args.overwrite)

    elif args.file:
        # deArquivo
        input_file = Path(args.file)
        if not input_file.exists():
            print(f"❌ ArquivoNãoExiste: {input_file}")
            sys.exit(1)

        with open(input_file, "r", encoding="utf-8") as f:
            keywords = [line.strip() for line in f if line.strip()]

        print(f"📥 deArquivo {len(keywords)} ")
        generator.batch_add_keywords(keywords, overwrite=args.overwrite)

    elif args.list:
        # 
        generator.list_keywords()

    else:
        # Modo
        print("\n🎤 （Modo）")
        print("EntradaEm， Ctrl+C ouEntrada 'q' \n")

        try:
            while True:
                chinese = input("EntradaEm: ").strip()

                if not chinese or chinese.lower() == "q":
                    break

                generator.add_keyword(chinese)
                print()

        except KeyboardInterrupt:
            print("\n\n👋 Já")

    # 
    if not args.list and (args.add or args.batch or args.file):
        generator.list_keywords()


if __name__ == "__main__":
    main()
