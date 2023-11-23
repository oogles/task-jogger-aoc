from pathlib import Path

from jogger.tasks import Task, TaskError

from ..utils.setup import find_next_day


class AdventOfCodeTask(Task):
    
    help = (
        'Initialise or run the Advent of Code puzzle solver/s for a given day.'
    )
    
    def add_arguments(self, parser):
        
        parser.add_argument(
            'day',
            nargs='?',
            help=(
                'The day [1-25] to operate on. Defaults to the next day without'
                ' a folder in the solutions/ subdirectory.'
            )
        )
    
    def handle(self, **options):
        
        day = self.get_day()
        
        puzzle_dir = Path(self.conf.project_dir, 'solutions', f'day{day:02d}')
        if not puzzle_dir.exists():
            self.initialise_puzzle(day, puzzle_dir)
        
        # TODO: Run solver/s
    
    def get_day(self):
        
        day = self.kwargs['day']
        project_dir = self.conf.project_dir
        
        if day:
            try:
                day = int(day)
            except ValueError:
                raise TaskError(f'Day must be provided as an integer.')
        else:
            # No explicit day is given, so find last day in solutions/ directory
            # and increment. Assume day 1 if there is no solutions/ directory.
            solutions_dir = Path(project_dir, 'solutions')
            if not solutions_dir.exists():
                day = 1
            else:
                day = find_next_day(solutions_dir)
        
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
