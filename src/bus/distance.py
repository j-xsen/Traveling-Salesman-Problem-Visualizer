def distance(point1, point2):
    """Calculate the Euclidean distance between two points in 2D space."""
    if point1 is None or point2 is None:
        return 0
    return ((point1.x - point2.x) ** 2 + (point1.y - point2.y) ** 2) ** 0.5
