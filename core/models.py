from dataclasses import dataclass, field
from typing import Optional, Union, List, Dict, Any

Lang = Dict[str, str]
Floors = Union[int, List[int], List[List[int]]]  # 50 | [11,20] | [[1,10], 20, [71,100]]

@dataclass
class Skill:
    name: Union[str, Lang] = field(default_factory=dict)
    desc: Union[str, Lang] = field(default_factory=dict)
    area_img: Optional[str] = None

@dataclass
class Aggro:
    sight: bool = False
    sound: bool = False
    distance_enabled: bool = False
    distance_range: Optional[int] = None

@dataclass
class Monster:
    name: Union[str, Lang] = field(default_factory=dict)
    img: Optional[str] = None
    floors: Optional[Floors] = None
    stun: bool = False
    warning: int = 0
    aggro: Aggro = field(default_factory=Aggro)
    roaming: bool = False
    skills: List[Skill] = field(default_factory=list)
    skills_Amount: Optional[int] = None
    boss: bool = False
    boss_img: Optional[str] = None

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "Monster":
        ag = d.get("aggro", {})
        aggro = Aggro(
            sight=bool(ag.get("sight", False)),
            sound=bool(ag.get("sound", False)),
            distance_enabled=bool(ag.get("distance", {}).get("enabled", False)),
            distance_range=ag.get("distance", {}).get("range"),
        )
        skills = [Skill(**s) for s in d.get("skills", []) if isinstance(s, dict)]
        return Monster(
            name=d.get("name", {}),
            img=d.get("img"),
            floors=d.get("floors"),
            stun=bool(d.get("stun", False)),
            warning=int(d.get("warning", 0)),
            aggro=aggro,
            roaming=bool(d.get("roaming", False)),
            skills=skills,
            skills_Amount=d.get("skills_Amount"),
            boss=bool(d.get("boss", False)),
            boss_img=d.get("boss_img"),
        )
