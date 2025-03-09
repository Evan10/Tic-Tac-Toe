BOARD_SIZE = 3
X = "X"
O = "O"

INVALID_MOVE = "Invalid move"
CONTINUE_GAME = "Continue"
TIE_GAME = "Tie"
X_WINS = "X win"
O_WINS = "Y win"


class TTT_position:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.validate()

    def validate(self):
        assert (
            self.x >= 0 and self.x < BOARD_SIZE and self.y >= 0 and self.y < BOARD_SIZE
        ), "invalid Tic Tac Toe position provided"

    @staticmethod
    def index_to_pos(i):
        """
        returns TTT_position based off of this shape
        0 | 1 | 2
        ---------
        3 | 4 | 5
        ---------
        6 | 7 | 8
        so an input of 3 would return (0,1)
        """
        try:
            pos = TTT_position(i % 3, i // 3)
        except AssertionError:
            return None
        return pos

    @staticmethod
    def pos_to_index(pos):
        """
        returns index based off of this shape
        0 | 1 | 2
        ---------
        3 | 4 | 5
        ---------
        6 | 7 | 8
        so an input of (0,1) would return 3
        """
        return pos.x + pos.y * 3

    def __repr__(self):
        return f"TTT_position({self.x},{self.y})"

    def __str__(self):
        return f"({self.x},{self.y})"


class tic_tac_toe:
    """
    core game logic for Tic Tac Toe game

    """

    def __init__(self):
        self.board = [["" for x in range(BOARD_SIZE)] for y in range(BOARD_SIZE)]
        self.is_x_turn = True
        self.event_stack = []
        self.player_moves = 0

    def update(self, pos: TTT_position):
        """
        returns INVALID_MOVE if the move wasn't valid and returns check_game_end's return value
        """
        if not self.validate_move(pos):
            return INVALID_MOVE
        player = X if self.is_x_turn else O
        self.board[pos.y][pos.x] = player

        self.event_stack.append(
            {
                "player": player,
                "index": pos.pos_to_index(pos),
                "move_number": self.player_moves,
            }
        )

        self.player_moves += 1
        self.is_x_turn = not self.is_x_turn
        return self.check_game_end()

    def get_board_pos(self, pos: TTT_position):
        return self.board[pos.y][pos.x]

    def validate_move(self, pos: TTT_position):
        return self.board[pos.y][pos.x] == ""

    def undo(self, turns):
        turns = turns if turns < len(self.event_stack) else len(self.event_stack)
        for i in range(turns):
            last_move = self.event_stack.pop()
            self.player_moves = last_move["move_number"]
            pos = TTT_position.index_to_pos(last_move["index"])
            self.board[pos.y][pos.x] = ""
            self.is_x_turn = last_move["player"] == X

    WIN_SHAPES = (
        (0, 1, 2),
        (3, 4, 5),
        (6, 7, 8),
        (0, 3, 6),
        (1, 4, 7),
        (2, 5, 8),
        (0, 4, 8),
        (2, 4, 6),
    )

    def check_game_end(self):
        """
        returns CONTINUE_GAME if not over, TIE_GAME if a tie, and X_WINS or O_WINS respectively for a winner
        """
        empty_space = False
        for shape in tic_tac_toe.WIN_SHAPES:
            locations = [
                self.get_board_pos(TTT_position.index_to_pos(i)) for i in shape
            ]
            if "" in locations:
                empty_space = True
            first = locations[0]
            if first == "":
                continue
            is_match = True
            for l in locations[1:]:
                if first != l:
                    is_match = False
                    break
            if is_match:
                return X_WINS if first == X else O_WINS
        return CONTINUE_GAME if empty_space else TIE_GAME

    def __str__(self):
        s = " | ".join(self.board[0])
        for r in self.board[1:]:
            s += f"\n -------- \n"
            s += " | ".join(r)
        return s
