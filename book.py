import os
import re
from typing import Dict, List, Optional
class TrieNode:
    def __init__(self):
        self.children: Dict[str, 'TrieNode'] = {}
        self.opening_name: Optional[str] = None
class OpeningBook:
    def __init__(self, openings_dir: str = "assets/openings"):
        self.root = TrieNode()
        self._load_openings(openings_dir)
    def _load_openings(self, directory: str):
        if not os.path.exists(directory):
            print(f"Warning: Opening book directory {directory} not found.")
            return
        count = 0
        for file_name in ['a.tsv', 'b.tsv', 'c.tsv', 'd.tsv', 'e.tsv']:
            file_path = os.path.join(directory, file_name)
            if not os.path.exists(file_path):
                continue
            with open(file_path, 'r', encoding='utf-8') as f:
                next(f, None) 
                for line in f:
                    parts = line.strip().split('\t')
                    if len(parts) >= 3:
                        name = parts[1]
                        pgn = parts[2]
                        self._add_to_trie(name, pgn)
                        count += 1
        print(f"Loaded {count} opening variations into the Opening Book.")
    def _add_to_trie(self, name: str, pgn: str):
        moves = self._parse_pgn(pgn)
        if not moves:
            return
        node = self.root
        for move in moves:
            if move not in node.children:
                node.children[move] = TrieNode()
            node = node.children[move]
        node.opening_name = name
    def _parse_pgn(self, pgn: str) -> List[str]:
        clean = re.sub(r'\d+\.', ' ', pgn)
        return clean.split()
    def get_theory_moves(self, history: List[str]) -> List[str]:
        node = self.root
        for move in history:
            if move in node.children:
                node = node.children[move]
            else:
                return [] 
        return list(node.children.keys())
    def get_opening_name(self, history: List[str]) -> Optional[str]:
        node = self.root
        last_name = None
        for move in history:
            if move in node.children:
                node = node.children[move]
                if node.opening_name:
                    last_name = node.opening_name
            else:
                break
        return last_name
