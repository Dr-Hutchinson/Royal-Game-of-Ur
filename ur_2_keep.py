import streamlit as st
#from streamlit.report_thread import get_report_ctx
#from streamlit.hashing import _CodeHasher
import random
import pandas as pd

# adapted from this source code: https://github.com/Ahemmetter/royal-game-of-ur/blob/master/royalgameofur.py
# note - 6-8-23 - code effort ended after being unable to get board to display game state after round. 


if 'board' not in st.session_state:
    st.session_state.board = [[None for _ in range(8)] for _ in range(3)]
if 'current_player' not in st.session_state:
    st.session_state.current_player = 1
if 'pieces' not in st.session_state:
    st.session_state.pieces = {1: [None]*7, 2: [None]*7}
if 'game_over' not in st.session_state:
    st.session_state.game_over = False

def draw_board():
    # Create a DataFrame to represent the game board
    board_df = pd.DataFrame(st.session_state.board)
    # Convert the DataFrame's data type to object
    board_df = board_df.astype(object)
    # Replace the values in the DataFrame with emojis
    board_df = board_df.replace({None: "□", 0: "□", 1: "🔴", 2: "🔵"})
    # Display the DataFrame in Streamlit
    st.table(board_df)

def initialize_game():
    # Initialize game state variables
    st.session_state.board = [[0]*8 for _ in range(3)]
    st.session_state.turn = 1
    st.session_state.selected = None
    st.session_state.moves = []
    st.session_state.winner = None
    st.session_state.dice = 0
    st.session_state.fishki = [[i for i in range(7)] for _ in range(2)]
    st.session_state.fishki_positions = [[None]*7 for _ in range(2)]
    #draw_board()
    # Set up GUI
    st.title("The Royal Game of Ur")
    st.markdown("Welcome to the Royal Game of Ur! Player 1's turn.")

# Call the function at the start of our script
if 'board' not in st.session_state.board:
    initialize_game()

class Game:
    def __init__(self):
        self.board = [[0]*8 for _ in range(3)]
        self.turn = random.choice([1, 2])
        self.dice = 0
        self.selected_piece = None
        self.winner = None
        self.fishki_positions = [[-1, -1, -1, -1, -1, -1, -1], [-1, -1, -1, -1, -1, -1, -1]]
        self.bpos = [0] * 7
        self.wpos = [0] * 7
        self.rosettes = [4, 8, 14]
        self.whiteturn = True
        self.wpath = [-1, 11, 8, 5, 2, 1, 4, 7, 10, 12, 13, 15, 14, 17, 18, 19, 16, 99]  # Define the path for white pieces here
        self.bpath = [-1, 9, 6, 3, 0, 1, 4, 7, 10, 12, 13, 15, 16, 19, 18, 17, 14, 99]  # Define the path for black pieces here

    def throw_dice(self):
        self.dice = random.randint(0, 4)
        st.session_state.dice = self.dice
        if self.dice == 0:
            st.write("You rolled a zero. Your turn is skipped.")
            self.change_turn()
        else:  # AI's turn
            if self.turn == 2:
                self.ai_move()
            self.change_turn()  # Move this line here

    def select_piece(self, piece):
        self.selected_piece = piece - 1  # Subtract 1 to adjust for 0-based indexing

    def show_moves(self):
        possible_moves = []
        for i in range(1, self.dice + 1):
            target_square = self.selected_piece + i
            # Check if the target square is within the board
            if target_square < 15:
                # Check if the target square is not occupied by a piece of the same color
                if self.board[target_square] != self.turn:
                    # Check if the target square is not a rosette square or the end square
                    if target_square not in [4, 8, 14]:
                        possible_moves.append(target_square)
            # Display the possible moves to the user
        st.write(f"Possible moves for piece {self.selected_piece}: {possible_moves}")

    def available_squares(self, piece):
        available_squares = []
        current_position = self.fishki_positions[self.turn-1][piece]
        for i in range(1, self.dice + 1):
            target_square = current_position + i
            # Check if the target square is within the board
            if target_square <= 14:
                # Check if the target square is not occupied by a piece of the same color
                row = (target_square-1) // 8
                col = (target_square-1) % 8
                if self.board[row][col] != self.turn:
                    available_squares.append(target_square)
        return available_squares

    def move_piece(self, stone, steps):
        stone = stone - 1
        st.write(f"Moving piece {stone} by {steps} steps")  # Debugging statement
        if self.whiteturn:
            path = self.wpath
            pos = self.wpos
            other_pos = self.bpos
        else:
            path = self.bpath
            pos = self.bpos
            other_pos = self.wpos
        # Check if the piece is at the start position
        if pos[stone] == 0:
            # Set the goal position to the start of the path plus the number of steps
            goal = path[1] + steps
        else:
            # Calculate the goal position
            goal = path[path.index(pos[stone]) + steps]
        # Check if the move is valid
        if goal not in pos and goal <= 17:
            # Handle collisions
            if goal in other_pos:
                if goal not in self.rosettes:
                    # Kick out the piece at the goal position
                    other_pos[other_pos.index(goal)] = -1
            # Move the piece
            pos[stone] = goal
            self.fishki_positions[self.turn-1][stone] = goal
            for i in range(3):
                for j in range(8):
                    if self.board[i][j] == self.turn:
                        self.board[i][j] = 0
            row = (self.fishki_positions[self.turn-1][stone]-1) // 8
            col = (self.fishki_positions[self.turn-1][stone]-1) % 8
            self.board[row][col] = self.turn
            # Check if the piece has reached the end of the game board
            if goal == 17:
                pos[stone] = 99
                st.write(f"Piece {stone} has reached the end of the game board!")
            # Switch turns unless the piece landed on a rosette
            if goal not in self.rosettes:
                self.whiteturn = not self.whiteturn
            st.write(f"Updated game board: {self.board}")
            st.write(f"Updated fishki_positions: {self.fishki_positions}")
        else:
            st.write("Invalid move!")
        # Update st.session_state.board
        #st.session_state.board = self.board
        # After updating the game board and fishki_positions, print them out
        board_df = pd.DataFrame(self.board).astype(object)
        st.write(f"Updated game board: {board_df}")
        st.write(f"Updated fishki_positions: {self.fishki_positions}")
        # Update st.session_state.board
        st.session_state.board = board_df.values.tolist()
        st.session_state.board = self.board


    def change_turn(self):
        self.turn = 3 - self.turn

    def find_winner(self):
        # Check if all pieces of a player have reached the end of the game board
        if self.fishki_positions[0].count(99) == 7:
            return 1  # Player 1 wins
        elif self.fishki_positions[1].count(99) == 7:
            return 2  # Player 2 wins
        return None  # No winner yet

    def ai_move(self):
        # Initialize the piece and square variables to None
        piece = None
        square = None

        # Check for a move that would capture an opponent's piece
        for i in range(7):
            if self.fishki_positions[1][i] + self.dice <= 14 and self.fishki_positions[1][i] + self.dice in self.fishki_positions[0]:
                piece = i
                square = self.fishki_positions[1][i] + self.dice
                break

        # If no capturing move was found, check for a move that would finish a piece
        if piece is None:
            for i in range(7):
                if self.fishki_positions[1][i] + self.dice == 14:
                    piece = i
                    square = self.fishki_positions[1][i] + self.dice
                    break

        # If no finishing move was found, check for a move to a rosette
        if piece is None:
            for i in range(7):
                if self.fishki_positions[1][i] + self.dice in [4, 8, 14]:
                    piece = i
                    square = self.fishki_positions[1][i] + self.dice
                    break

        # If no rosette move was found, move to another square
        if piece is None:
            for i in range(7):
                if self.fishki_positions[1][i] + self.dice <= 14:
                    piece = i
                    square = self.fishki_positions[1][i] + self.dice
                    break

        # If a move was found, apply it to the game state
        if piece is not None:
            self.fishki_positions[1][piece] = square

            # Print a debugging statement
            st.write(f"AI moved piece {piece} to square {square}")

        # If no move was found, skip the turn
        else:
            self.turn = not self.turn

        return self.fishki_positions

def main():
    # Call the function to draw the board
    draw_board()

    if 'game' not in st.session_state:
        st.session_state.game = Game()
    game = st.session_state.game

    if st.button("Throw Dice"):
        game.throw_dice()
        st.write(f"You rolled a {game.dice}.")
        if game.dice != 0:
            with st.form(key='my_form'):
                # Only display the pieces that are on the board
                available_pieces = [i for i in range(7) if game.fishki_positions[game.turn-1][i] is not None]
                piece = st.selectbox("Select Piece", options=available_pieces, key='selected_piece')
                # Only display the squares that the selected piece can move to
                available_squares = game.available_squares(piece)
                square = st.selectbox("Select Square", options=available_squares, key='selected_square')
                submit_button = st.form_submit_button(label='Submit')
                if submit_button:
                    game.selected_piece = piece # Add this line to update game.selected_piece
                    game.move_piece(game.selected_piece, game.dice) # Use the selections from the session state to update the game state
                    st.session_state.game = game
                    draw_board()
                    st.experimental_rerun()  # Rerun the app after updating the game state


    if game.turn == 2:
        game.ai_move()
        draw_board()

    if game.find_winner():
        st.write(f"Player {game.winner} wins!")
        st.stop()
    else:
        if game.turn == 2:
            game.ai_move()


if __name__ == "__main__":
    main()
