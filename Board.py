# The class of the board and the state of the game
class Board:
    # Initialize the board
    def __init__(self):
        # Start position and state of the game:
        # 0: empty square; 1/11: pawn; 2/12: knight; 3/13: bishop;
        # 4/14: rook; 5/15: queen; 6/16: king
        self.state = [
            [14, 12, 13, 15, 16, 13, 12, 14],
            [11, 11, 11, 11, 11, 11, 11, 11],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [1, 1, 1, 1, 1, 1, 1, 1],
            [4, 2, 3, 5, 6, 3, 2, 4],
        ]
        # Keeps track of whites king position (row, column)
        self.w_king_pos = (7, 4)
        # Keeps track of blacks king position (row, column)
        self.b_king_pos = (0, 4)

        # List of all the moves which were played
        self.move_history = []

        # Indicating whether white has to move or not
        self.white_move = True
        # Set to true if checkmate
        self.checkmate = False
        # Set to true if stalemate
        self.stalemate = False
        # Set to true if in check
        self.check = False
        # List of the checking pieces (row, column, direction from king)
        self.checks = []
        # List of the pins (row, column, direction)
        self.pins = []

        # Keeps track of an en passant square, if there is one (row, column)
        self.en_passant_square = ()

        # Castling rights
        self.b_king_castle = True
        self.w_king_castle = True
        self.b_queen_castle = True
        self.w_queen_castle = True

    # Makes a move;
    # undo has to be true if the move should be deleted => do the move backwards
    def make_move(self, move, undo=False):
        # Delete move if undo
        if undo:
            self.move_history.remove(move)
        # Append move if not undo
        else:
            self.move_history.append(move)

        # Undo checkmate and stalemate
        if undo:
            self.checkmate = False
            self.stalemate = False

        # Updates the castling rights
        self.update_castling_rights(move, undo)

        # Update the kings positions, if king was moved
        if move.piece == 6:  # piece is white king
            self.w_king_pos = move.new_pos if not undo else move.old_pos  # if undo the old position of the move is
            # the current king position
        elif move.piece == 16:  # piece is black king
            self.b_king_pos = move.new_pos if not undo else move.old_pos  # if undo the old position of the move is
            # the current king position

        # Move the piece
        # Set the old square (new square if undo) to 0 => empty
        if not undo:
            self.state[move.old_pos[0]][move.old_pos[1]] = 0
        else:
            self.state[move.new_pos[0]][move.new_pos[1]] = move.captured_piece
        # Set the new square (old square if undo) to the piece which was moved
        self.state[move.new_pos[0] if not undo else move.old_pos[0]][
            move.new_pos[1] if not undo else move.old_pos[1]] = move.piece

        # Makes special moves (en passant, castling, promotion)
        self.make_special_move(move, undo)

        # Switch the player
        self.white_move = not self.white_move

        # Check for a draw
        self.check_draw()

    # Reset the board
    def reset_board(self):
        # Reset the state
        self.state = [
            [14, 12, 13, 15, 16, 13, 12, 14],
            [11, 11, 11, 11, 11, 11, 11, 11],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [1, 1, 1, 1, 1, 1, 1, 1],
            [4, 2, 3, 5, 6, 3, 2, 4],
        ]
        # Reset kings positions
        self.w_king_pos = (7, 4)
        self.b_king_pos = (0, 4)

        # Reset the move_history
        self.move_history = []

        # Indicating whether white has to move or not
        self.white_move = True
        # Set to true if checkmate
        self.checkmate = False
        # Set to true if stalemate
        self.stalemate = False
        # Set to true if in check
        self.check = False
        # List of the checking pieces (row, column, direction from king)
        self.checks = []
        # List of the pins (row, column, direction)
        self.pins = []

        # Keeps track of an en passant square, if there is one (row, column)
        self.en_passant_square = ()

        # Castling rights
        self.b_king_castle = True
        self.w_king_castle = True
        self.b_queen_castle = True
        self.w_queen_castle = True

    # Takes a move and checks if this move breaks castling rights and updates them;
    # If undo it checks if the move broke castling rights
    def update_castling_rights(self, move, undo):
        if undo:
            if move.broke_queen_side_castle:
                if move.piece < 10:  # Check if move broke white queen side castle
                    self.w_queen_castle = True
                else:  # Move broke black queen side castle
                    self.b_queen_castle = True
            if move.broke_king_side_castle:
                if move.piece < 10:  # Check if move broke white king side castle
                    self.w_king_castle = True
                else:  # Move broke black king side castle
                    self.b_king_castle = True
        else:
            # Check if moved piece is a white rook
            if move.piece == 4:
                # Broke white queen side castle
                if move.old_pos == (7, 0) and self.w_queen_castle:
                    self.w_queen_castle = False
                    move.broke_queen_side_castle = True
                # Broke white king side castle
                elif move.old_pos == (7, 7) and self.w_king_castle:
                    self.w_king_castle = False
                    move.broke_king_side_castle = True
            # Check if piece is a black rook
            elif move.piece == 14:
                # Broke black queen side castle
                if move.old_pos == (0, 0) and self.b_queen_castle:
                    self.b_queen_castle = False
                    move.broke_queen_side_castle = True
                # Broke black king side castle
                elif move.old_pos == (0, 7) and self.b_king_castle:
                    self.b_king_castle = False
                    move.broke_king_side_castle = True
            # Check if piece is white king and there are castling rights left
            elif move.piece == 6 and (self.w_king_castle or self.w_queen_castle):
                # Determine the castling right, which the move broke
                # (king move breaks both, but if one right was already broken,
                # the king move broke only one)
                if self.w_king_castle:
                    move.broke_king_side_castle = True
                if self.w_queen_castle:
                    move.broke_queen_side_castle = True
                self.w_king_castle = False
                self.w_queen_castle = False
            # Check if piece is black king and there are castling rights left
            elif move.piece == 16 and (self.b_king_castle or self.b_queen_castle):
                # Determine the castling right, which the move broke
                # (king move breaks both, but if one right was already broken,
                # the king move broke only one)
                if self.b_king_castle:
                    move.broke_king_side_castle = True
                if self.b_queen_castle:
                    move.broke_queen_side_castle = True
                self.b_king_castle = False
                self.b_queen_castle = False

    # Make any special move
    # If undo it makes the move backwards
    def make_special_move(self, move, undo):
        # Check if move is a pawn promotion (the undo logic is already completed in the main make move function)
        if move.promotion and not undo:
            # Make a queen (5: white queen; 15: black queen)
            self.state[move.new_pos[0]][move.new_pos[1]] = 5 if self.white_move else 15
        # Check if move is an en passant capture
        elif move.en_passant_capture:
            if not undo:
                # Capture the piece on the row of the old position and the column of the new postion
                self.state[move.old_pos[0]][move.new_pos[1]] = 0
                # Reset en passant square
                self.en_passant_square = ()
            else:
                # Undo the capture => create pawn at the captured square (1: white pawn; 11: black pawn)
                self.state[move.old_pos[0]][move.new_pos[1]] = 1 if self.white_move else 11
                # Set the en passant square
                self.en_passant_square = (move.old_pos[0], move.new_pos[1])
        # Check if move creates en passant square => pawn moves two squares up
        elif (move.piece == 1 or move.piece == 11) and abs(move.new_pos[0] - move.old_pos[0]) == 2:
            if not undo:
                # Update the en passant square
                self.en_passant_square = (2 if not self.white_move else 5, move.new_pos[1])
            else:
                # Reset the en_passant square
                self.en_passant_square = ()
        # Check if move is castling move
        elif move.is_castle:
            if not undo:
                # White queen side
                if move.new_pos == (7, 2):
                    self.state[7][3] = 4  # Set the rook
                    self.state[7][0] = 0
                # White king side
                elif move.new_pos == (7, 6):
                    self.state[7][5] = 4  # Set the rook
                    self.state[7][7] = 0
                # Black queen side
                elif move.new_pos == (0, 2):
                    self.state[0][3] = 14  # Set the rook
                    self.state[0][0] = 0
                # Black king side
                elif move.new_pos == (0, 6):
                    self.state[0][5] = 14  # Set the rook
                    self.state[0][7] = 0
            else:
                # White queen side
                if move.new_pos == (7, 2):
                    self.state[7][3] = 0
                    self.state[7][0] = 4  # Set the rook
                # White king side
                elif move.new_pos == (7, 6):
                    self.state[7][5] = 0
                    self.state[7][7] = 4  # Set the rook
                # Black queen side
                elif move.new_pos == (0, 2):
                    self.state[0][3] = 0
                    self.state[0][0] = 14  # Set the rook
                # Black king side
                elif move.new_pos == (0, 6):
                    self.state[0][5] = 0
                    self.state[0][7] = 14  # Set the rook
        else:
            # No en passant
            self.en_passant_square = ()

    # Takes a (row, col) and returns if its attacked, how often its attacked and if there are pins on this square
    # if only_attack = True, the function will only return a bool value
    def check_square(self, r, c, only_attack=False):
        # Initialize return values
        attacked = False
        attackers = []
        pins = []

        # Directions: (row, col) 0-3 = Rook Directions; 4-7 = Bishop Directions
        directions = [(-1, 0), (0, 1), (0, -1), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]

        # Iterate through all the directions
        for j in range(len(directions)):
            d = directions[j]  # The current direction
            possible_pin = ()  # Keeps track of possible pins in this direction
            # Iterate in the direction
            for i in range(1, 8):
                current_r = r + (i * d[0])  # Set row of current square (the start row + the steps in a direction)
                current_c = c + (i * d[1])  # Set column of current square (the start col + the steps in a direction)
                # Check if the square is still on the board
                if 0 <= current_r < 8 and 0 <= current_c < 8:
                    piece = self.state[current_r][current_c]  # Get the piece on the current square
                    # Check if the piece is your own piece and not a king => because you cannot hide behind the king
                    if ((piece > 10 and not self.white_move) or (0 < piece < 10 and self.white_move)) and (
                            piece != 16 and piece != 6):
                        # Check if there is already a possible pin in that direction (if so there is no danger for
                        # attacks and pins, because two of our pieces are stacked up in that direction) => break
                        if possible_pin != ():
                            break
                        else:
                            possible_pin = (
                                current_r, current_c, d[0], d[1])  # There is a new possible pin in that direction
                    # Check if there is an enemy piece
                    elif (piece > 10 and self.white_move) or (0 < piece < 10 and not self.white_move):
                        # Check if the enemy piece can attack Check if there is a rook and the direction is a rook
                        # direction Check if there is a bishop and the direction is a bishop direction Check if there
                        # is a pawn and the direction is a direction from which the pawn can attack (different for
                        # black and white) Check if there is a queen Check if there is a king and the distance is 1
                        if (0 <= j <= 3 and (piece == 14 or piece == 4)) or (
                                4 <= j <= 7 and (piece == 13 or piece == 3)) or (
                                i == 1 and ((piece == 1 and 6 <= j <= 7) or (piece == 11 and 4 <= j <= 5))) or (
                                piece == 15 or piece == 5) or (i == 1 and (piece == 6 or piece == 16)):
                            # Check if there is a possible pin in the direction d
                            if possible_pin != ():
                                pins.append(possible_pin)  # The possible pin is now a real pin, because of the attacker

                            else:
                                # There is a direct attacker
                                attacked = True
                                attackers.append((current_r, current_c, d[0], d[1]))
                                break
                        else:
                            # There is an enemy piece which can not attack, so we do not have to check further in
                            # that direction
                            break
                else:
                    # Out of borders
                    break

        # Knight moves
        knight_moves = [(-1, -2), (-2, -1), (-2, 1), (-1, 2), (1, -2), (2, -1), (2, 1), (1, 2)]
        # Iterate through all the knight moves from start position
        for m in knight_moves:
            current_r = r + m[0]  # Set row of current square (the start row + the knight move)
            current_c = c + m[1]  # Set column of current square (the start column + the knight move)
            # Check if current square is still on the board
            if 0 <= current_r < 8 and 0 <= current_c < 8:
                piece = self.state[current_r][current_c]  # Get the piece from the current square
                # Check if the piece is a enemy knight, so it can attack the square
                if (piece == 12 and self.white_move) or (piece == 2 and not self.white_move):
                    # There is an attacking knight
                    attacked = True
                    attackers.append((current_r, current_c, m[0], m[1]))

        if only_attack:
            return attacked
        return attacked, attackers, pins

    # Check for a draw (no capture or pawn move in the last 50 moves)
    def check_draw(self):
        if len(self.move_history) >= 50:
            is_draw = True
            for move in self.move_history[-50:]:
                if move.captured_piece != 0 or move.piece == 1 or move.piece == 11:
                    is_draw = False
            if is_draw:
                self.stalemate = True
    # Get all legal moves in current position
    def get_legal_moves(self):
        # Prepare the return list
        moves = []
        # Get the current king row out of the king position of the correct color
        king_r = self.w_king_pos[0] if self.white_move else self.b_king_pos[0]
        # Get the current king col out of the king position of the correct color
        king_c = self.w_king_pos[1] if self.white_move else self.b_king_pos[1]
        # Update the check, pins, checks of board (check the square of the king)
        self.check, self.checks, self.pins = self.check_square(king_r, king_c)
        # Check if board is in check
        if self.check:
            # Check if there is only one check
            if len(self.checks) == 1:
                # Get all possible moves
                moves = self.get_moves()

                # Get the information about the check
                check_info = self.checks[0]
                check_r = check_info[0]  # Set the row of the checking piece
                check_c = check_info[1]  # Set the column of the checking piece
                checking_piece = self.state[check_r][check_c]  # Get the checking piece

                # List of the valid squares to avoid the check
                valid_squares = []

                # Check if the checking piece is a knight
                if checking_piece == 2 or checking_piece == 12:
                    # Knights can not be blocked, so the only valid square is the capture of the knight
                    valid_squares = [(check_r, check_c)]
                else:
                    # Iterate through the squares in the direction of the check
                    for i in range(1, 8):
                        # Blocking the check is a valid square
                        # (Going i steps in the check direction, which is in the checking_info 2/3)
                        valid_square = (king_r + check_info[2] * i, king_c + check_info[3] * i)
                        valid_squares.append(valid_square)
                        # Check if we iterated to the square where the attacker is and break
                        if valid_square[0] == check_r and valid_square[1] == check_c:
                            break

                # Remove every move which is not ending at one of the valid squares
                # Iteration backwards through all the possible moves, because we want to remove moves
                # If the iteration would be forward, the indexes would shift
                for i in range(len(moves) - 1, -1, -1):
                    # Check if piece of the move is a king => we cant block a check with our king
                    if moves[i].piece != 6 and moves[i].piece != 16:
                        # Check if the new position of the move is a valid square
                        if not moves[i].new_pos in valid_squares:
                            moves.remove(moves[i])
                    # Check if move is castling move and remove it (you can not castle if you are in check)
                    elif moves[i].is_castle:
                        moves.remove(moves[i])
            else:
                # If there is more than one check we can not block them, because there are at least two
                # => we have to move the king, so the only valid moves are king moves
                self.get_king_moves(king_r, king_c, moves)
        else:
            # There is no check, so all possible moves are legal
            moves = self.get_moves()

        # Check if there are no moves
        if len(moves) == 0:

            if self.check:
                self.checkmate = True
            else:
                self.stalemate = True

        # Return all the legal moves
        return moves

    # Get all possible moves in current position
    def get_moves(self):
        # List for all moves
        moves = []
        # Iterate through state (row, col)
        for row in range(8):
            for col in range(8):
                # Get piece at (row, col)
                piece = self.state[row][col]
                # Check if piece is ally piece, so it can be moved
                if ((self.white_move and piece < 10) or (piece > 10 and not self.white_move)) and piece != 0:
                    # If it is a pawn: get pawn moves
                    if piece == 1 or piece == 11:
                        self.get_pawn_moves(row, col, moves)
                    # If it is a knight: get knight moves
                    if piece == 2 or piece == 12:
                        self.get_knight_moves(row, col, moves)
                    # If it is a bishop: get moves in bishop directions
                    if piece == 3 or piece == 13:
                        self.get_direction_moves(row, col, moves, ((-1, -1), (1, 1), (1, -1), (-1, 1)))
                    # If it is a rook: get moves in rook directions
                    if piece == 4 or piece == 14:
                        self.get_direction_moves(row, col, moves, ((-1, 0), (0, 1), (1, 0), (0, -1)))
                    # If it is a queen: get moves in queen directions
                    if piece == 5 or piece == 15:
                        self.get_direction_moves(row, col, moves,
                                                 ((-1, 0), (0, 1), (1, 0), (0, -1), (-1, -1), (1, 1), (1, -1),
                                                  (-1, 1)), )
                    # If it is a king: get king+castle moves
                    if piece == 6 or piece == 16:
                        self.get_king_moves(row, col, moves)
                        self.get_castle_moves(row, col, moves)
        return moves

    # Get pawn moves from a square (row, col) and add them to moves
    def get_pawn_moves(self, row, col, moves):
        # Set to true if the piece on the square (row, col) is pinned
        piece_pinned = False
        # The direction from which the piece is pinned => the piece can still move in the direction where its pinned
        # from
        pin_dir = ()
        # Iterate through all the current pins of the board
        # (Iterate backwards because we want to remove the pin)
        for i in range(len(self.pins) - 1, -1, -1):
            # Check if the square of the pin is equal to the square on which we are currently checking for moves
            if self.pins[i][0] == row and self.pins[i][1] == col:
                # Set piece pinned to true if so
                piece_pinned = True
                # Set the pin direction
                pin_dir = (self.pins[i][2], self.pins[i][3])
                # Remove the pin and break
                self.pins.remove(self.pins[i])
                break

        # Check if its whites turn => its a white pawn (we checked this in the get_moves function)
        if self.white_move:
            # Check if the square in front of pawn is still on the board
            if row - 1 >= 0:
                # Normal Move
                # Check if square in front of pawn is empty
                if self.state[row - 1][col] == 0:
                    # Check if pawn is not pinned or the pin direction is the direction where its moving to => it can
                    # move
                    if not piece_pinned or pin_dir == (-1, 0):
                        # There is a possible move => on square up
                        moves.append(Move(self.state, (row, col), (row - 1, col)))
                        # Check if the two squares in front of pawn are still on the board
                        if row - 2 >= 0:
                            # Check if the two squares in front of pawn are empty and pawn is still on its start square
                            if self.state[row - 2][col] == 0 and row == 6:
                                # Two square move is possible
                                moves.append(Move(self.state, (row, col), (row - 2, col)))
                # Left Capture
                # Check if the column left from the pawn is still on the board
                if col - 1 >= 0:
                    # Check if pawn is not pinned or the pin direction is the direction where its moving to => it can
                    # move
                    if not piece_pinned or pin_dir == (-1, -1):
                        # Check if there is an enemy piece on square where the pawn can capture
                        if self.state[row - 1][col - 1] > 10:
                            # Capture move is possible
                            moves.append(Move(self.state, (row, col), (row - 1, col - 1)))
                        # Check if en passant square is where the pawn can capture
                        elif self.en_passant_square == (row - 1, col - 1):
                            # En passant capture is possible
                            moves.append(Move(self.state, (row, col), (row - 1, col - 1), en_passant=True))
                # Right Capture
                # Check if the column right from the pawn is still on the board
                if col + 1 < 8:
                    # Check if pawn is not pinned or the pin direction is the direction where its moving to => it can
                    # move
                    if not piece_pinned or pin_dir == (-1, 1):
                        # Check if there is an enemy piece on square where the pawn can capture
                        if self.state[row - 1][col + 1] > 10:
                            # Capture move is possible
                            moves.append(Move(self.state, (row, col), (row - 1, col + 1)))
                        # Check if en passant square is where the pawn can capture
                        elif self.en_passant_square == (row - 1, col + 1):
                            # En passant capture is possible
                            moves.append(Move(self.state, (row, col), (row - 1, col + 1), en_passant=True))
        else:
            # Its a black pawn
            # Check if the square in front of pawn is still on the board
            if row + 1 < 8:
                # Normal Move
                # Check if square in front of pawn is empty
                if self.state[row + 1][col] == 0:
                    # Check if pawn is not pinned or the pin direction is the direction where its moving to => it can
                    # move
                    if not piece_pinned or pin_dir == (1, 0):
                        moves.append(Move(self.state, (row, col), (row + 1, col)))
                        # There is a possible move => on square down
                        # Check if the two squares in front of pawn are still on the board
                        if row + 2 < 8:
                            # Check if the two squares in front of pawn are empty and pawn is still on its start square
                            if self.state[row + 2][col] == 0 and row == 1:
                                # Two square move is possible
                                moves.append(Move(self.state, (row, col), (row + 2, col)))
                # Left Capture
                # Check if the column left from the pawn is still on the board
                if col - 1 >= 0:
                    # Check if pawn is not pinned or the pin direction is the direction where its moving to => it can
                    # move
                    if not piece_pinned or pin_dir == (1, -1):
                        # Check if there is an enemy piece on square where the pawn can capture
                        if 0 < self.state[row + 1][col - 1] < 10:
                            # Capture move is possible
                            moves.append(Move(self.state, (row, col), (row + 1, col - 1)))
                        # Check if en passant square is where the pawn can capture
                        elif self.en_passant_square == (row + 1, col - 1):
                            # En passant capture is possible
                            moves.append(Move(self.state, (row, col), (row + 1, col - 1), en_passant=True))
                # Right Capture
                # Check if the column right from the pawn is still on the board
                if col + 1 < 8:
                    # Check if pawn is not pinned or the pin direction is the direction where its moving to => it can
                    # move
                    if not piece_pinned or pin_dir == (1, 1):
                        # Check if there is an enemy piece on square where the pawn can capture
                        if 0 < self.state[row + 1][col + 1] < 10:
                            # Capture move is possible
                            moves.append(Move(self.state, (row, col), (row + 1, col + 1)))
                        # Check if en passant square is where the pawn can capture
                        elif self.en_passant_square == (row + 1, col + 1):
                            # En passant capture is possible
                            moves.append(Move(self.state, (row, col), (row + 1, col + 1), en_passant=True))

    # Get knight moves from a square (row, col) and add them to moves
    def get_knight_moves(self, row, col, moves):
        # Set to true if piece is pinned
        # No pin direction, because the knight can not move in the direction where its pinned from
        piece_pinned = False
        # Iterate through all the current pins of the board
        # (Iterate backwards because we want to remove the pin)
        for i in range(len(self.pins) - 1, -1, -1):
            # Check if the square of the pin is equal to the square on which we are currently checking for moves
            if self.pins[i][0] == row and self.pins[i][1] == col:
                # Set piece pinned to true if so
                piece_pinned = True
                # Remove the pin and break
                self.pins.remove(self.pins[i])
                break
        # All the possible moves a knight can make
        knight_moves = [(-1, -2), (-2, -1), (-2, 1), (-1, 2), (1, -2), (2, -1), (2, 1), (1, 2)]
        # Iterate through the knight moves
        for m in knight_moves:
            # Check if the current square + the knight move is still on the board
            if 0 <= row + m[0] < 8 and 0 <= col + m[1] < 8:
                # Check if the piece is not pinned => it can move
                if not piece_pinned:
                    # Check if the square where its moving to is empty or an enemy piece is there
                    if (self.state[row + m[0]][col + m[1]] < 10 and not self.white_move) or self.state[row + m[0]][
                        col + m[1]] == 0 or (
                            self.state[row + m[0]][col + m[1]] > 10 and self.white_move):
                        # Found a possible knight move and add it to the list
                        moves.append(Move(self.state, (row, col), (row + m[0], col + m[1])))

    # Get moves in specific directions from a square (row, col) and add them to moves
    def get_direction_moves(self, row, col, moves, directions):
        # Set to true if the piece on the square (row, col) is pinned
        piece_pinned = False
        # The direction from which the piece is pinned => the piece can still move in the direction where its pinned from
        pin_dir = ()
        # Iterate through all the current pins of the board
        # (Iterate backwards because we want to remove the pin)
        for i in range(len(self.pins) - 1, -1, -1):
            # Check if the square of the pin is equal to the square on which we are currently checking for moves
            if self.pins[i][0] == row and self.pins[i][1] == col:
                # Set piece pinned to true if so
                piece_pinned = True
                # Set the pin direction
                pin_dir = (self.pins[i][2], self.pins[i][3])
                # Remove the pin and break
                self.pins.remove(self.pins[i])
                break

        # Iterate through the directions
        for d in directions:
            # Iterate through all the squares in this direction
            for i in range(1, 8):
                # Get the new coordinates (the old square + i squares in direction d)
                r = row + d[0] * i
                c = col + d[1] * i

                # Check if the new coordinates are still on the board
                if 0 <= r < 8 and 0 <= c < 8:
                    # Check if the piece is not pinned or the direction is the same as the direction we are trying to
                    # move (also negative because the pieces can move backwards as well)
                    if not piece_pinned or pin_dir == d or pin_dir == (-d[0], -d[1]):
                        # Set the square value, the piece can move to
                        possible_capture = self.state[r][c]
                        # Check if the square is empty
                        if possible_capture == 0:
                            # A possible move was found
                            moves.append(Move(self.state, (row, col), (r, c)))
                        # Check if there is an enemy piece on the new square
                        elif (possible_capture > 10 and self.white_move) or (
                                0 < possible_capture < 10 and not self.white_move):
                            # A possible capture move was found
                            moves.append(Move(self.state, (row, col), (r, c)))
                            # Break because we cant move through enemy pieces
                            break
                        else:
                            # We found an ally piece => cant move through ally pieces, so break
                            break
                else:
                    # We are off the board => break
                    break

    # Get king moves from a square (row, col) and add them to moves
    def get_king_moves(self, row, col, moves):
        # All directions in which a king can move
        directions = ((-1, 0), (0, 1), (1, 0), (0, -1), (-1, -1), (1, 1), (1, -1), (-1, 1))
        # iterate through directions
        for d in directions:
            # Get the new coordinates (the old square + i squares in direction d)
            r = row + d[0]
            c = col + d[1]
            # Check if the new coordinates are still on the board
            if 0 <= r < 8 and 0 <= c < 8:
                # Set the square value, the king can move to
                possible_capture = self.state[r][c]
                # Check if the square is empty or there is an enemy piece on it
                if possible_capture == 0 or (possible_capture > 10 and self.white_move) or (
                        0 < possible_capture < 10 and not self.white_move):
                    # Check if there would be a check on the new king position
                    check, checks, pins, = self.check_square(r, c)
                    if not check:
                        # If there is no attacker on the new king square it is a possible move
                        moves.append(Move(self.state, (row, col), (r, c)))

    # Get castle moves from a square (row, col) and add them to moves
    def get_castle_moves(self, row, col, moves):
        # Check if in check (Can not castle if in check
        if not self.check:
            # Check if its whites turn
            if self.white_move:
                # Check white has the castling right and the squares between rook and king are empty + check if the
                # king or the rook is attacked after castle
                if self.w_queen_castle and self.state[7][1] == 0 and self.state[7][2] == 0 and \
                        self.state[7][3] == 0 and self.state[7][0] == 4 and not self.check_square(7,
                                                                                                  2,
                                                                                                  only_attack=True) and not self.check_square(
                    7, 3, only_attack=True):
                    # White queen side castle is possible
                    moves.append(Move(self.state, (row, col), (7, 2), is_castle=True))
                # Check white has the castling right and the squares between rook and king are empty + check if the
                # king or the rook is attacked after castle
                if self.w_king_castle and self.state[7][5] == 0 and self.state[7][6] == 0 and self.state[7][
                    7] == 4 and not self.check_square(7, 6, only_attack=True) and not self.check_square(7, 5,
                                                                                                        only_attack=True):
                    # White king side castle is possible
                    moves.append(Move(self.state, (row, col), (7, 6), is_castle=True))
            else:
                # Check for black castling Check black has the castling right and the squares between rook and king
                # are empty + check if the king or the rook is attacked after castle
                if self.b_queen_castle and self.state[0][1] == 0 and self.state[0][2] == 0 and \
                        self.state[0][3] == 0 and self.state[0][0] == 14 and not self.check_square(0,
                                                                                                   2,
                                                                                                   only_attack=True) and not self.check_square(
                    0, 3, only_attack=True):
                    # Black queen side castle is possible
                    moves.append(Move(self.state, (row, col), (0, 2), is_castle=True))
                # Check black has the castling right and the squares between rook and king are empty + check if the
                # king or the rook is attacked after castle
                if self.b_king_castle and self.state[0][5] == 0 and self.state[0][6] == 0 and self.state[0][
                    7] == 14 and not self.check_square(0, 6, only_attack=True) and not self.check_square(0, 5,
                                                                                                         only_attack=True):
                    # Black king side castle is possible
                    moves.append(Move(self.state, (row, col), (0, 6), is_castle=True))


# The class of a move which contains information about it
class Move:
    # Initialize the move
    def __init__(self, state, old_pos, new_pos, en_passant=False, is_castle=False):
        # Piece which moves
        self.piece = state[old_pos[0]][old_pos[1]]
        # Piece/Number which is on the square its moving to
        self.captured_piece = state[new_pos[0]][new_pos[1]]
        # Position where its moving from
        self.old_pos = old_pos
        # Position where its moving to
        self.new_pos = new_pos
        # Extra information
        # Set to true if the move is an en passant capture
        self.en_passant_capture = en_passant
        # Set to true if the move is a castling move
        self.is_castle = is_castle
        # Later set, when making the move. It checks if the move broke a castling right
        self.broke_king_side_castle = False
        self.broke_queen_side_castle = False
        # Set to true if the move is a promotion
        self.promotion = (self.piece == 1 and new_pos[0] == 0) or (
                self.piece == 11 and new_pos[0] == 7)

    # Comparing moves
    def __eq__(self, other):
        # Check if the other is a move
        if isinstance(other, Move):
            # Compare start, end and piece
            return other.new_pos == self.new_pos and other.old_pos == self.old_pos and self.piece == other.piece

        return False
