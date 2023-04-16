import json
import accounts_db as hd
import subprocess

FILE = './src/stats.json'
ACCOUNTS_COUNT = 'accounts count'
PVP_PLAYED = 'pvp games played'
PVP_ROOMS = 'current pvp rooms'
CLOCKS = 'most used clock'
GAMES_PLAYED_TODAY = 'games played today'
ONLINE_PLAYERS = 'online players'

chess_clocks = ['5|0', '3|2', '10|5', '15|10', '30|0']
def initialize():
    stats = {
        ACCOUNTS_COUNT: hd.get_user_count(),
        PVP_PLAYED: 0,
        PVP_ROOMS: 0,
        CLOCKS: dict(zip(chess_clocks, [0] * len(chess_clocks))),
        GAMES_PLAYED_TODAY: 0,
        ONLINE_PLAYERS: 0,
    }
    with open(FILE, 'w') as stats_file:
        json.dump(stats, stats_file, indent=4)
        
def get_stats():
    with open(FILE, 'r') as stats_file:
        stats = json.load(stats_file)
    return stats


def update_stat(key: str, value):
    stats = get_stats()
    with open(FILE, 'w') as stats_file:
        stats[key] = value
        json.dump(stats, stats_file, indent=4)
        

def update_clock(clock: str):
    clocks = dict(get_stats()[CLOCKS])
    clocks[clock] += 1
    update_stat(CLOCKS, clocks)
    
        
def upon_close_pvp_room(clock: str):
    update_counter(PVP_ROOMS, -1)
    update_counter(GAMES_PLAYED_TODAY)
    update_counter(PVP_PLAYED)


def upon_close_pve_room():
    update_counter(GAMES_PLAYED_TODAY)
    

def upon_open_pvp_room():
    update_counter(PVP_ROOMS)
       
       
def update_counter(key: str, value: int=1):
    update_stat(key, get_stats()[key] + value)

def reset_counter(key: str):
    update_stat(key, 0)
    

initialize()