"""
for now, this is just a test file
"""

from datetime import datetime


def update_elo_tester():
    """
    RatA + K * (score - (1 / (1 + 10(RatB - RatA)/400)))
    K = 400/(games_played**1.5) + 16
    """
    p_elo = 1500
    o_elo = 1500
    p_k = 400 / 1 + 16
    o_k = 400 / 1 + 16
    p_score = 1
    o_score = 0
    p_new_elo = p_elo + p_k * (p_score - (1 / (1 + 10 ** ((o_elo - p_elo) / 400))))
    o_new_elo = o_elo + o_k * (o_score - (1 / (1 + 10 ** ((p_elo - o_elo) / 400))))
    print(p_new_elo)
    print(o_new_elo)

 
def main():
    """
    main function
    """
    current_time = datetime.now()
    print(current_time.strftime('%H:%M:%S'))
    
if __name__ == '__main__':
    main()
