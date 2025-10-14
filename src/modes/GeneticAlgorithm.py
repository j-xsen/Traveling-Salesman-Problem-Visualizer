from src.modes.Mode import Mode, ProblemType


class GeneticAlgorithm(Mode):
    def __init__(self, _map):
        super().__init__(ProblemType.GENETIC_ALGORITHM, 'Random100.tsp', _map)