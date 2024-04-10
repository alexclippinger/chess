### Game Status

#### Finished
1. **Basic Game State**: white or black to move
2. **En Passant**: pawn moved two steps to be next to opponent pawn on previous move
3. **Check**: including discovered checks
4. **Castling**: castling is legal only if not in check, not through check, the King/Rook's first move, and the path between the two is open

#### TODO
1. UI Elements
    - Allow promotion to Knight, Bishop, or Rook
    - Indicate check or checkmate
    - Indicate draw
2. Game Logic
    - Threefold repetition