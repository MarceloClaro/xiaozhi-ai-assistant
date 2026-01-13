"""
 、InformaçãoAguardar.
"""

from typing import Any, Dict, List

from .professional_data import TAOHUA_XING, WUXING, get_ten_gods_relation


class MarriageAnalyzer:
    """
    Dispositivo.
    """

    def __init__(self):
        self.marriage_gods = {
            "male": ["", ""],  # 
            "female": ["", ""],  # 
        }

    def analyze_marriage_timing(
        self, eight_char_data: Dict[str, Any], gender: int
    ) -> Dict[str, Any]:
        """
        .
        """
        result = {
            "marriage_star_analysis": self._analyze_marriage_star(
                eight_char_data, gender
            ),
            "marriage_age_range": self._predict_marriage_age(eight_char_data, gender),
            "favorable_years": self._get_favorable_marriage_years(
                eight_char_data, gender
            ),
            "marriage_obstacles": self._analyze_marriage_obstacles(eight_char_data),
            "spouse_characteristics": self._analyze_spouse_features(
                eight_char_data, gender
            ),
            "marriage_quality": self._evaluate_marriage_quality(
                eight_char_data, gender
            ),
        }
        return result

    def _analyze_marriage_star(
        self, eight_char_data: Dict[str, Any], gender: int
    ) -> Dict[str, Any]:
        """
        .
        """
        from .professional_data import ZHI_CANG_GAN, get_changsheng_state

        gender_key = "male" if gender == 1 else "female"
        target_gods = self.marriage_gods[gender_key]

        # DadosFormato
        year_gan = self._extract_gan_from_pillar(eight_char_data.get("year", {}))
        month_gan = self._extract_gan_from_pillar(eight_char_data.get("month", {}))
        day_gan = self._extract_gan_from_pillar(eight_char_data.get("day", {}))
        hour_gan = self._extract_gan_from_pillar(eight_char_data.get("hour", {}))

        marriage_stars = []

        # Pesquisar
        for position, gan in [
            ("", year_gan),
            ("", month_gan),
            ("", hour_gan),
        ]:
            if gan and gan != day_gan:
                ten_god = get_ten_gods_relation(day_gan, gan)
                if ten_god in target_gods:
                    # de
                    star_info = {
                        "position": position,
                        "star": ten_god,
                        "strength": self._evaluate_star_strength(position),
                        "element": self._get_gan_element(gan),
                        "quality": self._evaluate_star_quality(position, ten_god),
                        "seasonal_strength": self._get_seasonal_strength(
                            gan, month_gan
                        ),
                    }
                    marriage_stars.append(star_info)

        # Emde
        for position, pillar in [
            ("", eight_char_data.get("year", {})),
            ("", eight_char_data.get("month", {})),
            ("", eight_char_data.get("hour", {})),
        ]:
            zhi_name = self._extract_zhi_from_pillar(pillar)
            if zhi_name and zhi_name in ZHI_CANG_GAN:
                cang_gan_data = ZHI_CANG_GAN[zhi_name]

                for hidden_gan, strength in cang_gan_data.items():
                    if hidden_gan != day_gan:
                        ten_god = get_ten_gods_relation(day_gan, hidden_gan)
                        if ten_god in target_gods:
                            # Tipo
                            gan_type = self._determine_canggan_type(strength)

                            star_info = {
                                "position": position,
                                "star": ten_god,
                                "strength": self._get_hidden_strength(gan_type),
                                "element": self._get_gan_element(hidden_gan),
                                "type": f"{gan_type}",
                                "quality": self._evaluate_hidden_star_quality(
                                    zhi_name, hidden_gan, strength
                                ),
                                "changsheng_state": get_changsheng_state(
                                    day_gan, zhi_name
                                ),
                            }
                            marriage_stars.append(star_info)

        # de
        star_analysis = self._comprehensive_star_analysis(
            marriage_stars, day_gan, gender
        )

        return {
            "has_marriage_star": len(marriage_stars) > 0,
            "marriage_stars": marriage_stars,
            "star_count": len(marriage_stars),
            "star_strength": star_analysis["strength"],
            "star_quality": star_analysis["quality"],
            "star_distribution": star_analysis["distribution"],
            "marriage_potential": star_analysis["potential"],
            "improvement_suggestions": star_analysis["suggestions"],
        }

    def _predict_marriage_age(
        self, eight_char_data: Dict[str, Any], gender: int
    ) -> Dict[str, Any]:
        """
        .
        """
        from .professional_data import (
            CHANGSHENG_TWELVE,
            GAN_WUXING,
            HUAGAI_XING,
            TIANYI_GUIREN,
            WUXING_RELATIONS,
            ZHI_WUXING,
        )

        day_gan = self._extract_gan_from_pillar(eight_char_data.get("day", {}))
        day_zhi = self._extract_zhi_from_pillar(eight_char_data.get("day", {}))
        self._extract_gan_from_pillar(eight_char_data.get("month", {}))
        month_zhi = self._extract_zhi_from_pillar(eight_char_data.get("month", {}))
        year_zhi = self._extract_zhi_from_pillar(eight_char_data.get("year", {}))
        hour_zhi = self._extract_zhi_from_pillar(eight_char_data.get("hour", {}))

        # 
        factors = {
            "early_signs": [],
            "late_signs": [],
            "score": 50,  # Pontuação
            "detailed_analysis": [],
        }

        # 1. （）
        if day_zhi in "":
            factors["early_signs"].append("")
            factors["score"] -= 12
            factors["detailed_analysis"].append("")

        if day_zhi in "":
            factors["early_signs"].append("")
            factors["score"] -= 8
            factors["detailed_analysis"].append("，")

        if day_zhi in "Não":
            factors["late_signs"].append("Banco de dados")
            factors["score"] += 15
            factors["detailed_analysis"].append("Banco de dados，")

        # 2. 
        marriage_star_analysis = self._analyze_marriage_star(eight_char_data, gender)
        star_strength = marriage_star_analysis.get("star_strength", "")
        marriage_star_analysis.get("star_count", 0)

        if star_strength == "":
            factors["score"] -= 8
            factors["early_signs"].append("")
            factors["detailed_analysis"].append("，")
        elif star_strength == "":
            factors["score"] -= 5
            factors["early_signs"].append("")
        elif star_strength == "" or star_strength == "":
            factors["score"] += 10
            factors["late_signs"].append("")
            factors["detailed_analysis"].append("，Aguardando")

        # 3. 
        if day_gan in CHANGSHENG_TWELVE:
            changsheng_state = CHANGSHENG_TWELVE[day_gan].get(day_zhi, "")
            if changsheng_state in ["", "", ""]:
                factors["score"] -= 6
                factors["early_signs"].append(f"Em{changsheng_state}")
                factors["detailed_analysis"].append(
                    f"{changsheng_state}，"
                )
            elif changsheng_state in ["", "", ""]:
                factors["score"] += 8
                factors["late_signs"].append(f"Em{changsheng_state}")
                factors["detailed_analysis"].append(
                    f"{changsheng_state}，Tempo"
                )

        # 4. 
        all_zhi = [year_zhi, month_zhi, day_zhi, hour_zhi]

        # 
        tianyi_zhi = TIANYI_GUIREN.get(day_gan, "")
        if tianyi_zhi and any(zhi in tianyi_zhi for zhi in all_zhi):
            factors["score"] -= 5
            factors["early_signs"].append("")
            factors["detailed_analysis"].append("，")

        # 
        huagai_zhi = HUAGAI_XING.get(day_zhi, "")
        if huagai_zhi and any(zhi == huagai_zhi for zhi in all_zhi):
            factors["score"] += 12
            factors["late_signs"].append("")
            factors["detailed_analysis"].append("，")

        # 5. 
        day_element = GAN_WUXING.get(day_gan, "")
        month_element = ZHI_WUXING.get(month_zhi, "")

        if day_element and month_element:
            relation = WUXING_RELATIONS.get((month_element, day_element), "")
            if relation == "↓":  # 
                factors["score"] -= 6
                factors["early_signs"].append("")
                factors["detailed_analysis"].append("，")
            elif relation == "←":  # 
                factors["score"] += 8
                factors["late_signs"].append("")
                factors["detailed_analysis"].append("，Tempo")

        # 6. 
        spouse_palace_analysis = self._analyze_spouse_palace(day_zhi, month_zhi)
        factors["score"] += spouse_palace_analysis["age_adjustment"]
        factors["detailed_analysis"].extend(spouse_palace_analysis["analysis"])

        # 7. 
        if gender == 1:  # 
            factors["score"] -= 3  # 
            factors["detailed_analysis"].append("")
        else:  # 
            factors["score"] += 2
            factors["detailed_analysis"].append("")

        # 8. 
        final_score = max(20, min(80, factors["score"]))

        # Pontuação
        if final_score <= 30:
            age_prediction = ""
            age_range = "18-24"
            tendency = "，para"
        elif final_score <= 40:
            age_prediction = ""
            age_range = "22-27"
            tendency = "，"
        elif final_score <= 60:
            age_prediction = "Em"
            age_range = "25-30"
            tendency = "，"
        elif final_score <= 70:
            age_prediction = ""
            age_range = "28-35"
            tendency = "，Aguardando"
        else:
            age_prediction = ""
            age_range = "30-40"
            tendency = "，"

        return {
            "prediction": age_prediction,
            "age_range": age_range,
            "tendency": tendency,
            "score": final_score,
            "early_factors": factors["early_signs"],
            "late_factors": factors["late_signs"],
            "detailed_analysis": factors["detailed_analysis"],
            "analysis_basis": f"{day_gan}{day_zhi}de",
            "confidence": self._calculate_prediction_confidence(factors),
        }

    def _get_favorable_marriage_years(
        self, eight_char_data: Dict[str, Any], gender: int
    ) -> List[str]:
        """
        de - Usandode.
        """
        from .professional_data import YIMA_XING, ZHI_RELATIONS, ZHI_SAN_HE, ZHI_SAN_HUI

        day_zhi = eight_char_data.get("day", {}).get("earth_branch", {}).get("name", "")
        month_zhi = (
            eight_char_data.get("month", {}).get("earth_branch", {}).get("name", "")
        )
        year_zhi = (
            eight_char_data.get("year", {}).get("earth_branch", {}).get("name", "")
        )

        favorable_branches = []

        # 1.  - 
        if day_zhi in ZHI_RELATIONS:
            liuhe_zhi = ZHI_RELATIONS[day_zhi].get("", "")
            if liuhe_zhi:
                favorable_branches.append(
                    {"zhi": liuhe_zhi, "reason": "", "priority": ""}
                )

        # 2.  - 
        for sanhe_combo, element in ZHI_SAN_HE.items():
            if day_zhi in sanhe_combo:
                # EncontradoEmde
                for zhi in sanhe_combo:
                    if zhi != day_zhi:
                        favorable_branches.append(
                            {"zhi": zhi, "reason": f"{element}", "priority": ""}
                        )

        # 3.  - 
        for sanhui_combo, element in ZHI_SAN_HUI.items():
            if day_zhi in sanhui_combo:
                for zhi in sanhui_combo:
                    if zhi != day_zhi:
                        favorable_branches.append(
                            {"zhi": zhi, "reason": f"{element}", "priority": "Em"}
                        )

        # 4.  - 
        taohua_zhi = TAOHUA_XING.get(day_zhi, "")
        if taohua_zhi:
            favorable_branches.append(
                {"zhi": taohua_zhi, "reason": "", "priority": "Em"}
            )

        # 5.  - ，
        yima_zhi = YIMA_XING.get(day_zhi, "")
        if yima_zhi:
            favorable_branches.append(
                {"zhi": yima_zhi, "reason": "", "priority": "Em"}
            )

        # 6. de
        if month_zhi in ZHI_RELATIONS:
            month_liuhe = ZHI_RELATIONS[month_zhi].get("", "")
            if month_liuhe:
                favorable_branches.append(
                    {"zhi": month_liuhe, "reason": "", "priority": "Em"}
                )

        # 7. de
        if year_zhi in ZHI_RELATIONS:
            year_liuhe = ZHI_RELATIONS[year_zhi].get("", "")
            if year_liuhe:
                favorable_branches.append(
                    {"zhi": year_liuhe, "reason": "", "priority": ""}
                )

        # 
        unique_branches = {}
        for branch in favorable_branches:
            zhi = branch["zhi"]
            if zhi not in unique_branches or branch["priority"] == "":
                unique_branches[zhi] = branch

        # 
        priority_order = {"": 1, "Em": 2, "": 3}
        sorted_branches = sorted(
            unique_branches.values(), key=lambda x: priority_order[x["priority"]]
        )

        return [f"{branch['zhi']}({branch['reason']})" for branch in sorted_branches]

    def _analyze_spouse_palace(self, day_zhi: str, month_zhi: str) -> Dict[str, Any]:
        """
        （）de.
        """
        from .professional_data import WUXING_RELATIONS, ZHI_WUXING

        palace_analysis = {"age_adjustment": 0, "analysis": []}

        # 
        day_element = ZHI_WUXING.get(day_zhi, "")
        month_element = ZHI_WUXING.get(month_zhi, "")

        if day_element and month_element:
            relation = WUXING_RELATIONS.get((month_element, day_element), "")
            if relation == "↓":  # 
                palace_analysis["age_adjustment"] -= 4
                palace_analysis["analysis"].append("，")
            elif relation == "←":  # 
                palace_analysis["age_adjustment"] += 6
                palace_analysis["analysis"].append("，")

        # 
        palace_characteristics = {
            "": {"adjustment": -2, "desc": "，"},
            "": {"adjustment": 4, "desc": "，"},
            "": {"adjustment": -3, "desc": "，"},
            "": {"adjustment": 0, "desc": "e，"},
            "": {"adjustment": 5, "desc": "，"},
            "": {"adjustment": -1, "desc": "，Em"},
            "": {"adjustment": -4, "desc": "，"},
            "Não": {"adjustment": 3, "desc": "Nãoe，"},
            "": {"adjustment": -2, "desc": "，"},
            "": {"adjustment": 1, "desc": "，Em"},
            "": {"adjustment": 6, "desc": "，"},
            "": {"adjustment": -1, "desc": "，Em"},
        }

        if day_zhi in palace_characteristics:
            char = palace_characteristics[day_zhi]
            palace_analysis["age_adjustment"] += char["adjustment"]
            palace_analysis["analysis"].append(char["desc"])

        return palace_analysis

    def _calculate_prediction_confidence(self, factors: Dict[str, Any]) -> str:
        """
        .
        """
        early_count = len(factors["early_signs"])
        late_count = len(factors["late_signs"])
        analysis_count = len(factors["detailed_analysis"])

        # 
        if early_count >= 4 and late_count <= 1:
            consistency = ""
        elif late_count >= 4 and early_count <= 1:
            consistency = ""
        elif abs(early_count - late_count) <= 1:
            consistency = "Em"
        else:
            consistency = ""

        # 
        if analysis_count >= 8:
            depth = ""
        elif analysis_count >= 5:
            depth = ""
        else:
            depth = ""

        # 
        if consistency == "" and depth == "":
            return ""
        elif consistency == "" or depth == "":
            return ""
        elif consistency == "Em" and depth == "":
            return ""
        elif consistency == "Em" or depth == "":
            return "EmAguardar"
        else:
            return ""

    def _analyze_marriage_obstacles(self, eight_char_data: Dict[str, Any]) -> List[str]:
        """
        .
        """
        from .professional_data import HUAGAI_XING, analyze_zhi_combinations

        obstacles = []

        # 
        zhi_list = [
            eight_char_data.get("year", {}).get("earth_branch", {}).get("name", ""),
            eight_char_data.get("month", {}).get("earth_branch", {}).get("name", ""),
            eight_char_data.get("day", {}).get("earth_branch", {}).get("name", ""),
            eight_char_data.get("hour", {}).get("earth_branch", {}).get("name", ""),
        ]

        # （）
        day_zhi = zhi_list[2] if len(zhi_list) > 2 else ""

        # Usando
        zhi_relations = analyze_zhi_combinations(zhi_list)

        # 1.  - de
        if zhi_relations.get("chong"):
            for chong_desc in zhi_relations["chong"]:
                if day_zhi in chong_desc:
                    obstacles.append(f"{chong_desc}，")
                else:
                    obstacles.append(f"{chong_desc}，e")

        # 2.  - 
        if zhi_relations.get("xing"):
            for xing_desc in zhi_relations["xing"]:
                if day_zhi in xing_desc:
                    obstacles.append(f"{xing_desc}，")
                else:
                    obstacles.append(f"{xing_desc}，")

        # 3.  - 
        if zhi_relations.get("hai"):
            for hai_desc in zhi_relations["hai"]:
                if day_zhi in hai_desc:
                    obstacles.append(f"{hai_desc}，")
                else:
                    obstacles.append(f"{hai_desc}，")

        # 4.  - 
        day_gan = self._extract_gan_from_pillar(eight_char_data.get("day", {}))
        if day_gan:
            huagai_zhi = HUAGAI_XING.get(day_gan, "")
            if huagai_zhi and huagai_zhi in zhi_list:
                obstacles.append("，，Não")

        # 5. 
        if day_zhi:
            spouse_palace_obstacles = self._analyze_spouse_palace_obstacles(
                day_zhi, zhi_list
            )
            obstacles.extend(spouse_palace_obstacles)

        # 6. 
        marriage_star_analysis = self._analyze_marriage_star(
            eight_char_data, 1
        )  # 
        if marriage_star_analysis.get("star_count", 0) == 0:
            obstacles.append("，")
        elif marriage_star_analysis.get("star_strength") in ["", ""]:
            obstacles.append("，Não")

        # 7. 
        wuxing_obstacles = self._analyze_wuxing_marriage_obstacles(eight_char_data)
        obstacles.extend(wuxing_obstacles)

        # Limitado a
        unique_obstacles = list(set(obstacles))
        return unique_obstacles[:8]  # Retorno8

    def _analyze_spouse_palace_obstacles(
        self, day_zhi: str, zhi_list: List[str]
    ) -> List[str]:
        """
        de.
        """
        obstacles = []

        # 
        palace_issues = {
            "": "，",
            "": "，",
            "": "，Não",
            "Não": "Não，",
        }

        if day_zhi in palace_issues:
            obstacles.append(palace_issues[day_zhi])

        # 
        if zhi_list.count(day_zhi) > 1:
            obstacles.append(f"{day_zhi}，ModoConversão")

        return obstacles

    def _analyze_wuxing_marriage_obstacles(
        self, eight_char_data: Dict[str, Any]
    ) -> List[str]:
        """
        de.
        """
        from .professional_data import GAN_WUXING, ZHI_WUXING

        obstacles = []

        # 
        wuxing_count = {element: 0 for element in WUXING}

        # 
        for pillar_key in ["year", "month", "day", "hour"]:
            gan = self._extract_gan_from_pillar(eight_char_data.get(pillar_key, {}))
            if gan:
                element = GAN_WUXING.get(gan, "")
                if element in wuxing_count:
                    wuxing_count[element] += 1

        # 
        for pillar_key in ["year", "month", "day", "hour"]:
            zhi = self._extract_zhi_from_pillar(eight_char_data.get(pillar_key, {}))
            if zhi:
                element = ZHI_WUXING.get(zhi, "")
                if element in wuxing_count:
                    wuxing_count[element] += 1

        # 
        total_count = sum(wuxing_count.values())
        if total_count > 0:
            # Pesquisaroude
            for element, count in wuxing_count.items():
                ratio = count / total_count
                if ratio >= 0.5:  # 50%
                    obstacles.append(f"{element}，")
                elif ratio == 0:  # 
                    element_effects = {
                        "": "，Não，",
                        "": "，Não，",
                        "": "，Não，Conversão",
                        "": "，Não，",
                        "": "，Não，",
                    }
                    if element in element_effects:
                        obstacles.append(element_effects[element])

        return obstacles

    def _analyze_spouse_features(
        self, eight_char_data: Dict[str, Any], gender: int
    ) -> Dict[str, str]:
        """
         - Usando.
        """

        day_zhi = eight_char_data.get("day", {}).get("earth_branch", {}).get("name", "")
        day_gan = self._extract_gan_from_pillar(eight_char_data.get("day", {}))
        month_zhi = self._extract_zhi_from_pillar(eight_char_data.get("month", {}))

        # 
        basic_features = self._get_basic_spouse_features(day_zhi)

        # 
        wuxing_influence = self._analyze_wuxing_spouse_influence(day_zhi, month_zhi)

        # 
        canggan_influence = self._analyze_canggan_spouse_influence(day_zhi, day_gan)

        # 
        star_influence = self._analyze_marriage_star_spouse_influence(
            eight_char_data, gender
        )

        # 
        return {
            "personality": self._synthesize_personality(
                basic_features["personality"],
                wuxing_influence["personality"],
                star_influence["personality"],
            ),
            "appearance": self._synthesize_appearance(
                basic_features["appearance"],
                wuxing_influence["appearance"],
                canggan_influence["appearance"],
            ),
            "career_tendency": self._synthesize_career(
                basic_features["career"],
                wuxing_influence["career"],
                star_influence["career"],
            ),
            "relationship_mode": star_influence["relationship_mode"],
            "compatibility": self._evaluate_compatibility(day_gan, day_zhi, month_zhi),
            "improvement_suggestions": self._generate_spouse_improvement_suggestions(
                day_zhi, wuxing_influence, star_influence
            ),
        }

    def _get_basic_spouse_features(self, day_zhi: str) -> Dict[str, str]:
        """
        .
        """
        spouse_features = {
            "": {
                "personality": "，，，",
                "appearance": "EmAguardar，，",
                "career": "、、、IT",
            },
            "": {
                "personality": "，，，",
                "appearance": "，，",
                "career": "、、、",
            },
            "": {
                "personality": "，，，",
                "appearance": "，，",
                "career": "、、、",
            },
            "": {
                "personality": "e，，，",
                "appearance": "，，",
                "career": "、、、Conversão",
            },
            "": {
                "personality": "，，para，",
                "appearance": "EmAguardar，，",
                "career": "、、、",
            },
            "": {
                "personality": "，，，",
                "appearance": "Em，，",
                "career": "Conversão、、、",
            },
            "": {
                "personality": "，，，",
                "appearance": "，，",
                "career": "Fonte、、、",
            },
            "Não": {
                "personality": "，，，",
                "appearance": "EmAguardar，e，",
                "career": "、、、",
            },
            "": {
                "personality": "，，，",
                "appearance": "，，",
                "career": "、、、",
            },
            "": {
                "personality": "，，，",
                "appearance": "，，",
                "career": "、、、",
            },
            "": {
                "personality": "，，，",
                "appearance": "，，",
                "career": "、、、",
            },
            "": {
                "personality": "，，para，",
                "appearance": "，e，e",
                "career": "、、、",
            },
        }

        return spouse_features.get(
            day_zhi,
            {
                "personality": "e，para",
                "appearance": "，",
                "career": "",
            },
        )

    def _analyze_wuxing_spouse_influence(
        self, day_zhi: str, month_zhi: str
    ) -> Dict[str, str]:
        """
        de.
        """
        from .professional_data import WUXING_RELATIONS, ZHI_WUXING

        day_element = ZHI_WUXING.get(day_zhi, "")
        month_element = ZHI_WUXING.get(month_zhi, "")

        influence = {"personality": "", "appearance": "", "career": ""}

        if day_element and month_element:
            relation = WUXING_RELATIONS.get((month_element, day_element), "")

            if relation == "↓":  # 
                influence["personality"] = "，"
                influence["appearance"] = "，"
                influence["career"] = "Não，"
            elif relation == "←":  # 
                influence["personality"] = "，para"
                influence["appearance"] = "，"
                influence["career"] = "，"
            elif relation == "=":  # 
                influence["personality"] = "，NãoConversão"
                influence["appearance"] = "，"
                influence["career"] = ""

        return influence

    def _analyze_canggan_spouse_influence(
        self, day_zhi: str, day_gan: str
    ) -> Dict[str, str]:
        """
        de.
        """
        from .professional_data import GAN_WUXING, ZHI_CANG_GAN

        influence = {"appearance": ""}

        if day_zhi in ZHI_CANG_GAN:
            canggan_data = ZHI_CANG_GAN[day_zhi]

            # 
            main_gans = [gan for gan, strength in canggan_data.items() if strength >= 5]
            if main_gans:
                main_gan = main_gans[0]
                main_element = GAN_WUXING.get(main_gan, "")

                element_appearance = {
                    "": "，，",
                    "": "，，",
                    "": "，，e",
                    "": "，，",
                    "": "，，",
                }

                if main_element in element_appearance:
                    influence["appearance"] = element_appearance[main_element]

        return influence

    def _analyze_marriage_star_spouse_influence(
        self, eight_char_data: Dict[str, Any], gender: int
    ) -> Dict[str, str]:
        """
        de.
        """
        star_analysis = self._analyze_marriage_star(eight_char_data, gender)

        influence = {"personality": "", "career": "", "relationship_mode": ""}

        if star_analysis["has_marriage_star"]:
            star_strength = star_analysis["star_strength"]
            star_analysis["star_quality"]

            # 
            if star_strength in ["", ""]:
                influence["personality"] = "，"
                influence["career"] = "，"
                influence["relationship_mode"] = "，"
            elif star_strength == "Em":
                influence["personality"] = "e，Em"
                influence["career"] = ""
                influence["relationship_mode"] = "e，e"
            else:
                influence["personality"] = "，Não"
                influence["career"] = "Tempo"
                influence["relationship_mode"] = "，"
        else:
            influence["personality"] = "，"
            influence["career"] = "Não"
            influence["relationship_mode"] = "，"

        return influence

    def _synthesize_personality(self, basic: str, wuxing: str, star: str) -> str:
        """
        .
        """
        result = basic
        if wuxing:
            result += f"，{wuxing}"
        if star:
            result += f"，{star}"
        return result

    def _synthesize_appearance(self, basic: str, wuxing: str, canggan: str) -> str:
        """
        .
        """
        result = basic
        if canggan:
            result = canggan  # 
        if wuxing:
            result += f"，{wuxing}"
        return result

    def _synthesize_career(self, basic: str, wuxing: str, star: str) -> str:
        """
        .
        """
        result = basic
        if star:
            result = f"{basic}，{star}"
        if wuxing:
            result += f"，{wuxing}"
        return result

    def _evaluate_compatibility(
        self, day_gan: str, day_zhi: str, month_zhi: str
    ) -> str:
        """
        .
        """
        from .professional_data import ZHI_RELATIONS

        compatibility_score = 70  # Pontuação

        # Pesquisar
        if day_zhi in ZHI_RELATIONS:
            relations = ZHI_RELATIONS[day_zhi]
            if month_zhi == relations.get("", ""):
                compatibility_score += 20
                return "，"
            elif month_zhi in relations.get("", ()):
                compatibility_score += 15
                return "，e"
            elif month_zhi == relations.get("", ""):
                compatibility_score -= 30
                return "，"

        if compatibility_score >= 85:
            return ""
        elif compatibility_score >= 70:
            return ""
        elif compatibility_score >= 50:
            return ""
        else:
            return ""

    def _generate_spouse_improvement_suggestions(
        self,
        day_zhi: str,
        wuxing_influence: Dict[str, str],
        star_influence: Dict[str, str],
    ) -> List[str]:
        """
        .
        """
        suggestions = []

        # para
        zhi_suggestions = {
            "": ["，", "parade"],
            "": ["Aguardando，Não", "parae"],
            "": ["，", "parade"],
            "": ["，", "dee"],
            "": ["，", "parae"],
            "": ["，Não", ""],
            "": ["，", "paradee"],
            "Não": ["，", "de"],
            "": ["，", "paraConversãoe"],
            "": ["，", "e"],
            "": ["，", "parae"],
            "": ["para，", "e"],
        }

        if day_zhi in zhi_suggestions:
            suggestions.extend(zhi_suggestions[day_zhi])

        # para
        if "" in wuxing_influence.get("personality", ""):
            suggestions.append("，de")

        # para
        if "" in star_influence.get("relationship_mode", ""):
            suggestions.append("，")

        return suggestions[:4]  # Retorno4

    def _get_spouse_appearance(self, day_zhi: str) -> str:
        """
        .
        """
        appearance_map = {
            "": "EmAguardar，",
            "": "，",
            "": "，",
            "": "，",
            "": "EmAguardar，",
            "": "Em，",
            "": "，",
            "Não": "EmAguardar，e",
            "": "，",
            "": "，",
            "": "，",
            "": "，e",
        }
        return appearance_map.get(day_zhi, "")

    def _get_spouse_career(self, day_zhi: str) -> str:
        """
        .
        """
        career_map = {
            "": "、、",
            "": "、、",
            "": "、、",
            "": "、、",
            "": "、、",
            "": "Conversão、、",
            "": "Fonte、、",
            "Não": "、、",
            "": "、、",
            "": "、、",
            "": "、、",
            "": "、、",
        }
        return career_map.get(day_zhi, "")

    def _evaluate_marriage_quality(
        self, eight_char_data: Dict[str, Any], gender: int
    ) -> Dict[str, Any]:
        """
        .
        """
        day_gan = eight_char_data.get("day", {}).get("heaven_stem", {}).get("name", "")
        day_zhi = eight_char_data.get("day", {}).get("earth_branch", {}).get("name", "")

        # 
        good_combinations = [
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "Não",
            "",
            "",
        ]

        day_pillar = day_gan + day_zhi
        quality_score = 75  # Pontuação

        if day_pillar in good_combinations:
            quality_score += 10

        return {
            "score": quality_score,
            "level": (
                ""
                if quality_score >= 85
                else "" if quality_score >= 75 else ""
            ),
            "advice": self._get_marriage_advice(quality_score),
        }

    def _get_marriage_advice(self, score: int) -> str:
        """
        .
        """
        if score >= 85:
            return "，，"
        elif score >= 75:
            return "，"
        else:
            return "e，Conversão"

    def _evaluate_star_strength(self, position: str) -> str:
        """
        .
        """
        strength_map = {
            "": "",
            "": "",
            "": "Em",
            "": "Em",
            "": "",
            "": "Em",
        }
        return strength_map.get(position, "")

    def _extract_gan_from_pillar(self, pillar: Dict[str, Any]) -> str:
        """
        de  Em.
        """
        if "" in pillar:
            return pillar[""].get("", "")
        elif "heaven_stem" in pillar:
            return pillar["heaven_stem"].get("name", "")
        return ""

    def _extract_zhi_from_pillar(self, pillar: Dict[str, Any]) -> str:
        """
        de  Em.
        """
        if "" in pillar:
            return pillar[""].get("", "")
        elif "earth_branch" in pillar:
            return pillar["earth_branch"].get("name", "")
        return ""

    def _get_gan_element(self, gan: str) -> str:
        """
        .
        """
        from .professional_data import GAN_WUXING

        return GAN_WUXING.get(gan, "")

    def _analyze_hidden_marriage_stars(
        self, pillar: Dict[str, Any], day_gan: str, target_gods: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Emde.
        """
        hidden_stars = []

        if "" in pillar and "" in pillar[""]:
            canggan = pillar[""][""]
            for gan_type, gan_info in canggan.items():
                if gan_info and "" in gan_info:
                    hidden_gan = gan_info[""]
                    ten_god = get_ten_gods_relation(day_gan, hidden_gan)
                    if ten_god in target_gods:
                        hidden_stars.append(
                            {
                                "star": ten_god,
                                "strength": self._get_hidden_strength(gan_type),
                                "element": self._get_gan_element(hidden_gan),
                                "type": f"{gan_type}",
                            }
                        )

        return hidden_stars

    def _get_hidden_strength(self, gan_type: str) -> str:
        """
        .
        """
        strength_map = {"": "", "Em": "Em", "": ""}
        return strength_map.get(gan_type, "")

    def _evaluate_marriage_star_quality(
        self, marriage_stars: List[Dict[str, Any]]
    ) -> str:
        """
        .
        """
        if not marriage_stars:
            return ""

        strong_stars = sum(
            1 for star in marriage_stars if star["strength"] in ["", ""]
        )
        total_stars = len(marriage_stars)

        if strong_stars >= 2:
            return ""
        elif strong_stars == 1 and total_stars >= 2:
            return ""
        elif total_stars >= 1:
            return ""
        else:
            return ""

    def _evaluate_star_quality(self, position: str, ten_god: str) -> str:
        """
        .
        """
        # PosiçãoeTipo
        if position == "":
            return ""  # 
        elif position == "":
            return ""  # Vezes
        elif position == "":
            return ""  # 
        else:
            return ""

    def _get_seasonal_strength(self, gan: str, month_gan: str) -> str:
        """
        .
        """
        from .professional_data import GAN_WUXING, WUXING_RELATIONS

        gan_element = GAN_WUXING.get(gan, "")
        month_element = GAN_WUXING.get(month_gan, "")

        if not gan_element or not month_element:
            return "EmAguardar"

        # Pesquisar
        relation = WUXING_RELATIONS.get((month_element, gan_element), "")
        if relation == "↓":  # 
            return ""
        elif relation == "=":  # 
            return ""
        elif relation == "←":  # 
            return ""
        elif relation == "→":  # 
            return ""
        else:
            return "EmAguardar"

    def _determine_canggan_type(self, strength: int) -> str:
        """
        Tipo.
        """
        if strength >= 5:
            return ""
        elif strength >= 2:
            return "Em"
        else:
            return ""

    def _evaluate_hidden_star_quality(
        self, zhi_name: str, hidden_gan: str, strength: int
    ) -> str:
        """
        .
        """
        if strength >= 5:
            return ""
        elif strength >= 3:
            return ""
        elif strength >= 1:
            return ""
        else:
            return ""

    def _comprehensive_star_analysis(
        self, marriage_stars: List[Dict[str, Any]], day_gan: str, gender: int
    ) -> Dict[str, Any]:
        """
        .
        """
        if not marriage_stars:
            return {
                "strength": "",
                "quality": "",
                "distribution": "",
                "potential": "",
                "suggestions": ["Através de", "de"],
            }

        # de
        positions = [star["position"] for star in marriage_stars]
        star_types = [star["star"] for star in marriage_stars]

        # 
        strength_score = 0
        for star in marriage_stars:
            if star["strength"] == "":
                strength_score += 5
            elif star["strength"] == "":
                strength_score += 3
            elif star["strength"] == "Em":
                strength_score += 2
            else:
                strength_score += 1

        # Aguardar
        if strength_score >= 8:
            strength_level = ""
        elif strength_score >= 5:
            strength_level = ""
        elif strength_score >= 3:
            strength_level = "Em"
        else:
            strength_level = ""

        # 
        quality_scores = []
        for star in marriage_stars:
            quality = star.get("quality", "")
            if quality == "":
                quality_scores.append(4)
            elif quality == "":
                quality_scores.append(3)
            elif quality == "":
                quality_scores.append(2)
            else:
                quality_scores.append(1)

        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 1
        if avg_quality >= 3.5:
            quality_level = ""
        elif avg_quality >= 2.5:
            quality_level = ""
        elif avg_quality >= 1.5:
            quality_level = ""
        else:
            quality_level = ""

        # 
        distribution_desc = (
            f"{len(marriage_stars)}，Em{len(set(positions))}Posição"
        )

        # 
        if strength_score >= 6 and avg_quality >= 3:
            potential = ""
        elif strength_score >= 4 and avg_quality >= 2:
            potential = ""
        elif strength_score >= 2:
            potential = ""
        else:
            potential = ""

        # 
        suggestions = []
        if strength_score < 3:
            suggestions.append("，Através de")
        if avg_quality < 2:
            suggestions.append("Não，Aguardando")
        if "" not in positions and "" not in positions:
            suggestions.append("，")
        if len(set(star_types)) == 1:
            suggestions.append("Tipo，Modo")

        return {
            "strength": strength_level,
            "quality": quality_level,
            "distribution": distribution_desc,
            "potential": potential,
            "suggestions": (
                suggestions if suggestions else ["，"]
            ),
        }


# Dispositivo
_marriage_analyzer = None


def get_marriage_analyzer():
    """
    Dispositivo.
    """
    global _marriage_analyzer
    if _marriage_analyzer is None:
        _marriage_analyzer = MarriageAnalyzer()
    return _marriage_analyzer
