from py_core.bitboards import Pieces
from py_core.lookups import (
    get_sliding_moves,
    ROOK_OFFSETS,
    BISHOP_OFFSETS,
    KNIGHT_ATTACKS,
    KING_ATTACKS
)
from py_core.board import NOT_FILE_A, NOT_FILE_H
class MoveValidator:
    @staticmethod
    def is_square_attacked(sq: int, attacker_is_white: bool, pieces: Pieces) -> bool:
        pawn_idx   = 0 if attacker_is_white else 6
        knight_idx = 1 if attacker_is_white else 7
        bishop_idx = 2 if attacker_is_white else 8
        rook_idx   = 3 if attacker_is_white else 9
        queen_idx  = 4 if attacker_is_white else 10
        king_idx   = 5 if attacker_is_white else 11
        occupied = pieces.get_occupied_mask()
        if KNIGHT_ATTACKS[sq] & pieces.bitboards[knight_idx]:
            return True
        if KING_ATTACKS[sq] & pieces.bitboards[king_idx]:
            return True
        if attacker_is_white:
            pawn_attacks = 0
            if sq >= 7: pawn_attacks |= (1 << (sq - 7)) & NOT_FILE_H
            if sq >= 9: pawn_attacks |= (1 << (sq - 9)) & NOT_FILE_A
            if pawn_attacks & pieces.bitboards[pawn_idx]:
                return True
        else:
            pawn_attacks = 0
            if sq <= 56: pawn_attacks |= (1 << (sq + 7)) & NOT_FILE_A
            if sq <= 54: pawn_attacks |= (1 << (sq + 9)) & NOT_FILE_H
            if pawn_attacks & pieces.bitboards[pawn_idx]:
                return True
        straight_attacks = get_sliding_moves(sq, ROOK_OFFSETS, 0, occupied)
        if straight_attacks & (pieces.bitboards[rook_idx] | pieces.bitboards[queen_idx]):
            return True
        diagonal_attacks = get_sliding_moves(sq, BISHOP_OFFSETS, 0, occupied)
        if diagonal_attacks & (pieces.bitboards[bishop_idx] | pieces.bitboards[queen_idx]):
            return True
        return False
    @staticmethod
    def generate_legal_moves(sq: int, piece_idx: int, pieces: Pieces, pseudo_moves_bb: int, castling_rights: int, en_passant_sq: int = None) -> int:
        legal_moves_bb = 0
        is_white = piece_idx < 6
        king_idx = 5 if is_white else 11
        target_squares = []
        temp_bb = pseudo_moves_bb
        while temp_bb:
            lsb = (temp_bb & -temp_bb).bit_length() - 1
            target_squares.append(lsb)
            temp_bb &= temp_bb - 1
        for target_sq in target_squares:
            is_en_passant = piece_idx in [0, 6] and target_sq == en_passant_sq
            ep_capture_sq = -1
            captured_piece_idx = pieces.get_piece_at(target_sq)
            if is_en_passant:
                ep_capture_sq = target_sq - 8 if piece_idx == 0 else target_sq + 8
                captured_piece_idx = pieces.get_piece_at(ep_capture_sq)
            pieces.clear_piece(piece_idx, sq)
            if captured_piece_idx is not None:
                capture_target = ep_capture_sq if is_en_passant else target_sq
                pieces.clear_piece(captured_piece_idx, capture_target)
            pieces.set_piece(piece_idx, target_sq)
            if piece_idx == king_idx:
                king_sq = target_sq
            else:
                king_bb = pieces.bitboards[king_idx]
                king_sq = (king_bb & -king_bb).bit_length() - 1 if king_bb else -1
            if king_sq != -1:
                is_in_check = MoveValidator.is_square_attacked(king_sq, not is_white, pieces)
                if not is_in_check:
                    legal_moves_bb |= (1 << target_sq)
            pieces.clear_piece(piece_idx, target_sq)
            pieces.set_piece(piece_idx, sq)
            if captured_piece_idx is not None:
                capture_target = ep_capture_sq if is_en_passant else target_sq
                pieces.set_piece(captured_piece_idx, capture_target)
        if piece_idx == king_idx:
            occupied = pieces.get_occupied_mask()
            enemy_color = not is_white
            if is_white and sq == 4:
                if (castling_rights & 0b1000) and not (occupied & 0x60):
                    if not MoveValidator.is_square_attacked(4, enemy_color, pieces) and                       not MoveValidator.is_square_attacked(5, enemy_color, pieces) and                       not MoveValidator.is_square_attacked(6, enemy_color, pieces):
                        legal_moves_bb |= (1 << 6)
                if (castling_rights & 0b0100) and not (occupied & 0x0E):
                    if not MoveValidator.is_square_attacked(4, enemy_color, pieces) and                       not MoveValidator.is_square_attacked(3, enemy_color, pieces) and                       not MoveValidator.is_square_attacked(2, enemy_color, pieces):
                        legal_moves_bb |= (1 << 2)
            elif not is_white and sq == 60:
                if (castling_rights & 0b0010) and not (occupied & 0x6000000000000000):
                    if not MoveValidator.is_square_attacked(60, enemy_color, pieces) and                       not MoveValidator.is_square_attacked(61, enemy_color, pieces) and                       not MoveValidator.is_square_attacked(62, enemy_color, pieces):
                        legal_moves_bb |= (1 << 62)
                if (castling_rights & 0b0001) and not (occupied & 0x0E00000000000000):
                    if not MoveValidator.is_square_attacked(60, enemy_color, pieces) and                       not MoveValidator.is_square_attacked(59, enemy_color, pieces) and                       not MoveValidator.is_square_attacked(58, enemy_color, pieces):
                        legal_moves_bb |= (1 << 58)
        return legal_moves_bb
