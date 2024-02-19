import tkinter as tk
from PIL import Image, ImageTk
from board import BoardState


class ChessGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.board = BoardState()  # BoardState class manages the game state
        self.width = self.height = 1024
        self.square_side = (
            self.width // 8
        )  # Floor division to make sure piece fits in square
        self.squares = (
            {}
        )  # Cache squares for highlighting TODO: this doesn't feel right...
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
        self.canvas.bind(
            "<Button-1>", self.select_and_move_piece
        )  # Button-1 is left mouse, so left mouse selects a square containing a piece

        self.root.mainloop()

    ###############
    # BOARD SETUP #
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

    def load_piece_images(self):
        """Preloads images so that we only have to do this once"""
        pieces = ["rook", "knight", "bishop", "queen", "king", "pawn"]
        colors = ["black", "white"]
        for piece in pieces:
            for color in colors:
                img_path = f"piece_images/{color}-{piece}.png"
                img = tk.PhotoImage(file=img_path)
                self.piece_images[f"{color}-{piece}"] = img

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

    def delete_piece(self, row, col):
        piece_to_delete = self.piece_img_locations[f"{row}{col}"]
        self.canvas.delete(piece_to_delete)

    def place_piece(self, row, col):
        """This is the connection between the "back-end" and "front-end" setup"""
        piece = self.board.board[row][col]
        if piece is not None:
            img = self._get_piece_image(piece)
            self._draw_piece(img, row, col)

    def setup_pieces(self):
        """Places pieces on the board"""
        for row in range(8):
            for col in range(8):
                self.place_piece(row, col)

    ###############
    # GAME INPUTS #
    ###############

    def highlight_legal_moves(self, legal_moves: list):
        for potential_square in legal_moves:
            # We're going to indicate a potential move by creating a circle in the center of the potential squares
            row, col = potential_square
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

    def reset_legal_moves_highlight(self):
        """Easiest way is just un-highlighting all squares"""
        for circle in self.legal_move_circles:
            self.canvas.delete(circle)
        self.legal_move_circles = []

    def deselect_piece(self):
        """Deselect a piece by changing the color back to original state"""
        if self.cur_highlighted is not None:
            last_row, last_col = self.cur_highlighted
            last_square = self.squares.get((last_row, last_col))
            original_color = (
                "white" if (last_row + last_col) % 2 == 0 else "gray"
            )  # Need original color
            self.canvas.itemconfig(last_square, fill=original_color)
            self.cur_highlighted = None

    def make_move(self, start, end):
        # Move the piece
        start_row, start_col = start
        end_row, end_col = end
        self.board.move_piece(start, end)

        # Visually move the piece
        self.delete_piece(start_row, start_col)
        self.place_piece(end_row, end_col)

        # Restart for next move
        self.deselect_piece()
        self.reset_legal_moves_highlight()

    def select_and_move_piece(self, event):
        """Highlights a piece before moving it. Also may include showing legal moves in the future"""
        row_selected = event.y // self.square_side
        col_selected = event.x // self.square_side
        selected_square = (row_selected, col_selected)
        selected_piece = self.board.board[row_selected][col_selected]

        # First try to move the piece
        if self.cur_highlighted and selected_square in self.legal_moves:
            self.make_move(self.cur_highlighted, (row_selected, col_selected))
        elif selected_piece is not None and (
            self.board.white_to_move
            and selected_piece.color == "w"
            or not self.board.white_to_move
            and selected_piece.color == "b"
        ):
            # De-select the current square and reset legal move highlighting
            self.deselect_piece()
            self.reset_legal_moves_highlight()
            # Select the new square
            selected_square = self.squares.get((row_selected, col_selected))
            self.canvas.itemconfig(selected_square, fill="#90EE90")
            self.cur_highlighted = (row_selected, col_selected)
            # Highlight legal moves
            self.legal_moves = self.board.get_legal_moves(selected_piece)
            self.highlight_legal_moves(self.legal_moves)
        else:
            return None


if __name__ == "__main__":
    gui = ChessGUI()
