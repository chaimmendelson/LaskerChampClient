import json
from .accounts_db import get_accounts_count
from datetime import datetime
from .chess_rooms import *
from .client_class import CLIENTS
DAILY_FILE = 'src/daily_stat.json'

PVP_PLAYED = 'online'
ENGINE_PLAYED = 'engine'
NEW_ACCOUNTS = 'new'
STATS = [PVP_PLAYED, ENGINE_PLAYED, NEW_ACCOUNTS]

chess_clocks = ['5|0', '3|2', '10|5', '15|10', '30|0']

def now() -> str:
    return datetime.now().strftime('%Y-%m-%d')

def initialize_day() -> None:
    stats = {
        PVP_PLAYED: 0,
        ENGINE_PLAYED: 0,
        NEW_ACCOUNTS: 0,
    }
    file_data = get_stats()
    file_data[now()] = stats
    with open(DAILY_FILE, 'w') as daily_file:
        json.dump(file_data, daily_file, indent=4)
        
def get_stats() -> dict[str, dict[str, int]]:
    with open(DAILY_FILE, 'r') as stats_file:
        stats = json.load(stats_file)
    return stats


def get_today_stats() -> dict[str, dict[str, int]]:
    stats = get_stats()
    today = stats.get(now(), {PVP_PLAYED: 0, ENGINE_PLAYED: 0, NEW_ACCOUNTS: 0})
    current = get_current_statues()
    return dict(today=today, current=current)


def get_overall_stats() -> dict[str, dict[str, int] | dict[str, dict[str, int]]]:
    stats = get_stats()
    current = get_current_statues()
    return dict(overall=stats, current=current)

def get_current_statues() -> dict[str, int]:
    return dict(
        online = len([room for room in CHESS_ROOMS if isinstance(room, PlayerRoom)]),
        engine = len([room for room in CHESS_ROOMS if isinstance(room, EngineRoom)]),
        accounts = len(CLIENTS),
        count = get_accounts_count()
    )
    
    
    
def update_stat(key: str) -> None:
    if key not in STATS: return
    stats = get_stats()
    if stats.get(now()) is None:
        initialize_day()
        stats = get_stats()
    with open(DAILY_FILE, 'w') as stats_file:
        stats[now()][key] += 1
        json.dump(stats, stats_file, indent=4)
        
print(now())