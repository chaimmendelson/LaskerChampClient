"""
general functions that are used in multiple modules.
"""
import re  # for validating moves


def validate_move(move: str|None) -> str | None:
    """
    validate the given move and return a dict representation of it.
    """
    if move is None: return None
    move = move.lower()
    regex = r'^[a-h][1-8][a-h][1-8][q,r,b,n]?$'
    if not re.fullmatch(regex, move):
        return None
    return move
