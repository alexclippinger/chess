"""
Define a piece and everything about it, including
- color
- position on the board
- legal moves
"""


class Piece:
    def __init__(self, color: str, position: tuple):
        self.color = color
        self.position = position
        self.first_move = True  # This is important for pawns, kings, and rooks

    def _append_move_if_valid(self, row, col, move_list):
        """This rule applies no matter the board state"""
        if 0 <= row <= 7 and 0 <= col <= 7:
            move_list.append((row, col))


class Pawn(Piece):

    def potential_moves(self):
        """This will include potential moves not considering board state"""
        potential_moves = []  # initiate list of potential moves
        direction = (
            -1 if self.color == "w" else 1
        )  # which direction the pieces are moving on the board
        start_row, start_col = self.position

        # Move one step forward
        self._append_move_if_valid(start_row + direction, start_col, potential_moves)

        # Move two steps forward when on the first move
        if self.first_move:
            self._append_move_if_valid(
                start_row + (2 * direction), start_col, potential_moves
            )
        # Capturing (normal captures and en-passant)
        self._append_move_if_valid(
            start_row + direction, start_col - 1, potential_moves
        )
        self._append_move_if_valid(
            start_row + direction, start_col + 1, potential_moves
        )

        return potential_moves


class Rook(Piece):

    def potential_moves(self):
        """Rooks move in straight lines"""
        potential_moves = []
        start_row, start_col = self.position  # 0-7, 0-7
        potential_rows = [row for row in range(8) if row != start_row]
        potential_cols = [col for col in range(8) if col != start_col]
        for potential_row in potential_rows:
            self._append_move_if_valid(potential_row, start_col, potential_moves)
        for potential_col in potential_cols:
            self._append_move_if_valid(start_row, potential_col, potential_moves)
        return potential_moves


class Knight(Piece):
    def potential_moves():
        potential_moves = []  # initiate list of potential moves
        #
        return


class Bishop(Piece):
    def legal_moves():
        return


class Queen(Piece):
    def legal_moves():
        return


class King(Piece):

    def potential_moves(self):
        potential_moves = []
        start_row, start_col = self.position
        # A king can move one square in any direction
        for row_move in range(-1, 2):
            for col_move in range(-1, 2):
                # potential_moves.append((start_row + row_move, start_col + col_move))
                self._append_move_if_valid(
                    start_row + row_move, start_col + col_move, potential_moves
                )
        return potential_moves
