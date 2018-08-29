import pygame
import os
import grid_object as grid_o
import minesweeper_constants as const

import debugger

class GameManager(object):
    def __init__(self):
        pygame.init()

        self.my_path = "%s/.." % os.path.dirname(os.path.realpath(__file__))

        logo = pygame.image.load("%s/img/minesweeper_logo.png" % self.my_path)
        pygame.display.set_icon(logo)

        pygame.display.set_caption("Minesweeper")

        self.screen = pygame.display.set_mode((const.WIDTH, const.HEIGHT))

        self.background_tex = pygame.image.load("%s/img/background.png" % self.my_path)
        self.cell_textures = [
            pygame.image.load("%s/img/cell/cell_hidden.png" % self.my_path),
            pygame.image.load("%s/img/cell/cell_revealed.png" % self.my_path),
            pygame.image.load("%s/img/cell/mine.png" % self.my_path),
            pygame.image.load("%s/img/cell/mine_red.png" % self.my_path),
            pygame.image.load("%s/img/cell/flag.png" % self.my_path)
        ]
        self.number_tex_list   = [
            pygame.image.load("%s/img/numbers/num_1.png" % self.my_path),
            pygame.image.load("%s/img/numbers/num_2.png" % self.my_path),
            pygame.image.load("%s/img/numbers/num_3.png" % self.my_path),
            pygame.image.load("%s/img/numbers/num_4.png" % self.my_path),
            pygame.image.load("%s/img/numbers/num_5.png" % self.my_path),
            pygame.image.load("%s/img/numbers/num_6.png" % self.my_path),
            pygame.image.load("%s/img/numbers/num_7.png" % self.my_path),
            pygame.image.load("%s/img/numbers/num_8.png" % self.my_path)
        ]
        self.restart_button_list = [
            pygame.image.load("%s/img/restart_button/restart_button_green.png" % self.my_path),
            pygame.image.load("%s/img/restart_button/restart_button_yellow.png" % self.my_path),
            pygame.image.load("%s/img/restart_button/restart_button_red.png" % self.my_path),
            pygame.image.load("%s/img/restart_button/restart_button_green_clicked.png" % self.my_path),
            pygame.image.load("%s/img/restart_button/restart_button_yellow_clicked.png" % self.my_path),
            pygame.image.load("%s/img/restart_button/restart_button_red_clicked.png" % self.my_path)
        ]
        self.restart_button_rect = pygame.Rect(const.RESTART_BUTTON_COORD, const.RESTART_BUTTON_SIZE)

        self.ui_font = pygame.font.SysFont("monogame", 25, True)

        ##################
        # This part should match restart_game()
        self.grid = grid_o.Grid(self.cell_textures, self.number_tex_list)
        self.is_alive = True
        self.mines_placed = False
        self.mines_flagged = 0
        self.restart_button_state = 0
        ##################

        # For input
        self.left_mouse_held = False
        self.last_left_click = 0
        self.right_mouse_held = False
        self.last_cell_held = None

        self.debug = debugger.Debugger("debug.log")

    def play_game(self):
        self.mines_placed = False
        running = True
        while running:
            self.draw_game()
            input_exit_code = self.handle_input()
            if input_exit_code == -1:
                running = False
            elif input_exit_code == 1:
                self.restart_game()

    def restart_game(self):
        self.grid = grid_o.Grid(self.cell_textures, self.number_tex_list)
        self.is_alive = True
        self.mines_placed = False
        self.mines_flagged = 0
        self.restart_button_state = 0

    def handle_input(self):
        mouse_button_state = pygame.mouse.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        mouse_released = False
        if mouse_button_state[0] and not self.left_mouse_held:
            self.left_mouse_held = True
        elif not mouse_button_state[0] and self.left_mouse_held:
            self.left_mouse_held = False
            mouse_released = True

        if self.left_mouse_held and self.restart_button_rect.collidepoint(mouse_pos) and self.restart_button_state < 3:
            self.restart_button_state += 3
        if mouse_released and self.restart_button_rect.collidepoint(mouse_pos):
            return 1
        if self.last_cell_held:
            self.last_cell_held.held = False
        clicked_cell = self.grid.get_clicked_cell(mouse_pos)
        if self.restart_button_state == 1:
            self.restart_button_state = 0
        if self.left_mouse_held and clicked_cell and not clicked_cell.is_revealed:
            clicked_cell.held = True
            self.last_cell_held = clicked_cell
            if self.is_alive and not clicked_cell.flagged:
                self.restart_button_state = 1
        elif mouse_released or mouse_button_state[2]:
            if clicked_cell and self.is_alive:
                double_click = False
                if mouse_released:
                    now = pygame.time.get_ticks()
                    if now - self.last_left_click < const.DOUBLE_CLICK_TIME:
                        double_click = True
                    self.last_left_click = now
                if not self.mines_placed:
                    self.grid.place_mines(const.MINE_COUNT, clicked_cell.idx, const.EMPTY_RADIUS)
                    self.mines_placed = True
                if (mouse_released and not clicked_cell.flagged) or (mouse_button_state[2] and not self.right_mouse_held):
                    self.right_mouse_held = True
                    clicked_exit_code = clicked_cell.clicked(mouse_released, double_click)
                    if clicked_exit_code == 1:
                        self.mines_flagged += 1
                    elif clicked_exit_code == -1:
                        self.mines_flagged -= 1
                    elif clicked_exit_code == -2:
                        self.player_dies(clicked_cell)
                    elif clicked_exit_code == -3:
                        self.player_dies(clicked_cell.exploded_mine)

        elif not mouse_button_state[2] and self.right_mouse_held:
            self.right_mouse_held = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return -1
            #if event.type == pygame.KEYDOWN:
            #    if event.key == pygame.K_d:
            #        if clicked_cell:
            #            self.debug.write("Is flagged: %s\n" % str(clicked_cell.flagged))


    def player_dies(self, clicked_mine_cell):
        self.is_alive = False
        self.grid.reveal_all_mines()
        self.restart_button_state = 2
        clicked_mine_cell.highlight = True

    def draw_game(self):
        self.screen.blit(self.background_tex, (0,0))
        self.screen.blit(self.restart_button_list[self.restart_button_state], self.restart_button_rect.topleft)
        self.grid.draw(self.screen)
        self.draw_ui()
        pygame.display.flip()

    def draw_ui(self):
        mines_left_label = self.ui_font.render("%d" % (const.MINE_COUNT - self.mines_flagged), 1, (250, 104, 99))
        self.screen.blit(mines_left_label, const.MINES_LEFT_LABEL_POS)