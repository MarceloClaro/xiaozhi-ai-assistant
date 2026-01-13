"""
MCP paraMCPservidorde。
"""

import json
from typing import Any, Dict

from src.utils.logging_config import get_logger

from .bazi_calculator import get_bazi_calculator
from .engine import get_bazi_engine

logger = get_logger(__name__)


async def get_bazi_detail(args: Dict[str, Any]) -> str:
    """
    Tempo（ou）、Informação。
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

        calculator = get_bazi_calculator()
        result = calculator.build_bazi(
            solar_datetime=solar_datetime,
            lunar_datetime=lunar_datetime,
            gender=gender,
            eight_char_provider_sect=eight_char_provider_sect,
        )

        return json.dumps(
            {"success": True, "data": result.to_dict()}, ensure_ascii=False, indent=2
        )

    except Exception as e:
        logger.error(f"Falha: {e}")
        return json.dumps(
            {"success": False, "message": f"Falha: {str(e)}"},
            ensure_ascii=False,
        )


async def get_solar_times(args: Dict[str, Any]) -> str:
    """
    Tempo。
    """
    try:
        bazi = args.get("bazi")
        if not bazi:
            return json.dumps(
                {"success": False, "message": "ParâmetroNão  para"}, ensure_ascii=False
            )

        calculator = get_bazi_calculator()
        result = calculator.get_solar_times(bazi)

        return json.dumps(
            {"success": True, "data": {"Tempo": result, "": len(result)}},
            ensure_ascii=False,
            indent=2,
        )

    except Exception as e:
        logger.error(f"TempoFalha: {e}")
        return json.dumps(
            {"success": False, "message": f"TempoFalha: {str(e)}"},
            ensure_ascii=False,
        )


async def get_chinese_calendar(args: Dict[str, Any]) -> str:
    """
    Tempo（）deInformação。
    """
    try:
        solar_datetime = args.get("solar_datetime")

        engine = get_bazi_engine()

        # SeTempo，Analisando；entãoUsandoTempo
        if solar_datetime:
            solar_time = engine.parse_solar_time(solar_datetime)
            result = engine.get_chinese_calendar(solar_time)
        else:
            result = engine.get_chinese_calendar()  # UsandoTempo

        return json.dumps(
            {"success": True, "data": result.to_dict()}, ensure_ascii=False, indent=2
        )

    except Exception as e:
        logger.error(f"InformaçãoFalha: {e}")
        return json.dumps(
            {"success": False, "message": f"InformaçãoFalha: {str(e)}"},
            ensure_ascii=False,
        )


async def build_bazi_from_lunar_datetime(args: Dict[str, Any]) -> str:
    """
    Tempo、Informação（Já，Usandoget_bazi_detail）。
    """
    try:
        lunar_datetime = args.get("lunar_datetime")
        gender = args.get("gender", 1)
        eight_char_provider_sect = args.get("eight_char_provider_sect", 2)

        if not lunar_datetime:
            return json.dumps(
                {"success": False, "message": "lunar_datetimeParâmetroNão  para"},
                ensure_ascii=False,
            )

        calculator = get_bazi_calculator()
        result = calculator.build_bazi(
            lunar_datetime=lunar_datetime,
            gender=gender,
            eight_char_provider_sect=eight_char_provider_sect,
        )

        return json.dumps(
            {
                "success": True,
                "message": "Já，Usandoget_bazi_detail",
                "data": result.to_dict(),
            },
            ensure_ascii=False,
            indent=2,
        )

    except Exception as e:
        logger.error(f"TempoFalha: {e}")
        return json.dumps(
            {"success": False, "message": f"TempoFalha: {str(e)}"},
            ensure_ascii=False,
        )


async def build_bazi_from_solar_datetime(args: Dict[str, Any]) -> str:
    """
    Tempo、Informação（Já，Usandoget_bazi_detail）。
    """
    try:
        solar_datetime = args.get("solar_datetime")
        gender = args.get("gender", 1)
        eight_char_provider_sect = args.get("eight_char_provider_sect", 2)

        if not solar_datetime:
            return json.dumps(
                {"success": False, "message": "solar_datetimeParâmetroNão  para"},
                ensure_ascii=False,
            )

        calculator = get_bazi_calculator()
        result = calculator.build_bazi(
            solar_datetime=solar_datetime,
            gender=gender,
            eight_char_provider_sect=eight_char_provider_sect,
        )

        return json.dumps(
            {
                "success": True,
                "message": "Já，Usandoget_bazi_detail",
                "data": result.to_dict(),
            },
            ensure_ascii=False,
            indent=2,
        )

    except Exception as e:
        logger.error(f"TempoFalha: {e}")
        return json.dumps(
            {"success": False, "message": f"TempoFalha: {str(e)}"},
            ensure_ascii=False,
        )
