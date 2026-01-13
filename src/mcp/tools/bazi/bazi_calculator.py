"""
.
"""

from typing import Any, Dict, List, Optional

from .engine import get_bazi_engine
from .models import BaziAnalysis, EightChar, LunarTime, SolarTime
from .professional_analyzer import get_professional_analyzer


class BaziCalculator:
    """
    Dispositivo.
    """

    def __init__(self):
        self.engine = get_bazi_engine()
        self.professional_analyzer = get_professional_analyzer()

    def build_hide_heaven_object(
        self, heaven_stem: Optional[str], day_master: str
    ) -> Optional[Dict[str, str]]:
        """
        .
        """
        if not heaven_stem:
            return None

        return {
            "": heaven_stem,
            "": self._get_ten_star(day_master, heaven_stem),
        }

    def _get_ten_star(self, day_master: str, other_stem: str) -> str:
        """
        .
        """
        return self.professional_analyzer.get_ten_gods_analysis(day_master, other_stem)

    def build_sixty_cycle_object(
        self, sixty_cycle, day_master: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        .
        """
        heaven_stem = sixty_cycle.get_heaven_stem()
        earth_branch = sixty_cycle.get_earth_branch()

        if not day_master:
            day_master = heaven_stem.name

        return {
            "": {
                "": heaven_stem.name,
                "": heaven_stem.element,
                "": "" if heaven_stem.yin_yang == 1 else "",
                "": (
                    None
                    if day_master == heaven_stem.name
                    else self._get_ten_star(day_master, heaven_stem.name)
                ),
            },
            "": {
                "": earth_branch.name,
                "": earth_branch.element,
                "": "" if earth_branch.yin_yang == 1 else "",
                "": {
                    "": self.build_hide_heaven_object(
                        earth_branch.hide_heaven_main, day_master
                    ),
                    "Em": self.build_hide_heaven_object(
                        earth_branch.hide_heaven_middle, day_master
                    ),
                    "": self.build_hide_heaven_object(
                        earth_branch.hide_heaven_residual, day_master
                    ),
                },
            },
            "": sixty_cycle.sound,
            "": sixty_cycle.ten,
            "": "".join(sixty_cycle.extra_earth_branches),
            "": self._get_terrain(day_master, earth_branch.name),
            "": self._get_terrain(heaven_stem.name, earth_branch.name),
        }

    def _get_terrain(self, stem: str, branch: str) -> str:
        """
        .
        """
        from .professional_data import get_changsheng_state

        return get_changsheng_state(stem, branch)

    def build_gods_object(
        self, eight_char: EightChar, gender: int
    ) -> Dict[str, List[str]]:
        """
        .
        """
        from .professional_data import get_shensha

        # 
        eight_char.year.heaven_stem.name
        eight_char.month.heaven_stem.name
        day_gan = eight_char.day.heaven_stem.name
        eight_char.hour.heaven_stem.name

        year_zhi = eight_char.year.earth_branch.name
        month_zhi = eight_char.month.earth_branch.name
        day_zhi = eight_char.day.earth_branch.name
        hour_zhi = eight_char.hour.earth_branch.name

        # 
        result = {"": [], "": [], "": [], "": []}

        # （para）
        tianyi = get_shensha(day_gan, "tianyi")
        if tianyi:
            for zhi in [year_zhi, month_zhi, day_zhi, hour_zhi]:
                if zhi in tianyi:
                    if zhi == year_zhi:
                        result[""].append("")
                    if zhi == month_zhi:
                        result[""].append("")
                    if zhi == day_zhi:
                        result[""].append("")
                    if zhi == hour_zhi:
                        result[""].append("")

        # （para）
        wenchang = get_shensha(day_gan, "wenchang")
        if wenchang:
            for zhi in [year_zhi, month_zhi, day_zhi, hour_zhi]:
                if zhi == wenchang:
                    if zhi == year_zhi:
                        result[""].append("")
                    if zhi == month_zhi:
                        result[""].append("")
                    if zhi == day_zhi:
                        result[""].append("")
                    if zhi == hour_zhi:
                        result[""].append("")

        # （para）
        yima = get_shensha(day_zhi, "yima")
        if yima:
            for zhi in [year_zhi, month_zhi, day_zhi, hour_zhi]:
                if zhi == yima:
                    if zhi == year_zhi:
                        result[""].append("")
                    if zhi == month_zhi:
                        result[""].append("")
                    if zhi == day_zhi:
                        result[""].append("")
                    if zhi == hour_zhi:
                        result[""].append("")

        # （para）
        taohua = get_shensha(day_zhi, "taohua")
        if taohua:
            for zhi in [year_zhi, month_zhi, day_zhi, hour_zhi]:
                if zhi == taohua:
                    if zhi == year_zhi:
                        result[""].append("")
                    if zhi == month_zhi:
                        result[""].append("")
                    if zhi == day_zhi:
                        result[""].append("")
                    if zhi == hour_zhi:
                        result[""].append("")

        # （para）
        huagai = get_shensha(day_zhi, "huagai")
        if huagai:
            for zhi in [year_zhi, month_zhi, day_zhi, hour_zhi]:
                if zhi == huagai:
                    if zhi == year_zhi:
                        result[""].append("")
                    if zhi == month_zhi:
                        result[""].append("")
                    if zhi == day_zhi:
                        result[""].append("")
                    if zhi == hour_zhi:
                        result[""].append("")

        return result

    def build_decade_fortune_object(
        self, solar_time: SolarTime, eight_char: EightChar, gender: int, day_master: str
    ) -> Dict[str, Any]:
        """
        .
        """
        # 
        year_yin_yang = eight_char.year.heaven_stem.yin_yang
        month_gan = eight_char.month.heaven_stem.name
        month_zhi = eight_char.month.earth_branch.name

        fortune_list = []

        # Usando
        start_age = self._calculate_start_age(solar_time, eight_char, gender)

        for i in range(10):  # 10
            age_start = start_age + i * 10
            age_end = age_start + 9
            year_start = solar_time.year + age_start
            year_end = solar_time.year + age_end

            # Usando
            fortune_gz = self._calculate_fortune_ganzhi(
                month_gan, month_zhi, i + 1, gender, year_yin_yang
            )

            # e
            fortune_gan = fortune_gz[0]
            fortune_zhi = fortune_gz[1]

            # de
            from .professional_data import ZHI_CANG_GAN

            zhi_ten_gods = []
            zhi_canggan = []

            if fortune_zhi in ZHI_CANG_GAN:
                canggan_data = ZHI_CANG_GAN[fortune_zhi]
                for hidden_gan, strength in canggan_data.items():
                    ten_god = self._get_ten_star(day_master, hidden_gan)
                    zhi_ten_gods.append(f"{ten_god}({hidden_gan})")
                    zhi_canggan.append(f"{hidden_gan}({strength})")

            fortune_list.append(
                {
                    "": fortune_gz,
                    "Começar": year_start,
                    "Final": year_end,
                    "": self._get_ten_star(day_master, fortune_gan),
                    "": (
                        zhi_ten_gods if zhi_ten_gods else [f"{fortune_zhi}"]
                    ),
                    "": zhi_canggan if zhi_canggan else [fortune_zhi],
                    "Começar": age_start,
                    "Final": age_end,
                }
            )

        return {
            "Data": f"{solar_time.year + start_age}-{solar_time.month}-{solar_time.day}",
            "": start_age,
            "": fortune_list,
        }

    def _calculate_fortune_ganzhi(
        self, month_gan: str, month_zhi: str, step: int, gender: int, year_yin_yang: int
    ) -> str:
        """
        .
        """
        from .professional_data import GAN, ZHI

        # ：，
        if (gender == 1 and year_yin_yang == 1) or (
            gender == 0 and year_yin_yang == -1
        ):
            # 
            direction = 1
        else:
            # 
            direction = -1

        # deComeçar
        month_gan_idx = GAN.index(month_gan)
        month_zhi_idx = ZHI.index(month_zhi)

        # de
        fortune_gan_idx = (month_gan_idx + step * direction) % 10
        fortune_zhi_idx = (month_zhi_idx + step * direction) % 12

        return GAN[fortune_gan_idx] + ZHI[fortune_zhi_idx]

    def build_bazi(
        self,
        solar_datetime: Optional[str] = None,
        lunar_datetime: Optional[str] = None,
        gender: int = 1,
        eight_char_provider_sect: int = 2,
    ) -> BaziAnalysis:
        """
        .
        """

        if not solar_datetime and not lunar_datetime:
            raise ValueError("solarDatetimeelunarDatetimeEm")

        if solar_datetime:
            solar_time = self.engine.parse_solar_time(solar_datetime)
            lunar_time = self.engine.solar_to_lunar(solar_time)
        else:
            # ProcessandoTempo
            lunar_dt = self._parse_lunar_datetime(lunar_datetime)
            lunar_time = lunar_dt
            solar_time = self._lunar_to_solar(lunar_dt)

        # 
        eight_char = self.engine.build_eight_char(solar_time)
        day_master = eight_char.day.heaven_stem.name

        # Usando，Não（paraeTempoNão）
        zodiac = self._get_zodiac_by_lunar_year(solar_time)

        # 
        analysis = BaziAnalysis(
            gender=["", ""][gender],
            solar_time=self.engine.format_solar_time(solar_time),
            lunar_time=str(lunar_time),
            bazi=str(eight_char),
            zodiac=zodiac,
            day_master=day_master,
            year_pillar=self.build_sixty_cycle_object(eight_char.year, day_master),
            month_pillar=self.build_sixty_cycle_object(eight_char.month, day_master),
            day_pillar=self.build_sixty_cycle_object(eight_char.day),
            hour_pillar=self.build_sixty_cycle_object(eight_char.hour, day_master),
            fetal_origin=self._calculate_fetal_origin(eight_char),
            fetal_breath=self._calculate_fetal_breath(eight_char),
            own_sign=self._calculate_own_sign(eight_char),
            body_sign=self._calculate_body_sign(eight_char),
            gods=self.build_gods_object(eight_char, gender),
            fortune=self.build_decade_fortune_object(
                solar_time, eight_char, gender, day_master
            ),
            relations=self._build_relations_object(eight_char),
        )

        # UsandoDispositivo
        try:
            # UsandoDados
            eight_char_dict = eight_char.to_dict()
            detailed_analysis = self.professional_analyzer.analyze_eight_char_structure(
                eight_char_dict
            )
            detailed_text = self.professional_analyzer.get_detailed_fortune_analysis(
                eight_char_dict
            )

            # paraRetorno
            analysis._professional_analysis = detailed_analysis
            analysis._detailed_fortune_text = detailed_text
        except Exception as e:
            # SeFalha，Erro  Não
            analysis._professional_analysis = {"error": f"Falha: {e}"}
            analysis._detailed_fortune_text = f"Não: {e}"

        return analysis

    def _parse_lunar_datetime(self, lunar_datetime: str) -> LunarTime:
        """
        AnalisandoTempoCaracteres - SuportadoFormato.
        """
        import re
        from datetime import datetime

        # SuportadoEmFormato：2024 [Tempo]
        chinese_match = re.match(
            r"(\d{4})(\S+)(\S+)(?:\s+(.+))?", lunar_datetime
        )
        if chinese_match:
            year = int(chinese_match.group(1))
            month_str = chinese_match.group(2)
            day_str = chinese_match.group(3)
            time_str = chinese_match.group(4)  # deTempo

            # EmeData
            month = self._chinese_month_to_number(month_str)
            day = self._chinese_day_to_number(day_str)

            # AnalisandoTempo
            hour, minute, second = self._parse_time_part(time_str)

            return LunarTime(
                year=year,
                month=month,
                day=day,
                hour=hour,
                minute=minute,
                second=second,
            )

        # SuportadoFormato
        try:
            # TentativaISOFormato
            dt = datetime.fromisoformat(lunar_datetime)
        except ValueError:
            # TentativaFormato
            formats = [
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%d %H:%M",
                "%Y-%m-%d",
                "%Y/%m/%d %H:%M:%S",
                "%Y/%m/%d %H:%M",
                "%Y/%m/%d",
            ]

            dt = None
            for fmt in formats:
                try:
                    dt = datetime.strptime(lunar_datetime, fmt)
                    break
                except ValueError:
                    continue

            if dt is None:
                raise ValueError(f"Incapaz deAnalisandoTempoFormato: {lunar_datetime}")

        return LunarTime(
            year=dt.year,
            month=dt.month,
            day=dt.day,
            hour=dt.hour,
            minute=dt.minute,
            second=dt.second,
        )

    def _lunar_to_solar(self, lunar_time: LunarTime) -> SolarTime:
        """
        .
        """
        try:
            # Usandolunar-pythonde
            from lunar_python import Lunar

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

    def _calculate_fetal_origin(self, eight_char: EightChar) -> str:
        """
        .
        """
        from .professional_data import GAN, ZHI

        #  = Bits + Bits
        month_gan = eight_char.month.heaven_stem.name
        month_zhi = eight_char.month.earth_branch.name

        # Bits
        gan_idx = GAN.index(month_gan)
        fetal_gan = GAN[(gan_idx + 1) % 10]

        # Bits
        zhi_idx = ZHI.index(month_zhi)
        fetal_zhi = ZHI[(zhi_idx + 3) % 12]

        return f"{fetal_gan}{fetal_zhi}"

    def _calculate_fetal_breath(self, eight_char: EightChar) -> str:
        """
        .
        """
        from .professional_data import GAN, ZHI

        #  = 
        day_gan = eight_char.day.heaven_stem.name
        day_zhi = eight_char.day.earth_branch.name

        # 
        gan_idx = GAN.index(day_gan)
        zhi_idx = ZHI.index(day_zhi)

        # （）
        breath_gan = GAN[(gan_idx + 1) % 10 if gan_idx % 2 == 0 else (gan_idx - 1) % 10]
        breath_zhi = ZHI[(zhi_idx + 6) % 12]  # 

        return f"{breath_gan}{breath_zhi}"

    def _calculate_own_sign(self, eight_char: EightChar) -> str:
        """
        .
        """
        from .professional_data import GAN, ZHI

        # ：，，de，
        month_zhi = eight_char.month.earth_branch.name
        hour_zhi = eight_char.hour.earth_branch.name

        month_idx = ZHI.index(month_zhi)
        hour_idx = ZHI.index(hour_zhi)

        # ，para
        ming_gong_num = (month_idx - 2) % 12  # =0，=1...

        # de
        hour_offset = (hour_idx - 3) % 12  # =0，=1...
        ming_gong_num = (ming_gong_num - hour_offset) % 12

        ming_gong_zhi = ZHI[(ming_gong_num + 2) % 12]  # 

        # （Conversão：de）
        ming_gong_gan = GAN[ming_gong_num % 10]

        return f"{ming_gong_gan}{ming_gong_zhi}"

    def _calculate_body_sign(self, eight_char: EightChar) -> str:
        """
        .
        """
        from .professional_data import GAN, ZHI

        # ：depara
        month_zhi = eight_char.month.earth_branch.name
        hour_zhi = eight_char.hour.earth_branch.name

        month_idx = ZHI.index(month_zhi)
        hour_idx = ZHI.index(hour_zhi)

        # deparade
        shen_gong_idx = (month_idx + hour_idx) % 12
        shen_gong_zhi = ZHI[shen_gong_idx]

        # 
        shen_gong_gan = GAN[shen_gong_idx % 10]

        return f"{shen_gong_gan}{shen_gong_zhi}"

    def _build_relations_object(self, eight_char: EightChar) -> Dict[str, Any]:
        """
        .
        """
        from .professional_data import analyze_zhi_combinations

        # 
        zhi_list = [
            eight_char.year.earth_branch.name,
            eight_char.month.earth_branch.name,
            eight_char.day.earth_branch.name,
            eight_char.hour.earth_branch.name,
        ]

        # Usando
        relations = analyze_zhi_combinations(zhi_list)

        return {
            "": relations.get("sanhe", []),
            "": relations.get("liuhe", []),
            "": relations.get("sanhui", []),
            "": relations.get("chong", []),
            "": relations.get("xing", []),
            "": relations.get("hai", []),
        }

    def get_solar_times(self, bazi: str) -> List[str]:
        """
        deTempo.
        """
        pillars = bazi.split(" ")
        if len(pillars) != 4:
            raise ValueError("Formatoerro")

        year_pillar, month_pillar, day_pillar, hour_pillar = pillars

        # Analisando
        if (
            len(year_pillar) != 2
            or len(month_pillar) != 2
            or len(day_pillar) != 2
            or len(hour_pillar) != 2
        ):
            raise ValueError("Formatoerro，para  Caracteres")

        year_gan, year_zhi = year_pillar[0], year_pillar[1]
        month_gan, month_zhi = month_pillar[0], month_pillar[1]
        day_gan, day_zhi = day_pillar[0], day_pillar[1]
        hour_gan, hour_zhi = hour_pillar[0], hour_pillar[1]

        result_times = []

        # Pesquisa：1900-2100，ConversãoPesquisa
        for year in range(1900, 2100):
            try:
                # TentativaCorrespondência
                if self._match_year_pillar(year, year_gan, year_zhi):
                    # 
                    for month in range(1, 13):
                        if self._match_month_pillar(year, month, month_gan, month_zhi):
                            # Data，UsandodeData
                            import calendar

                            max_day = calendar.monthrange(year, month)[1]

                            for day in range(1, max_day + 1):
                                try:
                                    if self._match_day_pillar(
                                        year, month, day, day_gan, day_zhi
                                    ):
                                        # ，UsandodeEm
                                        for hour in [
                                            0,
                                            2,
                                            4,
                                            6,
                                            8,
                                            10,
                                            12,
                                            14,
                                            16,
                                            18,
                                            20,
                                            22,
                                        ]:  # 12deEm
                                            if self._match_hour_pillar(
                                                hour,
                                                hour_gan,
                                                hour_zhi,
                                                year,
                                                month,
                                                day,
                                            ):
                                                solar_time = f"{year}-{month:02d}-{day:02d} {hour:02d}:00:00"
                                                result_times.append(solar_time)

                                                # RetornoLimitado a
                                                if len(result_times) >= 20:
                                                    return result_times
                                except ValueError:
                                    continue  # Data
            except Exception:
                continue

        return result_times[:20]  # Retorno20Correspondência

    def _calculate_start_age(
        self, solar_time: SolarTime, eight_char: EightChar, gender: int
    ) -> int:
        """
        .
        """
        from lunar_python import Solar

        from .professional_data import GAN_YINYANG

        # 
        year_gan = eight_char.year.heaven_stem.name
        year_gan_yinyang = GAN_YINYANG.get(year_gan, 1)

        try:
            # TempodeSolar
            birth_solar = Solar.fromYmdHms(
                solar_time.year,
                solar_time.month,
                solar_time.day,
                solar_time.hour,
                solar_time.minute,
                solar_time.second,
            )

            # então：，
            if (gender == 1 and year_gan_yinyang == 1) or (
                gender == 0 and year_gan_yinyang == -1
            ):
                # ：parade
                lunar = birth_solar.getLunar()
                next_jieqi = lunar.getNextJieQi()

                if next_jieqi:
                    # deTempo
                    next_jieqi_solar = next_jieqi.getSolar()

                    # 
                    days_diff = self._calculate_days_diff(birth_solar, next_jieqi_solar)

                    #  =  / 3（）
                    start_age = max(1, days_diff // 3)
                else:
                    start_age = 3  # Valor
            else:
                # ：parade
                lunar = birth_solar.getLunar()
                prev_jieqi = lunar.getPrevJieQi()

                if prev_jieqi:
                    # deTempo
                    prev_jieqi_solar = prev_jieqi.getSolar()

                    # 
                    days_diff = self._calculate_days_diff(prev_jieqi_solar, birth_solar)

                    #  =  / 3（）
                    start_age = max(1, days_diff // 3)
                else:
                    start_age = 5  # Valor

            # Limitado aEm
            return max(1, min(start_age, 10))

        except Exception:
            # SeFalha，UsandoConversão
            if (gender == 1 and year_gan_yinyang == 1) or (
                gender == 0 and year_gan_yinyang == -1
            ):
                base_age = 3
            else:
                base_age = 5

            # 
            month_adjustment = {
                1: 0,
                2: 1,
                3: 0,
                4: 1,
                5: 0,
                6: 1,
                7: 0,
                8: 1,
                9: 0,
                10: 1,
                11: 0,
                12: 1,
            }

            final_age = base_age + month_adjustment.get(solar_time.month, 0)
            return max(1, min(final_age, 8))

    def _parse_time_part(self, time_str: str) -> tuple:
        """
        AnalisandoTempo，Retorno(hour, minute, second)
        """
        if not time_str:
            return (0, 0, 0)

        time_str = time_str.strip()

        # SuportadoFormato：、、Aguardar
        shichen_map = {
            "": 0,
            "": 0,
            "": 1,
            "": 1,
            "": 3,
            "": 3,
            "": 5,
            "": 5,
            "": 7,
            "": 7,
            "": 9,
            "": 9,
            "": 11,
            "": 11,
            "Não": 13,
            "Não": 13,
            "": 15,
            "": 15,
            "": 17,
            "": 17,
            "": 19,
            "": 19,
            "": 21,
            "": 21,
        }

        if time_str in shichen_map:
            return (shichen_map[time_str], 0, 0)

        # SuportadoTempoFormato：10、10:30Aguardar
        import re

        # Correspondência "103020Segundos" Formato
        chinese_time_match = re.match(r"(\d+)(?:(\d+))?(?:(\d+)Segundos)?", time_str)
        if chinese_time_match:
            hour = int(chinese_time_match.group(1))
            minute = int(chinese_time_match.group(2) or 0)
            second = int(chinese_time_match.group(3) or 0)
            return (hour, minute, second)

        # Correspondência "10:30:20" ou "10:30" Formato
        colon_time_match = re.match(r"(\d+):(\d+)(?::(\d+))?", time_str)
        if colon_time_match:
            hour = int(colon_time_match.group(1))
            minute = int(colon_time_match.group(2))
            second = int(colon_time_match.group(3) or 0)
            return (hour, minute, second)

        # Tempo（）
        if time_str.isdigit():
            hour = int(time_str)
            return (hour, 0, 0)

        # Retorno0
        return (0, 0, 0)

    def _chinese_month_to_number(self, month_str: str) -> int:
        """
        Empara.
        """
        month_map = {
            "": 1,
            "": 1,
            "": 2,
            "": 3,
            "": 4,
            "": 5,
            "": 6,
            "": 7,
            "": 8,
            "": 9,
            "": 10,
            "": 11,
            "": 12,
        }
        return month_map.get(month_str, 1)

    def _chinese_day_to_number(self, day_str: str) -> int:
        """
        Em  Datapara.
        """
        # 
        chinese_numbers = {
            "": 1,
            "": 2,
            "": 3,
            "": 4,
            "": 5,
            "": 6,
            "": 7,
            "": 8,
            "": 9,
            "": 10,
            "": 20,
            "": 30,
        }

        if "" in day_str:
            day_num = day_str.replace("", "")
            if day_num in chinese_numbers:
                return chinese_numbers[day_num]
            else:
                return int(day_num) if day_num.isdigit() else 1
        elif "" in day_str:
            if day_str == "":
                return 10
            elif day_str.startswith(""):
                remaining = day_str[1:]
                return 10 + chinese_numbers.get(
                    remaining, int(remaining) if remaining.isdigit() else 0
                )
            elif day_str.endswith(""):
                prefix = day_str[:-1]
                return (
                    chinese_numbers.get(prefix, int(prefix) if prefix.isdigit() else 1)
                    * 10
                )
        elif "" in day_str:
            remaining = day_str.replace("", "")
            if remaining in chinese_numbers:
                return 20 + chinese_numbers[remaining]
            else:
                return 20 + (int(remaining) if remaining.isdigit() else 0)
        elif "" in day_str:
            return 30
        else:
            # Tentativa
            if day_str in chinese_numbers:
                return chinese_numbers[day_str]
            try:
                return int(day_str)
            except ValueError:
                return 1

    def _calculate_days_diff(self, solar1, solar2) -> int:
        """
        Solarde.
        """
        try:
            from datetime import datetime

            dt1 = datetime(solar1.getYear(), solar1.getMonth(), solar1.getDay())
            dt2 = datetime(solar2.getYear(), solar2.getMonth(), solar2.getDay())

            return abs((dt2 - dt1).days)
        except Exception:
            return 3  # Valor

    def _match_year_pillar(self, year: int, gan: str, zhi: str) -> bool:
        """Correspondência - Versão，"""
        try:
            from lunar_python import Solar

            # para，Pesquisarde
            # Pesquisar（）
            solar_start = Solar.fromYmdHms(year, 1, 1, 0, 0, 0)
            lunar_start = solar_start.getLunar()
            bazi_start = lunar_start.getEightChar()

            # PesquisarEm（）
            solar_mid = Solar.fromYmdHms(year, 6, 1, 0, 0, 0)
            lunar_mid = solar_mid.getLunar()
            bazi_mid = lunar_mid.getEightChar()

            # Pesquisar
            solar_end = Solar.fromYmdHms(year, 12, 31, 23, 59, 59)
            lunar_end = solar_end.getLunar()
            bazi_end = lunar_end.getEightChar()

            # Se  EmTempo  deCorrespondência，paraCorrespondência
            year_gans = [
                bazi_start.getYearGan(),
                bazi_mid.getYearGan(),
                bazi_end.getYearGan(),
            ]
            year_zhis = [
                bazi_start.getYearZhi(),
                bazi_mid.getYearZhi(),
                bazi_end.getYearZhi(),
            ]

            for i in range(len(year_gans)):
                if year_gans[i] == gan and year_zhis[i] == zhi:
                    return True

            return False
        except Exception:
            return False

    def _match_month_pillar(self, year: int, month: int, gan: str, zhi: str) -> bool:
        """Correspondência - Versão，"""
        try:
            from lunar_python import Solar

            # para，PesquisarEm  Tempo
            # 、Em、deNão，Pesquisar
            test_days = [1, 8, 15, 22, 28]  # PesquisarData

            month_pillars = set()
            for day in test_days:
                try:
                    # Data
                    import calendar

                    max_day = calendar.monthrange(year, month)[1]
                    if day > max_day:
                        day = max_day

                    solar = Solar.fromYmdHms(year, month, day, 12, 0, 0)
                    lunar = solar.getLunar()
                    bazi = lunar.getEightChar()

                    month_gan = bazi.getMonthGan()
                    month_zhi = bazi.getMonthZhi()
                    month_pillars.add(f"{month_gan}{month_zhi}")
                except Exception:
                    continue

            # Se  EmdeCorrespondência，paraCorrespondência
            target_pillar = f"{gan}{zhi}"
            return target_pillar in month_pillars

        except Exception:
            return False

    def _match_day_pillar(
        self, year: int, month: int, day: int, gan: str, zhi: str
    ) -> bool:
        """
        Correspondência.
        """
        try:
            from lunar_python import Solar

            solar = Solar.fromYmdHms(year, month, day, 0, 0, 0)
            lunar = solar.getLunar()
            bazi = lunar.getEightChar()

            day_gan = bazi.getDayGan()
            day_zhi = bazi.getDayZhi()

            return day_gan == gan and day_zhi == zhi
        except Exception:
            return False

    def _match_hour_pillar(
        self,
        hour: int,
        gan: str,
        zhi: str,
        year: int = None,
        month: int = None,
        day: int = None,
    ) -> bool:
        """Correspondência - Versão，UsandoData"""
        try:
            from lunar_python import Solar

            # UsandoDataouData
            use_year = year if year else 2024
            use_month = month if month else 1
            use_day = day if day else 1

            solar = Solar.fromYmdHms(use_year, use_month, use_day, hour, 0, 0)
            lunar = solar.getLunar()
            bazi = lunar.getEightChar()

            hour_gan = bazi.getTimeGan()
            hour_zhi = bazi.getTimeZhi()

            return hour_gan == gan and hour_zhi == zhi
        except Exception:
            return False

    def _get_zodiac_by_lunar_year(self, solar_time: SolarTime) -> str:
        """
        （para，Não）
        """
        try:
            from lunar_python import Solar

            solar = Solar.fromYmdHms(
                solar_time.year,
                solar_time.month,
                solar_time.day,
                solar_time.hour,
                solar_time.minute,
                solar_time.second,
            )
            lunar = solar.getLunar()

            # Usandolunar-python（para）
            return lunar.getYearShengXiao()
        except Exception as e:
            # SeFalha，Usandodepara
            print(f"Falha，Usando: {e}")
            eight_char = self.engine.build_eight_char(solar_time)
            return eight_char.year.earth_branch.zodiac


# Dispositivo
_bazi_calculator = None


def get_bazi_calculator() -> BaziCalculator:
    """
    Dispositivo.
    """
    global _bazi_calculator
    if _bazi_calculator is None:
        _bazi_calculator = BaziCalculator()
    return _bazi_calculator
