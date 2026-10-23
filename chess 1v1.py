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

# Real Chess Unicode Symbols
UNICODE_PIECES = {
    'r': '♜', 'n': '♞', 'b': '♝', 'q': '♛', 'k': '♚', 'p': '♟',
    'R': '♖', 'N': '♘', 'B': '♗', 'Q': '♕', 'K': '♔', 'P': '♙'
}

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

def draw_game_over(screen, board, font_large, font_small):
    """Renders Win/Loss/Draw Banner"""
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    if board.is_checkmate():
        winner = "White" if board.turn == chess.BLACK else "Black"
        title = f"{winner.upper()} WINS!"
        sub = f"Checkmate! {winner} wins the game."
        color = (0, 255, 127) if winner == "White" else (255, 69, 0)
    else:
        title = "DRAW!"
        sub = "Stalemate or Insufficient Material."
        color = (255, 215, 0)

    text_surface = font_large.render(title, True, color)
    text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40))
    screen.blit(text_surface, text_rect)

    sub_surface = font_small.render(sub, True, (255, 255, 255))
    sub_rect = sub_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 10))
    screen.blit(sub_surface, sub_rect)

    restart_surface = font_small.render("Press 'R' to Restart", True, (200, 200, 200))
    restart_rect = restart_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 60))
    screen.blit(restart_surface, restart_rect)

def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Chess 1v1 - Local Multiplayer")
    clock = pygame.time.Clock()
    
    board = chess.Board()
    font = get_chess_font(52)
    font_large = pygame.font.SysFont("Arial", 48, bold=True)
    font_small = pygame.font.SysFont("Arial", 22)
    
    selected_square = None
    
    running = True
    while running:
        legal_moves = list(board.legal_moves)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            elif event.type == pygame.KEYDOWN:
                # Press 'R' to restart
                if event.key == pygame.K_r:
                    board.reset()
                    selected_square = None
                # Press 'U' to undo last move
                elif event.key == pygame.K_u and len(board.move_stack) >= 1:
                    board.pop()
                    selected_square = None
                
            elif event.type == pygame.MOUSEBUTTONDOWN and not board.is_game_over():
                location = pygame.mouse.get_pos()
                col = location[0] // SQ_SIZE
                row = location[1] // SQ_SIZE
                clicked_square = chess.square(col, 7 - row)
                
                if selected_square is None:
                    piece = board.piece_at(clicked_square)
                    # Select piece matching current player's turn
                    if piece and piece.color == board.turn:
                        selected_square = clicked_square
                else:
                    # Check for normal moves and promotions
                    move = chess.Move(selected_square, clicked_square)
                    promotion_move = chess.Move(selected_square, clicked_square, promotion=chess.QUEEN)
                    
                    if move in legal_moves:
                        board.push(move)
                    elif promotion_move in legal_moves:
                        board.push(promotion_move)
                    
                    selected_square = None

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