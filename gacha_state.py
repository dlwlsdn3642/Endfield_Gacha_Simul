from dataclasses import dataclass, field
from collections import Counter as CounterCls
from typing import Counter as TCounter
import random


@dataclass  # 다음 가챠로 이월되지 않음.
class GachaState:
    weapon_pity: int = 0  # 무기 스택(4)
    limited_weapon_pity: int = 0  # 무기 한정 스택(8)
    limited_char_pity: int = 0  # 캐릭터 한정 스택(120)

    got_limited_char: bool = False  # 한정 캐릭터 보유 여부
    got_limited_weapon: bool = False  # 한정 무기 보유 여부

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
    total_weapon_runs: int = 0  # 무기 가챠 횟수

    # 가챠에서 얻은 것의 희귀도 카운터(4, 5, 6 단위, 한정은 7)
    # 뽑은 캐릭터의 희귀도 개수
    obtained_chars_rarity: TCounter[int] = field(default_factory=CounterCls)
    # 뽑은 무기의 희귀도 개수
    obtained_weapon_rarity: TCounter[int] = field(default_factory=CounterCls)

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
    def __init__(self):
        self.player = PlayerState()

    def get_banner(self) -> GachaState:
        return GachaState()

    def get_limited_char(self, banner: GachaState):
        while not banner.got_limited_char:
            self.try_banner_gacha(banner)

    def get_limited_weapon(self, banner: GachaState):
        while not banner.got_limited_weapon:
            while self.player.weapon_gacha_resource < 1980:
                self.try_banner_gacha(banner)
            self.try_weapon_gacha(banner)

    def get_PlayerState(self) -> PlayerState:
        return self.player

    def try_banner_gacha(self, banner: GachaState):
        if not banner.got_limited_char and banner.limited_char_pity == 119:
            self.character_gacha_state_set(banner, 6, True)
            return

        BASE_P6 = 0.008
        BASE_P5 = 0.08
        SOFT_PITY_START = 64
        P6_STEP = 0.05

        pulls_done = self.player.six_pity
        soft_steps = max(pulls_done - SOFT_PITY_START, 0)

        p6 = BASE_P6 + P6_STEP * soft_steps
        p5 = BASE_P5 * ((1.0 - p6) / (1.0 - BASE_P6))

        roll = random.random()

        if self.player.six_pity >= 79 or roll < p6:
            self.character_gacha_state_set(banner, 6, random.choice([True, False]))
        elif self.player.five_pity >= 9 or roll < p6 + p5:
            self.character_gacha_state_set(banner, 5)
        else:
            self.character_gacha_state_set(banner, 4)

    def character_gacha_state_set(
        self, banner: GachaState, rarity: int, limited: bool = False
    ):
        if not banner.got_limited_char:
            banner.limited_char_pity += 1
        if rarity == 6:
            self.player.weapon_gacha_resource += 2000
            self.player.six_pity = 0
            self.player.five_pity = 0
            if limited:
                banner.got_limited_char = True
                rarity += 1
        elif rarity == 5:
            self.player.weapon_gacha_resource += 200
            self.player.six_pity += 1
            self.player.five_pity = 0
        elif rarity == 4:
            self.player.weapon_gacha_resource += 20
            self.player.six_pity += 1
            self.player.five_pity += 1
        self.player.total_char_runs += 1
        self.player.obtained_chars_rarity[rarity] += 1

    def try_weapon_gacha(self, banner: GachaState):
        COST = 1980
        P6 = 0.04
        P5 = 0.15
        P_LIMITED_GIVEN_6 = 0.25

        if self.player.weapon_gacha_resource < COST:
            return
        self.player.weapon_gacha_resource -= COST

        any_six = False
        limited_six = False

        def record_roll(rarity: int, limited: bool = False):
            nonlocal any_six, limited_six
            self.player.obtained_weapon_rarity[rarity] += 1
            if rarity == 6:
                any_six = True
                if limited:
                    limited_six = True

        pulls_left = 10
        guaranteed = None
        if (not banner.got_limited_weapon) and banner.limited_weapon_pity == 7:
            guaranteed = (6, True)
        elif banner.weapon_pity == 3:
            guaranteed = (6, random.random() < P_LIMITED_GIVEN_6)
        if guaranteed is not None:
            record_roll(*guaranteed)
            pulls_left -= 1

        for _ in range(pulls_left):
            r = random.random()
            if r < P6:
                record_roll(6, random.random() < P_LIMITED_GIVEN_6)
            elif r < P6 + P5:
                record_roll(5)
            else:
                record_roll(4)

        if any_six:
            banner.weapon_pity = 0
            if limited_six:
                banner.got_limited_weapon = True
            elif not banner.got_limited_weapon:
                banner.limited_weapon_pity += 1
        else:
            banner.weapon_pity += 1

        self.player.total_weapon_runs += 1
