import random
import pygame

# Width of play arena
WIDTH = 1185
# Height of play arena
HEIGHT = 720

CELLSIZE = 35
GRID_DIM = (32, 16)
GRID_START_COORD = (32, 127)
MINE_COUNT = 128
EMPTY_RADIUS = 3

class Cell(pygame.Rect):
    def __init__(self, left, top, width, height, textures, idx, grid):
        pygame.Rect.__init__(self, left, top, width, height)
        self.hidden_tex   = textures[0]
        self.revealed_tex = textures[1]
        self.mine_tex     = textures[2]
        self.number_tex   = None
        self.idx = idx
        self.grid = grid
        self.is_revealed = False
        self.is_mine = False
        self.number = -1

    def place_mine(self):
        self.is_mine = True

    def set_num(self, number, number_tex):
        self.number = number
        if number > 0:
            self.number_tex = number_tex

    def clicked(self, leftclick):
        if leftclick: # left click
            if self.is_revealed:
                pass
            else:
                return self.reveal(True)
        else: # right click
            pass # TODO: Place flag

    def reveal(self, player_click, seen=[]):
        if self.is_mine and player_click:
            self.is_revealed = True
            return 1
        elif self.is_mine:
            return 0
        elif self.number > 0:
            self.is_revealed = True
            return 0
        self.is_revealed = True
        seen.append(self.idx)
        for i in range(self.idx[0]-1, self.idx[0]+2):
            for j in range(self.idx[1]-1, self.idx[1]+2):
                if not (i < 0 or i > GRID_DIM[1]-1 or j < 0 or j > GRID_DIM[0]-1) \
                and (i,j) not in seen:
                    self.grid.cells[i][j].reveal(False, seen)
                    seen.append((i,j))
        return 0

    def draw(self, screen):
        if self.is_revealed:
            screen.blit(self.revealed_tex, self.topleft)
            if self.is_mine:
                screen.blit(self.mine_tex, self.topleft)
            elif self.number > 0:
                screen.blit(self.number_tex, self.topleft)
        else:
            screen.blit(self.hidden_tex, self.topleft)


class Grid(object):
    def __init__(self, cell_textures, number_tex_list):
        self.cells = []
        self.cell_textures = cell_textures
        self.number_tex_list = number_tex_list
        self.create_grid()

    def create_grid(self):
        self.cells = []
        pos = GRID_START_COORD
        for i in range(GRID_DIM[1]):
            row = []
            for j in range(GRID_DIM[0]):
                new_cell = Cell(pos[0], pos[1], CELLSIZE, CELLSIZE, self.cell_textures, (i,j), self)
                row.append(new_cell)
                pos = (pos[0]+CELLSIZE, pos[1])
            self.cells.append(row)
            pos = (GRID_START_COORD[0], pos[1] + CELLSIZE)

    def place_mines(self, mine_amount, first_click_idx, empty_radius):
        """ Place mines is called after first click so the player never clicks a mine on first click.
            There is also some radius of empty cells from the players first click """
        remaining_positions = []
        for i in range(GRID_DIM[1]):
            for j in range(GRID_DIM[0]):
                dist_from_click = max(first_click_idx[0], i) - min(first_click_idx[0], i)\
                                + max(first_click_idx[1], j) - min(first_click_idx[1], j)
                if dist_from_click > empty_radius:
                    remaining_positions.append((i,j))
        if mine_amount >= len(remaining_positions):
            print("Too many mines!!")
            mine_amount = remaining_positions
        while mine_amount > 0:
            rand_idx = random.randint(0, len(remaining_positions)-1)
            rand_pos = remaining_positions[rand_idx]
            del remaining_positions[rand_idx]
            self.cells[rand_pos[0]][rand_pos[1]].place_mine()
            mine_amount -= 1

        self.distribute_numbers()

    def distribute_numbers(self):
        for i in range(GRID_DIM[1]):
            for j in range(GRID_DIM[0]):
                if self.cells[i][j].is_mine:
                    continue
                num = self.get_cell_minecount(i, j)
                self.cells[i][j].set_num(num, self.number_tex_list[num-1])

    def get_cell_minecount(self, row, col):
        count = 0
        for i in range(row-1, row+2):
            for j in range(col-1, col+2):
                if i < 0 or i > GRID_DIM[1]-1 or j < 0 or j > GRID_DIM[0]-1:
                    continue
                if self.cells[i][j].is_mine:
                    count += 1
        return count

    def get_clicked_cell(self, click_pos):
        for i in range(GRID_DIM[1]):
            for j in range(GRID_DIM[0]):
                if self.cells[i][j].collidepoint(click_pos):
                    return self.cells[i][j]
        return None

    def draw(self, screen):
        for i in range(GRID_DIM[1]):
            for j in range(GRID_DIM[0]):
                self.cells[i][j].draw(screen)

class GameManager(object):
    def __init__(self):
        pygame.init()

        logo = pygame.image.load("img/minesweeper_logo.png")
        pygame.display.set_icon(logo)

        pygame.display.set_caption("Minesweeper")

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))

        self.background_tex    = pygame.image.load("img/background.png")
        self.cell_textures = [
            pygame.image.load("img/cell_hidden.png"),
            pygame.image.load("img/cell_revealed.png"),
            pygame.image.load("img/mine.png")
        ]
        self.number_tex_list   = [
            pygame.image.load("img/numbers/num_1.png"),
            pygame.image.load("img/numbers/num_2.png"),
            pygame.image.load("img/numbers/num_3.png"),
            pygame.image.load("img/numbers/num_4.png"),
            pygame.image.load("img/numbers/num_5.png"),
            pygame.image.load("img/numbers/num_6.png"),
            pygame.image.load("img/numbers/num_7.png"),
            pygame.image.load("img/numbers/num_8.png")
        ]
        self.restart_button_list = [
            pygame.image.load("img/restart_button_green.png"),
            pygame.image.load("img/restart_button_yellow.png"),
            pygame.image.load("img/restart_button_red.png"),
        ]

        self.grid = Grid(self.cell_textures, self.number_tex_list)
        self.is_alive = True

    def play_game(self):
        mines_placed = False
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return -1
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_button_state = pygame.mouse.get_pressed()
                    click_pos = pygame.mouse.get_pos()
                    if mouse_button_state[0] or mouse_button_state[1]:
                        clicked_cell = self.grid.get_clicked_cell(click_pos)
                        if clicked_cell:
                            if not mines_placed:
                                self.grid.place_mines(MINE_COUNT, clicked_cell.idx, EMPTY_RADIUS)
                                mines_placed = True
                            if clicked_cell.clicked(mouse_button_state[0]) == 1:
                                self.is_alive = False

            self.screen.blit(self.background_tex, (0,0))
            self.grid.draw(self.screen)
            pygame.display.flip()

def main():
    gamemanager = GameManager()
    gamemanager.play_game()

if __name__ == "__main__":
    main()