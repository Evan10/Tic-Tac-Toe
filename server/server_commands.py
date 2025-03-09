CMD = "command"
ARGS = "args"


# An underscore "_" before an argument denotes it as optional

HELP = {CMD: "help", ARGS: ()}

GET_PLAYER_ID = {CMD: "get_id", ARGS: ("username",)}

KICK_PLAYER = {CMD: "kick", ARGS: ("username_or_id", "_reason")}
QUIT_GAME = {CMD: "quit_game", ARGS: ("id",)}
QUIT_SERVER = {CMD: "quit_server", ARGS: ("_reason",)}

GET_PLAYER_LIST = {CMD: "get_players", ARGS: ()}
GET_GAME_LIST = {CMD: "get_games", ARGS: ()}
GET_PLAYER_QUEUE = {CMD: "get_queue", ARGS: ()}
