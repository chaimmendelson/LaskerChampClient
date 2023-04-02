import subprocess
import os
OUTPUT_FILE = 'src/output.txt'

def parse_run() -> dict[str, list|dict|str]:
    with open(OUTPUT_FILE, "r", encoding='utf-8') as file:
        file = file.read()
    file = file.split('---')
    file = [i for i in file if not i.startswith(' floor')]
    for i in range(len(file)):
        file[i] = file[i].strip().splitlines() # type: ignore
    settings = file.pop(0)[-1]
    items = []
    special_items: dict[str, list] = {}
    for i, line in enumerate(file):
        item_k = None
        floor = {}
        for item in line:
            if item == '':
                item_k = None
            elif item_k is None:
                if not item.endswith(':'):
                    continue
                item_k = item[:-1]
                if item_k not in floor.keys():
                    floor[item_k] = []
            else:
                if item_k in special_items.keys():
                    special_items[item_k].append(item[2:])
                else:
                    floor[item_k].append(item[2:])
        items.append(floor)
    return dict(settings=settings, items=items, special_items=special_items)


def search_seed(levels: int, seed: str):
    """
    write the items found in the seed to a file untill the level specified
    """
    os.system(f'java -jar src/seed-finder.jar {levels} {seed} > {OUTPUT_FILE}')
        
def get_items(seed: str, levels: int) -> dict[str, list|dict|str]:
    search_seed(levels, seed)
    run = parse_run()
    return run