import collections
import tkinter as tk
import time
import numpy as np
from mazelib import Maze
from mazelib.generate.Kruskal import Kruskal

from util import draw_maze

# set seed for numpy shuffle
np.random.seed(2)

size_rectangles = 15

side_length_square = 31
height = side_length_square
width = side_length_square
assert height % 2 == 1 and width % 2 == 1, "height and width have to be uneven"
m = Maze()
# m.generator = Prims(int((height-1)/2), int((width-1)/2))
m.generator = Kruskal(int((height - 1) / 2), int((width - 1) / 2))
m.generate()
m.start = (1, 1)
m.end = (height - 2, width - 2)
m.grid[m.start[1], m.start[0]] = 2
m.grid[m.end[1], m.end[0]] = 3

# make a tkinter window with a canvas that will show the maze
root = tk.Tk()
root.title("DFS: Solving maze with depth first search")
widget = tk.Label(root, text='DFS: Solving maze with depth first search', fg='white', bg='black')
widget.pack()
canvas = tk.Canvas(root, width=width * size_rectangles, height=height * size_rectangles)
canvas.pack()
fps = 2
# add label 

draw_maze(m.grid, canvas, size_rectangles)
time.sleep(1)

def dfs(grid, start):
    stack = collections.deque()
    stack.append(start)
    seen = set([start])
    # make two dim datastructur of size of the maze to store touples of x,y coordinates
    successor = [[0 for x in range(width)] for y in range(height)]
    path = []
    while stack:
        next_step = stack.pop()
        # print(next_step)
        y, x = next_step
        seen.add((y, x))
        if grid[y, x] != 3 and grid[y, x] != 2:
            grid[y, x] = 4
        if grid[y][x] == 3:
            # do backtracking to find the path
            while (y, x) != m.start:
                if grid[y, x] != 3:
                    grid[y, x] = 5
                path.append((y, x))
                y, x = successor[y][x]
            path.append(m.start)
            path.reverse()
            draw_maze(grid, canvas, size_rectangles)
            return True, path
        for y2, x2 in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)):  # directions
            if (0 <= x2 < width and  # X-axis in range
                    0 <= y2 < height and  # y-axis
                    grid[y2][x2] != 1 and  # not a wall
                    (y2, x2) not in seen):  # not visited
                stack.append((y2, x2))
                successor[y2][x2] = (y, x)
                draw_maze(grid, canvas, size_rectangles)
                # make a pause for 0.5 seconds
                # root.after(round(1000/fps))
    return False, path


success, path = dfs(m.grid, m.start)

print(success)
print(path)

root.mainloop()
