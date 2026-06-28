class GameState:
    def __init__(self, turn=0, castling_rights=0b1111, en_passant_sq=None):
        self.turn = turn
        self.castling_rights = castling_rights
        self.en_passant_sq = en_passant_sq
        self.is_in_check = False
        self.pending_promotion = None
        self.history = []
        self.move_log = []
    @classmethod
    def load_from_fen(cls, fen: str):
        parts = fen.split()
        if len(parts) < 4:
            return cls()
        turn = 0 if parts[1] == 'w' else 1
        castling_rights = 0
        if 'K' in parts[2]: castling_rights |= 0b1000
        if 'Q' in parts[2]: castling_rights |= 0b0100
        if 'k' in parts[2]: castling_rights |= 0b0010
        if 'q' in parts[2]: castling_rights |= 0b0001
        en_passant_sq = None
        if parts[3] != '-':
            file = ord(parts[3][0]) - ord('a')
            rank = int(parts[3][1]) - 1
            en_passant_sq = rank * 8 + file
        return cls(turn=turn, castling_rights=castling_rights, en_passant_sq=en_passant_sq)
    def to_fen(self, pieces) -> str:
        board_part = pieces.to_fen()
        turn_part = 'w' if self.turn == 0 else 'b'
        castling_part = ""
        if self.castling_rights & 0b1000: castling_part += "K"
        if self.castling_rights & 0b0100: castling_part += "Q"
        if self.castling_rights & 0b0010: castling_part += "k"
        if self.castling_rights & 0b0001: castling_part += "q"
        if not castling_part: castling_part = "-"
        ep_part = "-"
        if self.en_passant_sq is not None:
            file = self.en_passant_sq % 8
            rank = self.en_passant_sq // 8
            ep_part = f"{chr(ord('a') + file)}{rank + 1}"
        return f"{board_part} {turn_part} {castling_part} {ep_part} 0 1"
    def change_turn(self):
        self.turn = 1 - self.turn
    def update_castling_rights(self, new_rights: int):
        self.castling_rights = new_rights & 0b1111
    def handle_castling_rights_on_move(self, from_sq: int, to_sq: int):
        if from_sq == 4 or to_sq == 4:
            self.castling_rights &= 0b0011  
        if from_sq == 60 or to_sq == 60:
            self.castling_rights &= 0b1100  
        if from_sq == 7 or to_sq == 7:
            self.castling_rights &= 0b0111  
        if from_sq == 0 or to_sq == 0:
            self.castling_rights &= 0b1011  
        if from_sq == 63 or to_sq == 63:
            self.castling_rights &= 0b1101  
        if from_sq == 56 or to_sq == 56:
            self.castling_rights &= 0b1110  
    def set_en_passant(self, square):
        self.en_passant_sq = square
    def clear_en_passant(self):
        self.en_passant_sq = None
    def set_check(self, status: bool):
        self.is_in_check = status
    def set_promotion(self, promotion_data):
        self.pending_promotion = promotion_data
    def clear_promotion(self):
        self.pending_promotion = None
    def push_to_history(self):
        state_snapshot = (self.turn, self.castling_rights, self.en_passant_sq, self.is_in_check, self.pending_promotion)
        self.history.append(state_snapshot)
    def pop_from_history(self):
        if not self.history:
            return False  
        prev_turn, prev_castling, prev_ep, prev_check, prev_promo = self.history.pop()
        self.turn = prev_turn
        self.castling_rights = prev_castling
        self.en_passant_sq = prev_ep
        self.is_in_check = prev_check
        self.pending_promotion = prev_promo
        return True
