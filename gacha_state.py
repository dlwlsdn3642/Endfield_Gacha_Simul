from dataclasses import dataclass, field
from collections import Counter as CounterCls
from typing import Counter as TCounter


@dataclass  # 다음 가챠로 이월되지 않음.
class GachaState:
    char_runs: int = 0  # 캐릭터 가챠 횟수
    weapon_runs: int = 0  # 무기 가챠 횟수(10개 단위)

    weapon_pity: int = 0  # 무기 스택(4)
    limited_weapon_pity: int = 0  # 무기 한정 스택(8)
    limited_char_pity: int = 0  # 캐릭터 한정 스택(120)

    got_limited_char: bool = False  # 한정 캐릭터 보유 여부
    got_limited_weapon: bool = False  # 한정 무기 보유 여부
    pulls_until_first_obtain: int | None = None  # 명함까지 가챠 수

    # 값 오류 검증
    def __post_init__(self):
        # 스택 오류
        if not (0 <= self.limited_weapon_pity < 8):
            raise ValueError(
                f"limited_weapon_pity out of range: {self.limited_weapon_pity}"
            )
        if not (0 <= self.weapon_pity < 4):
            raise ValueError(f"weapon_pity out of range: {self.weapon_pity}")
        if not (0 <= self.limited_char_pity < 120):
            raise ValueError(
                f"limited_char_pity out of range: {self.limited_char_pity}"
            )


@dataclass  # 다음 가챠로 이월됨.
class PlayerState:
    total_char_runs: int = 0  # 캐릭터 가챠 횟수
    total_weapon_runs: int = 0  # 무기 가챠 횟수(10개 단위)

    # 가챠에서 얻은 것의 희귀도 카운터(4, 5, 6 단위)
    obtained_chars_rarity: TCounter[int] = field(
        default_factory=CounterCls
    )  # 뽑은 캐릭터의 희귀도 개수
    obtained_weapon_rarity: TCounter[int] = field(
        default_factory=CounterCls
    )  # 뽑은 무기의 희귀도 개수

    # 스택 카운터
    six_pity: int = 0  # 6성 스택(80)
    five_pity: int = 0  # 5성 스택(10)

    weapon_gacha_resource: int = 0  # 무기 가챠 재화

    # 값 오류 검증
    def __post_init__(self):
        # 스택 오류
        if not (0 <= self.six_pity < 80):
            raise ValueError(f"six_pity out of range: {self.six_pity}")
        if not (0 <= self.five_pity < 10):
            raise ValueError(f"five_pity out of range: {self.five_pity}")


class GachaSession:
    pass
    # player = PlayerState
