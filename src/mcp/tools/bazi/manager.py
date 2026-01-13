"""
Dispositivo ede。
"""

from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class BaziManager:
    """
    Dispositivo。
    """

    def __init__(self):
        """
        InicializandoDispositivo.
        """

    def init_tools(self, add_tool, PropertyList, Property, PropertyType):
        """
        Inicializando。
        """
        from .marriage_tools import (
            analyze_marriage_compatibility,
            analyze_marriage_timing,
        )
        from .tools import (
            build_bazi_from_lunar_datetime,
            build_bazi_from_solar_datetime,
            get_bazi_detail,
            get_chinese_calendar,
            get_solar_times,
        )

        # （）
        bazi_detail_props = PropertyList(
            [
                Property("solar_datetime", PropertyType.STRING, default_value=""),
                Property("lunar_datetime", PropertyType.STRING, default_value=""),
                Property("gender", PropertyType.INTEGER, default_value=1),
                Property(
                    "eight_char_provider_sect", PropertyType.INTEGER, default_value=2
                ),
            ]
        )
        add_tool(
            (
                "self.bazi.get_bazi_detail",
                "Tempo（ou）、deInformação。"
                "de，de。\n"
                "Usando：\n"
                "1. \n"
                "2. Pesquisar\n"
                "3. e\n"
                "4. \n"
                "5. Dados\n"
                "\n：\n"
                "- SuportadoeTempoEntrada\n"
                "- deInformação\n"
                "- 、、\n"
                "- SuportadoNão  de\n"
                "\nParâmetro：\n"
                "  solar_datetime: Tempo，ISOFormato，'2008-03-01T13:00:00+08:00'\n"
                "  lunar_datetime: Tempo，'2000-5-5 12:00:00'\n"
                "  gender: ，0=，1=\n"
                "  eight_char_provider_sect: ，1=23:00-23:59para，2=para（）\n"
                "\n：solar_datetimeelunar_datetimeEm",
                bazi_detail_props,
                get_bazi_detail,
            )
        )

        # Tempo
        solar_times_props = PropertyList([Property("bazi", PropertyType.STRING)])
        add_tool(
            (
                "self.bazi.get_solar_times",
                "deTempo。RetornodeTempoFormatopara：YYYY-MM-DD hh:mm:ss。\n"
                "Usando：\n"
                "1. Tempo\n"
                "2. Validandode\n"
                "3. deTempo\n"
                "4. Tempo\n"
                "\n：\n"
                "- Tempo\n"
                "- SuportadoTempodePesquisar\n"
                "- Tempo\n"
                "\nParâmetro：\n"
                "  bazi: ，、、、Ordem，\n"
                "        ：' Não  Não'",
                solar_times_props,
                get_solar_times,
            )
        )

        # Informação
        chinese_calendar_props = PropertyList(
            [Property("solar_datetime", PropertyType.STRING, default_value="")]
        )
        add_tool(
            (
                "self.bazi.get_chinese_calendar",
                "Tempo（）deEmInformação。"
                "deData、、、BitsAguardarInformação。\n"
                "Usando：\n"
                "1. Pesquisar\n"
                "2. \n"
                "3. Pesquisar\n"
                "4. Bits\n"
                "5. Conversão\n"
                "\n：\n"
                "- deInformação\n"
                "- eInformação\n"
                "- Bits\n"
                "- \n"
                "- \n"
                "- \n"
                "\nParâmetro：\n"
                "  solar_datetime: Tempo，ISOFormato，'2008-03-01T13:00:00+08:00'\n"
                "                 NãoentãoparaTempo",
                chinese_calendar_props,
                get_chinese_calendar,
            )
        )

        # Tempo（Já）
        lunar_bazi_props = PropertyList(
            [
                Property("lunar_datetime", PropertyType.STRING),
                Property("gender", PropertyType.INTEGER, default_value=1),
                Property(
                    "eight_char_provider_sect", PropertyType.INTEGER, default_value=2
                ),
            ]
        )
        add_tool(
            (
                "self.bazi.build_bazi_from_lunar_datetime",
                "Tempo、Informação。\n"
                "：Já，Usandoget_bazi_detail。\n"
                "\nParâmetro：\n"
                "  lunar_datetime: Tempo，：'2000-5-15 12:00:00'\n"
                "  gender: ，0=，1=\n"
                "  eight_char_provider_sect: ",
                lunar_bazi_props,
                build_bazi_from_lunar_datetime,
            )
        )

        # Tempo（Já）
        solar_bazi_props = PropertyList(
            [
                Property("solar_datetime", PropertyType.STRING),
                Property("gender", PropertyType.INTEGER, default_value=1),
                Property(
                    "eight_char_provider_sect", PropertyType.INTEGER, default_value=2
                ),
            ]
        )
        add_tool(
            (
                "self.bazi.build_bazi_from_solar_datetime",
                "Tempo、Informação。\n"
                "：Já，Usandoget_bazi_detail。\n"
                "\nParâmetro：\n"
                "  solar_datetime: Tempo，ISOFormato，'2008-03-01T13:00:00+08:00'\n"
                "  gender: ，0=，1=\n"
                "  eight_char_provider_sect: ",
                solar_bazi_props,
                build_bazi_from_solar_datetime,
            )
        )

        # 
        marriage_timing_props = PropertyList(
            [
                Property("solar_datetime", PropertyType.STRING, default_value=""),
                Property("lunar_datetime", PropertyType.STRING, default_value=""),
                Property("gender", PropertyType.INTEGER, default_value=1),
                Property(
                    "eight_char_provider_sect", PropertyType.INTEGER, default_value=2
                ),
            ]
        )
        add_tool(
            (
                "self.bazi.analyze_marriage_timing",
                "、e。"
                "de，Tempo、Aguardar。\\n"
                "Usando：\\n"
                "1. \\n"
                "2. e\\n"
                "3. e\\n"
                "4. IdentificandoEmde  Em\\n"
                "5. de\\n"
                "\\n：\\n"
                "- \\n"
                "- \\n"
                "- \\n"
                "- Identificando\\n"
                "- Tempo\\n"
                "\\nParâmetro：\\n"
                "  solar_datetime: Tempo，ISOFormato，'2008-03-01T13:00:00+08:00'\\n"
                "  lunar_datetime: Tempo，'2000-5-5 12:00:00'\\n"
                "  gender: ，0=，1=\\n"
                "  eight_char_provider_sect: \\n"
                "\\n：solar_datetimeelunar_datetimeEm",
                marriage_timing_props,
                analyze_marriage_timing,
            )
        )

        # 
        marriage_compatibility_props = PropertyList(
            [
                Property("male_solar_datetime", PropertyType.STRING, default_value=""),
                Property("male_lunar_datetime", PropertyType.STRING, default_value=""),
                Property(
                    "female_solar_datetime", PropertyType.STRING, default_value=""
                ),
                Property(
                    "female_lunar_datetime", PropertyType.STRING, default_value=""
                ),
            ]
        )
        add_tool(
            (
                "self.bazi.analyze_marriage_compatibility",
                "，Correspondência  eModo。"
                "Através de，Correspondênciae。\\n"
                "Usando：\\n"
                "1. \\n"
                "2. Correspondência\\n"
                "3. IdentificandoEmde\\n"
                "4. \\n"
                "5. Selecionando\\n"
                "\\n：\\n"
                "- Correspondência\\n"
                "- \\n"
                "- \\n"
                "- Correspondência\\n"
                "- \\n"
                "\\nParâmetro：\\n"
                "  male_solar_datetime: Tempo\\n"
                "  male_lunar_datetime: Tempo\\n"
                "  female_solar_datetime: Tempo\\n"
                "  female_lunar_datetime: Tempo\\n"
                "\\n：TempoInformaçãoouEm",
                marriage_compatibility_props,
                analyze_marriage_compatibility,
            )
        )


# Dispositivo
_bazi_manager = None


def get_bazi_manager() -> BaziManager:
    """
    Dispositivo。
    """
    global _bazi_manager
    if _bazi_manager is None:
        _bazi_manager = BaziManager()
    return _bazi_manager
