import logging
import random
import time
from common.tic_tac_toe_game import (
    TTT_position,
    tic_tac_toe,
    O,
    X,
    O_WINS,
    X_WINS,
    CONTINUE_GAME,
    TIE_GAME,
)
from common import message_types as mt
from client.player import player
from client.message_handler import message_handler
from common.utils import get_current_time, validate_message


class game_instance:

    def __init__(
        self,
        id,
        msg_hndlr: message_handler,
        start_game_message,
        player: player,
        opponent: player,
    ):
        self.id = id

        self.player = player
        self.opponent = opponent

        self.players = [player, opponent]

        self.player.team = start_game_message[mt.TEAM]
        self.opponent.team = O if start_game_message[mt.TEAM] == X else X

        self.id = start_game_message[mt.ID]
        self.TTT_game = tic_tac_toe()

        self.game_over = False
        self.winner = ""
        self.chat_log = []

        self.msg_hndlr = msg_hndlr

    def handle_opponent_move(self, msg):
        position_index = msg[mt.POSITION]
        if isinstance(position_index, int):
            TTT_pos = TTT_position.index_to_pos(position_index)
            result = self.TTT_game.update(TTT_pos)
            return result

    def player_chat_message(self, message):
        # TODO: Screen message before sending
        current_time = get_current_time()
        pckt = {
            mt.MESSAGE_TYPE: mt.CHAT_MESSAGE,
            mt.MESSAGE: message,
            mt.TIMESTAMP: current_time,
            mt.ID: self.player.id,
        }
        self.add_message_to_chat_log(pckt)
        self.msg_hndlr.add_to_queue(pckt)

    def add_message_to_chat_log(self, message):
        plyr = self.get_player_from_id(message[mt.ID])
        sender = (
            plyr.name
            if plyr is not None
            else "SERVER" if message[mt.ID] == self.id else "UNKNOWN"
        )

        self.chat_log.append(
            f"{message[mt.TIMESTAMP]}::{sender} > {message[mt.MESSAGE]}"
        )

    def player_move(self, move_index):
        move = TTT_position.index_to_pos(move_index)
        if self.TTT_game.is_x_turn != (self.player.team == X):
            return "Not your turn"
        elif not self.TTT_game.validate_move(move):
            return "Not a valid move"
        result = self.TTT_game.update(move)
        msg = {
            mt.MESSAGE_TYPE: mt.GAME_MOVE,
            mt.POSITION: move_index,
            mt.ID: self.player.id,
        }
        self.msg_hndlr.add_to_queue(msg)
        return result

    def game_end(self, winner):
        self.game_over = True
        self.winner = winner

    def recieve_chat_message(self, msg):
        self.add_message_to_chat_log(msg)

    def get_player_from_id(self, id):
        for p in self.players:
            if p.id == id:
                return p
        return None

    def get_team_from_player_id(self, id):
        for p in self.players:
            if p.id == id:
                return p.team
        return None

    def from_server(self, msg):
        msg_type = msg[mt.MESSAGE_TYPE]
        if msg_type == mt.INVALID:
            return
        elif msg_type == mt.GAME_MOVE:
            self.handle_opponent_move(msg)
        elif msg_type == mt.CHAT_MESSAGE:
            self.recieve_chat_message(msg)
        elif msg_type == mt.END_GAME:
            self.handle_opponent_move(msg)
            self.game_end(msg[mt.WINNER])
        else:
            logging.warning(
                f"Unexpected Messsage with type: {msg_type} received: {msg}"
            )

    def get_flattened_board(self):
        flattened_board = []
        for row in self.TTT_game.board:
            flattened_board.extend(row)
        return flattened_board

    def to_server(self, message):
        self.msg_hndlr.add_to_queue(message)

    def __str__(self):
        return f"game id: {self.id}, Opponent: {self.opponent!s}"
