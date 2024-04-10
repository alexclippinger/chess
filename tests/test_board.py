import pytest
from board import BoardState
from pieces.pieces import Piece, Pawn, Rook, Knight, Bishop, King, Queen


def test_board_setup():
    board_state = BoardState()
    assert isinstance(board_state.board[0][0], Rook)
    assert isinstance(board_state.board[0][1], Knight)


def test_pawn_movement():
    board_state = BoardState()
    start = (6, 0)
    end = (4, 0)
    board_state.move_piece(start, end)
    assert isinstance(board_state.board[4][0], Pawn)


def test_castling():
    board = BoardState()
    board.board[7][1] = None
    board.board[7][2] = None
    board.board[7][3] = None
    board.move_piece((7, 4), (7, 2))  # Attempt to castle queenside
    assert isinstance(board.board[7][2], King), "King should be castled"
    assert isinstance(board.board[7][3], Rook), "Rook should be castled"
