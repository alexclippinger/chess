from pieces import Piece, Pawn, Rook, Knight, Bishop, King, Queen
from copy import copy


class BoardState:
    def __init__(self):
        self.board = [[None for _ in range(8)] for _ in range(8)]
        self.setup_pieces()
        self.white_to_move = True
        self.move_log = (
            []
        )  # TODO: will want to store chess notation to eventually download game files
        # Game state related
        self.last_to_move = None
        # 1. related to en passant state
        self.en_passant_squares = []
        # 2. related to check
        self.check = False
        # 3. related to checkmate
        self.checkmate = False
        # 4. related to castling
        # self.castling = False

    ###############
    # SETUP
    ###############

    def setup_pieces(self):
        for col, piece_class in enumerate(
            [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
        ):
            # black pieces
            self.board[0][col] = piece_class("b", (0, col))  # Back rank
            self.board[1][col] = Pawn("b", (1, col))
            # white pieces
            self.board[6][col] = Pawn("w", (6, col))
            self.board[7][col] = piece_class("w", (7, col))

    def _get_color(self, opponent=False):
        if opponent:
            color = "b" if self.white_to_move else "w"
        else:
            color = "w" if self.white_to_move else "b"
        return color

    def _is_square_empty(self, position: tuple):
        """Going to need something like this to define legal moves"""
        x, y = position
        return self.board[x][y] is None

    ###############
    # PAWN MOVING
    ###############

    def _get_en_passant_move(self, piece):
        # "base" cases, probably remove
        if not isinstance(piece, Pawn) and not isinstance(self.last_to_move, Pawn):
            return  # make sure both pieces are pawns
        if self.last_to_move is None or self.last_to_move.first_move is False:
            return  # make sure there is a last move and that it was the pawn's first move

        # Get position of current pawn and opponent pawn moved on last turn
        last_to_move = self.last_to_move
        opp_row, opp_col = last_to_move.position
        piece_row, piece_col = piece.position
        direction = -1 if piece.color == "w" else 1

        if piece_row == opp_row and abs(piece_col - opp_col) == 1:
            potential_move = (piece_row + (1 * direction), opp_col)
            self.en_passant_squares.append(potential_move)
            return potential_move

    def _is_legal_pawn_move(self, piece, move):
        """
        1. If same file and empty
        2. If adjacent file and capturable piece
        3. If en passant (requires knowledge of previous move)
        """
        move_square = self.board[move[0]][move[1]]
        if piece.position[1] == move[1] and move_square is None:
            return True
        if (
            piece.position[1] != move[1]
            and move_square is not None
            and move_square.color != piece.color
        ):
            return True
        return False

    ###############
    # LEGAL MOVES
    ###############

    def _is_path_clear(self, start, end):
        """Check if all squares between a start and end square are empty"""
        start_row, start_col = start
        end_row, end_col = end
        row_step = 1 if end_row > start_row else -1 if end_row < start_row else 0
        col_step = 1 if end_col > start_col else -1 if end_col < start_col else 0

        current_row, current_col = start_row + row_step, start_col + col_step
        while (current_row, current_col) != end:
            if (
                (current_row > 7 or current_row < 0)
                or (current_col > 7 or current_row < 0)
                or self.board[current_row][current_col] is not None
            ):
                return False
            current_row += row_step
            current_col += col_step
        return True

    def _is_move_legal(self, piece, move):
        """Legal moves are initially empty squares or enemy pieces (capture)"""
        move_row, move_col = move
        move_square = self.board[move_row][move_col]
        if move_square is None:
            return True
        if move_square.color != piece.color:
            return True
        return False

    def _get_legal_moves(self, piece: Piece):
        """
        Delete moves from potential_moves that are not legal
        """
        # Get piece and potential moves
        potential_moves = piece.potential_moves()

        # Get list of legal moves
        legal_moves = []
        for move in potential_moves:
            if (
                self._is_path_clear(piece.position, move)
                and self._is_move_legal(piece, move)
                and not isinstance(piece, Knight)  # Knights don't need a clear path
            ):
                if isinstance(piece, Pawn):
                    if self._is_legal_pawn_move(piece, move):
                        legal_moves.append(move)
                    en_passant = self._get_en_passant_move(piece)
                    if en_passant is not None:
                        legal_moves.append(en_passant)
                else:
                    legal_moves.append(move)
            elif self._is_move_legal(piece, move) and isinstance(piece, Knight):
                legal_moves.append(move)

        return legal_moves

    ###############
    # CHECK
    ###############

    def _search_all_pieces_for_check(self):
        """Check if the opposing king is in check"""
        current_color = self._get_color()

        # Iterate through the entire board, could be a way to cut this down
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                piece = self.board[row][col]

                # If the piece belongs to the current player, get its legal moves
                if piece is not None and piece.color == current_color:
                    legal_moves = self._get_legal_moves(piece)

                    # Check if any legal move puts the opposing king in check
                    for move_row, move_col in legal_moves:
                        target_piece = self.board[move_row][move_col]
                        if (
                            target_piece is not None
                            and isinstance(target_piece, King)
                            and target_piece.color != current_color
                        ):
                            print("Check!")
                            self.check = True
                            return  # Return when a check is found
        self.check = False

    def _simulate_move(self, piece: Piece, move: tuple):
        original_position = piece.position
        destination_piece = self.board[move[0]][move[1]]
        self.board[original_position[0]][original_position[1]] = None
        self.board[move[0]][move[1]] = piece
        return original_position, destination_piece

    def _revert_simulated_move(
        self, piece: Piece, original_position: tuple, destination_piece: Piece
    ):
        self.board[original_position[0]][original_position[1]] = piece
        piece.position = original_position
        move_position = piece.position
        self.board[move_position[0]][move_position[1]] = destination_piece

    def _is_in_check(self, color):
        return False

    def filter_legal_moves_for_check(self, piece: Piece):
        legal_moves = self._get_legal_moves(piece)
        color = self._get_color()

        if not self.check:
            return legal_moves
        allowed_moves = []
        for move in legal_moves:
            original_position, destination_piece = self._simulate_move(piece, move)
            if not self._is_in_check(color):
                allowed_moves.append(move)
            self._revert_simulated_move(piece, original_position, destination_piece)
        return allowed_moves

    ###############
    # MOVING
    ###############

    def capture_piece(self, position):
        self.board[position[0]][position[1]] = None

    def move_piece(self, start: tuple, end: tuple):
        """
        Moves a piece from the start position to the end position.
        Ex: Pawn e2-e4 -> Pawn row=2col=4 to row=4col=4
        """
        start_row, start_col = start
        end_row, end_col = end
        moving_piece = self.board[start_row][start_col]

        self.board[end_row][end_col] = moving_piece
        self.board[start_row][start_col] = None

        # Update the piece's position and first_move attributes
        moving_piece.position = (end_row, end_col)

        # We want first_move=True for one more turn for en passant
        self.last_to_move = copy(moving_piece)
        if moving_piece.first_move:
            moving_piece.first_move = False

        # Before changing turns we need to know if the opponent is now in check
        self._search_all_pieces_for_check()

        # Change turn and reset other game states
        self.white_to_move = not self.white_to_move
        self.en_passant_squares = []
