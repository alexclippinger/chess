# Notes on Chess

- The board is 8x8 with a checkered pattern
- There is a starting position for both sides and piece
- Each piece has the ability to move in certain ways
- Each piece can either move to an empty square or capture another piece

### Board

A board square can either be vacant or occupied

### Pieces

What are consistent qualities of all pieces?
- They are all either white or black
- They can be captured

### Game Status

#### Finished
1. **Basic Game State**: white or black to move
2. **En Passant**: pawn moved two steps to be next to opponent pawn on previous move
2. Pawns can move two squares forward for first move and one thereafter. They capture diagonally.
3. All other basic piece logic (i.e., all pieces can move properly)
4. UI elements for game state inc. highlighted piece, legal moves, potential captures.

#### TODO
1. **TODO Game States**:
    - Castle is possible (King/Rook `first_move=True`, no pieces between, not in check or passing through check)
    - Check (king is attacked by opponent, can move or another piece can block)
    - Checkmate (king is attacked and cannot be protected)

**Current Status**:
Check is currently broken, seems that "simulated" moves are not properly reverted