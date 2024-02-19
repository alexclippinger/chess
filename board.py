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
            move_row, move_col = move
            move_square = self.board[move_row][move_col]
            if move_square is None:
                legal_moves.append(move)
            elif move_square.color != piece.color and move_square is not None:
                # TODO self.board.capture_piece()
                # TODO self.capture_piece_visual()
                legal_moves.append(move)
            else:
                continue

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
