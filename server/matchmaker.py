import logging

from common.utils import create_id
from server.game_instance import game_instance


class game_queue:

    def __init__(self):
        self.games: dict[str, game_instance] = {}
        self.player_queue = []

    def update(self):
        while len(self.player_queue) >= 2:
            id, new_game = self.create_game()
            self.games[id] = new_game
        self.games = {id: g for id, g in self.games.items() if not g.game_over}

    def add_player_to_queue(self, player):
        if not player.in_game:
            self.player_queue.append(player)
        else:
            logging.warning("Player attempted to join game queue while in a game")

    def remove_player_from_queue(self, player):
        try:
            self.player_queue.remove(player)
        except ValueError:
            logging.warning(
                "Player attempted to leave game queue when they werent in it"
            )

    def is_player_in_queue(self, player):
        return player in self.player_queue

    def get_2_players(self):
        return [self.player_queue.pop(0), self.player_queue.pop(0)]

    def create_game(self):
        players = self.get_2_players()
        game_id = create_id()
        game = game_instance(players, game_id)
        logging.info(f"New match started: {game!s} ")
        return game_id, game

    def get_game(self, id):
        return self.games.get(id, None)

    def force_quit_game(self, id):
        game: game_instance = self.games.pop(id, None)
        if game is None:
            logging.warning(f"No game with id {id} found")
            return
        game.force_quit()

    def force_quit_all_games(self):
        for game in self.games.values():
            game.force_quit()
        self.games.clear()

    def game_list_str(self):
        game_list = "Game List: \n"
        for g in self.games.values():
            game_list += f"{g!s}\n"
        return game_list

    def player_queue_list_str(self):
        player_queue_list = "Player Queue List:\n"
        for p in self.player_queue:
            player_queue_list += f"{p!s}\n"
        return player_queue_list
