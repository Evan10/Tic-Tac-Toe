import logging
import random
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
from common.utils import get_current_time


class game_instance:

    def __init__(self, players, id):
        self.players: list = players
        self.id = id
        self.TTT_game = tic_tac_toe()
        self.game_over = False
        self.chat_log = []
        self.start()

    def force_quit(self):

        msg = {
            mt.MESSAGE_TYPE: mt.END_GAME,
            mt.WINNER: mt.TIE,
            mt.POSITION: mt.BY_FORCE_QUIT,
        }
        self.to_players(msg)
        self.finish()

    def finish(self):
        for p in self.players:
            p.current_game = None
            p.in_game = False
            p.team = None
        self.game_over = True

    def start(self):
        teams = [X, O]
        for p in self.players:
            p.current_game = self
            p.in_game = True
            p.team = random.choice(teams)
            teams.remove(p.team)
            opp = [plyr for plyr in self.players if plyr.id != p.id][
                0
            ]  # TODO: make a less terrible solution to get opponent

            opp_msg = {
                mt.MESSAGE_TYPE: mt.OPPONENT_INFO,
                mt.USERNAME: opp.name,
                mt.ID: opp.id,
                mt.TEAM: X if p.team == O else O,
            }
            game_msg = {
                mt.MESSAGE_TYPE: mt.START_GAME,
                mt.TEAM: p.team,
                mt.ID: self.id,
                mt.OPPONENT_INFO: opp_msg,
            }
            self.to_player(p, game_msg)

    def handle_player_diconnect(self, id):
        # remaining player wins
        winning_player = [p for p in self.players if p.id != id][0]

        current_time = get_current_time()
        cht_msg = {
            mt.MESSAGE_TYPE: mt.CHAT_MESSAGE,
            mt.TIMESTAMP: current_time,
            mt.MESSAGE: "Opponent Disconnected",
            mt.ID: self.id,
        }
        msg = {
            mt.MESSAGE_TYPE: mt.END_GAME,
            mt.WINNER: winning_player.id,
            mt.POSITION: mt.BY_OPPONENT_DISCONNECT,
        }
        self.to_player(winning_player, cht_msg)
        self.to_player(winning_player, msg)
        self.finish()

    def handle_player_move(self, msg, id):
        player = self.find_player(id)
        position_index = msg[mt.POSITION]
        TTT_pos = TTT_position.index_to_pos(position_index)
        if player is None:
            logging.error(f"Player with id: {id} not found")
        if self.TTT_game.is_x_turn != (player.team == X):
            msg = {mt.MESSAGE_TYPE: mt.INVALID, mt.REASON: "Not your turn"}
            self.to_player(player, msg)
        elif not self.TTT_game.validate_move(TTT_pos):
            msg = {mt.MESSAGE_TYPE: mt.INVALID, mt.REASON: "Not a valid move"}
            self.to_player(player, msg)
        result = self.TTT_game.update(TTT_pos)

        if result == CONTINUE_GAME:
            msg = {
                mt.MESSAGE_TYPE: mt.GAME_MOVE,
                mt.POSITION: position_index,
                mt.ID: player.id,
            }
            self.to_players(msg)
        else:
            msg = {
                mt.MESSAGE_TYPE: mt.END_GAME,
                mt.WINNER: mt.TIE if result == TIE_GAME else id,
                mt.POSITION: position_index,
            }
            self.to_players(msg)
            self.finish()

    def handle_chat_message(self, msg, id):
        # TODO: Filter message
        sender = self.find_player(id)
        msg[mt.ID] = (
            sender.id
        )  # stops modified client from trying to change the sender id
        self.chat_log.append(msg)
        self.to_players_excluding(msg, sender)

    def from_player(self, msg, id):
        msg_type = msg[mt.MESSAGE_TYPE]
        if msg_type == mt.CLOSE_SESSION:
            self.handle_player_diconnect(id)
        elif msg_type == mt.JOIN_QUEUE or msg_type == mt.QUIT_QUEUE:
            return
        elif msg_type == mt.GAME_MOVE:
            self.handle_player_move(msg, id)
        elif msg_type == mt.CHAT_MESSAGE:
            self.handle_chat_message(msg, id)
        else:
            logging.warning(
                f"Unexpected Messsage with type: {msg_type} received: {msg}"
            )

    def find_player(self, ID):
        for player in self.players:
            if player.id == ID:
                return player
        return None

    def to_player(self, player, message):
        if player.add_to_client_queue is not None:
            player.add_to_client_queue(message)

    def to_players(self, message):
        for player in self.players:
            if player.add_to_client_queue is not None:
                player.add_to_client_queue(message)

    def to_players_excluding(self, message, excluded):
        for player in self.players:
            if player is excluded:
                continue
            if player.add_to_client_queue is not None:
                player.add_to_client_queue(message)

    def __str__(self):
        player_str = ""
        for p in self.players:
            player_str += f"[{p!s}], "
        return f"game id: {self.id}, players: {player_str}"
