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
        # Handle 404s, allow other status codes to propagate
        if e.code != 404:
            raise
        
        # Pages may 404 if they are completely invalid, or if the puzzle
        # has not yet been unlocked. Locked puzzles return more content
        # than the generic "404 Not Found" message included on truly
        # invalid pages, so use that to distinguish between the two.
        content = e.read()
        if 'not found' in content.decode('utf-8').lower():
            raise TaskError('Invalid puzzle URL. Did you configure a valid year?')
    
    match = PUZZLE_NAME_RE.search(content.decode('utf-8'))
    if match:
        return match.group(1)
    
    return None


def get_puzzle_input(year, day, session_cookie):
    """
    Return the input data of the puzzle for the given year and day, and for the
    individual represented by the given session cookie. Assume the day and year
    have already been validated.
    """
    
    puzzle_url = get_puzzle_url(year, day)
    input_url = f'{puzzle_url}/input'
    
    opener = urllib.request.build_opener()
    opener.addheaders.append(('Cookie', f'session={session_cookie}'))
    
    with opener.open(input_url) as response:
        return response.read().decode('utf-8')
