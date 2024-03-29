from mazelib.generate.Prims import Prims
from mazelib.generate.Kruskal import Kruskal
from mazelib import Maze
from mazelib.solve.BacktrackingSolver import BacktrackingSolver
import torch
from matplotlib.colors import ListedColormap
import numpy as np
import copy
import time

from util import *
from solver import *

# set seed for numpy shuffle
np.random.seed(2)

size_rectangles = 15
cmap1 = ListedColormap(['white', 'black', (0.4, 1, 0.2), 'purple'])
cmap2 = ListedColormap(['white', 'black', (0.4, 1, 0.2), 'purple', (0, 0.4, 0.8), 'red'])

side_length_square = 31
height = side_length_square
width = side_length_square

m = Maze()

if height % 2 == 0:
    height += 1
    print("height has to be uneven, adding 1 to height")
if width % 2 == 0:
    width += 1
    print("width has to be uneven, adding 1 to width")

m.generator = Prims(int((height - 1) / 2), int((width - 1) / 2))
# m.generator = Kruskal(int((height-1)/2), int((width-1)/2))
m.generate()
print(m.grid)
m.start = (1, 1)
m.end = (height - 2, width - 2)

# get the number of 0 in m.grid
num_ones = np.count_nonzero(m.grid == 0)

# for bfs
# build back the walls back up
bfs_grid = copy.deepcopy(m.grid)
bfs_grid[m.start[0], m.start[1] - 1] = 1
bfs_grid[m.end[0], m.end[1] + 1] = 1
# mark beginning and end
bfs_grid[m.start] = 2
bfs_grid[m.end[0], m.end[1]] = 3

start_time = time.time()
success, path, bfs_seen = bfs(bfs_grid, m.start)
bfs_frac_seen = len(bfs_seen) / num_ones
end_time = time.time()
bfs_time = end_time - start_time
print("time bfs: ", bfs_time)

# for dfs
# build back the walls back up
dfs_grid = copy.deepcopy(m.grid)
dfs_grid[m.start[0], m.start[1] - 1] = 1
dfs_grid[m.end[0], m.end[1] + 1] = 1
# mark beginning and end
dfs_grid[m.start] = 2
dfs_grid[m.end[0], m.end[1]] = 3
# start timer
start = time.time()
success, path, dfs_seen = dfs(dfs_grid, m.start)
dfs_frac_seen = len(dfs_seen) / num_ones
# end timer
end = time.time()
dfs_time = end - start
print("time dfs: ", dfs_time)

# do CA one time to allocate memory on the GPU and then do it again with time
# measurement
ca_grid = copy.deepcopy(m.grid)
ca_grid[m.start[0], m.start[1] - 1] = 0
ca_grid[m.end[0], m.end[1] + 1] = 0
kernel = torch.tensor([[0, 1, 0], [1, 0, 1], [0, 1, 0]]).float().to(getPytorchDevice())
count, tensor_grid = ca(ca_grid, kernel)

# for CA
ca_grid = copy.deepcopy(m.grid)
ca_grid[m.start[0], m.start[1] - 1] = 0
ca_grid[m.end[0], m.end[1] + 1] = 0
kernel = torch.tensor([[0, 1, 0], [1, 0, 1], [0, 1, 0]]).float().to(getPytorchDevice())
# start time
start_time = time.time()
count, tensor_grid = ca(ca_grid, kernel)
# end time
end_time = time.time()
print("count: ", count)
ca_time = end_time - start_time
print("time CA: ", ca_time)

# plot
tensor_grid = tensor_grid.cpu().numpy()
grid_with_path = copy.deepcopy(m.grid)
grid_original = copy.deepcopy(m.grid)
grid_with_path[tensor_grid == 0] = 5

grids = [grid_original, grid_with_path, bfs_grid, dfs_grid]
cmaps = ['Greys', cmap2, cmap2, cmap2]
titles = []
titles.append("original \n")
titles.append("CA, " + "time: " + str(round(ca_time * 1000, 1)) + "ms \n")
titles.append("BFS, " + "time: " + str(round(bfs_time * 1000, 1)) + "ms, \nfrac seen: " + str(round(bfs_frac_seen, 2)))
titles.append("DFS, " + "time: " + str(round(dfs_time * 1000, 1)) + "ms, \nfrac seen: " + str(round(dfs_frac_seen, 2)))

showNPNG(grids, cmaps, titles)
