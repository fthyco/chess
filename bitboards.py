WP, WN, WB, WR, WQ, WK = 0, 1, 2, 3, 4, 5      
BP, BN, BB, BR, BQ, BK = 6, 7, 8, 9, 10, 11    
class Pieces:
    def __init__(self, custom_layout=None):
        if custom_layout and len(custom_layout) == 12:
            self.bitboards = list(custom_layout)
        else:
            self.bitboards = [0] * 12 
    def set_piece(self, piece_idx: int, square: int):
        self.bitboards[piece_idx] |= (1 << square)
    def clear_piece(self, piece_idx: int, square: int):
        self.bitboards[piece_idx] &= ~(1 << square)
    def move_piece(self, piece_idx: int, from_square: int, to_square: int):
        self.clear_piece(piece_idx, from_square)
        self.set_piece(piece_idx, to_square)
    def get_piece_at(self, square: int):
        for piece_idx in range(12):
            if (self.bitboards[piece_idx] >> square) & 1:
                return piece_idx
        return None
    def get_white_mask(self) -> int:
        mask = 0
        for i in range(WP, WK + 1):
            mask |= self.bitboards[i]
        return mask
    def get_black_mask(self) -> int:
        mask = 0
        for i in range(BP, BK + 1):
            mask |= self.bitboards[i]
        return mask
    def get_occupied_mask(self) -> int:
        return self.get_white_mask() | self.get_black_mask()
    def get_empty_mask(self) -> int:
        return ~self.get_occupied_mask() & 0xFFFFFFFFFFFFFFFF
    @classmethod
    def load_from_fen(cls, fen: str):
        pieces = cls()
        board_part = fen.split()[0]
        char_to_idx = {
            'P': 0, 'N': 1, 'B': 2, 'R': 3, 'Q': 4, 'K': 5,
            'p': 6, 'n': 7, 'b': 8, 'r': 9, 'q': 10, 'k': 11
        }
        rank = 7
        file = 0
        for char in board_part:
            if char == '/':
                rank -= 1
                file = 0
            elif char.isdigit():
                file += int(char)
            else:
                sq = rank * 8 + file
                pieces.set_piece(char_to_idx[char], sq)
                file += 1
        return pieces
    def to_fen(self) -> str:
        idx_to_char = {
            0: 'P', 1: 'N', 2: 'B', 3: 'R', 4: 'Q', 5: 'K',
            6: 'p', 7: 'n', 8: 'b', 9: 'r', 10: 'q', 11: 'k'
        }
        fen_rows = []
        for rank in range(7, -1, -1):
            empty_count = 0
            row_str = ""
            for file in range(8):
                sq = rank * 8 + file
                piece_idx = self.get_piece_at(sq)
                if piece_idx is None:
                    empty_count += 1
                else:
                    if empty_count > 0:
                        row_str += str(empty_count)
                        empty_count = 0
                    row_str += idx_to_char[piece_idx]
            if empty_count > 0:
                row_str += str(empty_count)
            fen_rows.append(row_str)
        return "/".join(fen_rows)
