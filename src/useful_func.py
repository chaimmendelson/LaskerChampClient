"""
general functions that are used in multiple modules.
"""
import re  # for validating moves


def validate_move(move: str) -> dict[str, str] | None:
    """
    validate the given move and return a dict representation of it.
    """
    move = move.lower()
    regex = r'^[a-h][1-8][a-h][1-8][q,r,b,n]?$'
    if not re.fullmatch(regex, move):
        return None
    move_d: dict[str, str] = dict(move=move, src=move[:2], dst=move[2:4])
    if len(move) == 5:
        move_d.update(promotion=move[4])
    return move_d

def print(line: str):
    """
    write the given line to the file 'output.txt'.
    """
    # pylint: disable=redefined-builtin
    # add the line to the file 'output.txt'
    with open('src/output.txt', 'a', encoding='utf-8') as output_file:
        output_file.write(str(line) + '\n')


def clear_file():
    """
    clear the file 'output.txt'.
    """
    with open('src/output.txt', 'w', encoding='utf-8') as output_file:
        output_file.write('')
