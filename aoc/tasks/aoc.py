import datetime
from pathlib import Path

from jogger.tasks import Task, TaskError

from ..utils.setup import find_last_day, get_puzzle_input, get_puzzle_name


class AdventOfCodeTask(Task):
    
    help = (
        'Initialise or run the Advent of Code puzzle solver/s for a given day.'
    )
    
    def add_arguments(self, parser):
        
        # The `day` and `next` arguments are mutually exclusive
        group = parser.add_mutually_exclusive_group()
        
        group.add_argument(
            'day',
            nargs='?',
            help=(
                'The day [1-25] to operate on. If the given day has solvers, run'
                ' them. Otherwise, offer to create a template subdirectory for'
                ' the day. Defaults to the last day with a template subdirectory.'
            )
        )
        
        group.add_argument(
            '-n', '--next',
            action='store_true',
            help='Create a template subdirectory for the next day without one.'
        )
    
    def handle(self, **options):
        
        day = self.get_day()
        
        puzzle_dir = Path(self.conf.project_dir, 'solutions', f'day{day:02d}')
        if not puzzle_dir.exists():
            self.initialise_puzzle(day, puzzle_dir)
            return
        
        # TODO: Run solver/s
        self.stdout.write(f'Running solvers for day {day}...', style='label')
    
    def get_year(self):
        
        return self.settings.get('year', datetime.date.today().year)
    
    def get_day(self):
        
        day = self.kwargs['day']
        project_dir = self.conf.project_dir
        
        if day:
            try:
                day = int(day)
            except ValueError:
                raise TaskError(f'Day must be provided as an integer.')
        else:
            # No explicit day is given, so find last day in the `solutions/`
            # directory and increment if need be
            solutions_dir = Path(project_dir, 'solutions')
            day = find_last_day(solutions_dir)
            
            if self.kwargs['next']:
                day += 1
            
            if not day:
                # No previous days exist to run solvers for
                raise TaskError(
                    'No existing solvers to run. Use --next to create some.'
                )
        
        if not 1 <= day <= 25:
            raise TaskError(f'Invalid day ({day}). Must be between 1-25.')
        
        return day
    
    def initialise_puzzle(self, day, puzzle_dir):
        
        year = self.get_year()
        
        puzzle_name = get_puzzle_name(year, day)
        if not puzzle_name:
            raise TaskError(f'Puzzle for day {day} has not been unlocked.')
        
        try:
            answer = input(f'No puzzle solvers for day {day} exist. Create them now [y/N]? ')
        except KeyboardInterrupt:
            answer = None  # no
        
        if answer.lower() != 'y':
            self.stdout.write('Nothing to do.')
            raise SystemExit()
        
        self.stdout.write(f'\n--- Day {day}: {puzzle_name} ---', style='label')
        
        # Attempt to fetch input data first, so if any issues are encountered
        # the template isn't left partially created
        input_data = None
        session_cookie = self.settings.get('session_cookie')
        if not session_cookie:
            self.stdout.write(
                'Not fetching puzzle input: No session cookie configured.',
                style='warning'
            )
        else:
            self.stdout.write('Fetching puzzle input...')
            input_data = get_puzzle_input(year, day, session_cookie)
        
        # Create the directory and template content
        self.stdout.write('Creating template...')
        puzzle_dir.mkdir(parents=True)
        Path(puzzle_dir, '__init__.py').touch()
        
        if input_data:
            with Path(puzzle_dir, 'input').open('w') as f:
                f.write(input_data)
        
        solvers_template = Path(puzzle_dir, 'solvers.py')
        solvers_template.touch()
        
        self.stdout.write('Done')
        self.stdout.write(f'\nTemplate created at: {solvers_template}', style='success')
