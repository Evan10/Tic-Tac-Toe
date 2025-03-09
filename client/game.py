import pygame

from client.player import player
from client.gui.gui_handler import gui_handler
from client.message_handler import message_handler
import common.message_types as mt
from client.game_instance import game_instance
from client import consts
from client.gui.game_screen import disconnected_screen, main_menu_screen, match_screen
from common.utils import is_id


class game:

    def __init__(self, msg_hdnlr):

        pygame.init()

        self.player = None
        self.msg_hdnlr: message_handler = msg_hdnlr
        self.gui_hndlr = gui_handler(self)

        self.match_init_info = None
        self.current_opponent = None
        self.current_match: game_instance = None

    def loop(self):

        pygame.register_quit(self.msg_hdnlr.close)
        window: pygame.Surface = pygame.display.set_mode(
            (consts.WINDOW_DIMENSIONS["width"], consts.WINDOW_DIMENSIONS["height"])
        )
        pygame.display.set_caption("Tic Tac Toe Client")

        clock = pygame.time.Clock()
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type in (
                    pygame.MOUSEBUTTONDOWN,
                    pygame.MOUSEBUTTONUP,
                    pygame.KEYDOWN,
                ):
                    self.gui_hndlr.handle_event(event)
            self.handle_messages()
            self.gui_hndlr.draw(window)
            pygame.display.flip()
            clock.tick(consts.FRAME_RATE)
        pygame.quit()

    def init_player(self, name, id):
        self.player = player(id, name)

    def handle_messages(self):
        messages = self.msg_hdnlr.get_messages()
        for message in messages:
            self.handle_msg(message)

    def handle_msg(self, message):
        msg_type = message[mt.MESSAGE_TYPE]
        if msg_type == mt.KICK:
            self.on_disconnect(message)
            return
        elif msg_type == mt.START_SESSION:
            self.init_player(message[mt.USERNAME], message[mt.ID])
            self.switch_current_screen(main_menu_screen.SCREEN_NAME)
        elif msg_type == mt.START_GAME:

            opp_info = message[mt.OPPONENT_INFO]
            self.current_opponent = player(opp_info[mt.ID], opp_info[mt.USERNAME])
            self.current_opponent.team = opp_info[mt.TEAM]
            self.current_match = self.start_match(message)

        elif msg_type in (mt.GAME_MOVE, mt.CHAT_MESSAGE, mt.END_GAME, mt.INVALID):
            if self.current_match is not None:
                self.current_match.from_server(message)
            self.update_match_gui(msg_type, message)

    def switch_current_screen(self, screen_name):
        self.gui_hndlr.switch_screen(screen_name)

    def on_disconnect(self, message):
        dscnntd_scrn: disconnected_screen = self.gui_hndlr.get_screen(
            disconnected_screen.SCREEN_NAME
        )

        dscnntd_scrn.set_reason(message[mt.REASON])
        self.switch_current_screen(disconnected_screen.SCREEN_NAME)

    def update_match_gui(self, msg_type, message):
        mtch_scrn: match_screen = self.gui_hndlr.get_screen(match_screen.SCREEN_NAME)
        mtch_scrn.tic_tac_toe_board.update_board()
        mtch_scrn.update_chat_element()
        mtch_scrn.update_move_log()
        if msg_type == mt.END_GAME:
            winner = message[mt.WINNER]
            print(f"Winner ID: {winner}")
            if is_id(winner):
                winning_player = self.current_match.get_player_from_id(winner)
                mtch_scrn.trigger_game_over_message(f"{winning_player.name} wins!")
            else:
                mtch_scrn.trigger_game_over_message(winner)

    def send_client_info(self, username):
        msg = {mt.MESSAGE_TYPE: mt.CLIENT_INFO, mt.USERNAME: username}
        self.msg_hdnlr.add_to_queue(msg)

    def start_match(self, message):
        gm_instnc = game_instance(
            message[mt.ID], self.msg_hdnlr, message, self.player, self.current_opponent
        )
        mtch_scrn: match_screen = self.gui_hndlr.get_screen(match_screen.SCREEN_NAME)
        if mtch_scrn is not None:
            mtch_scrn.set_current_match(gm_instnc)
            self.gui_hndlr.switch_screen(match_screen.SCREEN_NAME)
        return gm_instnc

    def clear_current_game(self):
        self.match_init_info = None
        self.current_opponent = None
        self.current_match: game_instance = None

    def join_game_queue(self):
        msg = {mt.MESSAGE_TYPE: mt.JOIN_QUEUE}
        self.msg_hdnlr.add_to_queue(msg)

    def leave_game_queue(self):
        msg = {mt.MESSAGE_TYPE: mt.QUIT_QUEUE}
        self.msg_hdnlr.add_to_queue(msg)
