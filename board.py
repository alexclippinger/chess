from pieces import Piece, Pawn, Rook, Knight, Bishop, King, Queen
from copy import copy


class BoardState:
    def __init__(self):
        self.board = [[None for _ in range(8)] for _ in range(8)]
        self.setup_pieces()
        self.white_to_move = True
        # TODO: will want to store chess notation to eventually download game files
        self.move_log = []
        # Game state related
        self.last_to_move = None
        self.en_passant_squares = []
        self.check_white = False
        self.check_black = False
        self.castled_rook_position = None

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

    def _get_back_rank(self, opponent=False):
        if opponent:
            back_rank = 0 if self.white_to_move else 7
        else:
            back_rank = 7 if self.white_to_move else 0
        return back_rank

    ###############
    # PAWN MOVING
    ###############

    def _is_en_passant_allowed(self, piece):
        """Check both pieces are pawns and the previous move was the pawn's first"""
        return (
            isinstance(piece, Pawn)
            and isinstance(self.last_to_move, Pawn)
            and self.last_to_move.first_move
        )

    def _get_en_passant_move(self, piece):
        if self._is_en_passant_allowed(piece):
            # Get position of current pawn and opponent pawn moved on last turn
            opp_row, opp_col = self.last_to_move.position
            piece_row, piece_col = piece.position
            direction = -1 if piece.color == "w" else 1

            if piece_row == opp_row and abs(piece_col - opp_col) == 1:
                potential_move = (piece_row + direction, opp_col)
                self.en_passant_squares.append(potential_move)
                return potential_move

    def _is_legal_pawn_move(self, piece, move):
        move_square = self.board[move[0]][move[1]]
        forward_move = piece.position[1] == move[1] and move_square is None
        diagonal_capture = (
            piece.position[1] != move[1]
            and move_square is not None
            and move_square.color != piece.color
        )
        return forward_move or diagonal_capture

    def _promote_pawn_to_queen(self, position):
        self.board[position[0]][position[1]] = Queen(self._get_color(), position)

    def _promote_pawn_if_eligible(self, piece, end):
        end_row = self._get_back_rank(opponent=True)
        if isinstance(piece, Pawn) and end[0] == end_row:
            self._promote_pawn_to_queen(end)

    ###############
    # CASTLING
    ###############

    ### Castle eligibility ###

    def _is_square_under_attack(self, position):
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece is not None and piece.color == self._get_color(opponent=True):
                    moves = self.filter_legal_moves_for_check(piece)
                    if position in moves:
                        return True
        return False

    def _is_castle_through_check(self, start, end):
        direction = 1 if end[1] > start[1] else -1
        for col in range(start[1], end[1] + direction, direction):
            if self._is_square_under_attack((start[0], col)):
                return True
        return False

    def _castle_path_is_clear(self, rook, king):
        return self._is_path_clear(
            king.position, rook.position
        ) and not self._is_castle_through_check(king.position, rook.position)

    def _king_and_queen_can_castle(self, rook, king):
        """Check that the king and rook have not moved"""
        return isinstance(rook, Rook) and rook.first_move and king.first_move

    def _check_castle_eligibility(self, rook, king):
        return self._king_and_queen_can_castle(
            rook, king
        ) and self._castle_path_is_clear(rook, king)

    def _is_castle_legal(self, king):
        in_check = self.check_white if self.white_to_move else self.check_white
        if in_check:
            return False
        row = self._get_back_rank()
        kingside_rook = self.board[row][7]
        queenside_rook = self.board[row][0]
        kingside_castle = self._check_castle_eligibility(kingside_rook, king)
        queenside_castle = self._check_castle_eligibility(queenside_rook, king)
        return kingside_castle or queenside_castle

    ### Move pieces for castling ###

    def _get_rook_positions_for_castling(self, kingside):
        row = self._get_back_rank()
        if kingside:
            start, end = (row, 7), (row, 5)
        else:
            start, end = (row, 0), (row, 3)  # Queenside rook's start and end positions
        return start, end

    def _get_king_destination_for_castling(self, kingside):
        row = self._get_back_rank()
        return (row, 6) if kingside else (row, 2)

    def _move_pieces_for_castling(self, king, end):
        if self._is_castle_legal(king):
            kingside = end[1] == 6
            queenside = end[1] == 2
            if not (kingside or queenside):
                return

            rook_start, rook_end = self._get_rook_positions_for_castling(kingside)
            rook = self.board[rook_start[0]][rook_start[1]]
            king_end = self._get_king_destination_for_castling(kingside)

            self.castled_rook_position = rook.position
            self._simulate_move(king, king_end)
            self._simulate_move(rook, rook_end)
            self._finalize_move(rook)
            self._finalize_move(king)
            self._update_game_state_after_move()

    ###############
    # LEGAL MOVES
    ###############

    ### Default tests for legal moves ###

    def _is_path_clear(self, start, end):
        """Check if all squares between a start and end square are empty"""
        start_row, start_col = start
        end_row, end_col = end
        row_step = 1 if end_row > start_row else -1 if end_row < start_row else 0
        col_step = 1 if end_col > start_col else -1 if end_col < start_col else 0

        current_row, current_col = start_row + row_step, start_col + col_step
        while (current_row, current_col) != end:
            if (
                not (0 <= current_row < 8 and 0 <= current_col < 8)
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
        if move_square is None or move_square.color != piece.color:
            return True
        return False

    ### Get piece-specific legal moves ###

    def _get_pawn_legal_moves(self, pawn):
        legal_moves = []
        for move in pawn.potential_moves():
            if (
                self._is_legal_pawn_move(pawn, move)
                and self._is_path_clear(pawn.position, move)
                and self._is_move_legal(pawn, move)
            ):
                legal_moves.append(move)
        en_passant_move = self._get_en_passant_move(pawn)
        if en_passant_move:
            legal_moves.append(en_passant_move)
        return legal_moves

    def _get_king_legal_moves(self, king):
        legal_moves = []
        for move in king.potential_moves():
            if self._is_path_clear(king.position, move) and self._is_move_legal(
                king, move
            ):
                if self._is_castle_legal(king) and abs(king.position[1] - move[1]) > 1:
                    legal_moves.append(move)
                if abs(king.position[1] - move[1]) == 1 or king.position[0] != move[0]:
                    legal_moves.append(move)
        return legal_moves

    def _get_knight_legal_moves(self, knight):
        return [
            move
            for move in knight.potential_moves()
            if self._is_move_legal(knight, move)
        ]

    def _get_default_legal_moves(self, piece):
        return [
            move
            for move in piece.potential_moves()
            if self._is_move_legal(piece, move)
            and self._is_path_clear(piece.position, move)
        ]

    def _get_legal_moves(self, piece: Piece):
        """
        Delete moves from potential_moves that are not legal
        """
        if isinstance(piece, Pawn):
            return self._get_pawn_legal_moves(piece)
        elif isinstance(piece, King):
            return self._get_king_legal_moves(piece)
        elif isinstance(piece, Knight):
            return self._get_knight_legal_moves(piece)
        else:
            return self._get_default_legal_moves(piece)

    ###############
    # CHECK
    ###############

    def _get_king_position(self, opponent_king=True):
        king_color = self._get_color(opponent_king)
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if isinstance(piece, King) and piece.color == king_color:
                    return (row, col)
        return None

    def _update_check_status(self, is_check):
        if self.white_to_move:
            self.check_black = is_check
        else:
            self.check_white = is_check

    def _search_for_check(self, opponent_king=True, simulate=False):
        """Check if the specified king is in check."""
        king_color = self._get_color(opponent_king)
        king_position = self._get_king_position(opponent_king)
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece is None or piece.color == king_color:
                    continue
                if king_position in self._get_legal_moves(piece):
                    if not simulate:
                        self._update_check_status(True)
                    return True
        if not simulate:
            self._update_check_status(False)
        return False

    def _simulate_move(self, piece: Piece, move: tuple):
        original_position = piece.position
        destination_piece = self.board[move[0]][move[1]]
        self.board[original_position[0]][original_position[1]] = None
        self.board[move[0]][move[1]] = piece
        piece.position = move
        return original_position, destination_piece

    def _revert_simulated_move(
        self, piece: Piece, original_position: tuple, destination_piece: Piece
    ):
        self.board[piece.position[0]][piece.position[1]] = destination_piece
        self.board[original_position[0]][original_position[1]] = piece
        piece.position = original_position

    def filter_legal_moves_for_check(self, piece: Piece):
        allowed_moves = []
        for move in self._get_legal_moves(piece):
            original_position, destination_piece = self._simulate_move(piece, move)
            if not self._search_for_check(opponent_king=False, simulate=True):
                allowed_moves.append(move)
            self._revert_simulated_move(piece, original_position, destination_piece)
        return allowed_moves

    ###############
    # MOVING
    ###############

    def _finalize_move(self, moving_piece):
        self.last_to_move = copy(moving_piece)
        if moving_piece.first_move:
            moving_piece.first_move = False

    def _update_game_state_after_move(self):
        self._search_for_check(opponent_king=True)
        self.white_to_move = not self.white_to_move
        self.en_passant_squares = []

    def capture_piece(self, position):
        self.board[position[0]][position[1]] = None

    def move_piece(self, start: tuple, end: tuple):
        moving_piece = self.board[start[0]][start[1]]
        if isinstance(moving_piece, King) and abs(start[1] - end[1]) > 1:
            self._move_pieces_for_castling(moving_piece, end)
        else:
            self._simulate_move(moving_piece, end)
            self._promote_pawn_if_eligible(moving_piece, end)
            self._finalize_move(moving_piece)
            self._update_game_state_after_move()
