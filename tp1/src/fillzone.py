from random import randrange
from collections import deque

class FillzoneState:
    display_chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    
    def __init__(self, grid_size: int, color_count: int):
        self.grid_size = grid_size
        self.color_count = color_count
        self.grid = [[0 for _ in range(grid_size)] for _ in range(grid_size)]
    
     
    def play_color(self, color_index: int):
        from_color = self.grid[0][0]
        res = clone_fillzone(self)
        border = deque([(0, 0)])
        while (len(border) > 0):
            c = border.pop()
            res.grid[c[0]][c[1]] = color_index
            for neighbor in [(c[0]-1, c[1]), (c[0]+1, c[1]), (c[0], c[1]-1), (c[0], c[1]+1)]:
                if (neighbor[0] < 0 or neighbor[0] >= res.grid_size or neighbor[1] < 0 or neighbor[1] >= res.grid_size):
                    continue
                if (res.grid[neighbor[0]][neighbor[1]] != from_color or res.grid[neighbor[0]][neighbor[1]] == color_index):
                    continue
                border.append(neighbor)
        return res
    
    
    def __str__(self) -> str:
        s = ''
        for y in range(0, self.grid_size):
            for x in range(0, self.grid_size):
                s += self.display_chars[self.grid[x][y]].__str__()
            s += '\n'
        return s


def new_fillzone_game(grid_size, color_count) -> FillzoneState:
    g = FillzoneState(grid_size, color_count)
    for y in range(g.grid_size):
        for x in range(g.grid_size):
            g.grid[x][y] = randrange(0, g.color_count - 1)
    return g


def clone_fillzone(fz: FillzoneState) -> FillzoneState:
    g = FillzoneState(fz.grid_size, fz.color_count)
    for y in range(g.grid_size):
        for x in range(g.grid_size):
            g.grid[x][y] = fz.grid[x][y]
    return g