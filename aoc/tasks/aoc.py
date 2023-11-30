import datetime
from pathlib import Path
from time import perf_counter_ns

from jogger.tasks import Task, TaskError

from ..utils.setup import Puzzle, confirm, find_last_day, gather_sample_input


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
                raise TaskError('Day must be provided as an integer.')
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
        
        if not confirm(f'No puzzle solvers for day {day} exist. Create them now'):
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
        
        if run_part1:
            self.run_part(1, puzzle, sample)
        
        if run_part2:
            self.run_part(2, puzzle, sample)
    
    def verify_input(self, puzzle, sample_part):
        
        if not sample_part:
            # If a primary input file does not exist, attempt to fetch puzzle
            # input and create one automatically. If not possible, stop here:
            # the user will need to manually create the file.
            if not puzzle.input_path.exists():
                input_data = self.fetch_input_data(puzzle)
                if input_data is not None:
                    puzzle.input_path.write_text(input_data)
                else:
                    raise TaskError(
                        'No puzzle input found. Create an `input` file'
                        ' manually or configure a session cookie to fetch'
                        ' the input automatically.'
                    )
        else:
            # If a part-specific sample data file does not exist, prompt the
            # user to enter the sample data and save it to such a file.
            path = getattr(puzzle, f'sample{sample_part}_path')
            if not path.exists():
                self.stdout.write(f'No part {sample_part} sample data found.')
                
                # Part 2 can opt to use the same sample data as part 1 if it exists
                if sample_part == 2 and puzzle.sample1_path.exists():
                    if confirm('Use the same sample data as part 1'):
                        path.write_text(puzzle.sample1_path.read_text())
                        return
                
                self.stdout.write(
                    f'Enter part {sample_part} sample data below.'
                    ' You can enter/paste multiple lines. Use Ctrl+D to submit.'
                )
                input_data = gather_sample_input()
                path.write_text(input_data)
    
    def log_done(self, start_ns, error=False):
        
        duration = perf_counter_ns() - start_ns
        msg = 'error' if error else 'done'
        style = 'error' if error else None
        
        self.stdout.write(f'{msg} [{duration / 1e9:.6f}s]', style=style)
    
    def run_part(self, part, puzzle, sample):
        
        self.stdout.write(f'\n-- Part {part} --', style='label')
        
        sample_part = None if not sample else part
        
        # Ensure input/sample data exists, creating it if necessary, before
        # reading/processing it to pass to the solver
        self.verify_input(puzzle, sample_part)
        
        data_type = self.styler.warning('sample') if sample else 'input'
        self.stdout.write(f'Processing {data_type} data... ', ending='')
        
        input_start = perf_counter_ns()
        try:
            input_data = puzzle.read_input_data(sample_part)
        except Exception:
            self.log_done(input_start, error=True)
            raise
        else:
            self.log_done(input_start)
        
        self.stdout.write('Running solver... ', ending='')
        
        solve_start = perf_counter_ns()
        try:
            solution = puzzle.run_solver(part, input_data)
        except Exception:
            self.log_done(solve_start, error=True)
            raise
        else:
            self.log_done(solve_start)
        
        self.stdout.write(f'\nSolution: {solution}', style='label')
