from py_core.lookups import get_piece_moves
from py_core.validator import MoveValidator
def sq_to_name(sq: int) -> str:
    file = sq % 8
    rank = sq // 8
    return f"{chr(ord('a') + file)}{rank + 1}"
def get_disambiguation(from_sq: int, to_sq: int, piece_idx: int, pieces, state) -> str:
    if piece_idx in [0, 6, 5, 11]:  
        return ""
    same_pieces = []
    bb = pieces.bitboards[piece_idx]
    temp = bb
    while temp:
        lsb = (temp & -temp).bit_length() - 1
        same_pieces.append(lsb)
        temp &= temp - 1
    conflicts = []
    is_white = piece_idx < 6
    friendly_mask = pieces.get_white_mask() if is_white else pieces.get_black_mask()
    enemy_mask = pieces.get_black_mask() if is_white else pieces.get_white_mask()
    occupied = pieces.get_occupied_mask()
    for other_sq in same_pieces:
        if other_sq != from_sq:
            pseudo = get_piece_moves(other_sq, piece_idx, friendly_mask, enemy_mask, occupied, state.en_passant_sq)
            legal = MoveValidator.generate_legal_moves(other_sq, piece_idx, pieces, pseudo, state.castling_rights, state.en_passant_sq)
            if (legal >> to_sq) & 1:
                conflicts.append(other_sq)
    if not conflicts:
        return ""
    from_file = from_sq % 8
    from_rank = from_sq // 8
    file_conflict = any(c_sq % 8 == from_file for c_sq in conflicts)
    rank_conflict = any(c_sq // 8 == from_rank for c_sq in conflicts)
    if not file_conflict:
        return chr(ord('a') + from_file)
    elif not rank_conflict:
        return str(from_rank + 1)
    return f"{chr(ord('a') + from_file)}{from_rank + 1}"
def move_to_san(from_sq: int, to_sq: int, piece_idx: int, is_capture: bool,
                is_check: bool, is_mate: bool, is_castling: bool,
                promotion_piece_idx: int = None,
                disambiguation: str = "") -> str:
    if is_castling:
        if to_sq > from_sq:  
            san = "O-O"
        else:                
            san = "O-O-O"
    else:
        piece_chars = ['P', 'N', 'B', 'R', 'Q', 'K', 'P', 'N', 'B', 'R', 'Q', 'K']
        piece_char = piece_chars[piece_idx]
        if piece_char == 'P':
            if is_capture:
                file = from_sq % 8
                san = f"{chr(ord('a') + file)}x{sq_to_name(to_sq)}"
            else:
                san = sq_to_name(to_sq)
        else:
            san = piece_char + disambiguation
            if is_capture:
                san += "x"
            san += sq_to_name(to_sq)
    if promotion_piece_idx is not None:
        promotion_chars = ['P', 'N', 'B', 'R', 'Q', 'K', 'P', 'N', 'B', 'R', 'Q', 'K']
        san += f"={promotion_chars[promotion_piece_idx]}"
    if is_mate:
        san += "#"
    elif is_check:
        san += "+"
    return san
def san_to_move(san: str, state, pieces) -> tuple[int, int, int]:
    is_white_turn = state.turn == 0
    clean_san = san.replace("#", "").replace("+", "")
    if clean_san == "O-O":
        from_sq = 4 if is_white_turn else 60
        to_sq = 6 if is_white_turn else 62
        piece_idx = 5 if is_white_turn else 11
        return from_sq, to_sq, piece_idx
    elif clean_san == "O-O-O":
        from_sq = 4 if is_white_turn else 60
        to_sq = 2 if is_white_turn else 58
        piece_idx = 5 if is_white_turn else 11
        return from_sq, to_sq, piece_idx
    is_pawn = clean_san[0].islower()
    if is_pawn:
        piece_char = 'P'
        target_str = clean_san[-2:] if "=" not in clean_san else clean_san.split("=")[0][-2:]
        disambiguation = clean_san[0] if "x" in clean_san else ""
    else:
        piece_char = clean_san[0]
        target_str = clean_san[-2:]
        idx = 1
        end_idx = len(clean_san) - 2
        if "=" in clean_san:
            target_str = clean_san.split("=")[0][-2:]
            end_idx = clean_san.index("=") - 2
        if "x" in clean_san:
            target_str = clean_san.split("x")[1][:2]
            end_idx = clean_san.index("x")
        if end_idx >= idx:
            disambiguation = clean_san[idx:end_idx]
        else:
            disambiguation = ""
    target_file = ord(target_str[0]) - ord('a')
    target_rank = int(target_str[1]) - 1
    to_sq = target_rank * 8 + target_file
    piece_char_to_idx = {'P': 0, 'N': 1, 'B': 2, 'R': 3, 'Q': 4, 'K': 5}
    piece_idx = piece_char_to_idx[piece_char]
    if not is_white_turn:
        piece_idx += 6
    friendly_mask = pieces.get_white_mask() if is_white_turn else pieces.get_black_mask()
    enemy_mask = pieces.get_black_mask() if is_white_turn else pieces.get_white_mask()
    occupied = pieces.get_occupied_mask()
    same_pieces = []
    bb = pieces.bitboards[piece_idx]
    temp = bb
    while temp:
        lsb = (temp & -temp).bit_length() - 1
        same_pieces.append(lsb)
        temp &= temp - 1
    candidates = []
    for sq in same_pieces:
        pseudo = get_piece_moves(sq, piece_idx, friendly_mask, enemy_mask, occupied, state.en_passant_sq)
        legal = MoveValidator.generate_legal_moves(sq, piece_idx, pieces, pseudo, state.castling_rights, state.en_passant_sq)
        if (legal >> to_sq) & 1:
            candidates.append(sq)
    if len(candidates) == 1:
        return candidates[0], to_sq, piece_idx
    for sq in candidates:
        file_char = chr(ord('a') + (sq % 8))
        rank_char = str((sq // 8) + 1)
        if disambiguation == file_char or disambiguation == rank_char or disambiguation == file_char + rank_char:
            return sq, to_sq, piece_idx
    if len(candidates) > 0:
        return candidates[0], to_sq, piece_idx
    return -1, -1, -1
