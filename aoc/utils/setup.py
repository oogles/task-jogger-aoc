import re

DAY_DIR_RE = re.compile(r'^day\d+$')


def find_next_day(solutions_dir):
    """
    Return an integer representing the first day not present as a subdirectory
    (in the format `day{n}`) in the given puzzle solutions directory.
    """
    
    max_day = 0
    for x in solutions_dir.iterdir():
        if not x.is_dir():
            continue
        
        last_dir_name = x.parts[-1]
        if DAY_DIR_RE.match(last_dir_name):
            day = int(last_dir_name.replace('day', ''))
            if day > max_day:
                max_day = day
    
    return max_day + 1
