from environments.df_maze import Maze

# Maze dimensions (ncols, nrows)
nx, ny = 10, 10
maze = Maze(nx, ny)

print(maze)
maze.write_svg('maze.svg')
