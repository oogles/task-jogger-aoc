from pathlib import Path

from jogger.tasks import Task, TaskError

from ..utils.setup import find_last_day


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
    
    def get_day(self):
        
        day = self.kwargs['day']
        project_dir = self.conf.project_dir
        
        if day:
            try:
                day = int(day)
            except ValueError:
                raise TaskError(f'Day must be provided as an integer.')
        else:
            # No explicit day is given, so find last day in `solutions/`
            # directory and increment
            solutions_dir = Path(project_dir, 'solutions')
            day = find_last_day(solutions_dir)
            
            if self.kwargs['next']:
                # Initialise the next day
                day += 1
            
            if not day:
                # No previous days exist to run solvers for
                raise TaskError(
                    'No existing solvers to run. Use --next to create some.'
                )
        
        if not 1 <= day <= 25:
            raise TaskError(f'Invalid day ({day}). Must be between 1-25.')
        
        # TODO: Check the day's puzzle has been unlocked
        
        return day
    
    def initialise_puzzle(self, day, puzzle_dir):
        
        if not puzzle_dir.exists():
            try:
                answer = input(f'No puzzle solvers for day {day} exist. Create them now [y/N]? ')
            except KeyboardInterrupt:
                answer = None  # no
            
            if answer.lower() != 'y':
                self.stdout.write('Nothing to do.')
                raise SystemExit()
        
        # Create the directory and an `__init__.py` and `solvers.py` file
        puzzle_dir.mkdir(parents=True)
        Path(puzzle_dir, '__init__.py').touch()
        
        solvers_template = Path(puzzle_dir, 'solvers.py')
        solvers_template.touch()
        
        # TODO: Populate the template, fetch input
        
        self.stdout.write(f'Created solvers template: {solvers_template}', style='success')
