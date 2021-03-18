import csv
import math
from Board import Move
from main import display_board
from main import load_images
import pygame as p
import random
import time
import json

# All openings, which are still possilble
current_possible_openings = []


# Returns the value of the different pieces
def get_piece_value(piece):
    # Pawn is worth 10
    if piece == 1 or piece == 11:
        return 10
    # Knight is worth 20
    elif piece == 2 or piece == 12:
        return 30
    # Bishop is worth 30
    elif piece == 3 or piece == 13:
        return 30
    # Rook is worth 50
    elif piece == 4 or piece == 14:
        return 50
    # Queen is worth 90
    elif piece == 5 or piece == 15:
        return 90
    else:
        return 0


# Returns the value of the current board state (negative is good for black and positive is good for white)
def get_value_of_board(board):
    # Return value
    value = 0
    # This map indicates the points where knights and pawns are most valuable
    pawn_knight_map = [
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 2, 1, 1, 2, 0, 0],
        [0, 0, 2, 4, 4, 2, 0, 0],
        [0, 0, 2, 4, 4, 2, 0, 0],
        [0, 0, 2, 1, 1, 2, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0]]
    # If there is a checkmate the value is infinity or -infinity
    if board.checkmate:
        return float("-inf") if board.white_move else float("inf")
    # Stalemate is worth 0
    if board.stalemate:
        return 0
    # Iterate through state to count material
    for i in range(len(board.state)):
        for j in range(len(board.state[i])):
            # COUNT MATERIAL
            piece = board.state[i][j]
            # Black pieces
            if piece > 10:
                value -= get_piece_value(piece)
            # White pieces
            elif piece != 0:
                value += get_piece_value(piece)

            # USE THE KNIGHT/PAWN MAP
            # Check if the piece is white pawn or knight (add value)
            if piece == 1 or piece == 2:
                value += pawn_knight_map[i][j]
            # Check if the piece is a black pawn or knight (subtract value)
            elif piece == 11 or piece == 12:
                value -= pawn_knight_map[i][j]

    # REWARD CASTLING
    for move in board.move_history:
        if move.is_castle and move.piece == 6:
            value += 25
        elif move.is_castle and move.piece == 16:
            value -= 25

    return value


# Uses the best algorithm to find a move
def find_best_move(board, legal_moves, use_openings=True):
    # Counts the number of calculated positions calls
    global position_counter
    position_counter = 0
    # Check if it should use openings and check if its one of the first moves or we have possible openings
    if use_openings and (0 < len(board.move_history) < 3 or len(current_possible_openings) != 0):
        # Wait a small amount of time, so it wont move instantly if ai is playing against itself
        time.sleep(0.4)
        # Check if the openings are still usable
        check_for_opening_move(board)
        # Check if after the new openings calculation there is still an opening
        if len(current_possible_openings) > 0:
            # Take a random opening out of the possible ones
            opening = current_possible_openings[random.randint(0, len(current_possible_openings)) - 1]
            # Split the notation list into single notations
            moves_str_list = opening[3].split(' ')
            # Transform the notation list into usable move classes
            moves_in_opening = notation_list_to_moves(moves_str_list)
            # Get the next move from the opening
            move = moves_in_opening[len(board.move_history)]
            # Get the same move as a legal move (if there is some special move, the move would not have the right
            # properties if we take it out of the opening)
            for legal_move in legal_moves:
                if move == legal_move:
                    move = legal_move
            # Print the opening name
            print("Playing the " + opening[1])
            # Return the move as the best move
            return move
        print('No openings found :/')
    # Shuffle the list so there is variety
    random.shuffle(legal_moves)
    # Return the min max algorithm
    return find_min_max_alpha_beta(5, legal_moves, board, float("-inf"), float("inf"), True)


# Return a random move out of legal_moves
def find_random_move(legal_moves, delay=0):
    time.sleep(delay)
    if len(legal_moves) > 0:
        return legal_moves[random.randint(0, len(legal_moves) - 1)]
    return None


# Uses the MinMaxAlgorithm with alpha beta pruning to find a move Takes a search depths, the current legal moves,
# the board, a, b, and the is_first boolean, which is true if its the first node in the tree
def find_min_max_alpha_beta(depth, moves, board, a, b, is_first, use_move_sorting=True):
    # Check if move sorting is activated which makes the algorithm for efficient
    if use_move_sorting:
        # Sort the moves according to capture value (reverse = true, because captures should be looked at first)
        moves.sort(key=sort_moves, reverse=True)
    # Position_counter stores the number of positions calculated
    # Best_move is the best move
    global position_counter, best_move
    # Check if its the first Node
    # Assign the best_move to a random move => if there is no best move, it will pick a random
    if is_first:
        best_move = find_random_move(moves)
    # Foreach time in this function the position counter increases, because its a new position
    position_counter += 1
    # Check if the depth is 0 => we completed a branch; or if the game ended
    if depth == 0 or board.checkmate or board.stalemate:
        # Get the value of the current state
        value = get_value_of_board(board)
        # Check if its the first Node
        if is_first:
            # If so return the best move
            return best_move
        # Return the value of the state to the node above
        return value
    # The max depth is not reached yet => go deeper
    # Check if its whites turn
    elif board.white_move:
        # The best evaluation for white is initially -infinity => white tries to maximize the value => high value is
        # good for white
        max_eval = float("-inf")
        # Iterate through all the moves for white
        for move in moves:
            # Make the move pseudo
            board.make_move(move, is_pseudo=True)
            # Create a new child node (with depth -1 => the depth get every time smaller, so sometime when it is
            # zero, it will return a value all the way up)
            evaluation = find_min_max_alpha_beta(depth - 1, board.get_legal_moves(), board, a, b, False)
            # Check if the evaluation of this child is greater (white tries to maximize) than the max_eval
            if evaluation > max_eval:
                # Set the max eval
                max_eval = evaluation
                # If its the first node, the new best value is also the best move
                if is_first:
                    best_move = move
            # Undo the pseudo move
            board.make_move(move, is_pseudo=True, undo=True)
            # Set the alpha to the new max
            a = max(a, evaluation)
            # If beta is lower than alpha the rest of the tree is not important anymore, because there can not be a
            # better value
            if b <= a:
                break

        # If it is the first value, it should return a move
        if is_first:
            print("Evaluation in " + str(depth) + " Moves: " + str(max_eval / 10) + " (calculated " + str(
                position_counter) + " positions)")
            return best_move
        # Pass the evaluation to the parent node
        return max_eval
    else:
        # The best evaluation for black is initially infinity => black tries to minimize the value => low value is
        # good for black
        min_eval = float("inf")
        # Iterate through all the moves for black
        for move in moves:
            # Make the move pseudo
            board.make_move(move, is_pseudo=True)
            # Create a new child node (with depth -1 => the depth get every time smaller, so sometime when it is
            # zero, it will return a value all the way up)
            evaluation = find_min_max_alpha_beta(depth - 1, board.get_legal_moves(), board, a, b, False)
            # Check if the evaluation of this child is lower (black tries to minimize) than the min_eval
            if evaluation < min_eval:
                # Set the min eval
                min_eval = evaluation
                # If its the first node, the new best value is also the best move
                if is_first:
                    best_move = move
            # Undo the pseudo move
            board.make_move(move, is_pseudo=True, undo=True)
            # Set the beta to the new min
            b = min(b, evaluation)
            # If beta is lower than alpha the rest of the tree is not important anymore, because there can not be a
            # better value
            if b <= a:
                break

        # If it is the first value, it should return a move
        if is_first:
            print("Evaluation in " + str(depth) + " Moves: " + str(min_eval / 10) + " (calculated " + str(
                position_counter) + " positions)")
            return best_move
        # Pass the evaluation to the parent node
        return min_eval


# Key function of move sorting (sort the moves according to captures)
def sort_moves(move):
    return get_piece_value(move.captured_piece)


# Takes the current state checks for current possible openings and sets the global variable
def check_for_opening_move(board):
    # This is the first or second (black or white) move of the game, so we want to iterate through
    # the whole directory
    if 0 < len(board.move_history) < 3:
        # File names of the opening information
        files = ["a.tsv", "b.tsv", "c.tsv", "d.tsv", "e.tsv"]
        # Iterate through all the opening files
        for file_name in files:
            # Open the file as a csv file
            with open("openings/" + file_name) as csv_file:
                # Read the csv file
                opening_lib = csv.reader(csv_file, delimiter='\t')
                # Iterate through all the rows in the csv file
                for r in opening_lib:
                    # The moves of the opening are in the 3rd column of the csv file
                    moves_str = r[3]
                    # At the first row there is a explanation of the columns => do not read that
                    if moves_str != "moves":
                        # Split the moves string into separate moves
                        moves_str_list = moves_str.split(' ')
                        # Transform the simple string notation into moves
                        moves_in_opening = notation_list_to_moves(moves_str_list)
                        # Check if the moves from this opening were actual played, so we can use the next move of
                        # this opening
                        # Also check if there is a move left
                        if board.move_history == moves_in_opening[:len(board.move_history)] and len(
                                moves_in_opening) > len(board.move_history):
                            # Append the row of the csv to the current possible openings
                            current_possible_openings.append(r)
    # We are not at the first move => Check if there are any openings left
    elif len(current_possible_openings) != 0:
        print('Searching for openings... in ' + str(len(current_possible_openings)) + " different openings")
        # Iterate through all the openings (Backwards, because we want to remove the opening if it is not fitting
        # anymore)
        for i in range(len(current_possible_openings) - 1, -1, -1):
            # Get the 3rd Column (the move notation)
            moves_str = current_possible_openings[i][3]
            # Split the moves string into separate moves
            moves_str_list = moves_str.split(' ')
            # Transform the simple string notation into moves
            moves_in_opening = notation_list_to_moves(moves_str_list)
            # Check if the moves from this opening were actual played, so we can use the next move of
            # this opening
            # Also check if there is a move left
            if board.move_history == moves_in_opening[:len(board.move_history)] and len(moves_in_opening) > len(
                    board.move_history):
                # If so the opening is still usable
                pass
            else:
                # The opening is not usable anymore
                current_possible_openings.remove(current_possible_openings[i])


# Transforms a list of notations into moves (is starting at the init state, so only openings are transformable)
def notation_list_to_moves(notation_list):
    # Initialize the state
    state = [
        [14, 12, 13, 15, 16, 13, 12, 14],
        [11, 11, 11, 11, 11, 11, 11, 11],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [1, 1, 1, 1, 1, 1, 1, 1],
        [4, 2, 3, 5, 6, 3, 2, 4]]
    # List which will be returned
    moves = []
    # Iterate through all the notations
    for notation in notation_list:
        # Split the notation (e.g. e2e4 => e2, e4) into start and end position
        first_part, second_part = notation[:len(notation) // 2], notation[len(notation) // 2:]
        # Set the old and new position of the move
        old_pos = not_to_pos(first_part)
        new_pos = not_to_pos(second_part)
        # Get the piece which moves
        piece = state[old_pos[0]][old_pos[1]]
        # Declare the move
        move = Move(state, old_pos, new_pos)
        # Append the move to return list
        moves.append(move)
        # Make the move
        state[old_pos[0]][old_pos[1]] = 0
        state[new_pos[0]][new_pos[1]] = piece
    # Return the moves list
    return moves


# Transforms a simple notation of chess (e.g. e4) into a usable position
def not_to_pos(notation):
    # Dict for the translation of the column letter
    letter_to_column = {
        "a": 0,
        "b": 1,
        "c": 2,
        "d": 3,
        "e": 4,
        "f": 5,
        "g": 6,
        "h": 7,
    }
    # Return the transformed position
    return 8 - int(notation[1]), letter_to_column[notation[0]]


# Transforms a usable position into a simple notation of chess (e.g. e4)
def pos_to_not(pos):
    # Dict for the translation of the column letter
    letter_to_column = {
        0: "a",
        1: "b",
        2: "c",
        3: "d",
        4: "e",
        5: "f",
        6: "g",
        7: "h",
    }

    # Return the transformed position
    return letter_to_column[pos[1]] + str(8 - pos[0])


# Transforms a move into a notation (e.g. e2e4)
def move_to_notation(move):
    return str(pos_to_not(move.old_pos)) + str(pos_to_not(move.new_pos))


# Own Monte Carlo Tree Search
# Main Function of the training
def train_monte_carlo_tree(board, screen, clock, show=False):
    load_images()
    # Display the board based on the state, selected position and highlighted squares
    display_board(board, screen, (), [])
    # Pygame refresh
    p.display.flip()
    clock.tick(30)

    training_cycles = 5000
    saving_rate = 1000
    counter = 1
    for i in range(int(training_cycles / saving_rate)):
        with open("mcts.json", "r") as file:
            tree = json.load(file)
            for j in range(saving_rate):
                node = selection(tree["start"], board, screen, clock, show)
                print("Selection completed")
                child_index = expansion(node, board)
                print("Expansion completed")
                new_node = node["children"][child_index]
                result = simulation(board, screen, clock, show)
                print("Simulation completed")
                backpropagation(result, tree["start"], new_node)
                print("Backpropagation completed")
                board.reset_board()
                print(str(counter) + "/" + str(training_cycles))
                counter += 1
        print("SAVED")
        with open("mcts.json", "w") as file:
            json.dump(tree, file, indent=8)

    most_explored = float("-inf")
    highest_win_rate = float("-inf")
    move_with_best_win_rate = None
    for child in tree["start"]["children"]:
        if child["visits"] > most_explored:
            most_explored = child["visits"]
        if (child["win"] / child["visits"]) > highest_win_rate:
            highest_win_rate = (child["win"] / child["visits"])
            move_with_best_win_rate = child

        print(str(child["move_history"]) + ": " + str(child["visits"]))
    print("most explored node was visited: " + str(most_explored) + " times")
    print("Highest win rate is " + str(highest_win_rate) + " at move " + str(move_with_best_win_rate["move_history"]))


def ucb_val(node):
    return (node["win"] / (node["visits"] + (10 ** -6))) + (1.4 * math.sqrt(
        math.log(node["parent_visits"] + 10 ** -6) / (node["visits"] + (10 ** -10))))
    # return node["win"] + 2 * (
    # math.sqrt(math.log(node["parent_visits"] + math.e + (10 ** -6)) / (node["visits"] + (10 ** -10))))


def selection(node, board, screen, clock, show):
    legal_moves = board.get_legal_moves()

    if len(node["move_history"]) != 0:
        move = notation_list_to_moves(node["move_history"])[-1]
        for legal_move in legal_moves:
            if move == legal_move:
                print("made move " + str(move_to_notation(legal_move)))
                board.make_move(legal_move)
                if show:
                    # Display the board based on the state, selected position and highlighted squares
                    display_board(board, screen, (), [])

                    # Pygame refresh
                    p.display.flip()
                    clock.tick(30)

    legal_moves = board.get_legal_moves()
    if len(node["children"]) < len(legal_moves):
        print("Legal moves: " + str([move_to_notation(move) for move in legal_moves]))
        print("Length of children: " + str(len(node["children"])))
        print("Found something unexplored")
        return node

    max_ucb = float("-inf")
    best_child = None
    for child in node["children"]:
        current_ucb = ucb_val(child)
        if current_ucb > max_ucb:
            max_ucb = current_ucb
            best_child = child
    return selection(best_child, board, screen, clock, show)


def expansion(node, board):
    legal_moves = board.get_legal_moves()
    expanded_moves = []
    unexpanded_moves = []

    for child in node["children"]:
        expanded_moves.append(notation_list_to_moves(child["move_history"])[-1])
    for move in legal_moves:
        if move not in expanded_moves:
            unexpanded_moves.append(move)
    print("Unexpanded moves " + str([move_to_notation(m) for m in unexpanded_moves]))
    random_expansion_move = find_random_move(unexpanded_moves)

    if random_expansion_move is None:
        raise Exception("Random expansion move is None")

    node["children"].append({
        "move_history": node["move_history"] + [move_to_notation(random_expansion_move)],
        "parent_visits": node["visits"],
        "visits": 0,
        "win": 0,
        "children": [
        ]
    })

    return len(node["children"]) - 1


def simulation(board, screen, clock, show):
    legal_moves = board.get_legal_moves()
    if board.checkmate or board.stalemate:
        if board.checkmate and board.white_move:
            print("Simulated Win Black")
            return -1
        elif board.checkmate and not board.white_move:
            print("Simulated Win White")
            return 1
        else:
            print("Simulated Draw")
            return 0

    else:

        random_move = find_random_move(legal_moves)
        if random_move is None:
            raise Exception("Random move is None")
        board.make_move(random_move)
        if show:
            # Display the board based on the state, selected position and highlighted squares
            display_board(board, screen, (), [])

            # Pygame refresh
            p.display.flip()
            clock.tick(30)
        return simulation(board, screen, clock, show)


def backpropagation(result, label_node, simulated_node):
    current_node = label_node
    whites_turn = True
    while current_node["move_history"] != simulated_node["move_history"]:
        current_node["visits"] += 1
        if result == 0:
            current_node["win"] += 0.5
        elif result == 1:
            current_node["win"] += 1 if whites_turn else 0
        else:
            current_node["win"] += 1 if not whites_turn else 0
        whites_turn = not whites_turn

        for child in current_node["children"]:
            child["parent_visits"] += 1
            if child["move_history"] == simulated_node["move_history"][:len(child["move_history"])]:
                current_node = child

    current_node["visits"] += 1
    if result == 0:
        current_node["win"] += 0.5
    elif result == 1:
        current_node["win"] += 1 if whites_turn else 0
    else:
        current_node["win"] += 1 if not whites_turn else 0
