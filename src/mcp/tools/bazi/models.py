"""
dadosModelo。
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class HeavenStem:
    """"""

    name: str
    element: str  # 
    yin_yang: int  # ，1=，-1=

    def __str__(self):
        return self.name

    def get_element(self):
        return self.element

    def get_yin_yang(self):
        return self.yin_yang

    def get_ten_star(self, other_stem: "HeavenStem") -> str:
        """
        .
        """
        # 
        return self._calculate_ten_star(other_stem)

    def _calculate_ten_star(self, other: "HeavenStem") -> str:
        """ - Usandodados"""
        from .professional_data import get_ten_gods_relation

        return get_ten_gods_relation(self.name, other.name)


@dataclass
class EarthBranch:
    """"""

    name: str
    element: str  # 
    yin_yang: int  # 
    zodiac: str  # 
    hide_heaven_main: Optional[str] = None  # 
    hide_heaven_middle: Optional[str] = None  # Em
    hide_heaven_residual: Optional[str] = None  # 

    def __str__(self):
        return self.name

    def get_element(self):
        return self.element

    def get_yin_yang(self):
        return self.yin_yang

    def get_zodiac(self):
        return self.zodiac

    def get_hide_heaven_stem_main(self):
        return self.hide_heaven_main

    def get_hide_heaven_stem_middle(self):
        return self.hide_heaven_middle

    def get_hide_heaven_stem_residual(self):
        return self.hide_heaven_residual


@dataclass
class SixtyCycle:
    """
    .
    """

    heaven_stem: HeavenStem
    earth_branch: EarthBranch
    sound: str  # 
    ten: str  # 
    extra_earth_branches: List[str]  # 

    def __str__(self):
        return f"{self.heaven_stem.name}{self.earth_branch.name}"

    def get_heaven_stem(self):
        return self.heaven_stem

    def get_earth_branch(self):
        return self.earth_branch

    def get_sound(self):
        return self.sound

    def get_ten(self):
        return self.ten

    def get_extra_earth_branches(self):
        return self.extra_earth_branches


@dataclass
class EightChar:
    """"""

    year: SixtyCycle
    month: SixtyCycle
    day: SixtyCycle
    hour: SixtyCycle

    def __str__(self):
        return f"{self.year} {self.month} {self.day} {self.hour}"

    def get_year(self):
        return self.year

    def get_month(self):
        return self.month

    def get_day(self):
        return self.day

    def get_hour(self):
        return self.hour

    def to_dict(self) -> Dict[str, Any]:
        """
        paraFormato，Usando.
        """
        return {
            "year": {
                "heaven_stem": {"name": self.year.heaven_stem.name},
                "earth_branch": {"name": self.year.earth_branch.name},
            },
            "month": {
                "heaven_stem": {"name": self.month.heaven_stem.name},
                "earth_branch": {"name": self.month.earth_branch.name},
            },
            "day": {
                "heaven_stem": {"name": self.day.heaven_stem.name},
                "earth_branch": {"name": self.day.earth_branch.name},
            },
            "hour": {
                "heaven_stem": {"name": self.hour.heaven_stem.name},
                "earth_branch": {"name": self.hour.earth_branch.name},
            },
        }


@dataclass
class LunarTime:
    """
    Tempo.
    """

    year: int
    month: int
    day: int
    hour: int
    minute: int
    second: int
    is_leap: bool = False  # 

    def __str__(self):
        leap_text = "" if self.is_leap else ""
        return f"{self.year}{leap_text}{self.month}{self.day}{self.hour}{self.minute}{self.second}Segundos"


@dataclass
class SolarTime:
    """
    Tempo.
    """

    year: int
    month: int
    day: int
    hour: int
    minute: int
    second: int

    def __str__(self):
        return f"{self.year}{self.month}{self.day}{self.hour}{self.minute}{self.second}Segundos"

    def get_year(self):
        return self.year

    def get_month(self):
        return self.month

    def get_day(self):
        return self.day

    def get_hour(self):
        return self.hour

    def get_minute(self):
        return self.minute

    def get_second(self):
        return self.second


@dataclass
class BaziAnalysis:
    """
    .
    """

    gender: str  # 
    solar_time: str  # 
    lunar_time: str  # 
    bazi: str  # 
    zodiac: str  # 
    day_master: str  # 
    year_pillar: Dict[str, Any]  # 
    month_pillar: Dict[str, Any]  # 
    day_pillar: Dict[str, Any]  # 
    hour_pillar: Dict[str, Any]  # 
    fetal_origin: str  # 
    fetal_breath: str  # 
    own_sign: str  # 
    body_sign: str  # 
    gods: Dict[str, List[str]]  # 
    fortune: Dict[str, Any]  # 
    relations: Dict[str, Any]  # 

    def to_dict(self) -> Dict[str, Any]:
        """
        para.
        """
        result = {
            "": self.gender,
            "": self.solar_time,
            "": self.lunar_time,
            "": self.bazi,
            "": self.zodiac,
            "": self.day_master,
            "": self.year_pillar,
            "": self.month_pillar,
            "": self.day_pillar,
            "": self.hour_pillar,
            "": self.fetal_origin,
            "": self.fetal_breath,
            "": self.own_sign,
            "": self.body_sign,
            "": self.gods,
            "": self.fortune,
            "": self.relations,
        }

        # （SeExiste）
        if hasattr(self, "_professional_analysis"):
            result[""] = self._professional_analysis
        if hasattr(self, "_detailed_fortune_text"):
            result[""] = self._detailed_fortune_text

        return result


@dataclass
class ChineseCalendar:
    """
    Informação.
    """

    solar_date: str  # 
    lunar_date: str  # 
    gan_zhi: str  # 
    zodiac: str  # 
    na_yin: str  # 
    lunar_festival: Optional[str]  # 
    solar_festival: Optional[str]  # 
    solar_term: str  # 
    twenty_eight_star: str  # 
    pengzu_taboo: str  # 
    joy_direction: str  # Bits
    yang_direction: str  # Bits
    yin_direction: str  # Bits
    mascot_direction: str  # Bits
    wealth_direction: str  # Bits
    clash: str  # 
    suitable: str  # 
    avoid: str  # 

    def to_dict(self) -> Dict[str, Any]:
        """
        para.
        """
        return {
            "": self.solar_date,
            "": self.lunar_date,
            "": self.gan_zhi,
            "": self.zodiac,
            "": self.na_yin,
            "": self.lunar_festival,
            "": self.solar_festival,
            "": self.solar_term,
            "": self.twenty_eight_star,
            "": self.pengzu_taboo,
            "Bits": self.joy_direction,
            "Bits": self.yang_direction,
            "Bits": self.yin_direction,
            "Bits": self.mascot_direction,
            "Bits": self.wealth_direction,
            "": self.clash,
            "": self.suitable,
            "": self.avoid,
        }
