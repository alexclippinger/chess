class Piece:
    def __init__(self, color: str, position: tuple):
        self.color = color
        self.position = position
        self.first_move = True  # This is important for pawns, kings, and rooks

    def _valid_move(self, row, col):
        if 0 <= row <= 7 and 0 <= col <= 7:
            return True
        return False

    def _append_move_if_valid(self, row, col, move_list):
        """This rule applies no matter the board state"""
        if self._valid_move(row, col):
            move_list.append((row, col))

    def _straight_moves(self):
        potential_moves = []
        start_row, start_col = self.position  # 0-7, 0-7
        potential_rows = [row for row in range(8) if row != start_row]
        potential_cols = [col for col in range(8) if col != start_col]
        for potential_row in potential_rows:
            self._append_move_if_valid(potential_row, start_col, potential_moves)
        for potential_col in potential_cols:
            self._append_move_if_valid(start_row, potential_col, potential_moves)
        return potential_moves

    def _diagonal_moves(self):
        potential_moves = []
        start_row, start_col = self.position

        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        for direction in directions:
            for step in range(1, 8):
                move_row = start_row + step * direction[0]
                move_col = start_col + step * direction[1]
                if not self._valid_move(move_row, move_col):
                    break
                self._append_move_if_valid(move_row, move_col, potential_moves)
        return potential_moves


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
        return self._straight_moves()


class Knight(Piece):
    def potential_moves(self):
        potential_moves = []
        start_row, start_col = self.position

        knight_steps = [-2, -1, 1, 2]
        move_combos = [
            (i, j) for i in knight_steps for j in knight_steps if abs(i) != abs(j)
        ]

        for move in move_combos:
            move_row = start_row + move[0]
            move_col = start_col + move[1]
            self._append_move_if_valid(move_row, move_col, potential_moves)

        return potential_moves


class Bishop(Piece):
    def potential_moves(self):
        """Bishops move in diagonal lines"""
        return self._diagonal_moves()


class Queen(Piece):
    def potential_moves(self):
        return self._straight_moves() + self._diagonal_moves()


class King(Piece):

    def potential_moves(self):
        potential_moves = []
        start_row, start_col = self.position
        # A king can move one square in any direction
        for row_move in range(-1, 2):
            for col_move in range(-1, 2):
                self._append_move_if_valid(
                    start_row + row_move, start_col + col_move, potential_moves
                )
        # A king can castle
        if self.first_move:
            row, col = self.position
            potential_moves.extend([(row, col + 2), (row, col - 2)])
        return potential_moves
