import logging
from common.utils import is_id
from server.player import player


class player_handler:

    def __init__(self):
        self.players: dict[str, player] = {}

    def update(self):
        self.players = {id: p for id, p in self.players.items() if p.connected}

    def add_player(self, id, player):
        self.players[id] = player

    async def kick_player(self, player: player, reason="Unknown Reason"):
        if player is None:
            logging.warning(
                "None was passed in when the method expected a player instance"
            )
        await player._kick_player(reason)
        del self.players[player.id]

    async def kick_player_given_identifier(self, args):
        user_identifier = args[0]
        reason = "Unknown Reason" if len(args) < 2 else args[1]
        player = None
        if is_id(user_identifier):
            player = self.players.get(user_identifier)
        else:
            try:
                player = self.find_player_using_username(user_identifier)
            except LookupError as e:
                if e.args[1] != 0:
                    message = f"Multiple users with username {user_identifier} found"
                else:
                    message = f"No player with username {user_identifier} found"
                logging.warning(message)
                return
        if player is not None:
            await self.kick_player(player, reason)
        else:
            logging.warning("Player not found")

    async def kick_all_players(self, reason="Unknown Reason"):
        for p in self.players.values():
            await p._kick_player(reason)
        del self.players
        self.players = {}

    def find_player_using_username(self, username):
        matching = [p for p in self.players.values() if p.name == username]
        if len(matching) != 1:
            raise LookupError(
                f"Expected 1 match but got {len(matching)} matches", len(matching)
            )
        return matching[0]

    def get_id_given_username(self, username):
        p = None
        try:
            p: player = self.find_player_using_username(self.players, username)
        except LookupError as e:
            if e.args[1] != 0:
                message = f"Multiple users with username {username} found"
            else:
                f"No player with username {username} found"
            logging.warning(message)
        if p != None:
            logging.info(f"Player with username {username} has ID: {p.id}")
        return p

    def get_player_list_str(self):
        player_list = "Player List: \n"
        for p in self.players.values():
            player_list += f"{p!s}\n"
        return player_list
