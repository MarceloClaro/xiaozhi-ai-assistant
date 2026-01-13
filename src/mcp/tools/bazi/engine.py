"""
.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

import pendulum
from lunar_python import Lunar, Solar

from .models import (
    ChineseCalendar,
    EarthBranch,
    EightChar,
    HeavenStem,
    LunarTime,
    SixtyCycle,
    SolarTime,
)
from .professional_data import (
    GAN,
    GAN_WUXING,
    GAN_YINYANG,
    SHENG_XIAO,
    ZHI,
    ZHI_CANG_GAN,
    ZHI_WUXING,
    ZHI_YINYANG,
)


class BaziEngine:
    """
    .
    """

    #  -  professional_data.py deDados
    HEAVEN_STEMS = {}
    for gan in GAN:
        HEAVEN_STEMS[gan] = HeavenStem(
            name=gan, element=GAN_WUXING[gan], yin_yang=GAN_YINYANG[gan]
        )

    #  -  professional_data.py deDados
    EARTH_BRANCHES = {}
    for i, zhi in enumerate(ZHI):
        # de
        cang_gan = ZHI_CANG_GAN.get(zhi, {})
        cang_gan_list = list(cang_gan.keys())

        #  EarthBranch 
        EARTH_BRANCHES[zhi] = EarthBranch(
            name=zhi,
            element=ZHI_WUXING[zhi],
            yin_yang=ZHI_YINYANG[zhi],
            zodiac=SHENG_XIAO[i],
            hide_heaven_main=cang_gan_list[0] if len(cang_gan_list) > 0 else None,
            hide_heaven_middle=cang_gan_list[1] if len(cang_gan_list) > 1 else None,
            hide_heaven_residual=cang_gan_list[2] if len(cang_gan_list) > 2 else None,
        )

    def __init__(self):
        """
        Inicializando.
        """

    def parse_solar_time(self, iso_date: str) -> SolarTime:
        """
        AnalisandoTempoCaracteres（SuportadoFormato）- UsandopendulumConversão，Processando.
        """
        try:
            # UsandopendulumAnalisandoTempo，SuportadoFormato
            dt = pendulum.parse(iso_date)

            # Processando
            if dt.timezone_name == "UTC":
                # SependulumAnalisandoparaUTC（OriginalEntradaNenhum），TempoProcessando
                dt = dt.replace(tzinfo=pendulum.timezone("Asia/Shanghai"))
            elif dt.timezone_name is None:
                # SeNenhumInformação，ConfigurandoparaTempo
                dt = dt.replace(tzinfo=pendulum.timezone("Asia/Shanghai"))
            elif dt.timezone_name != "Asia/Shanghai":
                # paraTempo
                dt = dt.in_timezone("Asia/Shanghai")

            return SolarTime(
                year=dt.year,
                month=dt.month,
                day=dt.day,
                hour=dt.hour,
                minute=dt.minute,
                second=dt.second,
            )
        except Exception:
            # SependulumAnalisandoFalha，TentativaFormato
            formats = [
                "%Y-%m-%dT%H:%M:%S+08:00",
                "%Y-%m-%dT%H:%M:%S+0800",
                "%Y-%m-%dT%H:%M:%S.%f+08:00",
                "%Y-%m-%dT%H:%M:%S.%f",
                "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%dT%H:%M+08:00",
                "%Y-%m-%dT%H:%M",
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%d %H:%M",
                "%Y-%m-%d",
                "%Y/%m/%d %H:%M:%S",
                "%Y/%m/%d %H:%M",
                "%Y/%m/%d",
                "%Y%m%d %H%M%SSegundos",
                "%Y%m%d %H%M",
                "%Y%m%d",
            ]

            dt = None
            for fmt in formats:
                try:
                    dt = datetime.strptime(iso_date, fmt)
                    break
                except ValueError:
                    continue

            if dt is None:
                raise ValueError(
                    f"Incapaz deAnalisandoTempoFormato: {iso_date}，SuportadodeFormatoISO8601、Em  FormatoAguardar"
                )

            return SolarTime(
                year=dt.year,
                month=dt.month,
                day=dt.day,
                hour=dt.hour,
                minute=dt.minute,
                second=dt.second,
            )

    def solar_to_lunar(self, solar_time: SolarTime) -> LunarTime:
        """
         - Processando.
        """
        try:
            # Usandolunar-pythonde
            solar = Solar.fromYmdHms(
                solar_time.year,
                solar_time.month,
                solar_time.day,
                solar_time.hour,
                solar_time.minute,
                solar_time.second,
            )
            lunar = solar.getLunar()

            # para
            is_leap = lunar.isLeap() if hasattr(lunar, "isLeap") else False

            # Selunar-pythonNenhumisLeap，Usando
            if not hasattr(lunar, "isLeap"):
                # Através deCaracteres（Se""）
                month_str = lunar.getMonthInChinese()
                is_leap = "" in month_str

            return LunarTime(
                year=lunar.getYear(),
                month=lunar.getMonth(),
                day=lunar.getDay(),
                hour=lunar.getHour(),
                minute=lunar.getMinute(),
                second=lunar.getSecond(),
                is_leap=is_leap,
            )
        except Exception as e:
            raise ValueError(f"Falha: {e}")

    def lunar_to_solar(self, lunar_time: LunarTime) -> SolarTime:
        """
         - Processando.
        """
        try:
            # Processando
            if lunar_time.is_leap:
                # Se，Usando
                lunar = Lunar.fromYmdHms(
                    lunar_time.year,
                    -lunar_time.month,  # 
                    lunar_time.day,
                    lunar_time.hour,
                    lunar_time.minute,
                    lunar_time.second,
                )
            else:
                # 
                lunar = Lunar.fromYmdHms(
                    lunar_time.year,
                    lunar_time.month,
                    lunar_time.day,
                    lunar_time.hour,
                    lunar_time.minute,
                    lunar_time.second,
                )

            solar = lunar.getSolar()

            return SolarTime(
                year=solar.getYear(),
                month=solar.getMonth(),
                day=solar.getDay(),
                hour=solar.getHour(),
                minute=solar.getMinute(),
                second=solar.getSecond(),
            )
        except Exception as e:
            raise ValueError(f"Falha: {e}")

    def build_eight_char(self, solar_time: SolarTime) -> EightChar:
        """
        .
        """
        try:
            # Usandolunar-python
            solar = Solar.fromYmdHms(
                solar_time.year,
                solar_time.month,
                solar_time.day,
                solar_time.hour,
                solar_time.minute,
                solar_time.second,
            )
            lunar = solar.getLunar()
            bazi = lunar.getEightChar()

            # 
            year_gan = bazi.getYearGan()
            year_zhi = bazi.getYearZhi()
            year_cycle = self._create_sixty_cycle(year_gan, year_zhi)

            # 
            month_gan = bazi.getMonthGan()
            month_zhi = bazi.getMonthZhi()
            month_cycle = self._create_sixty_cycle(month_gan, month_zhi)

            # 
            day_gan = bazi.getDayGan()
            day_zhi = bazi.getDayZhi()
            day_cycle = self._create_sixty_cycle(day_gan, day_zhi)

            # 
            time_gan = bazi.getTimeGan()
            time_zhi = bazi.getTimeZhi()
            time_cycle = self._create_sixty_cycle(time_gan, time_zhi)

            return EightChar(
                year=year_cycle, month=month_cycle, day=day_cycle, hour=time_cycle
            )
        except Exception as e:
            raise ValueError(f"Falha: {e}")

    def _create_sixty_cycle(self, gan_name: str, zhi_name: str) -> SixtyCycle:
        """
        Criando.
        """
        heaven_stem = self.HEAVEN_STEMS[gan_name]
        earth_branch = self.EARTH_BRANCHES[zhi_name]

        # 
        try:
            # UsandoDados
            sound = self._get_nayin(gan_name, zhi_name)
        except Exception as e:
            # Erro，Não
            print(f"Falha: {gan_name}{zhi_name} - {e}")
            sound = "Não"

        # e - Conversão
        ten = self._get_ten(gan_name, zhi_name)
        extra_branches = self._get_kong_wang(gan_name, zhi_name)

        return SixtyCycle(
            heaven_stem=heaven_stem,
            earth_branch=earth_branch,
            sound=sound,
            ten=ten,
            extra_earth_branches=extra_branches,
        )

    def _get_nayin(self, gan: str, zhi: str) -> str:
        """
        .
        """
        from .professional_data import get_nayin

        return get_nayin(gan, zhi)

    def _get_ten(self, gan: str, zhi: str) -> str:
        """ - Usando"""
        from .professional_data import GAN, ZHI

        try:
            # Usandode
            gan_idx = GAN.index(gan)
            zhi_idx = ZHI.index(zhi)

            # EmEmde（de1Começar）
            jiazi_number = (gan_idx * 6 + zhi_idx * 5) % 60
            if jiazi_number == 0:
                jiazi_number = 60

            # de
            xun_starts = ["", "", "", "", "", ""]

            # Em（10para）
            xun_index = (jiazi_number - 1) // 10

            if 0 <= xun_index < len(xun_starts):
                return xun_starts[xun_index]
            else:
                # Usandode
                return self._calculate_xun_by_position(jiazi_number)
        except (ValueError, IndexError) as e:
            print(f"Falha: {gan}{zhi} - {e}")
            return ""

    def _get_kong_wang(self, gan: str, zhi: str) -> List[str]:
        """ - Usando"""
        from .professional_data import GAN, ZHI

        try:
            gan_idx = GAN.index(gan)
            zhi_idx = ZHI.index(zhi)

            # EmEmde
            jiazi_number = (gan_idx * 6 + zhi_idx * 5) % 60
            if jiazi_number == 0:
                jiazi_number = 60

            # Em
            xun_index = (jiazi_number - 1) // 10

            # de
            kong_wang_table = [
                ["", ""],  # 
                ["", ""],  # 
                ["", "Não"],  # 
                ["", ""],  # 
                ["", ""],  # 
                ["", ""],  # 
            ]

            if 0 <= xun_index < len(kong_wang_table):
                return kong_wang_table[xun_index]
            else:
                # 
                return self._calculate_kong_wang_by_position(jiazi_number)
        except (ValueError, IndexError) as e:
            print(f"Falha: {gan}{zhi} - {e}")
            return ["", ""]  # Retorno

    def format_solar_time(self, solar_time: SolarTime) -> str:
        """
        FormatoConversãoTempo.
        """
        return f"{solar_time.year}{solar_time.month}{solar_time.day}{solar_time.hour}{solar_time.minute}{solar_time.second}Segundos"

    def format_lunar_time(self, lunar_time: LunarTime) -> str:
        """
        FormatoConversãoTempo.
        """
        return f"{lunar_time.year}{lunar_time.month}{lunar_time.day}{lunar_time.hour}{lunar_time.minute}{lunar_time.second}Segundos"

    def get_chinese_calendar(
        self, solar_time: Optional[SolarTime] = None
    ) -> ChineseCalendar:
        """EmInformação - Usandolunar-python"""
        if solar_time is None:
            # Usando
            now = pendulum.now("Asia/Shanghai")
            solar_time = SolarTime(
                now.year, now.month, now.day, now.hour, now.minute, now.second
            )

        try:
            solar = Solar.fromYmdHms(
                solar_time.year,
                solar_time.month,
                solar_time.day,
                solar_time.hour,
                solar_time.minute,
                solar_time.second,
            )
            lunar = solar.getLunar()

            # Informação
            bazi = lunar.getEightChar()

            return ChineseCalendar(
                solar_date=self.format_solar_time(solar_time),
                lunar_date=f"{lunar.getYearInChinese()}{lunar.getMonthInChinese()}{lunar.getDayInChinese()}",
                gan_zhi=f"{bazi.getYear()} {bazi.getMonth()} {bazi.getDay()}",
                zodiac=lunar.getYearShengXiao(),
                na_yin=lunar.getDayNaYin(),
                lunar_festival=(
                    ", ".join(lunar.getFestivals()) if lunar.getFestivals() else None
                ),
                solar_festival=(
                    ", ".join(solar.getFestivals()) if solar.getFestivals() else None
                ),
                solar_term=lunar.getJieQi() or "",
                twenty_eight_star=lunar.getXiu(),
                pengzu_taboo=lunar.getPengZuGan() + " " + lunar.getPengZuZhi(),
                joy_direction=lunar.getPositionXi(),
                yang_direction=lunar.getPositionYangGui(),
                yin_direction=lunar.getPositionYinGui(),
                mascot_direction=lunar.getPositionFu(),
                wealth_direction=lunar.getPositionCai(),
                clash=f"{lunar.getDayChongDesc()}",
                suitable=", ".join(lunar.getDayYi()[:5]),  # 5
                avoid=", ".join(lunar.getDayJi()[:5]),  # 5
            )
        except Exception as e:
            raise ValueError(f"InformaçãoFalha: {e}")

    def _calculate_xun_by_position(self, jiazi_number: int) -> str:
        """
        .
        """
        # de professional_data.py Usando GANZHI_60
        # de
        xun_starts = ["", "", "", "", "", ""]

        xun_index = (jiazi_number - 1) // 10
        if 0 <= xun_index < len(xun_starts):
            return xun_starts[xun_index]
        else:
            return ""

    def _calculate_kong_wang_by_position(self, jiazi_number: int) -> List[str]:
        """
        .
        """
        # de
        kong_wang_table = [
            ["", ""],  # 
            ["", ""],  # 
            ["", "Não"],  # 
            ["", ""],  # 
            ["", ""],  # 
            ["", ""],  # 
        ]

        xun_index = (jiazi_number - 1) // 10
        if 0 <= xun_index < len(kong_wang_table):
            return kong_wang_table[xun_index]
        else:
            return ["", ""]

    def get_detailed_lunar_info(self, solar_time: SolarTime) -> Dict[str, Any]:
        """
        deInformação.
        """
        try:
            solar = Solar.fromYmdHms(
                solar_time.year,
                solar_time.month,
                solar_time.day,
                solar_time.hour,
                solar_time.minute,
                solar_time.second,
            )
            lunar = solar.getLunar()

            # Informação
            current_jieqi = lunar.getJieQi()
            next_jieqi = lunar.getNextJieQi()
            prev_jieqi = lunar.getPrevJieQi()

            # Informação
            return {
                "current_jieqi": current_jieqi,
                "next_jieqi": next_jieqi.toString() if next_jieqi else None,
                "prev_jieqi": prev_jieqi.toString() if prev_jieqi else None,
                "lunar_festivals": lunar.getFestivals(),
                "solar_festivals": solar.getFestivals(),
                "twenty_eight_star": lunar.getXiu(),
                "day_position": {
                    "xi": lunar.getPositionXi(),
                    "yang_gui": lunar.getPositionYangGui(),
                    "yin_gui": lunar.getPositionYinGui(),
                    "fu": lunar.getPositionFu(),
                    "cai": lunar.getPositionCai(),
                },
                "pengzu_taboo": {
                    "gan": lunar.getPengZuGan(),
                    "zhi": lunar.getPengZuZhi(),
                },
                "day_suitable": lunar.getDayYi(),
                "day_avoid": lunar.getDayJi(),
                "day_clash": lunar.getDayChongDesc(),
            }
        except Exception as e:
            print(f"InformaçãoFalha: {e}")
            return {}


# 
_bazi_engine = None


def get_bazi_engine() -> BaziEngine:
    """
    .
    """
    global _bazi_engine
    if _bazi_engine is None:
        _bazi_engine = BaziEngine()
    return _bazi_engine
