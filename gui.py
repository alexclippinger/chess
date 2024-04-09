import tkinter as tk
from PIL import Image, ImageTk
from board import BoardState


class ChessGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.board_state = BoardState()  # BoardState class manages the game state
        self.width = self.height = 1024
        # Floor division to make sure piece fits in square
        self.square_side = self.width // 8
        self.squares = {}
        self.piece_images = {}  # Cache for loaded piece images
        self.piece_img_locations = {}
        self.cur_highlighted = None
        self.legal_move_circles = []
        self.legal_moves = []
        self.init_ui()

    def init_ui(self):
        # All of this is involved with setting up the game
        self.root.title("Chess")
        self.canvas = tk.Canvas(self.root, width=self.width, height=self.height)
        self.canvas.pack()
        self.draw_board()
        self.load_piece_images()  # Caches the piece images
        self.setup_pieces()

        # This is involved with playing the game
        # Button-1 is left mouse, so left mouse selects a square containing a piece
        self.canvas.bind("<Button-1>", self.select_and_move_piece)
        self.root.mainloop()

    ###############
    # DEBUGGING
    ###############

    def print_debug_board(self):
        # debugging
        for inner_list in self.board_state.board:
            print(
                [
                    obj.__class__.__name__ if obj is not None else "    "
                    for obj in inner_list
                ]
            )
        print("---------------------------------------")
        print(f"White to move: {self.board_state.white_to_move}")
        print(f"White in check: {self.board_state.check_white}")
        print(f"Black in check: {self.board_state.check_black}")

    ###############
    # BOARD SETUP
    ###############

    def draw_board(self):
        """Draws an 8x8 board"""
        for row in range(8):
            color = "white" if row % 2 == 0 else "gray"  # Start with white
            for col in range(8):
                x1 = col * self.square_side
                y1 = row * self.square_side
                x2 = x1 + self.square_side
                y2 = y1 + self.square_side
                square = self.canvas.create_rectangle(
                    x1, y1, x2, y2, fill=color, outline="black", width=1, tags="area"
                )
                self.squares[(row, col)] = square
                color = "gray" if color == "white" else "white"  # Alternate with grey

    def _resize_image(self, img):
        img_resized = img.resize(
            (round(self.width / 8), round(self.height / 8)), Image.ANTIALIAS
        )
        img_tk = ImageTk.PhotoImage(img_resized)
        return img_tk

    def _load_image(self, color, piece):
        img_path = f"piece_images/{color}-{piece}.png"
        img = Image.open(img_path).convert("RGBA")
        img_tk = self._resize_image(img)
        self.piece_images[f"{color}-{piece}"] = img_tk

    def load_piece_images(self):
        """Preloads images so that we only have to do this once"""
        pieces = ["rook", "knight", "bishop", "queen", "king", "pawn"]
        colors = ["black", "white"]
        for piece in pieces:
            for color in colors:
                self._load_image(color, piece)

    def _get_piece_image(self, piece):
        """Helper to get image corresponding to each piece on the board at setup"""
        piece_type = piece.__class__.__name__.lower()  # 'pawn', 'rook', etc.
        color = "black" if piece.color == "b" else "white"
        return self.piece_images[f"{color}-{piece_type}"]

    def _draw_piece(self, img, row, col):
        """Helper to draw piece on the board using preloaded image from dict"""
        x = (col * self.square_side) + self.square_side / 2
        y = (row * self.square_side) + self.square_side / 2
        visual_piece = self.canvas.create_image(x, y, image=img)
        self.piece_img_locations[f"{row}{col}"] = visual_piece

    def _delete_piece(self, row, col):
        piece_to_delete = self.piece_img_locations[f"{row}{col}"]
        self.canvas.delete(piece_to_delete)

    def _place_piece(self, row, col):
        """This is the connection between the "back-end" and "front-end" setup"""
        piece = self.board_state.board[row][col]
        if piece is not None:
            img = self._get_piece_image(piece)
            self._draw_piece(img, row, col)

    def setup_pieces(self):
        """Places pieces on the board"""
        for row in range(8):
            for col in range(8):
                self._place_piece(row, col)

    ###############
    # HIGHLIGHTING
    ###############

    def _highlight_potential_capture(self, square):
        row, col = square
        if (
            self.board_state.board[row][col] is not None
            or square in self.board_state.en_passant_squares
        ):
            capture_square = self.squares.get((row, col))
            self.canvas.itemconfig(capture_square, outline="red", width=3)

    def _highlight_potential_move(self, square):
        row, col = square
        col_center = (col * self.square_side) + (self.square_side / 2)
        row_center = (row * self.square_side) + (self.square_side / 2)
        radius = self.square_side / 8
        circle = self.canvas.create_oval(
            col_center - radius,
            row_center - radius,
            col_center + radius,
            row_center + radius,
            fill="darkblue",
        )
        self.legal_move_circles.append(circle)

    def _highlight_legal_moves(self, legal_moves: list):
        for potential_square in legal_moves:
            self._highlight_potential_move(potential_square)
            self._highlight_potential_capture(potential_square)

    def _reset_legal_moves_highlight(self):
        """Easiest way is just un-highlighting all squares"""
        for circle in self.legal_move_circles:
            self.canvas.delete(circle)
        self.legal_move_circles = []

    def _reset_capture_highlight(self):
        for tup in self.squares:
            square = self.squares.get((tup))
            self.canvas.itemconfig(square, outline="black", width=1)

    def _deselect_piece(self):
        """Deselect a piece by changing the color back to original state"""
        if self.cur_highlighted is not None:
            last_row, last_col = self.cur_highlighted
            last_square = self.squares.get((last_row, last_col))
            original_color = (
                "white" if (last_row + last_col) % 2 == 0 else "gray"
            )  # Need original color
            self.canvas.itemconfig(last_square, fill=original_color)
            self.cur_highlighted = None

    def _reset_hightlight(self):
        self._deselect_piece()
        self._reset_legal_moves_highlight()
        self._reset_capture_highlight()

    ###############
    # GAME INPUTS
    ###############

    def _is_capture(self, start, end):
        captor = self.board_state.board[start[0]][start[1]]
        captee = self.board_state.board[end[0]][end[1]]
        if captor is not None and captee is not None and captor.color != captee.color:
            return True
        return False

    def _handle_en_passant(self, end):
        if end in self.board_state.en_passant_squares:
            # Update end to the correct pawn position just for deletion
            direction = 1 if self.board_state.white_to_move else -1
            ep_end_row = end[0] + (1 * direction)
            self._delete_piece(ep_end_row, end[1])
            self.board_state.capture_piece((ep_end_row, end[1]))

    def _handle_capture(self, start, end):
        if self._is_capture(start, end):
            self._delete_piece(end[0], end[1])
            self.board_state.capture_piece(end)

    def _handle_castle(self, end):
        if self.board_state.castled_rook_position is not None:
            rook_position = self.board_state.castled_rook_position
            self._delete_piece(rook_position[0], rook_position[1])
            rook_end_col = 5 if end[1] == 6 else 3
            self._place_piece(end[0], rook_end_col)
            self.board_state.castled_rook_position = None

    def _make_move(self, start, end):
        # Handle special cases
        self._handle_en_passant(end)
        self._handle_capture(start, end)
        # Move the piece
        self.board_state.move_piece(start, end)
        self._handle_castle(end)  # Relies on move_piece updating game state
        self._delete_piece(start[0], start[1])
        self._place_piece(end[0], end[1])
        # Restart for next move
        self._reset_hightlight()
        self.print_debug_board()

    def _get_selected_square(self, event):
        row = event.y // self.square_side
        col = event.x // self.square_side
        return (row, col)

    def _highlight_selected_piece(self, selected_square):
        row_selected, col_selected = selected_square
        selected_piece = self.board_state.board[row_selected][col_selected]
        # De-select the current square and reset legal move highlighting
        self._deselect_piece()
        self._reset_hightlight()
        # Select the new square
        selected_square = self.squares.get((row_selected, col_selected))
        self.canvas.itemconfig(selected_square, fill="#90EE90")
        self.cur_highlighted = (row_selected, col_selected)
        # Highlight legal moves
        self.legal_moves = self.board_state.filter_legal_moves_for_check(selected_piece)
        self._highlight_legal_moves(self.legal_moves)

    def select_and_move_piece(self, event):
        """Highlights a piece before moving it."""
        selected_square = self._get_selected_square(event)
        selected_piece = self.board_state.board[selected_square[0]][selected_square[1]]

        # First try to move the piece
        if self.cur_highlighted and selected_square in self.legal_moves:
            self._make_move(self.cur_highlighted, selected_square)
        # Change piece to move
        elif selected_piece is not None and self.board_state.white_to_move == (
            selected_piece.color == "w"
        ):
            self._highlight_selected_piece(selected_square)
        else:
            return None


if __name__ == "__main__":
    gui = ChessGUI()
