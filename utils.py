from dataclasses import dataclass
import heapq
from typing import Iterator, List, Optional


class PriorityQueue:
    def __init__(self):
        self.heap = []

    def empty(self):
        return len(self.heap) == 0

    def push(self, item, priority):
        entry = (priority, self.count, item)
        heapq.heappush(self.heap, entry)

    def pop(self):
        (_, _, item) = heapq.heappop(self.heap)
        return item

    def __len__(self):
        return len(self.heap)


@dataclass
class Position:
    x: int
    y: int

    def __hash__(self):
        return hash(f"{self.x},{self.y}")


class ShortestPathState:
    def __init__(
        self, pos: Position, cost: int, prev: Optional["ShortestPathState"] = None
    ):
        self.pos = pos
        self.cost = cost
        self.prev = prev

    def __eq__(self, other):
        return self.pos == other.pos

    def __hash__(self) -> int:
        return hash(self.pos)


class ShortestPathSearchProblem:
    def __init__(self, start: Position, goal: Position, visited: List[List[bool]]):
        self.start = start
        self.goal = goal
        self.visited = visited

    def get_start_state(self) -> ShortestPathState:
        return ShortestPathState(self.start, 0)

    def is_goal_state(self, state: ShortestPathState) -> bool:
        return state.pos == self.goal

    def get_successors(self, state: ShortestPathState) -> Iterator[ShortestPathState]:
        m = len(self.visited)
        n = len(self.visited[0])

        for x, y in ((0, 1), (1, 0), (-1, 0), (0, -1)):
            children = Position(state.pos.x + x, state.pos.y + y)
            cond = (
                children.x >= 0
                and children.x < n
                and children.y >= 0
                and children.y < m
                and self.visited[children.y][children.x]
            )
            if cond:
                yield ShortestPathState(children, state.cost + 1, state)


def a_star_route(problem: ShortestPathSearchProblem) -> List[str]:
    pass


visited = [
    [True, True, True, True],
    [True, True, True, True],
    [True, True, True, True],
    [True, True, True, True],
]
problem = ShortestPathSearchProblem(Position(1, 1), Position(3, 3), visited)
start = problem.get_start_state()
for children in problem.get_successors(start):
    print(children.pos)
