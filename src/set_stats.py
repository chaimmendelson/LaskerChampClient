import json
import subprocess

FILE = './src/stats.json'
ACCOUNTS_COUNT = 'accounts_count'
PVP_PLAYED = 'pvp_played'
PVP_ROOMS = 'pvp_rooms'
ELO_AMOUNT = 'elo_amount'
CLOCKS_RATE = 'clocks_rate'
GAMES_PLAYED_TODAY = 'games_played_today'

def initialize():
    stats = {
        ACCOUNTS_COUNT: 0,
        PVP_PLAYED: 0,
        PVP_ROOMS: 0,
        ELO_AMOUNT: 0,
        CLOCKS_RATE: 0,
        GAMES_PLAYED_TODAY: 0
    }
    with open(FILE, 'w') as stats_file:
        json.dump(stats, stats_file, indent=4)
        
def get_stats():
    with open(FILE, 'r') as stats_file:
        stats = json.load(stats_file)
    return stats


def update_stat(key: str, value):
    with open(FILE, 'w') as stats_file:
        stats = json.load(stats_file)
        stats[key] = value
        json.dump(stats, stats_file, indent=4)
        
        
def update_counter(key: str, value: int=1):
    update_stat(key, get_stats()[key] + value)

def reset_counter(key: str):
    update_stat(key, 0)
    

initialize()
print(get_stats())