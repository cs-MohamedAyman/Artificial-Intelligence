from random import *

def same_col_indexes(grid, i, j, N, itself=True):
    sub_grid_column = i % N
    cell_column = j % N
    for a in range(sub_grid_column, len(grid), N):
        for b in range(cell_column, len(grid), N):
            if (a, b) == (i, j) and not itself:
                continue
            yield (a, b)

def same_row_indexes(grid, i, j, N, itself=True):   
    sub_grid_row = int(i / N)
    cell_row = int(j / N)
    for a in range(sub_grid_row * N, sub_grid_row * N + N):
        for b in range(cell_row * N, cell_row * N + N):
            if (a, b) == (i, j) and not itself:
                continue
            yield (a, b)

def get_cells_from_indexes(grid, indexes):
    for a, b in indexes:
        yield grid[a][b]

def solve(grid, population_size=1000, selection_rate=0.5, max_generations_count=1000, mutation_rate=0.05):
    # square root of the problem grid's size
    N = int(len(grid) ** .5)

    def empty_grid(elem_gen=None):
        res = []
        for i in range(len(grid)):
            row = []
            for j in range(len(grid)):
                row += [(None if elem_gen is None else elem_gen(i, j))]
            res += [row]
        return res

    # this is done to avoid changes in the input argument
    grid = empty_grid(lambda i, j: grid[i][j])

    def same_sub_grid_indexes(i, j, itself=True):
        for k in range(len(grid)):
            if k == j and not itself:
                continue
            yield (i, k)

    def pencil_mark(track_grid, i, j):
        # remove from same sub-grid cells
        for a, b in same_sub_grid_indexes(i, j, itself=False):
            if track_grid[a][b] is not None and grid[i][j] in track_grid[a][b]:
                track_grid[a][b].remove(grid[i][j])
        # remove from same row cells
        for a, b in same_row_indexes(grid, i, j, N, itself=False):
            if track_grid[a][b] is not None and grid[i][j] in track_grid[a][b]:
                track_grid[a][b].remove(grid[i][j])
        # remove from same column cells
        for a, b in same_col_indexes(grid, i, j, N, itself=False):
            if track_grid[a][b] is not None and grid[i][j] in track_grid[a][b]:
                track_grid[a][b].remove(grid[i][j])

    def fill_predetermined_cells():
        track_grid = empty_grid(lambda *args: [val for val in range(1, len(grid) + 1)])
        for i in range(len(grid)):
            for j in range(len(grid)):
                if grid[i][j] is not None:
                    pencil_mark(track_grid, i, j)
        while True:
            anything_changed = False
            for i in range(len(grid)):
                for j in range(len(grid)):
                    if track_grid[i][j] is None:
                        continue
                    if len(track_grid[i][j]) == 0:
                        raise Exception('The puzzle is not solvable.')
                    elif len(track_grid[i][j]) == 1:
                        grid[i][j] = track_grid[i][j][0]
                        pencil_mark(track_grid, i, j)
                        track_grid[i][j] = None
                        anything_changed = True
            if not anything_changed:
                break
        return grid

    def generate_initial_population():
        cands = []
        for k in range(population_size):
            cand = empty_grid()
            for i in range(len(grid)):
                shuff_sub_grid = [n for n in range(1, len(grid) + 1)]
                shuffle(shuff_sub_grid)
                for j in range(len(grid)):
                    if grid[i][j] is not None:
                        cand[i][j] = grid[i][j]
                        shuff_sub_grid.remove(grid[i][j])
                for j in range(len(grid)):
                    if cand[i][j] is None:
                        cand[i][j] = shuff_sub_grid.pop()
            cands.append(cand)
        return cands

    def fitness(grid):
        row_duplic_count = 0
        # calculate rows duplicates
        for a, b in same_col_indexes(grid, 0, 0, N):
            row = list(get_cells_from_indexes(grid, same_row_indexes(grid, a, b, N)))
            row_duplic_count += len(row) - len(set(row))
        return row_duplic_count

    def selection(cands):
        index_fitness = []
        for i in range(len(cands)):
            index_fitness.append(tuple([i, fitness(cands[i])]))
        index_fitness.sort(key=lambda elem: elem[1])
        selected_part = index_fitness[0: int(len(index_fitness) * selection_rate)]
        indexes = [e[0] for e in selected_part]
        return [cands[i] for i in indexes], selected_part[0][1]

    fill_predetermined_cells()
    popul = generate_initial_population()
    best_fitness = None
    for i in range(max_generations_count):
        popul, best_fitness = selection(popul)
        if i == max_generations_count - 1 or fitness(popul[0]) == 0:
            break
        shuffle(popul)
        new_popul = []
        new_popul = popul.pop()
        new_popul = popul.pop()
        # mutation
        for cand in new_popul[:int(len(new_popul) * mutation_rate)]:
            rand_sub_grid = randint(0, 8)
            possible_swaps = []
            for grid_ele_idx in range(len(grid)):
                if grid[rand_sub_grid][grid_ele_idx] is None:
                    possible_swaps.append(grid_ele_idx)
            if len(possible_swaps) > 1:
                shuffle(possible_swaps)
                first_index = possible_swaps.pop()
                second_index = possible_swaps.pop()
                tmp = cand[rand_sub_grid][first_index]
                cand[rand_sub_grid][first_index] = cand[rand_sub_grid][second_index]
                cand[rand_sub_grid][second_index] = tmp
        while True:
            sol_1 = popul.pop()
            sol_2 = popul.pop()
            cross_pnt = randint(0, len(grid) - 2)
            sol_1[cross_pnt], sol_2[cross_pnt+1] = sol_2[cross_pnt+1], sol_1[cross_pnt]
            new_popul += [sol_1, sol_2]
        popul.extend(new_popul)
    return popul[0], best_fitness

content = ''
content += '0 3 0 0 8 0 7 0 0\n'
content += '0 7 1 2 0 0 0 6 9\n'
content += '0 5 6 9 0 4 0 0 1\n'
content += '4 0 9 0 6 0 1 0 5\n'
content += '0 0 0 0 5 9 3 2 0\n'
content += '3 8 0 0 0 7 0 4 6\n'
content += '0 9 8 3 0 0 2 0 0\n'
content += '6 0 3 0 0 0 0 8 4\n'
content += '7 0 2 5 1 0 0 9 0'
print("content\n" + content + '\n')

lines = content.split('\n')
grid = [[] for i in range(len(lines))]
sqrt_n = int(len(lines) ** .5)
for j in range(len(lines)):
    line_values = [int(value) for value in lines[j].split()]
    for i in range(len(line_values)):
        grid[i // sqrt_n + j // sqrt_n * sqrt_n].append(line_values[i])

solution, best_fitness = solve(grid)
print("Best fitness value:", best_fitness)
output_str = ''
for a, b in same_col_indexes(solution, 0, 0, sqrt_n):
    row = list(get_cells_from_indexes(solution, same_row_indexes(solution, a, b, sqrt_n)))
    output_str += " ".join(map(str, row)) + '\n'
print(output_str[:])
