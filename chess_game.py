import pygame
import chess
import sys


# Initialize Pygame
pygame.init()

# Setup Display
WIDTH, HEIGHT = 600, 600
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
FPS = 30

# Colors
COLOR_LIGHT = (240, 217, 181)
COLOR_DARK = (181, 136, 99)
COLOR_SELECT = (255, 255, 102)
COLOR_HIGHLIGHT = (106, 135, 89)
COLOR_BANNER = (0, 0, 0, 200)

# Real Chess Unicode Symbols
UNICODE_PIECES = {
    'r': '♜', 'n': '♞', 'b': '♝', 'q': '♛', 'k': '♚', 'p': '♟',
    'R': '♖', 'N': '♘', 'B': '♗', 'Q': '♕', 'K': '♔', 'P': '♙'
}

# Piece Values for AI Evaluation
PIECE_VALUES = {
    chess.PAWN: 100, chess.KNIGHT: 320, chess.BISHOP: 330,
    chess.ROOK: 500, chess.QUEEN: 900, chess.KING: 20000
}

# Positional Advantage Tables (PST) to make AI play strategically
PAWN_TABLE = [
     0,  0,  0,  0,  0,  0,  0,  0,
    50, 50, 50, 50, 50, 50, 50, 50,
    10, 10, 20, 30, 30, 20, 10, 10,
     5,  5, 10, 27, 27, 10,  5,  5,
     0,  0,  0, 20, 20,  0,  0,  0,
     5, -5,-10,  0,  0,-10, -5,  5,
     5, 10, 10,-20,-20, 10, 10,  5,
     0,  0,  0,  0,  0,  0,  0,  0
]

KNIGHT_TABLE = [
   -50,-40,-30,-30,-30,-30,-40,-50,
   -40,-20,  0,  0,  0,  0,-20,-40,
   -30,  0, 10, 15, 15, 10,  0,-30,
   -30,  5, 15, 20, 20, 15,  5,-30,
   -30,  0, 15, 20, 20, 15,  0,-30,
   -30,  5, 10, 15, 15, 10,  5,-30,
   -40,-20,  0,  5,  5,  0,-20,-40,
   -50,-40,-30,-30,-30,-30,-40,-50
]

def get_chess_font(size=52):
    """Loads a font that supports Chess Symbols"""
    fonts_to_try = ["Apple Symbols", "Arial Unicode MS", "DejaVu Sans", "Segoe UI Symbol"]
    for font_name in fonts_to_try:
        try:
            return pygame.font.SysFont(font_name, size)
        except:
            pass
    return pygame.font.Font(None, size)

def draw_board(screen):
    """Draws Chessboard Grid"""
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = COLOR_LIGHT if (r + c) % 2 == 0 else COLOR_DARK
            pygame.draw.rect(screen, color, pygame.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))

def draw_pieces(screen, board, font):
    """Renders Chess Pieces"""
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            col = chess.square_file(square)
            row = 7 - chess.square_rank(square)
            symbol = UNICODE_PIECES[piece.symbol()]
            
            text_color = (255, 255, 255) if piece.color == chess.WHITE else (20, 20, 20)
            center_x = col * SQ_SIZE + SQ_SIZE // 2
            center_y = row * SQ_SIZE + SQ_SIZE // 2
            
            if piece.color == chess.WHITE:
                shadow_surface = font.render(symbol, True, (50, 50, 50))
                shadow_rect = shadow_surface.get_rect(center=(center_x + 2, center_y + 2))
                screen.blit(shadow_surface, shadow_rect)

            text_surface = font.render(symbol, True, text_color)
            text_rect = text_surface.get_rect(center=(center_x, center_y))
            screen.blit(text_surface, text_rect)

def draw_highlights(screen, selected_square, legal_moves):
    """Highlights selected piece and valid moves"""
    if selected_square is not None:
        col = chess.square_file(selected_square)
        row = 7 - chess.square_rank(selected_square)
        s = pygame.Surface((SQ_SIZE, SQ_SIZE))
        s.set_alpha(160)
        s.fill(COLOR_SELECT)
        screen.blit(s, (col * SQ_SIZE, row * SQ_SIZE))

        for move in legal_moves:
            if move.from_square == selected_square:
                to_col = chess.square_file(move.to_square)
                to_row = 7 - chess.square_rank(move.to_square)
                pygame.draw.circle(screen, COLOR_HIGHLIGHT, 
                                   (to_col * SQ_SIZE + SQ_SIZE // 2, to_row * SQ_SIZE + SQ_SIZE // 2), 12)

def evaluate_board(board):
    """Evaluates position using piece values + board positions"""
    if board.is_checkmate():
        return -99999 if board.turn == chess.BLACK else 99999
    if board.is_stalemate() or board.is_insufficient_material():
        return 0
    
    score = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            val = PIECE_VALUES[piece.piece_type]
            
            # Positional score additions
            position_score = 0
            if piece.piece_type == chess.PAWN:
                position_score = PAWN_TABLE[square if piece.color == chess.WHITE else chess.square_mirror(square)]
            elif piece.piece_type == chess.KNIGHT:
                position_score = KNIGHT_TABLE[square if piece.color == chess.WHITE else chess.square_mirror(square)]

            total_val = val + position_score
            score += total_val if piece.color == chess.WHITE else -total_val
            
    return score

def minimax(board, depth, alpha, beta, is_maximizing):
    """Minimax Algorithm with Alpha-Beta Pruning"""
    if depth == 0 or board.is_game_over():
        return evaluate_board(board), None

    legal_moves = list(board.legal_moves)
    best_move = None

    if is_maximizing:
        max_eval = -999999
        for move in legal_moves:
            board.push(move)
            eval_score, _ = minimax(board, depth - 1, alpha, beta, False)
            board.pop()
            if eval_score > max_eval:
                max_eval = eval_score
                best_move = move
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break
        return max_eval, best_move
    else:
        min_eval = 999999
        for move in legal_moves:
            board.push(move)
            eval_score, _ = minimax(board, depth - 1, alpha, beta, True)
            board.pop()
            if eval_score < min_eval:
                min_eval = eval_score
                best_move = move
            beta = min(beta, eval_score)
            if beta <= alpha:
                break
        return min_eval, best_move

def draw_game_over(screen, board, font_large, font_small):
    """Renders Win/Loss/Draw Banner"""
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180)) # Semi-transparent dark background
    screen.blit(overlay, (0, 0))

    if board.is_checkmate():
        if board.turn == chess.BLACK:
            title = "YOU WIN!"
            sub = "Checkmate by White!"
            color = (0, 255, 127)
        else:
            title = "GAME OVER!"
            sub = "AI (Black) Won by Checkmate!"
            color = (255, 69, 0)
    else:
        title = "DRAW!"
        sub = "Stalemate or Insufficient Material."
        color = (255, 215, 0)

    # Main Result
    text_surface = font_large.render(title, True, color)
    text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40))
    screen.blit(text_surface, text_rect)

    # Subtext
    sub_surface = font_small.render(sub, True, (255, 255, 255))
    sub_rect = sub_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 10))
    screen.blit(sub_surface, sub_rect)

    # Restart Hint
    restart_surface = font_small.render("Press 'R' to Restart", True, (200, 200, 200))
    restart_rect = restart_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 60))
    screen.blit(restart_surface, restart_rect)

def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Smart Chess - Player vs AI")
    clock = pygame.time.Clock()
    
    board = chess.Board()
    font = get_chess_font(52)
    font_large = pygame.font.SysFont("Arial", 48, bold=True)
    font_small = pygame.font.SysFont("Arial", 22)
    
    selected_square = None
    ai_depth = 2  # Set to 3 for even stronger AI (will take ~1 sec per move)
    
    running = True
    while running:
        legal_moves = list(board.legal_moves)

        # PLAYER & SYSTEM INPUTS
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            elif event.type == pygame.KEYDOWN:
                # Press 'R' to restart
                if event.key == pygame.K_r:
                    board.reset()
                    selected_square = None
                # Press 'U' to undo last move (Undo both AI & Player move)
                elif event.key == pygame.K_u and len(board.move_stack) >= 2:
                    board.pop()
                    board.pop()
                    selected_square = None
                
            elif event.type == pygame.MOUSEBUTTONDOWN and board.turn == chess.WHITE and not board.is_game_over():
                location = pygame.mouse.get_pos()
                col = location[0] // SQ_SIZE
                row = location[1] // SQ_SIZE
                clicked_square = chess.square(col, 7 - row)
                
                if selected_square is None:
                    piece = board.piece_at(clicked_square)
                    if piece and piece.color == chess.WHITE:
                        selected_square = clicked_square
                else:
                    move = chess.Move(selected_square, clicked_square)
                    promotion_move = chess.Move(selected_square, clicked_square, promotion=chess.QUEEN)
                    
                    if move in legal_moves:
                        board.push(move)
                    elif promotion_move in legal_moves:
                        board.push(promotion_move)
                    
                    selected_square = None

        # COMPUTER TURN (BLACK)
        if board.turn == chess.BLACK and not board.is_game_over():
            pygame.time.delay(200) # Small delay for smooth feel
            _, ai_move = minimax(board, ai_depth, -999999, 999999, False)
            if ai_move:
                board.push(ai_move)

        # RENDER UI
        draw_board(screen)
        draw_highlights(screen, selected_square, legal_moves)
        draw_pieces(screen, board, font)
        
        # DRAW GAME OVER SCREEN
        if board.is_game_over():
            draw_game_over(screen, board, font_large, font_small)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()






