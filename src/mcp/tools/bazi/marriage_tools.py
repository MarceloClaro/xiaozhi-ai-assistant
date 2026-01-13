"""
.
"""

import json
from typing import Any, Dict, List

from src.utils.logging_config import get_logger

from .bazi_calculator import get_bazi_calculator
from .marriage_analyzer import get_marriage_analyzer

logger = get_logger(__name__)


async def analyze_marriage_timing(args: Dict[str, Any]) -> str:
    """
    eInformação.
    """
    try:
        solar_datetime = args.get("solar_datetime")
        lunar_datetime = args.get("lunar_datetime")
        gender = args.get("gender", 1)
        eight_char_provider_sect = args.get("eight_char_provider_sect", 2)

        if not solar_datetime and not lunar_datetime:
            return json.dumps(
                {
                    "success": False,
                    "message": "solar_datetimeelunar_datetimeEm",
                },
                ensure_ascii=False,
            )

        # Informação
        calculator = get_bazi_calculator()
        bazi_result = calculator.build_bazi(
            solar_datetime=solar_datetime,
            lunar_datetime=lunar_datetime,
            gender=gender,
            eight_char_provider_sect=eight_char_provider_sect,
        )

        # 
        marriage_analyzer = get_marriage_analyzer()

        # deDadosFormato
        eight_char_dict = {
            "year": bazi_result.year_pillar,
            "month": bazi_result.month_pillar,
            "day": bazi_result.day_pillar,
            "hour": bazi_result.hour_pillar,
        }

        marriage_analysis = marriage_analyzer.analyze_marriage_timing(
            eight_char_dict, gender
        )

        # 
        result = {
            "basic_info": {
                "": bazi_result.bazi,
                "": "" if gender == 1 else "",
                "": bazi_result.day_master,
                "": bazi_result.zodiac,
            },
            "marriage_analysis": marriage_analysis,
        }

        return json.dumps(
            {"success": True, "data": result}, ensure_ascii=False, indent=2
        )

    except Exception as e:
        logger.error(f"Falha: {e}")
        return json.dumps(
            {"success": False, "message": f"Falha: {str(e)}"},
            ensure_ascii=False,
        )


async def analyze_marriage_compatibility(args: Dict[str, Any]) -> str:
    """
    .
    """
    try:
        # Informação
        male_solar = args.get("male_solar_datetime")
        male_lunar = args.get("male_lunar_datetime")

        # Informação
        female_solar = args.get("female_solar_datetime")
        female_lunar = args.get("female_lunar_datetime")

        if not (male_solar or male_lunar) or not (female_solar or female_lunar):
            return json.dumps(
                {
                    "success": False,
                    "message": "deTempoInformação",
                },
                ensure_ascii=False,
            )

        calculator = get_bazi_calculator()

        # 
        male_bazi = calculator.build_bazi(
            solar_datetime=male_solar, lunar_datetime=male_lunar, gender=1
        )

        # 
        female_bazi = calculator.build_bazi(
            solar_datetime=female_solar, lunar_datetime=female_lunar, gender=0
        )

        # 
        compatibility_result = _analyze_compatibility(male_bazi, female_bazi)

        result = {
            "male_info": {
                "": male_bazi.bazi,
                "": male_bazi.day_master,
                "": male_bazi.zodiac,
            },
            "female_info": {
                "": female_bazi.bazi,
                "": female_bazi.day_master,
                "": female_bazi.zodiac,
            },
            "compatibility": compatibility_result,
        }

        return json.dumps(
            {"success": True, "data": result}, ensure_ascii=False, indent=2
        )

    except Exception as e:
        logger.error(f"Falha: {e}")
        return json.dumps(
            {"success": False, "message": f"Falha: {str(e)}"},
            ensure_ascii=False,
        )


def _analyze_compatibility(male_bazi, female_bazi) -> Dict[str, Any]:
    """ - Usando"""
    # 
    male_day_gan = male_bazi.day_master
    female_day_gan = female_bazi.day_pillar[""][""]

    male_day_zhi = male_bazi.day_pillar[""][""]
    female_day_zhi = female_bazi.day_pillar[""][""]

    # 
    element_analysis = _analyze_element_compatibility(male_day_gan, female_day_gan)

    # 
    zodiac_analysis = _analyze_zodiac_compatibility(
        male_bazi.zodiac, female_bazi.zodiac
    )

    # 
    pillar_analysis = _analyze_pillar_compatibility(
        male_day_gan + male_day_zhi, female_day_gan + female_day_zhi
    )

    # 
    branch_analysis = _analyze_branch_relationships(male_bazi, female_bazi)

    # 
    complement_analysis = _analyze_complement(male_bazi, female_bazi)

    # 
    total_score = (
        element_analysis["score"] * 0.3
        + zodiac_analysis["score"] * 0.2
        + pillar_analysis["score"] * 0.2
        + branch_analysis["score"] * 0.15
        + complement_analysis["score"] * 0.15
    )

    return {
        "overall_score": round(total_score, 1),
        "overall_level": _get_compatibility_level(total_score),
        "element_analysis": element_analysis,
        "zodiac_analysis": zodiac_analysis,
        "pillar_analysis": pillar_analysis,
        "branch_analysis": branch_analysis,
        "complement_analysis": complement_analysis,
        "suggestions": _get_professional_suggestions(
            total_score, element_analysis, zodiac_analysis
        ),
    }


def _analyze_element_compatibility(male_gan: str, female_gan: str) -> Dict[str, Any]:
    """
    .
    """
    from .professional_data import GAN_WUXING, WUXING_RELATIONS

    male_element = GAN_WUXING.get(male_gan, "")
    female_element = GAN_WUXING.get(female_gan, "")

    element_relation = WUXING_RELATIONS.get((male_element, female_element), "")

    # NãoBits
    score_map = {
        "↓": 90,  # ，
        "=": 80,  # ，
        "←": 50,  # ，
        "→": 55,  # ，
        "↑": 85,  # ，
    }

    desc_map = {
        "↓": "，，e",
        "=": "，，",
        "←": "，，",
        "→": "，，",
        "↑": "，，",
    }

    return {
        "male_element": male_element,
        "female_element": female_element,
        "relation": element_relation,
        "score": score_map.get(element_relation, 70),
        "description": desc_map.get(element_relation, "e"),
    }


def _analyze_zodiac_compatibility(
    male_zodiac: str, female_zodiac: str
) -> Dict[str, Any]:
    """
    .
    """
    from .professional_data import ZHI_CHONG, ZHI_HAI, ZHI_LIUHE, ZHI_SANHE, ZHI_XING

    # 
    zodiac_to_zhi = {
        "": "",
        "": "",
        "": "",
        "": "",
        "": "",
        "": "",
        "": "",
        "": "Não",
        "": "",
        "": "",
        "": "",
        "": "",
    }

    male_zhi = zodiac_to_zhi.get(male_zodiac, "")
    female_zhi = zodiac_to_zhi.get(female_zodiac, "")

    # Pesquisar
    if (male_zhi, female_zhi) in ZHI_LIUHE or (female_zhi, male_zhi) in ZHI_LIUHE:
        return {
            "score": 90,
            "level": "",
            "description": "，",
            "relation": "",
        }

    # Pesquisar
    for sanhe_group in ZHI_SANHE:
        if male_zhi in sanhe_group and female_zhi in sanhe_group:
            return {
                "score": 85,
                "level": "",
                "description": "，",
                "relation": "",
            }

    # Pesquisar
    if (male_zhi, female_zhi) in ZHI_CHONG or (female_zhi, male_zhi) in ZHI_CHONG:
        return {
            "score": 30,
            "level": "Não",
            "description": "，",
            "relation": "",
        }

    # Pesquisar
    for xing_group in ZHI_XING:
        if male_zhi in xing_group and female_zhi in xing_group:
            return {
                "score": 40,
                "level": "Não",
                "description": "，Conversão",
                "relation": "",
            }

    # Pesquisar
    if (male_zhi, female_zhi) in ZHI_HAI or (female_zhi, male_zhi) in ZHI_HAI:
        return {
            "score": 45,
            "level": "Não",
            "description": "，Não",
            "relation": "",
        }

    # 
    return {
        "score": 70,
        "level": "",
        "description": "e，",
        "relation": "e",
    }


def _analyze_pillar_compatibility(
    male_pillar: str, female_pillar: str
) -> Dict[str, Any]:
    """
    .
    """
    if male_pillar == female_pillar:
        return {"score": 55, "description": "，Conversão"}

    # 
    male_gan, male_zhi = male_pillar[0], male_pillar[1]
    female_gan, female_zhi = female_pillar[0], female_pillar[1]

    score = 70  # Pontuação

    # 
    from .professional_data import get_ten_gods_relation

    gan_relation = get_ten_gods_relation(male_gan, female_gan)
    if gan_relation in ["", "", "", ""]:
        score += 10

    # 
    from .professional_data import ZHI_CHONG, ZHI_LIUHE

    if (male_zhi, female_zhi) in ZHI_LIUHE or (female_zhi, male_zhi) in ZHI_LIUHE:
        score += 15
    elif (male_zhi, female_zhi) in ZHI_CHONG or (female_zhi, male_zhi) in ZHI_CHONG:
        score -= 20

    return {
        "score": min(95, max(30, score)),
        "description": f"：{gan_relation}",
    }


def _analyze_branch_relationships(male_bazi, female_bazi) -> Dict[str, Any]:
    """
    .
    """
    # 
    male_branches = [
        male_bazi.year_pillar[""][""],
        male_bazi.month_pillar[""][""],
        male_bazi.day_pillar[""][""],
        male_bazi.hour_pillar[""][""],
    ]

    female_branches = [
        female_bazi.year_pillar[""][""],
        female_bazi.month_pillar[""][""],
        female_bazi.day_pillar[""][""],
        female_bazi.hour_pillar[""][""],
    ]

    # 
    from .professional_data import analyze_zhi_combinations

    combined_branches = male_branches + female_branches
    relationships = analyze_zhi_combinations(combined_branches)

    score = 70
    if relationships.get("liuhe", []):
        score += 10
    if relationships.get("sanhe", []):
        score += 8
    if relationships.get("chong", []):
        score -= 15
    if relationships.get("xing", []):
        score -= 10

    return {
        "score": min(95, max(30, score)),
        "relationships": relationships,
        "description": f"：{len(relationships.get('liuhe', []))}、{len(relationships.get('chong', []))}",
    }


def _analyze_complement(male_bazi, female_bazi) -> Dict[str, Any]:
    """
    .
    """
    # 
    from .professional_data import GAN_WUXING, WUXING, ZHI_WUXING

    male_elements = []
    female_elements = []

    # 
    for pillar in [
        male_bazi.year_pillar,
        male_bazi.month_pillar,
        male_bazi.day_pillar,
        male_bazi.hour_pillar,
    ]:
        gan = pillar[""][""]
        zhi = pillar[""][""]
        male_elements.extend([GAN_WUXING.get(gan, ""), ZHI_WUXING.get(zhi, "")])

    # 
    for pillar in [
        female_bazi.year_pillar,
        female_bazi.month_pillar,
        female_bazi.day_pillar,
        female_bazi.hour_pillar,
    ]:
        gan = pillar[""][""]
        zhi = pillar[""][""]
        female_elements.extend([GAN_WUXING.get(gan, ""), ZHI_WUXING.get(zhi, "")])

    # 
    from collections import Counter

    male_counter = Counter(male_elements)
    female_counter = Counter(female_elements)

    # 
    complement_score = 0
    for element in WUXING:
        male_count = male_counter.get(element, 0)
        female_count = female_counter.get(element, 0)

        # 
        if male_count > 0 and female_count == 0:
            complement_score += 5
        elif male_count == 0 and female_count > 0:
            complement_score += 5
        elif abs(male_count - female_count) <= 1:
            complement_score += 2

    return {
        "score": min(90, 50 + complement_score),
        "male_elements": dict(male_counter),
        "female_elements": dict(female_counter),
        "description": f"，{complement_score}",
    }


def _get_professional_suggestions(
    total_score: float,
    element_analysis: Dict[str, Any],
    zodiac_analysis: Dict[str, Any],
) -> List[str]:
    """
    .
    """
    suggestions = []

    if total_score >= 80:
        suggestions.extend(["，", "，"])
    elif total_score >= 70:
        suggestions.extend(["，", "，"])
    elif total_score >= 60:
        suggestions.extend(["", "，Conversão"])
    else:
        suggestions.extend(["", "Conversão"])

    # 
    if element_analysis["relation"] == "←":
        suggestions.append("，")
    elif element_analysis["relation"] == "→":
        suggestions.append("，")

    # 
    if zodiac_analysis["relation"] == "":
        suggestions.append("，Conversãoou")

    return suggestions


def _get_compatibility_level(score: float) -> str:
    """
    Aguardar.
    """
    if score >= 80:
        return "Aguardar"
    elif score >= 70:
        return "Em"
    elif score >= 60:
        return "EmAguardar"
    else:
        return "Aguardar"


def _get_compatibility_suggestions(score: float) -> List[str]:
    """
    .
    """
    if score >= 80:
        return ["，", "，", "Continuar"]
    elif score >= 70:
        return ["，", "，", ""]
    elif score >= 60:
        return [
            "",
            "，Conversão",
            "",
            "então",
        ]
    else:
        return [
            "",
            "Conversão",
            "",
            "",
        ]
