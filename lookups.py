from py_core.board import NOT_FILE_A, NOT_FILE_B, NOT_FILE_G, NOT_FILE_H, RANK_2, RANK_7, FILES, RANKS
ROOK_OFFSETS = [8, -8, 1, -1]          
BISHOP_OFFSETS = [9, 7, -7, -9]        
QUEEN_OFFSETS = ROOK_OFFSETS + BISHOP_OFFSETS
KNIGHT_ATTACKS = [0] * 64
KING_ATTACKS = [0] * 64
def precompute_knight_attacks():
    for sq in range(64):
        attacks = 0
        knight = 1 << sq
        attacks |= (knight << 17) & NOT_FILE_A  
        attacks |= (knight << 15) & NOT_FILE_H  
        attacks |= (knight << 10) & NOT_FILE_A & NOT_FILE_B  
        attacks |= (knight << 6)  & NOT_FILE_G & NOT_FILE_H  
        attacks |= (knight >> 15) & NOT_FILE_A  
        attacks |= (knight >> 17) & NOT_FILE_H  
        attacks |= (knight >> 6)  & NOT_FILE_A & NOT_FILE_B  
        attacks |= (knight >> 10) & NOT_FILE_G & NOT_FILE_H  
        KNIGHT_ATTACKS[sq] = attacks & 0xFFFFFFFFFFFFFFFF
def precompute_king_attacks():
    for sq in range(64):
        attacks = 0
        king = 1 << sq
        attacks |= (king << 8)  
        attacks |= (king >> 8)  
        attacks |= (king << 1) & NOT_FILE_A  
        attacks |= (king << 9) & NOT_FILE_A  
        attacks |= (king >> 7) & NOT_FILE_A  
        attacks |= (king >> 1) & NOT_FILE_H  
        attacks |= (king << 7) & NOT_FILE_H  
        attacks |= (king >> 9) & NOT_FILE_H  
        KING_ATTACKS[sq] = attacks & 0xFFFFFFFFFFFFFFFF
precompute_knight_attacks()
precompute_king_attacks()
def get_sliding_moves(sq: int, offsets: list, friendly_mask: int, enemy_mask: int) -> int:
    moves_bb = 0
    for offset in offsets:
        current_sq = sq
        while True:
            rank_prev = current_sq // 8
            file_prev = current_sq % 8
            current_sq += offset
            if not (0 <= current_sq <= 63):
                break
            rank_curr = current_sq // 8
            file_curr = current_sq % 8
            if offset in [1, -1] and rank_curr != rank_prev:
                break
            if offset in [7, -7, 9, -9] and abs(file_curr - file_prev) > 1:
                break
            target_mask = 1 << current_sq
            if target_mask & friendly_mask:
                break
            moves_bb |= target_mask
            if target_mask & enemy_mask:
                break
    return moves_bb
def get_piece_moves(sq: int, piece_idx: int, friendly_mask: int, enemy_mask: int, occupied: int, en_passant_sq: int = None) -> int:
    moves_bb = 0
    if piece_idx in [1, 7]:
        moves_bb = KNIGHT_ATTACKS[sq] & ~friendly_mask
    elif piece_idx in [5, 11]:
        moves_bb = KING_ATTACKS[sq] & ~friendly_mask
    elif piece_idx in [3, 9]:
        moves_bb = get_sliding_moves(sq, ROOK_OFFSETS, friendly_mask, enemy_mask)
    elif piece_idx in [2, 8]:
        moves_bb = get_sliding_moves(sq, BISHOP_OFFSETS, friendly_mask, enemy_mask)
    elif piece_idx in [4, 10]:
        moves_bb = get_sliding_moves(sq, QUEEN_OFFSETS, friendly_mask, enemy_mask)
    elif piece_idx == 0:
        forward = sq + 8
        if forward <= 63 and not ((1 << forward) & occupied):
            moves_bb |= (1 << forward)
            if ((1 << sq) & RANK_2) and not ((1 << (sq + 16)) & occupied):
                moves_bb |= (1 << (sq + 16))
        for cap_offset, mask in [(7, NOT_FILE_H), (9, NOT_FILE_A)]:
            target_sq = sq + cap_offset
            if target_sq <= 63:
                target_mask = 1 << target_sq
                if (target_mask & mask):
                    if (target_mask & enemy_mask):
                        moves_bb |= target_mask
                    elif en_passant_sq is not None and target_sq == en_passant_sq:
                        moves_bb |= target_mask
    elif piece_idx == 6:
        forward = sq - 8
        if forward >= 0 and not ((1 << forward) & occupied):
            moves_bb |= (1 << forward)
            if ((1 << sq) & RANK_7) and not ((1 << (sq - 16)) & occupied):
                moves_bb |= (1 << (sq - 16))
        for cap_offset, mask in [(-7, NOT_FILE_A), (-9, NOT_FILE_H)]:
            target_sq = sq + cap_offset
            if target_sq >= 0:
                target_mask = 1 << target_sq
                if (target_mask & mask):
                    if (target_mask & enemy_mask):
                        moves_bb |= target_mask
                    elif en_passant_sq is not None and target_sq == en_passant_sq:
                        moves_bb |= target_mask
    return moves_bb & 0xFFFFFFFFFFFFFFFF
