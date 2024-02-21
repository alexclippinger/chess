from pieces import Piece, Pawn, Rook, Knight, Bishop, King, Queen


class BoardState:
    def __init__(self):
        self.board = [[None for _ in range(8)] for _ in range(8)]
        self.setup_pieces()
        self.white_to_move = True
        self.move_log = (
            []
        )  # TODO: will want to store chess notation to eventually download game files

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

    def is_square_empty(self, position: tuple):
        """Going to need something like this to define legal moves"""
        x, y = position
        return self.board[x][y] is None

    def is_path_clear(self, start, end):
        """Check if all squares between a start and end square are empty"""
        start_row, start_col = start
        end_row, end_col = end
        row_step = 1 if end_row > start_row else -1 if end_row < start_row else 0
        col_step = 1 if end_col > start_col else -1 if end_col < start_col else 0

        current_row, current_col = start_row + row_step, start_col + col_step
        while (current_row, current_col) != end:
            if self.board[current_row][current_col] is not None:
                return False
            current_row += row_step
            current_col += col_step
        return True

    def is_move_legal(self, piece, move):
        """Legal moves are initially empty squares or enemy pieces (capture)"""
        move_row, move_col = move
        move_square = self.board[move_row][move_col]
        if move_square is None:
            return True
        if move_square.color != piece.color:
            return True  # TODO: capture logic ?
        return False

    def get_legal_moves(self, piece: Piece):
        """
        Delete moves from potential_moves that are not legal
        TODO: For non-knights, pieces cannot jump both friendly or enemy pieces.
            need to break or something
        """
        # Get piece and potential moves
        potential_moves = piece.potential_moves()

        # Get list of legal moves
        legal_moves = []
        for move in potential_moves:
            if (
                self.is_path_clear(piece.position, move)
                and self.is_move_legal(piece, move)
                and not isinstance(piece, Knight)  # Knights don't need a clear path
            ):
                legal_moves.append(move)
            elif self.is_move_legal(piece, move) and isinstance(piece, Knight):
                legal_moves.append(move)

        return legal_moves

    def move_piece(self, start: tuple, end: tuple):
        """
        Moves a piece from the start position to the end position.
        Ex: Pawn e2-e4 -> Pawn row=2col=4 to row=4col=4
        """
        start_row, start_col = start
        end_row, end_col = end
        moving_piece = self.board[start_row][start_col]

        # Move the piece
        self.board[end_row][end_col] = moving_piece
        self.board[start_row][start_col] = None

        # Update the piece's position and first_move attributes
        moving_piece.position = (end_row, end_col)
        if moving_piece.first_move:
            moving_piece.first_move = False

        # Change turn
        self.white_to_move = not self.white_to_move
