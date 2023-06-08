import streamlit as st
#from streamlit.report_thread import get_report_ctx
#from streamlit.hashing import _CodeHasher
import random

#class SessionState(object):
    #def __init__(self, **kwargs):
        #"""A new SessionState object."""
        #for key, val in kwargs.items():
            #setattr(self, key, val)


#def get_session_state(session_id):
    #ctx = get_report_ctx()
    #session_infos = getattr(ctx, "session_infos", None)
    #if session_infos is None:
    #    session_infos = ctx.session_infos = {}
    #if session_id not in session_infos:
    #    session_infos[session_id] = SessionState()
    #return session_infos[session_id]


#session_id = _CodeHasher().to_bytes(get_report_ctx().session_id)
#session_state = get_session_state(session_id)

if 'board' not in st.session_state:
    st.session_state.board = [[None for _ in range(8)] for _ in range(3)]

if 'current_player' not in st.session_state:
    st.session_state.current_player = 1

if 'pieces' not in st.session_state:
    st.session_state.pieces = {1: [None]*7, 2: [None]*7}

if 'game_over' not in st.session_state:
    st.session_state.game_over = False



#if not hasattr(session_state, 'board'):
    #session_state.board = [[None for _ in range(8)] for _ in range(3)]

#if not hasattr(session_state, 'current_player'):
    #session_state.current_player = 1  # 1 for player 1, 2 for player 2

#if not hasattr(session_state, 'pieces'):
    # Initialize the pieces for each player. Each player has 7 pieces.
    #session_state.pieces = {1: [None]*7, 2: [None]*7}

#if not hasattr(session_state, 'game_over'):
    #session_state.game_over = False

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

    # Set up GUI
    st.title("The Royal Game of Ur")
    st.markdown("Welcome to the Royal Game of Ur! Player 1's turn.")

# Call the function at the start of our script
if 'board' not in st.session_state.board:
    initialize_game()

def draw_board():
    # Draw the game board
    for row in range(3):
        for col in range(8):
            if st.session_state.board[row][col] is None:
                # Draw an empty square
                st.markdown(":white_large_square:", unsafe_allow_html=True)
            elif st.session_state.board[row][col] == 1:
                # Draw a square with a piece for player 1
                st.markdown(":red_circle:", unsafe_allow_html=True)
            elif st.session_state.board[row][col] == 2:
                # Draw a square with a piece for player 2
                st.markdown(":blue_circle:", unsafe_allow_html=True)
        st.write("\n")  # Start a new line



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
            if self.turn == 2:  # AI's turn
                self.ai_move(self.board, self.fishki_positions, self.dice)

    def select_piece(self, piece):
        self.selected_piece = piece

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

    def move_piece(self, stone, steps):
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

            # Check if the piece has reached the end of the game board
            if goal == 17:
                pos[stone] = 99
                st.write(f"Piece {stone} has reached the end of the game board!")

            # Switch turns unless the piece landed on a rosette
            if goal not in self.rosettes:
                self.whiteturn = not self.whiteturn

        else:
            st.write("Invalid move!")

        #return bpos, wpos, whiteturn

    def change_turn(self):
        self.turn = 3 - self.turn

    def find_winner(self):
        # Check if all pieces of a player have reached the end of the game board
        if self.fishki_positions[0].count(99) == 7:
            return 1  # Player 1 wins
        elif self.fishki_positions[1].count(99) == 7:
            return 2  # Player 2 wins
        return None  # No winner yet

    def ai_move(board, positions, roll):
        # Check if it's the AI's turn
        if not board['turn']:
            # If the roll is not zero, make a move
            if roll != 0:
                # Check for a move that would capture an opponent's piece
                for i in range(7):
                    if positions['b'][i] + roll <= 14 and positions['b'][i] + roll in positions['w']:
                        positions['b'][i] += roll
                        positions['w'].remove(positions['b'][i])
                        return positions

                # Check for a move that would finish a piece
                for i in range(7):
                    if positions['b'][i] + roll == 14:
                        positions['b'][i] += roll
                        return positions

                # Check for a move to a rosette
                for i in range(7):
                    if positions['b'][i] + roll in [4, 8, 14]:
                        positions['b'][i] += roll
                        return positions

                # Move to another square
                for i in range(7):
                    if positions['b'][i] + roll <= 14:
                        positions['b'][i] += roll
                        return positions

            # If the roll is zero, skip the turn
            else:
                board['turn'] = not board['turn']

        return positions

def main():
    st.title("Royal Game of Ur")

    if 'game' not in st.session_state:
        st.session_state.game = Game()

    game = st.session_state.game

    # Call the function to draw the board
    draw_board()

    if st.button("Throw Dice"):
        game.throw_dice()

    if game.dice != 0:
        piece = st.selectbox("Select Piece", options=range(1, 8))
        game.select_piece(piece)

        square = st.selectbox("Select Square", options=range(1, 15))
        game.move_piece(square, game.dice)


    game.change_turn()

    if game.find_winner():
        st.write(f"Player {game.winner} wins!")
        st.stop()
    else:
        if game.turn == 2:  # AI's turn
            game.ai_move(game.board, game.fishki_positions, game.dice)

if __name__ == "__main__":
    main()
