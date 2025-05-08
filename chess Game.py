# Complete Chess Game with AI (Minimax + Alpha-Beta Pruning)

import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import copy
import time

# --------------------------- PIECE VALUES --------------------------- #
PIECE_SCORES = {
    "pawn": 10,
    "knight": 30,
    "bishop": 30,
    "rook": 50,
    "queen": 90,
    "king": 900
}

# --------------------------- MAIN CLASSES --------------------------- #

class Piece:
    def __init__(self, name, color):
        self.name = name  # pawn, knight, etc.
        self.color = color  # 'w' or 'b'

    def __repr__(self):
        return f"{self.color}_{self.name}"

class ChessGame:
    def __init__(self, root):
        self.root = root
        self.board = self.create_initial_board()
        self.images = {}
        
        # Configure root window
        self.root.title("Chess Game")
        self.root.configure(bg="#2c3e50")  # Dark blue background
        
        # Create main frame
        self.main_frame = tk.Frame(root, bg="#2c3e50")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create canvas for chess board
        self.canvas = tk.Canvas(self.main_frame, width=640, height=640, bg="#2c3e50", highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, padx=20, pady=20)
        
        # Create move history frame
        self.history_frame = tk.Frame(self.main_frame, width=250, bg="#34495e")
        self.history_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=20, pady=20)
        
        # Create move history title
        history_title = tk.Label(self.history_frame, text="Move History", 
                               font=("Arial", 14, "bold"), bg="#34495e", fg="white")
        history_title.pack(pady=10)
        
        # Create move history text widget
        self.history_text = tk.Text(self.history_frame, height=40, width=25, 
                                  bg="#2c3e50", fg="white", font=("Arial", 10))
        self.history_text.pack(fill=tk.Y, expand=True, padx=10)
        self.history_text.config(state=tk.DISABLED)
        
        # Create scrollbar for move history
        self.history_scrollbar = tk.Scrollbar(self.history_frame, bg="#34495e")
        self.history_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.history_text.config(yscrollcommand=self.history_scrollbar.set)
        self.history_scrollbar.config(command=self.history_text.yview)
        
        # Create status label
        self.status_label = tk.Label(self.history_frame, text="White's turn", 
                                   font=("Arial", 12, "bold"), bg="#34495e", fg="white")
        self.status_label.pack(pady=10)
        
        # Create game info frame
        info_frame = tk.Frame(self.history_frame, bg="#34495e")
        info_frame.pack(pady=10)
        
        # Add piece value info
        piece_values = tk.Label(info_frame, text="Piece Values:\nPawn: 10\nKnight: 30\nBishop: 30\nRook: 50\nQueen: 90\nKing: 900",
                              font=("Arial", 10), bg="#34495e", fg="white", justify=tk.LEFT)
        piece_values.pack(pady=5)
        
        self.turn = 'w'
        self.selected = None
        self.ai_color = 'b'
        self.search_depth = 3
        self.move_history = []
        self.white_king_moved = False
        self.black_king_moved = False
        self.white_rooks_moved = [False, False]
        self.black_rooks_moved = [False, False]
        self.en_passant_target = None
        self.load_images()
        self.draw_board()
        self.canvas.bind("<Button-1>", self.click_handler)
        self.ask_player_side()

    def create_initial_board(self):
        board = [[None]*8 for _ in range(8)]
        pieces = ["rook", "knight", "bishop", "queen", "king", "bishop", "knight", "rook"]
        for i in range(8):
            board[1][i] = Piece("pawn", 'b')
            board[6][i] = Piece("pawn", 'w')
            board[0][i] = Piece(pieces[i], 'b')
            board[7][i] = Piece(pieces[i], 'w')
        return board

    def load_images(self):
        for color in ['w', 'b']:
            for name in ["rook", "knight", "bishop", "queen", "king", "pawn"]:
                img = Image.open(f"{color}_{name}.png").resize((80, 80))
                self.images[f"{color}_{name}"] = ImageTk.PhotoImage(img)

    def draw_board(self):
        self.canvas.delete("all")
        
        # Define colors
        light_square = "#f0d9b5"  # Light beige
        dark_square = "#b58863"   # Dark brown
        highlight_color = "#2ecc71"  # Green for selected square
        legal_move_color = "#3498db"  # Blue for legal moves
        
        # Draw squares
        for r in range(8):
            for c in range(8):
                x1, y1 = c*80, r*80
                x2, y2 = x1+80, y1+80
                
                # Draw square
                color = light_square if (r+c)%2 == 0 else dark_square
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")
                
                # Highlight selected square
                if self.selected and self.selected == (r, c):
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill=highlight_color, outline="")
                
                # Highlight legal moves
                if self.selected:
                    if self.valid_move(self.selected, (r, c)):
                        self.canvas.create_oval(x1+30, y1+30, x2-30, y2-30, fill=legal_move_color, outline="")
                
                # Draw piece
                piece = self.board[r][c]
                if piece:
                    self.canvas.create_image(x1+40, y1+40, image=self.images[str(piece)])
        
        # Draw coordinates
        files = "abcdefgh"
        ranks = "87654321"
        for i in range(8):
            # Files (letters)
            self.canvas.create_text(i*80 + 40, 640 - 10, text=files[i], font=("Arial", 10))
            # Ranks (numbers)
            self.canvas.create_text(10, i*80 + 40, text=ranks[i], font=("Arial", 10))

    def click_handler(self, event):
        if self.turn != self.ai_color:
            row, col = event.y // 80, event.x // 80
            piece = self.board[row][col]
            if self.selected:
                if self.valid_move(self.selected, (row, col)):
                    self.make_move(self.selected, (row, col))
                    self.turn = 'b' if self.turn == 'w' else 'w'
                    self.draw_board()
                    self.root.after(100, self.ai_move)
                self.selected = None
            elif piece and piece.color == self.turn:
                self.selected = (row, col)

    def valid_move(self, src, dst):
        src_row, src_col = src
        dst_row, dst_col = dst
        piece = self.board[src_row][src_col]
        target = self.board[dst_row][dst_col]

        # Basic validation
        if not piece or piece.color != self.turn:
            return False
        if target and target.color == piece.color:
            return False

        # Piece-specific validation
        if piece.name == "pawn":
            if not self.is_valid_pawn_move(src, dst):
                return False
        elif piece.name == "rook":
            if not self.is_valid_rook_move(src, dst):
                return False
        elif piece.name == "knight":
            if not self.is_valid_knight_move(src, dst):
                return False
        elif piece.name == "bishop":
            if not self.is_valid_bishop_move(src, dst):
                return False
        elif piece.name == "queen":
            if not self.is_valid_queen_move(src, dst):
                return False
        elif piece.name == "king":
            if not self.is_valid_king_move(src, dst):
                return False

        # Simulate the move to check if it would leave the king in check
        temp_board = copy.deepcopy(self.board)
        temp_board[dst_row][dst_col] = piece
        temp_board[src_row][src_col] = None
        
        # Temporarily replace the board
        original_board = self.board
        self.board = temp_board
        
        # Check if the move would leave the king in check
        king_pos = None
        for r in range(8):
            for c in range(8):
                p = temp_board[r][c]
                if p and p.name == "king" and p.color == piece.color:
                    king_pos = (r, c)
                    break
            if king_pos:
                break
        
        is_valid = not self.is_square_under_attack(king_pos, piece.color)
        
        # Restore the original board
        self.board = original_board
        
        return is_valid

    def is_valid_pawn_move(self, src, dst):
        src_row, src_col = src
        dst_row, dst_col = dst
        piece = self.board[src_row][src_col]
        target = self.board[dst_row][dst_col]
        direction = -1 if piece.color == 'w' else 1
        start_row = 6 if piece.color == 'w' else 1

        # Forward move
        if src_col == dst_col:
            # Single step
            if dst_row == src_row + direction and not target:
                return True
            # Double step from starting position
            if (src_row == start_row and dst_row == src_row + 2*direction and 
                not target and not self.board[src_row + direction][src_col]):
                return True
            return False

        # Capture move (including en passant)
        if abs(dst_col - src_col) == 1 and dst_row == src_row + direction:
            # Normal capture
            if target and target.color != piece.color:
                return True
            # En passant capture
            if (self.en_passant_target and 
                dst_row == self.en_passant_target[0] and 
                dst_col == self.en_passant_target[1]):
                return True
        return False

    def is_valid_rook_move(self, src, dst):
        src_row, src_col = src
        dst_row, dst_col = dst

        # Must move in straight line
        if src_row != dst_row and src_col != dst_col:
            return False

        # Check for pieces in between
        if src_row == dst_row:
            step = 1 if dst_col > src_col else -1
            for col in range(src_col + step, dst_col, step):
                if self.board[src_row][col]:
                    return False
        else:
            step = 1 if dst_row > src_row else -1
            for row in range(src_row + step, dst_row, step):
                if self.board[row][src_col]:
                    return False

        return True

    def is_valid_knight_move(self, src, dst):
        src_row, src_col = src
        dst_row, dst_col = dst
        row_diff = abs(dst_row - src_row)
        col_diff = abs(dst_col - src_col)
        return (row_diff == 2 and col_diff == 1) or (row_diff == 1 and col_diff == 2)

    def is_valid_bishop_move(self, src, dst):
        src_row, src_col = src
        dst_row, dst_col = dst

        # Must move diagonally
        if abs(dst_row - src_row) != abs(dst_col - src_col):
            return False

        # Check for pieces in between
        row_step = 1 if dst_row > src_row else -1
        col_step = 1 if dst_col > src_col else -1
        row, col = src_row + row_step, src_col + col_step
        while row != dst_row and col != dst_col:
            if self.board[row][col]:
                return False
            row += row_step
            col += col_step

        return True

    def is_valid_queen_move(self, src, dst):
        # Queen moves like rook or bishop
        return self.is_valid_rook_move(src, dst) or self.is_valid_bishop_move(src, dst)

    def is_valid_king_move(self, src, dst):
        src_row, src_col = src
        dst_row, dst_col = dst
        row_diff = abs(dst_row - src_row)
        col_diff = abs(dst_col - src_col)

        # Normal king move
        if row_diff <= 1 and col_diff <= 1:
            return True

        # Castling
        if row_diff == 0 and col_diff == 2:
            return self.is_valid_castle(src, dst)

        return False

    def is_valid_castle(self, src, dst):
        src_row, src_col = src
        dst_col = dst[1]
        piece = self.board[src_row][src_col]
        
        # Check if king has moved
        if piece.color == 'w' and self.white_king_moved:
            return False
        if piece.color == 'b' and self.black_king_moved:
            return False

        # Determine which rook to check
        rook_col = 0 if dst_col < src_col else 7
        rook_moved = (self.white_rooks_moved[0] if dst_col < src_col else self.white_rooks_moved[1]) if piece.color == 'w' else \
                    (self.black_rooks_moved[0] if dst_col < src_col else self.black_rooks_moved[1])

        if rook_moved:
            return False

        # Check if squares between king and rook are empty
        start = min(src_col, rook_col) + 1
        end = max(src_col, rook_col)
        for col in range(start, end):
            if self.board[src_row][col]:
                return False

        # Check if king would be in check during castling
        step = -1 if dst_col < src_col else 1
        for col in range(src_col, dst_col + step, step):
            if self.is_square_under_attack((src_row, col), piece.color):
                return False

        return True

    def is_square_under_attack(self, square, color):
        row, col = square
        opponent_color = 'b' if color == 'w' else 'w'
        
        # Check for pawn attacks
        pawn_direction = 1 if color == 'w' else -1
        for dc in [-1, 1]:
            r, c = row + pawn_direction, col + dc
            if 0 <= r < 8 and 0 <= c < 8:
                piece = self.board[r][c]
                if piece and piece.color == opponent_color and piece.name == "pawn":
                    return True

        # Check for knight attacks
        knight_moves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
                       (1, -2), (1, 2), (2, -1), (2, 1)]
        for dr, dc in knight_moves:
            r, c = row + dr, col + dc
            if 0 <= r < 8 and 0 <= c < 8:
                piece = self.board[r][c]
                if piece and piece.color == opponent_color and piece.name == "knight":
                    return True

        # Check for bishop/queen attacks (diagonals)
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        for dr, dc in directions:
            r, c = row + dr, col + dc
            while 0 <= r < 8 and 0 <= c < 8:
                piece = self.board[r][c]
                if piece:
                    if piece.color == opponent_color and (piece.name == "bishop" or piece.name == "queen"):
                        return True
                    break
                r += dr
                c += dc

        # Check for rook/queen attacks (straight lines)
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dr, dc in directions:
            r, c = row + dr, col + dc
            while 0 <= r < 8 and 0 <= c < 8:
                piece = self.board[r][c]
                if piece:
                    if piece.color == opponent_color and (piece.name == "rook" or piece.name == "queen"):
                        return True
                    break
                r += dr
                c += dc

        # Check for king attacks
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                r, c = row + dr, col + dc
                if 0 <= r < 8 and 0 <= c < 8:
                    piece = self.board[r][c]
                    if piece and piece.color == opponent_color and piece.name == "king":
                        return True

        return False

    def update_move_history(self, move_record):
        self.history_text.config(state=tk.NORMAL)
        
        # Convert move to algebraic notation
        piece = move_record['piece']
        src = move_record['src']
        dst = move_record['dst']
        captured = move_record['captured']
        
        # Get piece symbol
        piece_symbol = ''
        if piece.name != 'pawn':
            piece_symbol = piece.name[0].upper()
        
        # Get file and rank
        files = 'abcdefgh'
        ranks = '87654321'
        src_file = files[src[1]]
        src_rank = ranks[src[0]]
        dst_file = files[dst[1]]
        dst_rank = ranks[dst[0]]
        
        # Build move string
        move_str = f"{piece_symbol}{src_file}{src_rank}{dst_file}{dst_rank}"
        if captured:
            move_str = f"{piece_symbol}{src_file}x{dst_file}{dst_rank}"
        
        # Add castling notation
        if move_record['castling']:
            move_str = "O-O" if move_record['castling'] == 'kingside' else "O-O-O"
        
        # Add check/checkmate notation
        temp_board = copy.deepcopy(self.board)
        temp_board[dst[0]][dst[1]] = piece
        temp_board[src[0]][src[1]] = None
        if self.is_checkmate(self.get_opponent(piece.color)):
            move_str += "#"
        elif self.is_in_check(self.get_opponent(piece.color)):
            move_str += "+"
        
        # Add move to history
        move_number = len(self.move_history) // 2 + 1
        if piece.color == 'w':
            self.history_text.insert(tk.END, f"{move_number}. {move_str} ")
        else:
            self.history_text.insert(tk.END, f"{move_str}\n")
        
        self.history_text.see(tk.END)
        self.history_text.config(state=tk.DISABLED)
        
        # Update status label
        self.status_label.config(text=f"{'White' if self.turn == 'w' else 'Black'}'s turn")

    def make_move(self, src, dst):
        src_row, src_col = src
        dst_row, dst_col = dst
        piece = self.board[src_row][src_col]
        target = self.board[dst_row][dst_col]

        # Record the move
        move_record = {
            'piece': piece,
            'src': src,
            'dst': dst,
            'captured': target,
            'en_passant': None,
            'castling': None,
            'promotion': None
        }

        # Handle castling
        if piece.name == "king" and abs(dst_col - src_col) == 2:
            move_record['castling'] = 'queenside' if dst_col < src_col else 'kingside'
            # Move the rook
            rook_col = 0 if dst_col < src_col else 7
            rook_dst_col = dst_col + 1 if dst_col < src_col else dst_col - 1
            self.board[dst_row][rook_dst_col] = self.board[dst_row][rook_col]
            self.board[dst_row][rook_col] = None

        # Handle en passant capture
        if (piece.name == "pawn" and 
            abs(dst_col - src_col) == 1 and 
            not target and 
            self.en_passant_target and 
            dst == self.en_passant_target):
            captured_pawn_row = dst_row + (1 if piece.color == 'w' else -1)
            move_record['en_passant'] = (captured_pawn_row, dst_col)
            self.board[captured_pawn_row][dst_col] = None

        # Handle pawn promotion
        if piece.name == "pawn" and (dst_row == 0 or dst_row == 7):
            # For now, automatically promote to queen
            # TODO: Add promotion choice UI
            self.board[src_row][src_col] = Piece("queen", piece.color)
            move_record['promotion'] = "queen"

        # Update en passant target
        self.en_passant_target = None
        if piece.name == "pawn" and abs(dst_row - src_row) == 2:
            self.en_passant_target = (src_row + (dst_row - src_row) // 2, src_col)

        # Update king and rook moved status
        if piece.name == "king":
            if piece.color == 'w':
                self.white_king_moved = True
            else:
                self.black_king_moved = True
        elif piece.name == "rook":
            if piece.color == 'w':
                if src_col == 0:
                    self.white_rooks_moved[0] = True
                elif src_col == 7:
                    self.white_rooks_moved[1] = True
            else:
                if src_col == 0:
                    self.black_rooks_moved[0] = True
                elif src_col == 7:
                    self.black_rooks_moved[1] = True

        # Make the move
        self.board[dst_row][dst_col] = piece
        self.board[src_row][src_col] = None

        # Add move to history
        self.move_history.append(move_record)
        self.update_move_history(move_record)

        # Check for checkmate or stalemate
        if self.is_checkmate(self.turn):
            messagebox.showinfo("Game Over", f"Checkmate! {'White' if self.turn == 'b' else 'Black'} wins!")
            self.root.quit()
        elif self.is_stalemate(self.turn):
            messagebox.showinfo("Game Over", "Stalemate! The game is a draw.")
            self.root.quit()

    def is_checkmate(self, color):
        if not self.is_in_check(color):
            return False
        
        # Try all possible moves
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece and piece.color == color:
                    for dr in range(8):
                        for dc in range(8):
                            if self.valid_move((r, c), (dr, dc)):
                                # Simulate the move
                                temp_board = copy.deepcopy(self.board)
                                temp_board[dr][dc] = piece
                                temp_board[r][c] = None
                                
                                # Check if king is still in check
                                if not self.is_in_check_after_move(color, temp_board):
                                    return False
        return True

    def is_stalemate(self, color):
        if self.is_in_check(color):
            return False
        
        # Check if any legal moves are available
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece and piece.color == color:
                    for dr in range(8):
                        for dc in range(8):
                            if self.valid_move((r, c), (dr, dc)):
                                # Simulate the move
                                temp_board = copy.deepcopy(self.board)
                                temp_board[dr][dc] = piece
                                temp_board[r][c] = None
                                
                                # Check if move would not leave king in check
                                if not self.is_in_check_after_move(color, temp_board):
                                    return False
        return True

    def is_in_check(self, color):
        # Find the king
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece and piece.name == "king" and piece.color == color:
                    return self.is_square_under_attack((r, c), color)
        return False

    def is_in_check_after_move(self, color, board):
        # Find the king
        for r in range(8):
            for c in range(8):
                piece = board[r][c]
                if piece and piece.name == "king" and piece.color == color:
                    # Temporarily replace the board
                    original_board = self.board
                    self.board = board
                    result = self.is_square_under_attack((r, c), color)
                    self.board = original_board
                    return result
        return False

    def ai_move(self):
        if self.turn == self.ai_color:
            # Use minimax to find the best move
            best_score, best_move = self.minimax(self.board, self.search_depth, True)
            
            if best_move:
                self.make_move(best_move[0], best_move[1])
                self.turn = 'b' if self.turn == 'w' else 'w'
                self.draw_board()
            else:
                # No legal moves available
                if self.is_in_check(self.ai_color):
                    messagebox.showinfo("Game Over", f"Checkmate! {'White' if self.turn == 'b' else 'Black'} wins!")
                else:
                    messagebox.showinfo("Game Over", "Stalemate! The game is a draw.")
                self.root.quit()

    def minimax(self, board, depth, maximizing):
        if depth == 0:
            return self.evaluate_board(board), None

        # Generate all possible moves with move ordering
        all_moves = []
        color = self.ai_color if maximizing else self.get_opponent(self.ai_color)
        
        # First, collect all moves
        for r in range(8):
            for c in range(8):
                piece = board[r][c]
                if piece and piece.color == color:
                    for dr in range(8):
                        for dc in range(8):
                            if self.valid_move((r, c), (dr, dc)):
                                all_moves.append(((r, c), (dr, dc)))
        
        if not all_moves:
            # No legal moves available
            if self.is_in_check(color):
                return float('-inf') if maximizing else float('inf'), None
            else:
                return 0, None  # Stalemate
        
        # Order moves to prioritize captures and center control
        def move_score(move):
            src, dst = move
            piece = board[src[0]][src[1]]
            target = board[dst[0]][dst[1]]
            score = 0
            
            # Prioritize captures
            if target:
                score += PIECE_SCORES[target.name] * 10
            
            # Prioritize center control
            if dst[0] in [3,4] and dst[1] in [3,4]:
                score += 5
            
            # Prioritize developing pieces
            if piece.name in ['knight', 'bishop'] and src[0] in [0,7]:
                score += 3
            
            # Penalize moving the same piece repeatedly
            if len(self.move_history) > 0:
                last_move = self.move_history[-1]
                if last_move['src'] == src:
                    score -= 15
            
            return score
        
        # Sort moves by score
        all_moves.sort(key=move_score, reverse=maximizing)

        if maximizing:
            max_eval = float('-inf')
            best_move = None
            for move in all_moves:
                # Simulate the move
                temp_board = copy.deepcopy(board)
                src, dst = move
                temp_board[dst[0]][dst[1]] = temp_board[src[0]][src[1]]
                temp_board[src[0]][src[1]] = None
                
                # Temporarily replace the board
                original_board = self.board
                self.board = temp_board
                
                # Check if the move is legal
                king_pos = None
                for r in range(8):
                    for c in range(8):
                        piece = temp_board[r][c]
                        if piece and piece.name == "king" and piece.color == self.ai_color:
                            king_pos = (r, c)
                            break
                    if king_pos:
                        break
                
                if not self.is_square_under_attack(king_pos, self.ai_color):
                    eval = self.minimax(temp_board, depth - 1, False)[0]
                if eval > max_eval:
                        max_eval = eval
                        best_move = move
                
                # Restore the original board
                self.board = original_board
            
            return max_eval, best_move
        else:
            min_eval = float('inf')
            best_move = None
            for move in all_moves:
                # Simulate the move
                temp_board = copy.deepcopy(board)
                src, dst = move
                temp_board[dst[0]][dst[1]] = temp_board[src[0]][src[1]]
                temp_board[src[0]][src[1]] = None
                
                # Temporarily replace the board
                original_board = self.board
                self.board = temp_board
                
                # Check if the move is legal
                king_pos = None
                for r in range(8):
                    for c in range(8):
                        piece = temp_board[r][c]
                        if piece and piece.name == "king" and piece.color == self.get_opponent(self.ai_color):
                            king_pos = (r, c)
                            break
                    if king_pos:
                        break
                
                if not self.is_square_under_attack(king_pos, self.get_opponent(self.ai_color)):
                    eval = self.minimax(temp_board, depth - 1, True)[0]
                if eval < min_eval:
                        min_eval = eval
                        best_move = move
                
                # Restore the original board
                self.board = original_board
            
            return min_eval, best_move

    def evaluate_board(self, board):
        score = 0
        
        # Material score (doubled importance)
        material_score = 0
        for r in range(8):
            for c in range(8):
                piece = board[r][c]
                if piece:
                    val = PIECE_SCORES[piece.name]
                    material_score += val if piece.color == self.ai_color else -val
        score += material_score * 2

        # Development score
        development_score = 0
        for r in range(8):
            for c in range(8):
                piece = board[r][c]
                if piece and piece.color == self.ai_color:
                    if piece.name in ['knight', 'bishop']:
                        # Penalize pieces still on starting squares
                        if (piece.color == 'w' and r == 7) or (piece.color == 'b' and r == 0):
                            development_score -= 5
                        # Bonus for pieces in the center
                        if r in [3,4] and c in [3,4]:
                            development_score += 10
        score += development_score

        # Position score
        position_score = 0
        piece_square_tables = {
            'pawn': [
                [0,  0,  0,  0,  0,  0,  0,  0],
                [50, 50, 50, 50, 50, 50, 50, 50],
                [10, 10, 20, 30, 30, 20, 10, 10],
                [5,  5, 10, 25, 25, 10,  5,  5],
                [0,  0,  0, 20, 20,  0,  0,  0],
                [5, -5,-10,  0,  0,-10, -5,  5],
                [5, 10, 10,-20,-20, 10, 10,  5],
                [0,  0,  0,  0,  0,  0,  0,  0]
            ],
            'knight': [
                [-50,-40,-30,-30,-30,-30,-40,-50],
                [-40,-20,  0,  0,  0,  0,-20,-40],
                [-30,  0, 10, 15, 15, 10,  0,-30],
                [-30,  5, 15, 20, 20, 15,  5,-30],
                [-30,  0, 15, 20, 20, 15,  0,-30],
                [-30,  5, 10, 15, 15, 10,  5,-30],
                [-40,-20,  0,  5,  5,  0,-20,-40],
                [-50,-40,-30,-30,-30,-30,-40,-50]
            ],
            'bishop': [
                [-20,-10,-10,-10,-10,-10,-10,-20],
                [-10,  0,  0,  0,  0,  0,  0,-10],
                [-10,  0,  5, 10, 10,  5,  0,-10],
                [-10,  5,  5, 10, 10,  5,  5,-10],
                [-10,  0, 10, 10, 10, 10,  0,-10],
                [-10, 10, 10, 10, 10, 10, 10,-10],
                [-10,  5,  0,  0,  0,  0,  5,-10],
                [-20,-10,-10,-10,-10,-10,-10,-20]
            ],
            'rook': [
                [0,  0,  0,  0,  0,  0,  0,  0],
                [5, 10, 10, 10, 10, 10, 10,  5],
                [-5,  0,  0,  0,  0,  0,  0, -5],
                [-5,  0,  0,  0,  0,  0,  0, -5],
                [-5,  0,  0,  0,  0,  0,  0, -5],
                [-5,  0,  0,  0,  0,  0,  0, -5],
                [-5,  0,  0,  0,  0,  0,  0, -5],
                [0,  0,  0,  5,  5,  0,  0,  0]
            ],
            'queen': [
                [-20,-10,-10, -5, -5,-10,-10,-20],
                [-10,  0,  0,  0,  0,  0,  0,-10],
                [-10,  0,  5,  5,  5,  5,  0,-10],
                [-5,  0,  5,  5,  5,  5,  0, -5],
                [0,  0,  5,  5,  5,  5,  0, -5],
                [-10,  5,  5,  5,  5,  5,  0,-10],
                [-10,  0,  5,  0,  0,  0,  0,-10],
                [-20,-10,-10, -5, -5,-10,-10,-20]
            ],
            'king': [
                [-30,-40,-40,-50,-50,-40,-40,-30],
                [-30,-40,-40,-50,-50,-40,-40,-30],
                [-30,-40,-40,-50,-50,-40,-40,-30],
                [-30,-40,-40,-50,-50,-40,-40,-30],
                [-20,-30,-30,-40,-40,-30,-30,-20],
                [-10,-20,-20,-20,-20,-20,-20,-10],
                [20, 20,  0,  0,  0,  0, 20, 20],
                [20, 30, 10,  0,  0, 10, 30, 20]
            ]
        }

        for r in range(8):
            for c in range(8):
                piece = board[r][c]
                if piece:
                    if piece.color == self.ai_color:
                        table = piece_square_tables[piece.name]
                        position_score += table[r][c]
                    else:
                        table = piece_square_tables[piece.name]
                        position_score -= table[7-r][c]
        score += position_score

        # Mobility score
        ai_moves = len(self.generate_all_moves(board, self.ai_color))
        opponent_moves = len(self.generate_all_moves(board, self.get_opponent(self.ai_color)))
        mobility_score = (ai_moves - opponent_moves) * 0.1
        score += mobility_score

        # Center control score
        center_squares = [(3,3), (3,4), (4,3), (4,4)]
        center_score = 0
        for r, c in center_squares:
            piece = board[r][c]
            if piece:
                if piece.color == self.ai_color:
                    center_score += 5
                else:
                    center_score -= 5
        score += center_score

        # King safety score
        ai_king_pos = None
        opponent_king_pos = None
        for r in range(8):
            for c in range(8):
                piece = board[r][c]
                if piece and piece.name == "king":
                    if piece.color == self.ai_color:
                        ai_king_pos = (r, c)
                    else:
                        opponent_king_pos = (r, c)

        if ai_king_pos:
            # Penalize if king is in the center during opening/middlegame
            if ai_king_pos[0] in [3,4] and ai_king_pos[1] in [3,4]:
                score -= 20
            # Bonus for castling
            if ai_king_pos[1] in [2,6]:  # Kingside or queenside castled
                score += 15

        if opponent_king_pos:
            # Penalize if opponent's king is in the center during opening/middlegame
            if opponent_king_pos[0] in [3,4] and opponent_king_pos[1] in [3,4]:
                score += 20
            # Penalty for opponent castling
            if opponent_king_pos[1] in [2,6]:
                score -= 15

        # Pawn structure score
        pawn_score = 0
        for r in range(8):
            for c in range(8):
                piece = board[r][c]
                if piece and piece.name == "pawn":
                    # Penalize doubled pawns
                    for r2 in range(8):
                        if r2 != r and board[r2][c] and board[r2][c].name == "pawn" and board[r2][c].color == piece.color:
                            pawn_score -= 5 if piece.color == self.ai_color else 5
                    # Bonus for passed pawns
                    is_passed = True
                    for r2 in range(8):
                        for c2 in range(max(0, c-1), min(8, c+2)):
                            if board[r2][c2] and board[r2][c2].name == "pawn" and board[r2][c2].color != piece.color:
                                is_passed = False
                                break
                        if not is_passed:
                            break
                    if is_passed:
                        pawn_score += 10 if piece.color == self.ai_color else -10
        score += pawn_score

        return score

    def generate_all_moves(self, board, color):
        # Dummy implementation — replace with legal move generator
        moves = []
        for r in range(8):
            for c in range(8):
                piece = board[r][c]
                if piece and piece.color == color:
                    for dr in [-1, 0, 1]:
                        for dc in [-1, 0, 1]:
                            nr, nc = r+dr, c+dc
                            if 0 <= nr < 8 and 0 <= nc < 8:
                                if not board[nr][nc] or board[nr][nc].color != color:
                                    moves.append(((r, c), (nr, nc)))
        return moves

    def get_opponent(self, color):
        return 'b' if color == 'w' else 'w'

    def ask_player_side(self):
        # Create a new window for game setup
        setup_window = tk.Toplevel(self.root)
        setup_window.title("Game Setup")
        setup_window.geometry("400x300")
        setup_window.configure(bg="#2c3e50")
        
        # Make the window modal
        setup_window.transient(self.root)
        setup_window.grab_set()
        
        # Center the window
        setup_window.update_idletasks()
        width = setup_window.winfo_width()
        height = setup_window.winfo_height()
        x = (setup_window.winfo_screenwidth() // 2) - (width // 2)
        y = (setup_window.winfo_screenheight() // 2) - (height // 2)
        setup_window.geometry(f'{width}x{height}+{x}+{y}')
        
        # Create main frame
        main_frame = tk.Frame(setup_window, bg="#2c3e50")
        main_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
        
        # Add title
        title = tk.Label(main_frame, text="Chess Game Setup", 
                        font=("Arial", 16, "bold"), bg="#2c3e50", fg="white")
        title.pack(pady=10)
        
        # Add side selection
        side_frame = tk.Frame(main_frame, bg="#2c3e50")
        side_frame.pack(pady=10)
        
        side_label = tk.Label(side_frame, text="Choose your side:", 
                            font=("Arial", 12), bg="#2c3e50", fg="white")
        side_label.pack()
        
        side_var = tk.StringVar(value="white")
        white_btn = tk.Radiobutton(side_frame, text="White", variable=side_var, 
                                 value="white", bg="#2c3e50", fg="white", 
                                 selectcolor="#34495e", activebackground="#2c3e50")
        black_btn = tk.Radiobutton(side_frame, text="Black", variable=side_var, 
                                 value="black", bg="#2c3e50", fg="white", 
                                 selectcolor="#34495e", activebackground="#2c3e50")
        white_btn.pack(side=tk.LEFT, padx=10)
        black_btn.pack(side=tk.LEFT, padx=10)
        
        # Add difficulty selection
        diff_frame = tk.Frame(main_frame, bg="#2c3e50")
        diff_frame.pack(pady=10)
        
        diff_label = tk.Label(diff_frame, text="Choose AI difficulty:", 
                            font=("Arial", 12), bg="#2c3e50", fg="white")
        diff_label.pack()
        
        diff_var = tk.StringVar(value="3")
        diff_scale = tk.Scale(diff_frame, from_=1, to=5, orient=tk.HORIZONTAL,
                            variable=diff_var, bg="#2c3e50", fg="white",
                            troughcolor="#34495e", highlightthickness=0)
        diff_scale.pack(pady=5)
        
        # Add difficulty descriptions
        diff_desc = tk.Label(diff_frame, 
                           text="1: Beginner\n2: Novice\n3: Intermediate\n4: Advanced\n5: Expert",
                           font=("Arial", 10), bg="#2c3e50", fg="white", justify=tk.LEFT)
        diff_desc.pack()
        
        # Add start button
        def start_game():
            self.ai_color = 'b' if side_var.get() == "white" else 'w'
            self.search_depth = int(diff_var.get())
            setup_window.destroy()
            if self.ai_color == 'w':
                self.ai_move()
        
        start_btn = tk.Button(main_frame, text="Start Game", command=start_game,
                            font=("Arial", 12), bg="#3498db", fg="white",
                            activebackground="#2980b9", relief=tk.FLAT)
        start_btn.pack(pady=20)

# --------------------------- MAIN PROGRAM --------------------------- #

if __name__ == '__main__':
    root = tk.Tk()
    root.title("Chess with AI - Minimax + Alpha-Beta")
    game = ChessGame(root)
    root.mainloop()
