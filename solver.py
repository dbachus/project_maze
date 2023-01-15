import collections
import copy
import numpy as np

import torch

from util import getPytorchDevice, draw_maze


def ca(grid, start=None, canvas=None, size_rectangles=None):
    """ start is not used in this example"""
    long_grid = grid.astype(np.long)
    tensor_grid = torch.tensor(long_grid).float().to(getPytorchDevice())
    kernel = torch.tensor([[0, 1, 0], [1, 0, 1], [0, 1, 0]]).float().to(getPytorchDevice())

    # make convolution and padd the borders with ones
    conv_grid = torch.nn.functional.conv2d(tensor_grid.unsqueeze(0).unsqueeze(0), kernel.unsqueeze(0).unsqueeze(0),
                                           padding=1).squeeze(0).squeeze(0)
    # where conv_grid >= 3, set tensor_grid to 1
    temp_grid = copy.deepcopy(tensor_grid)
    tensor_grid[conv_grid >= 3] = 1
    # while tensor_grid not equal to temp_grid
    count = 0
    # TODO problem: tensor_grid and temp_grid are the same but they shouldnt
    while not torch.equal(tensor_grid, temp_grid):
        # temp = tensor_grid
        temp_grid = copy.deepcopy(tensor_grid)
        # make convolution
        conv_grid = torch.nn.functional.conv2d(tensor_grid.unsqueeze(0).unsqueeze(0), kernel.unsqueeze(0).unsqueeze(0),
                                               padding=1).squeeze(0).squeeze(0)
        # where conv_grid >= 3, set tensor_grid to 1
        tensor_grid[conv_grid >= 3] = 1
        count += 1
        draw_maze(tensor_grid, canvas, size_rectangles)

    return count, tensor_grid


def bfs(grid, start, canvas=None, size_rectangles=None):
    height = len(grid)
    width = len(grid[0])
    queue = collections.deque()
    queue.append(start)
    seen = set([start])
    # make two dim datastructur of size of the maze to store touples of x,y coordinates
    successor = [[0 for x in range(width)] for y in range(height)]
    path = []
    while queue:
        next_step = queue.popleft()
        # print(next_step)
        y, x = next_step
        if grid[y, x] != 3 and grid[y, x] != 2:
            grid[y, x] = 4
        if grid[y][x] == 3:
            # do backtracking to find the path
            while (y, x) != start:
                if grid[y, x] != 3:
                    grid[y, x] = 5
                path.append((y, x))
                y, x = successor[y][x]
            path.append(start)
            path.reverse()
            draw_maze(grid, canvas, size_rectangles)
            return True, path, seen
        for y2, x2 in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)):  # directions
            if (0 <= x2 < width and  # X-axis in range
                    0 <= y2 < height and  # y-axis
                    grid[y2][x2] != 1 and  # not a wall
                    (y2, x2) not in seen):  # not visited
                queue.append((y2, x2))
                seen.add((y2, x2))
                successor[y2][x2] = (y, x)
                draw_maze(grid, canvas, size_rectangles)
    return False, path, seen


# function dfs
def dfs(grid, start, canvas=None, size_rectangles=None):
    height = len(grid)
    width = len(grid[0])

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
        if grid[y, x] != 3 and grid[y, x] != 2:
            grid[y, x] = 4
        if grid[y][x] == 3:
            # do backtracking to find the path
            while (y, x) != start:
                if grid[y, x] != 3:
                    grid[y, x] = 5
                path.append((y, x))
                y, x = successor[y][x]
            path.append(start)
            path.reverse()
            if canvas is not None:
                draw_maze(grid, canvas, size_rectangles)
            return True, path, seen
        for y2, x2 in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)):  # directions
            if (0 <= x2 < width and  # X-axis in range
                    0 <= y2 < height and  # y-axis
                    grid[y2][x2] != 1 and  # not a wall
                    (y2, x2) not in seen):  # not visited
                stack.append((y2, x2))
                seen.add((y2, x2))
                successor[y2][x2] = (y, x)
                if canvas is not None:
                    draw_maze(grid, canvas, size_rectangles)
    return False, path, seen
