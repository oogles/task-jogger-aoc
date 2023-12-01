import re
import urllib.request
from importlib import import_module
from pathlib import Path

from jogger.tasks import TaskError

DAY_DIR_RE = re.compile(r'^day\d+$')
PUZZLE_NAME_RE = re.compile(r'<h2>--- Day \d+: (.+) ---</h2>')
AOC_BASE_URL = 'https://adventofcode.com'


def confirm(prompt):
    
    try:
        answer = input(f'{prompt} [y/n]? ')
    except KeyboardInterrupt:
        return False  # no
    
    return answer.lower() == 'y'


def gather_sample_input():
    
    lines = []
    try:
        while True:
            lines.append(input())
    except EOFError:
        pass
    
    return '\n'.join(lines)


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


def make_puzzle_request(url, opener=None):
    """
    Make a request to the given Advent of Code puzzle URL and return the
    response content. Handle 404 responses, differentiating between locked
    puzzles and truly invalid URLs. Return None if the puzzle is locked.
    """
    
    if not opener:
        opener = urllib.request.build_opener()
    
    try:
        with opener.open(url) as response:
            return response.read().decode('utf-8')
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
        
        return None  # a locked puzzle


class Puzzle:
    """
    An Advent of Code puzzle for a specific year and day. Handles requesting
    remote puzzle data and creating the local files necessary for writing
    puzzle solvers.
    """
    
    def __init__(self, solutions_dir, year, day):
        
        self.year = year
        self.day = day
        
        self.url = f'{AOC_BASE_URL}/{year}/day/{day}'
        self.directory = Path(solutions_dir, f'day{day:02d}')
        
        self.input_path = Path(self.directory, 'input')
        self.sample1_path = Path(self.directory, 'sample1')
        self.sample2_path = Path(self.directory, 'sample2')
        
        self._imported_solvers = None
    
    @property
    def solvers_module(self):
        
        if self._imported_solvers is None:
            try:
                self._imported_solvers = import_module(f'solutions.day{self.day:02d}.solvers')
            except ModuleNotFoundError:
                raise TaskError(f'No solvers module found for day {self.day}.')
        
        return self._imported_solvers
    
    def fetch_title(self):
        """
        Return the title of the puzzle by inspecting its webpage, if it has
        been unlocked. Otherwise, return None.
        """
        
        content = make_puzzle_request(self.url)
        
        if content:
            match = PUZZLE_NAME_RE.search(content)
            if match:
                return match.group(1)
        
        return None
    
    def fetch_input(self, session_cookie):
        """
        Download and return the input data of the puzzle for the individual
        represented by the given session cookie.
        """
        
        opener = urllib.request.build_opener()
        opener.addheaders.append(('Cookie', f'session={session_cookie}'))
        
        url = f'{self.url}/input'
        
        return make_puzzle_request(url, opener)
    
    def create_template(self, input_data=None):
        """
        Create and populate the directory for this puzzle. Create a file for
        the input data, if any is given, and a file for the puzzle solvers.
        Return the path to the latter.
        """
        
        base_dir = self.directory
        
        base_dir.mkdir(parents=True)
        Path(base_dir, '__init__.py').touch()
        
        input_path = Path(base_dir, 'input')
        if input_data:
            input_path.write_text(input_data)
        else:
            input_path.touch()
        
        solvers_file = Path(base_dir, 'solvers.py')
        solvers_file.write_text(solver_template)
        
        return solvers_file
    
    def read_input_data(self, sample_part=None):
        """
        Read the content of the appropriate input file and apply the defined
        parser function (from `solvers.input_parser`) to it, if any.
        Return the (optionally) processed content.
        """
        
        if not sample_part:
            path = self.input_path
        else:
            path = getattr(self, f'sample{sample_part}_path')
        
        content = path.read_text()
        
        parser = getattr(self.solvers_module, 'input_parser', None)
        if parser:
            content = parser(content)
        
        return content
    
    def run_solver(self, part, input_data):
        """
        Run the solver function for the given part of the puzzle, passing the
        given input data.
        """
        
        try:
            solver = getattr(self.solvers_module, f'part{part}')
        except AttributeError:
            raise TaskError(f'No solver found for part {part}.')
        
        try:
            return solver(input_data)
        except NotImplementedError:
            raise TaskError(f'No solver implemented for part {part}.')


solver_template = """from aoc.utils import parsing

input_parser = parsing.split_lines


def part1(input_data):
    
    raise NotImplementedError()


def part2(input_data):
    
    raise NotImplementedError()
"""
