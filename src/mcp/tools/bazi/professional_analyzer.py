"""
Dispositivo Usandodadosde.
"""

from typing import Any, Dict, List

from .professional_data import (
    GAN_WUXING,
    WUXING,
    WUXING_RELATIONS,
    ZHI_CANG_GAN,
    ZHI_WUXING,
    analyze_zhi_combinations,
    get_changsheng_state,
    get_nayin,
    get_shensha,
    get_ten_gods_relation,
)


class ProfessionalAnalyzer:
    """Dispositivo - Usandodedados"""

    def __init__(self):
        """
        InicializandoDispositivo.
        """

    def get_ten_gods_analysis(self, day_master: str, other_stem: str) -> str:
        """
        .
        """
        return get_ten_gods_relation(day_master, other_stem)

    def analyze_eight_char_structure(
        self, eight_char_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        .
        """
        year_gan = (
            eight_char_data.get("year", {}).get("heaven_stem", {}).get("name", "")
        )
        year_zhi = (
            eight_char_data.get("year", {}).get("earth_branch", {}).get("name", "")
        )
        month_gan = (
            eight_char_data.get("month", {}).get("heaven_stem", {}).get("name", "")
        )
        month_zhi = (
            eight_char_data.get("month", {}).get("earth_branch", {}).get("name", "")
        )
        day_gan = eight_char_data.get("day", {}).get("heaven_stem", {}).get("name", "")
        day_zhi = eight_char_data.get("day", {}).get("earth_branch", {}).get("name", "")
        hour_gan = (
            eight_char_data.get("hour", {}).get("heaven_stem", {}).get("name", "")
        )
        hour_zhi = (
            eight_char_data.get("hour", {}).get("earth_branch", {}).get("name", "")
        )

        # Informação
        gan_list = [year_gan, month_gan, day_gan, hour_gan]
        zhi_list = [year_zhi, month_zhi, day_zhi, hour_zhi]

        analysis = {
            "day_master": day_gan,
            "ten_gods": self._analyze_ten_gods(day_gan, gan_list, zhi_list),
            "nayin": self._analyze_nayin(gan_list, zhi_list),
            "changsheng": self._analyze_changsheng(day_gan, zhi_list),
            "zhi_relations": analyze_zhi_combinations(zhi_list),
            "wuxing_balance": self._analyze_wuxing_balance(gan_list, zhi_list),
            "shensha": self._analyze_shensha(gan_list, zhi_list),
            "strength": self._analyze_day_master_strength(day_gan, month_zhi, zhi_list),
            "useful_god": self._determine_useful_god(
                day_gan, month_zhi, gan_list, zhi_list
            ),
        }

        return analysis

    def _analyze_ten_gods(
        self, day_master: str, gan_list: List[str], zhi_list: List[str]
    ) -> Dict[str, List[str]]:
        """
        .
        """
        ten_gods = {
            "": [],
            "": [],
            "": [],
            "": [],
            "": [],
            "": [],
            "": [],
            "": [],
            "": [],
            "": [],
        }

        # 
        for i, gan in enumerate(gan_list):
            if gan == day_master:
                continue

            ten_god = get_ten_gods_relation(day_master, gan)
            pillar_names = ["", "", "", ""]
            if ten_god in ten_gods:
                ten_gods[ten_god].append(f"{pillar_names[i]}{gan}")

        # 
        pillar_names = ["", "", "", ""]
        for i, zhi in enumerate(zhi_list):
            cang_gan = ZHI_CANG_GAN.get(zhi, {})
            for gan, strength in cang_gan.items():
                if gan == day_master:
                    continue

                ten_god = get_ten_gods_relation(day_master, gan)
                if ten_god in ten_gods:
                    ten_gods[ten_god].append(
                        f"{pillar_names[i]}{zhi}{gan}({strength})"
                    )

        return ten_gods

    def _analyze_nayin(self, gan_list: List[str], zhi_list: List[str]) -> List[str]:
        """
        .
        """
        nayin_list = []
        pillar_names = ["", "", "", ""]

        for i, (gan, zhi) in enumerate(zip(gan_list, zhi_list)):
            nayin = get_nayin(gan, zhi)
            nayin_list.append(f"{pillar_names[i]}{gan}{zhi}：{nayin}")

        return nayin_list

    def _analyze_changsheng(self, day_master: str, zhi_list: List[str]) -> List[str]:
        """
        .
        """
        changsheng_list = []
        pillar_names = ["", "", "", ""]

        for i, zhi in enumerate(zhi_list):
            state = get_changsheng_state(day_master, zhi)
            changsheng_list.append(f"{pillar_names[i]}{zhi}：{state}")

        return changsheng_list

    def _analyze_wuxing_balance(
        self, gan_list: List[str], zhi_list: List[str]
    ) -> Dict[str, Any]:
        """
        .
        """
        wuxing_count = {element: 0 for element in WUXING}

        # 
        for gan in gan_list:
            wuxing = GAN_WUXING.get(gan, "")
            if wuxing in wuxing_count:
                wuxing_count[wuxing] += 2  # 

        # 
        for zhi in zhi_list:
            wuxing = ZHI_WUXING.get(zhi, "")
            if wuxing in wuxing_count:
                wuxing_count[wuxing] += 1

            # 
            cang_gan = ZHI_CANG_GAN.get(zhi, {})
            for gan, strength in cang_gan.items():
                wuxing = GAN_WUXING.get(gan, "")
                if wuxing in wuxing_count:
                    wuxing_count[wuxing] += strength / 10  # 

        # ede
        max_wuxing = max(wuxing_count, key=wuxing_count.get)
        min_wuxing = min(wuxing_count, key=wuxing_count.get)

        return {
            "distribution": wuxing_count,
            "strongest": max_wuxing,
            "weakest": min_wuxing,
            "balance_score": self._calculate_balance_score(wuxing_count),
        }

    def _calculate_balance_score(self, wuxing_count: Dict[str, float]) -> float:
        """
        Pontuação（0-100，100para）
        """
        values = list(wuxing_count.values())
        if not values:
            return 0

        average = sum(values) / len(values)
        variance = sum((v - average) ** 2 for v in values) / len(values)
        # para0-100Pontuação，Pontuação
        balance_score = max(0, 100 - variance * 10)
        return round(balance_score, 2)

    def _analyze_shensha(
        self, gan_list: List[str], zhi_list: List[str]
    ) -> Dict[str, List[str]]:
        """
         - Versão，PesquisarePesquisarde.
        """
        shensha = {
            "": [],
            "": [],
            "": [],
            "": [],
            "": [],
        }

        day_gan = gan_list[2] if len(gan_list) > 2 else ""
        day_zhi = zhi_list[2] if len(zhi_list) > 2 else ""
        pillar_names = ["", "", "", ""]

        # Pesquisarde
        day_gan_shensha = [
            ("tianyi", ""),
            ("wenchang", ""),
        ]

        for shensha_type, shensha_name in day_gan_shensha:
            shensha_zhi = get_shensha(day_gan, shensha_type)
            if shensha_zhi:
                for i, zhi in enumerate(zhi_list):
                    if zhi in shensha_zhi:
                        shensha[shensha_name].append(f"{pillar_names[i]}{zhi}")

        # Pesquisarde
        day_zhi_shensha = [
            ("yima", ""),
            ("taohua", ""),
            ("huagai", ""),
        ]

        for shensha_type, shensha_name in day_zhi_shensha:
            shensha_zhi = get_shensha(day_zhi, shensha_type)
            if shensha_zhi:
                for i, zhi in enumerate(zhi_list):
                    if zhi == shensha_zhi:  # Retornode
                        shensha[shensha_name].append(f"{pillar_names[i]}{zhi}")

        return shensha

    def _analyze_day_master_strength(
        self, day_master: str, month_zhi: str, zhi_list: List[str]
    ) -> Dict[str, Any]:
        """
        .
        """
        # 
        month_element = ZHI_WUXING.get(month_zhi, "")
        day_element = GAN_WUXING.get(day_master, "")

        # 
        month_relation = WUXING_RELATIONS.get((day_element, month_element), "")

        # 
        same_element_count = 0
        help_element_count = 0

        for zhi in zhi_list:
            zhi_element = ZHI_WUXING.get(zhi, "")
            if zhi_element == day_element:
                same_element_count += 1
            elif WUXING_RELATIONS.get((zhi_element, day_element)) == "↓":  # 
                help_element_count += 1

        # 
        strength_score = 0
        if month_relation == "↑":  # 
            strength_score -= 30
        elif month_relation == "↓":  # 
            strength_score += 30
        elif month_relation == "=":  # 
            strength_score += 20
        elif month_relation == "←":  # 
            strength_score -= 20
        elif month_relation == "→":  # 
            strength_score -= 10

        strength_score += same_element_count * 15
        strength_score += help_element_count * 10

        if strength_score >= 30:
            strength_level = ""
        elif strength_score >= 10:
            strength_level = "Eme"
        elif strength_score >= -10:
            strength_level = ""
        else:
            strength_level = ""

        return {
            "level": strength_level,
            "score": strength_score,
            "month_relation": month_relation,
            "same_element_count": same_element_count,
            "help_element_count": help_element_count,
        }

    def _determine_useful_god(
        self, day_master: str, month_zhi: str, gan_list: List[str], zhi_list: List[str]
    ) -> Dict[str, Any]:
        """
        .
        """
        day_element = GAN_WUXING.get(day_master, "")
        strength_analysis = self._analyze_day_master_strength(
            day_master, month_zhi, zhi_list
        )

        useful_gods = []
        avoid_gods = []

        if strength_analysis["level"] in ["", ""]:
            # 
            for element in WUXING:
                relation = WUXING_RELATIONS.get((day_element, element), "")
                if relation == "→":  # para
                    useful_gods.append(f"{element}（）")
                elif relation == "↓":  # para
                    useful_gods.append(f"{element}（）")
                elif relation == "←":  # para
                    useful_gods.append(f"{element}（）")
        else:
            # 
            for element in WUXING:
                relation = WUXING_RELATIONS.get((element, day_element), "")
                if relation == "↓":  # para
                    useful_gods.append(f"{element}（）")
                elif relation == "=":  # para
                    useful_gods.append(f"{element}（）")

        return {
            "useful_gods": useful_gods[:3],  # 3
            "avoid_gods": avoid_gods[:3],  # 3
            "strategy": (
                "" if strength_analysis["level"] in ["", ""] else ""
            ),
        }

    def get_detailed_fortune_analysis(self, eight_char_data: Dict[str, Any]) -> str:
        """
        de.
        """
        analysis = self.analyze_eight_char_structure(eight_char_data)

        result_lines = []
        result_lines.append("===  ===\n")

        # 
        result_lines.append(
            f"【】{analysis['day_master']}（{GAN_WUXING.get(analysis['day_master'], '')}）"
        )
        result_lines.append(
            f"【】{analysis['strength']['level']}（：{analysis['strength']['score']}）"
        )
        result_lines.append("")

        # 
        result_lines.append("【】")
        for god_name, positions in analysis["ten_gods"].items():
            if positions:
                result_lines.append(f"  {god_name}：{', '.join(positions)}")
        result_lines.append("")

        # 
        result_lines.append("【】")
        result_lines.append(f"  ：{analysis['useful_god']['strategy']}")
        if analysis["useful_god"]["useful_gods"]:
            result_lines.append(
                f"  ：{', '.join(analysis['useful_god']['useful_gods'])}"
            )
        result_lines.append("")

        # 
        result_lines.append("【】")
        for element, count in analysis["wuxing_balance"]["distribution"].items():
            result_lines.append(f"  {element}：{count:.1f}")
        result_lines.append(f"  ：{analysis['wuxing_balance']['balance_score']}")
        result_lines.append("")

        # 
        result_lines.append("【】")
        for relation_type, relations in analysis["zhi_relations"].items():
            if relations:
                result_lines.append(f"  {relation_type}：{', '.join(relations)}")
        result_lines.append("")

        # 
        result_lines.append("【】")
        for shensha_name, positions in analysis["shensha"].items():
            if positions:
                result_lines.append(f"  {shensha_name}：{', '.join(positions)}")
        result_lines.append("")

        # 
        result_lines.append("【】")
        for nayin in analysis["nayin"]:
            result_lines.append(f"  {nayin}")

        return "\n".join(result_lines)


# Dispositivo
_professional_analyzer = None


def get_professional_analyzer() -> ProfessionalAnalyzer:
    """
    Dispositivo.
    """
    global _professional_analyzer
    if _professional_analyzer is None:
        _professional_analyzer = ProfessionalAnalyzer()
    return _professional_analyzer
