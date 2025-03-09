


import pygame
from client.game_instance import game_instance
from client.gui.element import button
from common.tic_tac_toe_game import tic_tac_toe


class match_board:

    def __init__(self,match_screen):
        self.TTT_game = None
        self.game_buttons: list[button] = []
        self.setup_interactables(match_screen)


    def set_TTT_game(self, TTT_game:game_instance):
        self.TTT_game=TTT_game

    def reset_buttons(self):
        for btn in self.game_buttons:
            btn.set_disabled(False)
            btn.change_text("")

    def setup_interactables(self, match_screen):
        if len(self.game_buttons)>0:
            self.reset_buttons()
            return
        for y in range(3):
            for x in range(3):
                rect = pygame.rect.Rect(10+ x*160 , 10 + y*160, 150,150)
                index = (y*3) + x
                def b_effect(btn:button):
                    if self.TTT_game != None:
                        effect = self.TTT_game.player_move(btn.index)
                        print(effect)
                        if effect not in ("Not your turn", "Not a valid move"):
                            btn.change_text(self.TTT_game.player.team)
                            btn.set_disabled(True)
                        else:
                            match_screen.pop_up_message.set_text(effect)
                            match_screen.pop_up_message.show(1)
                        

                self.game_buttons.append(match_screen.create_button(rect, b_effect, "", index))
    
    def update_board(self):
        board = self.TTT_game.get_flattened_board()
        for btn in self.game_buttons:
            i = btn.index
            btn.change_text(board[i])
            btn.set_disabled(board[i] != "")
                