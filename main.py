import pygame as p
import Ai
from Board import Board
from Board import Move

# Pygame information
HEIGHT = WIDTH = 512
MAX_FPS = 15
# Size of each square
SQUARE_SIZE = HEIGHT // 8
# Images dict {int : image}
IMAGES = {}


# Loads the images from the images folder
def load_images():
    # List of all pieces in the game
    pieces = [1, 2, 3, 4, 5, 6, 11, 12, 13, 14, 15, 16]
    for piece in pieces:
        # Setting up the images dict
        IMAGES[piece] = p.image.load('images/' + str(piece) + ".png")


# Displays the board
def display_board(board, screen, selected_pos, highlighted):
    # Define the basic colors (0: light squares, 1: dark squares, 2: highlighted squares, 3: selected squares,
    # 4: last move)
    colors = [(232, 235, 239), (125, 135, 150), (255, 99, 71), p.Color('red'), p.Color('blue')]
    # Iterate through the whole board
    for row in range(8):
        for column in range(8):
            surf = p.Surface((SQUARE_SIZE, SQUARE_SIZE))  # Create a square
            surf.fill(colors[(row + column) % 2])  # Even squares are light, odds are dark
            screen.blit(surf, (
                column * SQUARE_SIZE, row * SQUARE_SIZE))  # Place the surface on the correct position on the board
            if selected_pos == (row, column):  # Check if square is the selected one
                selected_square = p.Surface((SQUARE_SIZE, SQUARE_SIZE))  # Create new square
                selected_square.fill(colors[3])  # Color it
                selected_square.set_alpha(50)  # Set the alpha, so one can see the square under it
                screen.blit(selected_square, (
                    column * SQUARE_SIZE, row * SQUARE_SIZE))  # Place the surface on the correct position on the board
            if (row, column) in highlighted:  # Check if square is in highlighted
                square = p.Surface((SQUARE_SIZE, SQUARE_SIZE))  # Create new square
                square.fill(colors[2])  # Color it
                square.set_alpha(120)  # Set the alpha, so one can see the square under it
                screen.blit(square, (
                    column * SQUARE_SIZE, row * SQUARE_SIZE))  # Place the surface on the correct position on the board
            if len(board.move_history) > 0:  # Check if there is a last move
                if (row, column) == board.move_history[
                    -1].new_pos:  # Check if the new position of the last move is at the current position of iteration
                    square = p.Surface((SQUARE_SIZE, SQUARE_SIZE))  # Create new square
                    square.fill(colors[4])  # Color it
                    square.set_alpha(30)  # Set the alpha, so one can see the square under it
                    screen.blit(square, (
                        column * SQUARE_SIZE,
                        row * SQUARE_SIZE))  # Place the surface on the correct position on the board
                if (row, column) == board.move_history[
                    -1].old_pos:  # Check if the new position of the last move is at the current position of iteration
                    square = p.Surface((SQUARE_SIZE, SQUARE_SIZE))  # Create new square
                    square.fill(colors[4])  # Color it
                    square.set_alpha(30)  # Set the alpha, so one can see the square under it
                    screen.blit(square, (
                        column * SQUARE_SIZE,
                        row * SQUARE_SIZE))  # Place the surface on the correct position on the board
            if board.state[row][
                column] != 0:  # Place the image of the current piece (last if condition, so there is no layer over it
                image = IMAGES[board.state[row][column]]  # Set the correct image
                screen.blit(image,
                            p.Rect(column * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE,
                                   SQUARE_SIZE))  # Place it on the screen


# Takes an event and handles it => return if moved or not + highlighted squares + selected position
def handle_human_turn(event, board, legal_moves, selected_pos, highlighted):
    # Declare new variables to return
    new_highlighted = []
    new_selected_pos = ()
    # Check if event is a click
    if event.type == p.MOUSEBUTTONDOWN:
        # Get the mouse position
        position = p.mouse.get_pos()
        # Get column on chess board
        c = position[0] // SQUARE_SIZE
        # Get row on chess board
        r = position[1] // SQUARE_SIZE

        # Check if there is an ally piece on the clicked square and the old selected position is empty
        # => A new piece was selected for the move
        if board.state[r][c] != 0 and selected_pos == () and (
                (0 < board.white_move and board.state[r][c] < 10) or (
                board.state[r][c] > 10 and not board.white_move)):
            # Set the new selected position
            new_selected_pos = (r, c)
            # Add the legal moves from this position into the new highlighted
            # => the player can see his options with the selected piece
            for move in legal_moves:
                if move.old_pos == new_selected_pos:
                    new_highlighted.append(move.new_pos)
            # Not moved yet, update highlighted squares, there is a new selected position
            return False, new_highlighted, new_selected_pos
        # Check if there is already a selected position
        elif selected_pos != ():
            # Check if the player clicks on another of his pieces
            # switch the selected position and the highlighted
            if selected_pos != (r, c) and (board.state[r][c] != 0 and
                                           (0 < board.white_move and board.state[r][c] < 10) or (
                                                   board.state[r][c] > 10 and not board.white_move)):
                # Set the selected position
                new_selected_pos = (r, c)
                # Add the legal moves from this position into highlighted
                # => the player can see his options with the selected piece
                for move in legal_moves:
                    if move.old_pos == new_selected_pos:
                        new_highlighted.append(move.new_pos)
                # Not moved yet, new highlighted squares, the selected position switched
                return False, new_highlighted, new_selected_pos
            # Check if the player clicked on a new square
            # The selected position is not equal to the square the player just clicked
            elif selected_pos != (r, c):
                # Define the move (old pos = selected_pos, new pos = (r, c))
                move = Move(board.state, selected_pos, (r, c))
                # Check if move is legal
                for legal_move in legal_moves:
                    if move == legal_move:
                        # Make move
                        # (Make the legal move, because it could have special booleans e.g. castling)
                        board.make_move(legal_move)
                        # Moved = True, reset highlighted, reset selected position
                        return True, new_highlighted, new_selected_pos
                # It was not a legal move
                # Not moved yet, reset highlighted, reset selected position
                return False, new_highlighted, new_selected_pos
            else:
                # The same position was clicked again (selected pos == (r, c))
                # => deselect + highlighted empty
                # Not moved yet, reset highlighted, reset selected position
                return False, new_highlighted, new_selected_pos
        else:
            # => deselect + highlighted empty
            # Not moved yet, reset highlighted, reset selected position
            return False, new_highlighted, new_selected_pos
    else:
        # Nothing happened => return the old values
        return False, highlighted, selected_pos


# Main Method with game loop
def main():
    # Init pygame and setup screen
    p.init()
    p.display.set_caption('Chess')
    p.font.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()

    # Initialize a new board
    board = Board()

    # Load the images
    load_images()

    # Game loop boolean
    playing = True
    # Moved boolean (set to true for 1 iteration if moved)
    moved = False
    # Player 1 (true if human, false if ai)
    player1 = True
    # Player 2 (ture if human, false if ai)
    player2 = False
    # Keeps track of the current selected position (row, column)
    selected_pos = ()
    # Keeps track of the legal moves in the current position
    legal_moves = board.get_legal_moves()
    # Keeps track of the highlighted squares on the board
    highlighted = []
    # Monte Carlo Tree training Mode
    training_mode = False

    # Train the Monte Carlo Tree
    if training_mode:
        Ai.train_monte_carlo_tree(board, screen, clock)

    # MAIN GAME LOOP
    while playing and not training_mode:
        # Iterating through every event which pygame receives (events can be mouse clicks or key presses)
        for event in p.event.get():
            # Check if the application closes
            if event.type == p.QUIT:
                # Stop the game loop
                playing = False
            # Check if its a human turn
            elif ((player1 and board.white_move) or (
                    player2 and not board.white_move)) and not moved:  # Its a human turn
                # Update variables with handle_human_turn
                moved, highlighted, selected_pos = handle_human_turn(event, board, legal_moves, selected_pos,
                                                                     highlighted)

        # Display the board based on the state, selected position and highlighted squares
        display_board(board, screen, selected_pos, highlighted)

        # Pygame refresh
        p.display.flip()
        clock.tick(MAX_FPS)

        # Setup a new move
        if moved:
            moved = False
            if board.checkmate:
                print("Checkmate")
            elif board.stalemate:
                print('Stalemate')
            legal_moves = board.get_legal_moves()

        # AI has to move
        if not (player1 and board.white_move) and not (player2 and not board.white_move):
            # Find the best move

            move = Ai.find_best_move(board, legal_moves)
            if move is not None:
                board.make_move(move)
                moved = True


if __name__ == "__main__":
    # Run the main method
    main()
    # Quit the pygame application
    p.quit()
