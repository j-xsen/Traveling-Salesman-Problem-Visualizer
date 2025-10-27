from src.modes.Mode import Mode, ProblemType


class WisdomOfCrowds(Mode):
    def __init__(self, _map):
        super().__init__(ProblemType.WISDOM_OF_CROWDS, 'Random11.tsp', _map)