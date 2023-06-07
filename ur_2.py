import streamlit as st
from streamlit.report_thread import get_report_ctx
from streamlit.hashing import _CodeHasher
import random

class SessionState(object):
    def __init__(self, **kwargs):
        """A new SessionState object."""
        for key, val in kwargs.items():
            setattr(self, key, val)


def get_session_state(session_id):
    ctx = get_report_ctx()
    session_infos = getattr(ctx, "session_infos", None)
    if session_infos is None:
        session_infos = ctx.session_infos = {}
    if session_id not in session_infos:
        session_infos[session_id] = SessionState()
    return session_infos[session_id]


session_id = _CodeHasher().to_bytes(get_report_ctx().session_id)
session_state = get_session_state(session_id)

if not hasattr(session_state, 'board'):
    session_state.board = [[None for _ in range(8)] for _ in range(3)]

if not hasattr(session_state, 'current_player'):
    session_state.current_player = 1  # 1 for player 1, 2 for player 2

if not hasattr(session_state, 'pieces'):
    # Initialize the pieces for each player. Each player has 7 pieces.
    session_state.pieces = {1: [None]*7, 2: [None]*7}

if not hasattr(session_state, 'game_over'):
    session_state.game_over = False

def initialize_game():
    # Initialize game state variables
    session_state.board = [[0]*8 for _ in range(3)]
    session_state.turn = 1
    session_state.selected = None
    session_state.moves = []
    session_state.winner = None
    session_state.dice = 0
    session_state.fishki = [[i for i in range(7)] for _ in range(2)]
    session_state.fishki_positions = [[None]*7 for _ in range(2)]

    # Set up GUI
    st.title("The Royal Game of Ur")
    st.markdown("Welcome to the Royal Game of Ur! Player 1's turn.")

# Call the function at the start of our script
if 'board' not in session_state:
    initialize_game()

def draw_board():
    # Draw the game board
    for row in range(3):
        for col in range(8):
            if session_state.board[row][col] is None:
                # Draw an empty square
                st.markdown(":white_large_square:", unsafe_allow_html=True)
            elif session_state.board[row][col] == 1:
                # Draw a square with a piece for player 1
                st.markdown(":red_circle:", unsafe_allow_html=True)
            elif session_state.board[row][col] == 2:
                # Draw a square with a piece for player 2
                st.markdown(":blue_circle:", unsafe_allow_html=True)
        st.write("\n")  # Start a new line

# Call the function to draw the board
draw_board()

class Game:
    def __init__(self):
        self.board = [[0]*8 for _ in range(3)]
        self.turn = random.choice([1, 2])
        self.dice = 0
        self.selected_piece = None
        self.winner = None

    def throw_dice(self):
        self.dice = random.randint(0, 4)
        st.session_state.dice = self.dice

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

    def move_piece(self, square):
        # TODO: Implement this method

    def change_turn(self):
        self.turn = 3 - self.turn

    def find_winner(self):
        # TODO: Implement this method

    def ai_move(self):
        # TODO: Implement this method

def main():
    st.title("Royal Game of Ur")

    if 'game' not in st.session_state:
        st.session_state.game = Game()

    game = st.session_state.game

    if st.button("Throw Dice"):
        game.throw_dice()

    piece = st.selectbox("Select Piece", options=range(1, 8))
    game.select_piece(piece)

    square = st.selectbox("Select Square", options=range(1, 15))
    game.move_piece(square)

    game.change_turn()

    if game.find_winner():
        st.write(f"Player {game.winner} wins!")
    else:
        if game.turn == 2:  # AI's turn
            game.ai_move()

if __name__ == "__main__":
    main()
