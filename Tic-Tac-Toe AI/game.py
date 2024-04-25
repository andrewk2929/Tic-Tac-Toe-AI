import sys
import pygame
import numpy as np
import random
import copy
import time

from constants import *

# Human - Player 1
# AI - Player 2
# eval of -1 means AI is 100% going to win
# eval of 0 means otherwise

pygame.init()
win = pygame.display.set_mode((WIDTH, HEIGHT))
win.fill(BG_COLOR)

def menu():
    # main menu
    pygame.display.set_caption("Main Menu")

    run = True
    while run:
        player_mouse = pygame.mouse.get_pos()

        win.fill("white")

        main_menu_font = pygame.font.Font("freesansbold.ttf", 45)
        main_menu_text = main_menu_font.render("Main Menu", True, "Black")
        main_menu_rect = main_menu_text.get_rect(center = (300, 75))
        win.blit(main_menu_text, main_menu_rect)

        click_font = pygame.font.Font("freesansbold.ttf", 40)
        click_text = click_font.render("Click Any Button To Start", True, "Black")
        click_rect = click_text.get_rect(center = (300, 175))
        win.blit(click_text, click_rect)

        controls_font = pygame.font.Font("freesansbold.ttf", 25)
        controls_text = controls_font.render("Controls", True, "Black")
        controls_rect = controls_text.get_rect(center = (300, 285))
        win.blit(controls_text, controls_rect)

        g_r_controls = controls_font.render("G - Change Gamemode  R - Reset", True, "Black")
        g_r_rect = g_r_controls.get_rect(center = (300, 350))
        win.blit(g_r_controls, g_r_rect)

        zero_one_controls = controls_font.render("0 - Easy AI   1 - Hard AI", True, "Black")
        zero_one_rect = g_r_controls.get_rect(center = (300, 400))
        win.blit(zero_one_controls, zero_one_rect)

        m_controls = controls_font.render("M - Back to Main Menu", True, "Black")
        m_rect = g_r_controls.get_rect(center = (300, 450))
        win.blit(m_controls, m_rect)

        game_modes_font = pygame.font.Font("freesansbold.ttf", 15)
        default_game_mode = game_modes_font.render("Default Game Mode: Hard AI", True, "Black")
        default_rect = default_game_mode.get_rect(center = (200, 500))
        win.blit(default_game_mode, default_rect)

        other_game_mode = game_modes_font.render("Other Game Modes: Easy AI, PVP", True, "Black")
        other_rect = other_game_mode.get_rect(center = (218, 525))
        win.blit(other_game_mode, other_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()

        pygame.display.update()

class Board:
    def __init__(self):
        self.squares = np.zeros((ROWS, COLS))
        self.empty_sqrs = self.squares
        self.marked_sqrs = 0

    def final_state(self, show = False):
        '''
            return 0 if no one won yet
            return 1 if player 1 wins
            return 2 if player 2 wins
        '''

        # vertical wins
        for col in range(COLS):
            # check for win
            if self.squares[0][col] == self.squares[1][col] == self.squares[2][col] != 0:
                if show:
                    WIN_COLOR = CIR_COLOR if self.squares[0][col] == 2 else CROSS_COLOR
                    start_pos = (col * SQSIZE + SQSIZE // 2, 20)
                    end_pos = (col * SQSIZE + SQSIZE // 2, HEIGHT - 20)
                    pygame.draw.line(win, WIN_COLOR, start_pos, end_pos, LINE_WIDTH)
                return self.squares[0][col]

        # horizontal wins
        for row in range(ROWS):
            # check for win
            if self.squares[row][0] == self.squares[row][1] == self.squares[row][2] != 0:
                if show:
                    WIN_COLOR = CIR_COLOR if self.squares[row][0] == 2 else CROSS_COLOR
                    start_pos = (20, row * SQSIZE + SQSIZE // 2)
                    end_pos = (WIDTH - 20, row * SQSIZE + SQSIZE // 2)
                    pygame.draw.line(win, WIN_COLOR, start_pos, end_pos, LINE_WIDTH)
                return self.squares[row][0]

        # desc diagonal win
        # check for win
        if self.squares[0][0] == self.squares[1][1] == self.squares[2][2] != 0:
            if show:
                WIN_COLOR = CIR_COLOR if self.squares[1][1] == 2 else CROSS_COLOR
                start_pos = (20, 20)
                end_pos = (WIDTH - 20, HEIGHT - 20)
                pygame.draw.line(win, WIN_COLOR, start_pos, end_pos, LINE_WIDTH)
            return self.squares[1][1]

        # asc diagonal win
        # check for win
        if self.squares[2][0] == self.squares[1][1] == self.squares[0][2] != 0:
            if show:
                WIN_COLOR = CIR_COLOR if self.squares[1][1] == 2 else CROSS_COLOR
                start_pos = (20, HEIGHT - 20)
                end_pos = (WIDTH - 20, 20)
                pygame.draw.line(win, WIN_COLOR, start_pos, end_pos, LINE_WIDTH)
            return self.squares[1][1]

        return 0

    def mark_sqr(self, row, col, player):
        self.squares[row][col] = player
        self.marked_sqrs += 1

    def empty_sqr(self, row, col):
        return self.squares[row][col] == 0

    def get_empty_sqrs(self):
        empty_sqrs = []
        for row in range(ROWS):
            for col in range(COLS):
                if self.empty_sqr(row, col):
                    empty_sqrs.append((row, col))

        return empty_sqrs

    def is_full(self):
        return self.marked_sqrs == 9

    def is_empty(self):
        return self.empty_sqrs == 9

class AI:
    def __init__(self, level = 1, player = 2):
        self.level = level
        self.player = player

    def random(self, board):
        empty_sqrs = board.get_empty_sqrs()
        index = random.randrange(0, len(empty_sqrs))

        return empty_sqrs[index]

    def minimax(self, board, maximizing):
        case = board.final_state()

        # player 1 wins
        if case == 1:
            return 1, None

        # player 2 wins
        if case == 2:
            return -1, None

        # draw
        elif board.is_full():
            return 0, None

        if maximizing:
            # human
            max_eval = -10
            best_move = None
            empty_sqrs = board.get_empty_sqrs()

            for (row, col) in empty_sqrs:
                temp_board = copy.deepcopy(board)
                temp_board.mark_sqr(row, col, 1)
                eval = self.minimax(temp_board, False)[0]
                if eval > max_eval:
                    max_eval = eval
                    best_move = (row, col)

            return max_eval, best_move

        elif not maximizing:
            # AI
            min_eval = 10 # any number more than 1
            best_move = None
            empty_sqrs = board.get_empty_sqrs()

            for (row, col) in empty_sqrs:
                temp_board = copy.deepcopy(board)
                temp_board.mark_sqr(row, col, self.player)
                eval = self.minimax(temp_board, True)[0]
                if eval < min_eval:
                    min_eval = eval
                    best_move = (row, col)

            return min_eval, best_move


    def eval(self, main_board):
        if self.level == 0:
            # random AI
            eval = 'random'
            move = self.random(main_board)
        else:
            # minimax AI
            eval, move = self.minimax(main_board, False)

        print(f"AI has chosen to move in square position {move} with an evaluation of {eval}")

        return move

class Game:
    def __init__(self):
        self.board = Board()
        self.ai = AI()
        self.player = 1 # player_1 = cross player_2 = circle
        self.gamemode = 'ai'
        self.running = True
        self.show_lines()

    def make_move(self, row, col):
        self.board.mark_sqr(row, col, self.player)
        self.draw_fig(row, col)
        self.switch_player()

    def show_lines(self):
        # bg
        win.fill(BG_COLOR)

        # vertical
        pygame.draw.line(win, LINE_COLOR, (SQSIZE, 0), (SQSIZE, HEIGHT), LINE_WIDTH)
        pygame.draw.line(win, LINE_COLOR, (WIDTH - SQSIZE, 0), (WIDTH - SQSIZE, HEIGHT), LINE_WIDTH)

        # horizontal
        pygame.draw.line(win, LINE_COLOR, (0, SQSIZE), (WIDTH, SQSIZE), LINE_WIDTH)
        pygame.draw.line(win, LINE_COLOR, (0, HEIGHT - SQSIZE), (WIDTH, HEIGHT - SQSIZE), LINE_WIDTH)

    def draw_fig(self, row, col):
        if self.player == 1:
            # draw cross

            # desc line
            START_DESC = (col * SQSIZE + OFFSET, row * SQSIZE + OFFSET)
            END_DESC = (col * SQSIZE + SQSIZE - OFFSET, row * SQSIZE + SQSIZE - OFFSET)
            pygame.draw.line(win, CROSS_COLOR, START_DESC, END_DESC, CROSS_WIDTH)

            # asc line
            START_ASC = (col * SQSIZE + OFFSET, row * SQSIZE + SQSIZE - OFFSET)
            END_ASC = (col * SQSIZE + SQSIZE - OFFSET, row * SQSIZE + OFFSET)
            pygame.draw.line(win, CROSS_COLOR, START_ASC, END_ASC, CROSS_WIDTH)

        elif self.player == 2:
            # draw circle
            CENTER = (col * SQSIZE + SQSIZE // 2, row * SQSIZE + SQSIZE // 2)
            pygame.draw.circle(win, CIR_COLOR, CENTER, RADIUS, CIR_WIDTH)

    def switch_player(self):
        self.player = self.player % 2 + 1

    def change_gamemode(self):
        self.gamemode = 'ai' if self.gamemode == 'pvp' else 'pvp'

    def is_over(self):
        return self.board.final_state(show = True) != 0 or self.board.is_full()

    def reset(self):
        self.__init__() # calls a new game (reset)

def main():

    game = Game()
    board = game.board
    ai = game.ai

    pygame.display.set_caption("Tic Tac Toe AI")

    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                # g key - change gamemode
                if event.key == pygame.K_g:
                    game.change_gamemode()

                # r key - reset game
                if event.key == pygame.K_r:
                    game.reset()
                    board = game.board
                    ai = game.ai

                # m key - back to main menu
                if event.key == pygame.K_m:
                    menu()

                # 0 key - random ai (change ai level to 0)
                if event.key == pygame.K_0:
                    ai.level = 0

                # 1 key - ai level 1
                if event.key == pygame.K_1:
                    ai.level = 1

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                row = pos[1] // SQSIZE
                col = pos[0] // SQSIZE
                
                if board.empty_sqr(row, col) and game.running:
                    game.make_move(row, col)

                    if game.is_over():
                        game.running = False

                elif game.running == False:
                    time.sleep(1.5)
                    game_over()

        if game.gamemode == "ai" and game.player == ai.player and game.running:
            pygame.display.update()

            row, col = ai.eval(board)
            game.make_move(row, col)

            if game.is_over():
                game.running = False

        elif game.running == False:
            time.sleep(1.5)
            game_over()

        pygame.display.update()


def game_over():
    pygame.display.set_caption("Game Over")

    run = True
    while run:
        player_mouse = pygame.mouse.get_pos()

        win.fill("white")

        game_over_font = pygame.font.Font("freesansbold.ttf", 45)
        game_over_text = game_over_font.render("Game Over", True, "Black")
        game_over_rect = game_over_text.get_rect(center = (300, 75))
        win.blit(game_over_text, game_over_rect)

        controls = pygame.font.Font("freesansbold.ttf", 20)
        controls_txt = controls.render("Type r to restart or m to go back to main menu or e to exit", True, "Black")
        control_rect = controls_txt.get_rect(center = (300, 150))
        win.blit(controls_txt, control_rect)


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    main()
                if event.key == pygame.K_m:
                    menu()
                if event.key == pygame.K_e:
                    pygame.quit()
                    sys.exit()

        pygame.display.update()

if __name__ == "__main__":
    menu()