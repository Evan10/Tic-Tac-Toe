MESSAGE_SEPARATOR = "<sep>"


MESSAGE_TYPE = "Type"

START_SESSION = "Start session"
CLOSE_SESSION = "Close session"

CLIENT_INFO = "Client info"
OPPONENT_INFO = "Opponent info"

START_GAME = "Start game"
GAME_MOVE = "Game move"
END_GAME = "End game"

CHAT_MESSAGE = "Chat message"

JOIN_QUEUE = "Join queue"
QUIT_QUEUE = "Quit queue"

INVALID = "Invalid"
KICK = "kick"

USERNAME = "Username"
ID = "ID"

TEAM = "Team"

WINNER = "Winner"
# WINNER will be TIE if game is a tie
TIE = "Tie"

POSITION = "Position"
# replaces the value asosciated with the key position in message if opponent disconnects
BY_OPPONENT_DISCONNECT = "BOD"
# replaces the value asosciated with the key position in message if game is ended by server
BY_FORCE_QUIT = "BSQ"

TIMESTAMP = "Timestamp"
MESSAGE = "Message"

REASON = "Reason"

MESSAGE_DATA = {
    START_SESSION: [ID, USERNAME],
    CLOSE_SESSION: [],
    CLIENT_INFO: [USERNAME],
    OPPONENT_INFO: [USERNAME, ID, TEAM],
    START_GAME: [TEAM, ID, OPPONENT_INFO],
    GAME_MOVE: [POSITION, ID],
    END_GAME: [WINNER, POSITION],
    CHAT_MESSAGE: [TIMESTAMP, MESSAGE, ID],
    JOIN_QUEUE: [],
    QUIT_QUEUE: [],
    INVALID: [REASON],
    KICK: [REASON],
}
