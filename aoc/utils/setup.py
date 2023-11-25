import re
import urllib.request

from jogger.tasks import TaskError

DAY_DIR_RE = re.compile(r'^day\d+$')
PUZZLE_NAME_RE = re.compile(r'<h2>--- Day \d+: (.+) ---</h2>')
AOC_BASE_URL = 'https://adventofcode.com'


def find_last_day(solutions_dir):
    """
    Return an integer representing the last day present as a subdirectory
    (in the format `day{n}`) in the given puzzle solutions directory. Return
    0 if the given directory does not exist or contains no matching subdirectories.
    """
    
    max_day = 0
    
    if not solutions_dir.exists():
        return max_day
    
    for x in solutions_dir.iterdir():
        if not x.is_dir():
            continue
        
        last_dir_name = x.parts[-1]
        if DAY_DIR_RE.match(last_dir_name):
            day = int(last_dir_name.replace('day', ''))
            if day > max_day:
                max_day = day
    
    return max_day


def get_puzzle_url(year, day):
    """
    Return the URL for the puzzle input for the given year and day.
    """
    
    return f'{AOC_BASE_URL}/{year}/day/{day}'


def get_puzzle_name(year, day):
    """
    Return the title of the puzzle for the given year and day, if it has been
    unlocked. Otherwise return None.
    """
    
    url = get_puzzle_url(year, day)
    
    try:
        with urllib.request.urlopen(url) as response:
            content = response.read()
    except urllib.error.HTTPError as e:
        if e.code == 404:
            raise TaskError('Invalid puzzle URL. Did you configure a valid year?')
        
        raise
    
    match = PUZZLE_NAME_RE.search(content.decode('utf-8'))
    if match:
        return match.group(1)
    
    return None
