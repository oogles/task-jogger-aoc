import datetime
from pathlib import Path

from jogger.tasks import Task, TaskError

from ..utils.setup import Puzzle, find_last_day


class AdventOfCodeTask(Task):
    
    help = (
        'Initialise or run the Advent of Code puzzle solver/s for a given day.'
    )
    
    def add_arguments(self, parser):
        
        # The `day` and `next` arguments are mutually exclusive
        day_group = parser.add_mutually_exclusive_group()
        
        day_group.add_argument(
            'day',
            nargs='?',
            help=(
                'The day [1-25] to operate on. If the given day has solvers, run'
                ' them. Otherwise, offer to create a template subdirectory for'
                ' the day. Defaults to the last day with a template subdirectory.'
            )
        )
        
        day_group.add_argument(
            '-n', '--next',
            action='store_true',
            help='Create a template subdirectory for the next day without one.'
        )
        
        # All remaining arguments are also effectively mutually exclusive with
        # --next, but are simply ignored if --next is provided
        
        parser.add_argument(
            '-s', '--sample',
            action='store_true',
            help='Run the solver/s using sample data instead of the full input data.'
        )
        
        # The `part1` and `part2` arguments are mutually exclusive with each
        # other. If both parts should be run, neither argument should be given.
        part_group = parser.add_mutually_exclusive_group()
        part_group.add_argument(
            '-1', '--part1',
            action='store_true',
            help='Run the solver for part 1 of the puzzle only.'
        )
        
        part_group.add_argument(
            '-2', '--part2',
            action='store_true',
            help='Run the solver for part 2 of the puzzle only.'
        )
    
    def handle(self, **options):
        
        year = self.get_year()
        day = day = self.get_day()
        solutions_dir = Path(self.conf.project_dir, 'solutions')
        
        puzzle = Puzzle(solutions_dir, year, day)
        if not puzzle.directory.exists():
            self.initialise_puzzle(puzzle)
            return
        
        self.run_solvers(puzzle)
    
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
    
    def fetch_input_data(self, puzzle):
        
        input_data = None
        session_cookie = self.settings.get('session_cookie')
        if not session_cookie:
            self.stdout.write(
                'Not fetching puzzle input: No session cookie configured.',
                style='warning'
            )
        else:
            self.stdout.write('Fetching puzzle input...')
            input_data = puzzle.fetch_input(session_cookie)
        
        return input_data
    
    def initialise_puzzle(self, puzzle):
        
        day = puzzle.day
        
        puzzle_title = puzzle.fetch_title()
        if not puzzle_title:
            raise TaskError(f'Puzzle for day {day} has not been unlocked.')
        
        try:
            answer = input(f'No puzzle solvers for day {day} exist. Create them now [y/N]? ')
        except KeyboardInterrupt:
            answer = None  # no
        
        if answer.lower() != 'y':
            self.stdout.write('Nothing to do.')
            raise SystemExit()
        
        self.stdout.write(f'\n--- Day {day}: {puzzle_title} ---', style='label')
        
        # Attempt to fetch input data first, so if any issues are encountered
        # the template isn't left partially created
        input_data = self.fetch_input_data(puzzle)
        
        # Create the directory and template content
        self.stdout.write('Creating template...')
        solvers_file = puzzle.create_template(input_data)
        
        self.stdout.write('Done')
        self.stdout.write(f'\nTemplate created at: {solvers_file}', style='success')
    
    def run_solvers(self, puzzle):
        
        title = f'Solving: Day {puzzle.day}'
        run_part1 = True
        run_part2 = True
        
        if self.kwargs['part1']:
            title = f'{title} (part 1)'
            run_part2 = False
        elif self.kwargs['part2']:
            title = f'{title} (part 2)'
            run_part1 = False
        
        # Style the title and surrounding dashes manually (rather than using
        # `style='label'` on the stdout.write() call) so that the sample data
        # warning, if added, doesn't cancel the styles part way through the line
        title = self.styler.label(title)
        dashes = self.styler.label('---')
        
        sample = self.kwargs['sample']
        if sample:
            title = f'{title} {self.styler.warning("[sample data]")}'
        
        self.stdout.write(f'{dashes} {title} {dashes}')
        
        self.stdout.write(f'\nProcessing input data...')
        
        if run_part1:
            self.stdout.write('\nRunning part 1 solver...')
            result = None
            self.stdout.write(f'Result: {result}')
        
        if run_part2:
            self.stdout.write('\nRunning part 2 solver...')
            result = None
            self.stdout.write(f'Result: {result}')
