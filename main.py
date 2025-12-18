from gacha_state import GachaSession
from dataclasses import dataclass, fields
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import sys
import time

if sys._is_gil_enabled():
    print(
        "GIL이 켜져 있습니다."
        "\n멀티스레드를 활용하기 위해서는 Python 3.14.x free-threaded 빌드가 필요합니다."
        "\npy install 3.14t 를 사용하여 설치할 수 있습니다."
        "\npython3.14t.exe '파일경로'로 실행할 수 있습니다."
    )
else:
    print("GIL이 꺼져 있습니다.\n멀티스레드가 의도대로 동작합니다.")


@dataclass
class result:
    # 평균 캐릭터 가챠 횟수
    avg_char_pulls: float = 0.0
    # 평균 무기뽑 횟수
    avg_weapon_pulls: float = 0.0
    # 전무를 뽑았을 때 평균 한정 갯수
    avg_limited_count_at_signature: float = 0.0
    # 남은 평균 무기뽑 재화 수
    avg_remaining_weapon_currency: float = 0.0
    # 남은 평균 캐릭터 가챠 스택 수
    avg_remaining_char_pity: float = 0.0
    # 명함 이후 평균 가챠 수
    avg_pulls_after_first_copy: float = 0.0
    # 명함을 먹은 시점의 평균
    avg_pulls_to_first_copy: float = 0.0


def worker(chunk: int) -> result:
    total_worker_result = result()
    for _ in range(chunk):
        worker_result = result()
        player = GachaSession()

        banner = player.get_banner()
        player.get_limited_char(banner)

        player_state = player.get_PlayerState()
        worker_result.avg_pulls_to_first_copy = player_state.total_char_runs

        player.get_limited_weapon(banner)
        player_state = player.get_PlayerState()

        worker_result.avg_char_pulls = player_state.total_char_runs
        worker_result.avg_weapon_pulls = player_state.total_weapon_runs
        worker_result.avg_limited_count_at_signature = (
            player_state.obtained_chars_rarity[7]
        )
        worker_result.avg_remaining_weapon_currency = player_state.weapon_gacha_resource
        worker_result.avg_remaining_char_pity = player_state.six_pity
        worker_result.avg_pulls_after_first_copy = (
            player_state.total_char_runs - worker_result.avg_pulls_to_first_copy
        )
        for f in fields(result):
            setattr(
                total_worker_result,
                f.name,
                getattr(total_worker_result, f.name) + getattr(worker_result, f.name),
            )
    return total_worker_result


total_try = 500_000
num_workers = min(total_try, os.cpu_count() or 1)
chunk, remainder = divmod(total_try, num_workers)
total_result = result()

start_time = time.time()
with ThreadPoolExecutor(max_workers=num_workers) as ex:
    futures = [ex.submit(worker, chunk + (i < remainder)) for i in range(num_workers)]
    for workers in as_completed(futures):
        worker_result: result = workers.result()
        for f in fields(result):
            setattr(
                total_result,
                f.name,
                getattr(total_result, f.name) + getattr(worker_result, f.name),
            )
for f in fields(result):
    setattr(
        total_result,
        f.name,
        getattr(total_result, f.name) / total_try,
    )
end_time = time.time()
total_time = end_time - start_time

str_list = [
    "평균 캐릭터 가챠 횟수:",
    "평균 무기뽑 횟수:",
    "전무를 뽑았을 때 평균 한정 갯수:",
    "남은 평균 무기뽑 재화 수:",
    "남은 평균 캐릭터 가챠 스택 수:",
    "명함 이후 평균 가챠 수:",
    "명함을 먹은 시점의 평균:",
]
print("\n\n시도 횟수:", total_try, "소요시간:", total_time)
for f, st in zip(fields(result), str_list):
    print(st, getattr(total_result, f.name))
