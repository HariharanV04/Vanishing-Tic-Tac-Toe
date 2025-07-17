import streamlit as st
import time
from typing import List, Tuple, Optional

# Initialize session state
if 'board' not in st.session_state:
    st.session_state.board = [['' for _ in range(3)] for _ in range(3)]
if 'move_history' not in st.session_state:
    st.session_state.move_history = []
if 'current_player' not in st.session_state:
    st.session_state.current_player = 'X'
if 'game_over' not in st.session_state:
    st.session_state.game_over = False
if 'winner' not in st.session_state:
    st.session_state.winner = None
if 'vanish_after' not in st.session_state:
    st.session_state.vanish_after = 3

def reset_game():
    """Reset the game state"""
    st.session_state.board = [['' for _ in range(3)] for _ in range(3)]
    st.session_state.move_history = []
    st.session_state.current_player = 'X'
    st.session_state.game_over = False
    st.session_state.winner = None

def check_winner(board: List[List[str]]) -> Optional[str]:
    """Check if there's a winner on the board"""
    # Check rows
    for row in board:
        if row[0] == row[1] == row[2] != '':
            return row[0]
    
    # Check columns
    for col in range(3):
        if board[0][col] == board[1][col] == board[2][col] != '':
            return board[0][col]
    
    # Check diagonals
    if board[0][0] == board[1][1] == board[2][2] != '':
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] != '':
        return board[0][2]
    
    return None

def is_board_full(board: List[List[str]]) -> bool:
    """Check if the board is full"""
    for row in board:
        for cell in row:
            if cell == '':
                return False
    return True

def make_move(row: int, col: int):
    """Make a move and handle vanishing logic"""
    if st.session_state.game_over or st.session_state.board[row][col] != '':
        return
    
    # Make the move
    st.session_state.board[row][col] = st.session_state.current_player
    st.session_state.move_history.append((row, col, st.session_state.current_player, time.time()))
    
    # Handle vanishing - remove moves older than vanish_after
    if len(st.session_state.move_history) > st.session_state.vanish_after * 2:
        # Remove the oldest move
        old_move = st.session_state.move_history.pop(0)
        old_row, old_col = old_move[0], old_move[1]
        st.session_state.board[old_row][old_col] = ''
    
    # Check for winner
    winner = check_winner(st.session_state.board)
    if winner:
        st.session_state.winner = winner
        st.session_state.game_over = True
    elif is_board_full(st.session_state.board):
        st.session_state.game_over = True
        st.session_state.winner = "Tie"
    else:
        # Switch player
        st.session_state.current_player = 'O' if st.session_state.current_player == 'X' else 'X'

def get_cell_style(row: int, col: int) -> str:
    """Get CSS style for a cell based on its age"""
    cell_value = st.session_state.board[row][col]
    if cell_value == '':
        return "background-color: #f0f0f0; border: 2px solid #ddd;"
    
    # Find the age of this move
    move_age = 0
    for i, (r, c, player, timestamp) in enumerate(reversed(st.session_state.move_history)):
        if r == row and c == col:
            move_age = i
            break
    
    # Color based on age (newer moves are more vibrant)
    if cell_value == 'X':
        alpha = max(0.3, 1 - (move_age * 0.2))
        color = f"rgba(255, 99, 132, {alpha})"
    else:  # 'O'
        alpha = max(0.3, 1 - (move_age * 0.2))
        color = f"rgba(54, 162, 235, {alpha})"
    
    return f"background-color: {color}; border: 2px solid #333; color: white; font-weight: bold;"

# Streamlit UI
st.set_page_config(page_title="Vanishing Tic-Tac-Toe", page_icon="🎮", layout="centered")

st.title("🎮 Vanishing Tic-Tac-Toe")
st.markdown("*A strategic twist on the classic game - pieces vanish after a few turns!*")

# Game settings
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    vanish_turns = st.selectbox("Pieces vanish after:", [2, 3, 4, 5], index=1, key="vanish_setting")
    if vanish_turns != st.session_state.vanish_after:
        st.session_state.vanish_after = vanish_turns
        reset_game()

with col2:
    if st.button("🔄 New Game", type="primary"):
        reset_game()

with col3:
    st.metric("Moves until vanish:", st.session_state.vanish_after * 2)

# Game status
if st.session_state.game_over:
    if st.session_state.winner == "Tie":
        st.success("🤝 It's a tie!")
    else:
        st.success(f"🎉 Player {st.session_state.winner} wins!")
else:
    st.info(f"🎯 Current player: **{st.session_state.current_player}**")

# Game board
st.markdown("### Game Board")

# Custom CSS for better styling
st.markdown("""
<style>
.game-button {
    height: 80px;
    font-size: 32px;
    font-weight: bold;
    border-radius: 10px;
    margin: 2px;
    transition: all 0.3s ease;
}
.game-button:hover {
    transform: scale(1.05);
}
</style>
""", unsafe_allow_html=True)

# Create the game board
for row in range(3):
    cols = st.columns(3)
    for col in range(3):
        with cols[col]:
            cell_value = st.session_state.board[row][col]
            button_text = cell_value if cell_value else "  "
            
            # Create button with custom styling
            if st.button(
                button_text,
                key=f"cell_{row}_{col}",
                disabled=st.session_state.game_over or cell_value != '',
                help=f"Click to place {st.session_state.current_player}" if not st.session_state.game_over and cell_value == '' else None
            ):
                make_move(row, col)
                st.rerun()

# Game rules and info
with st.expander("📋 Game Rules"):
    st.markdown(f"""
    **Vanishing Tic-Tac-Toe Rules:**
    
    1. **Basic Rules**: Same as regular tic-tac-toe - get 3 in a row to win!
    
    2. **Vanishing Mechanic**: Pieces disappear after {st.session_state.vanish_after * 2} total moves have been made
    
    3. **Strategy**: Plan ahead! Your early moves will vanish, so timing is crucial
    
    4. **Winning**: Get 3 in a row before your pieces vanish
    
    5. **Visual Cues**: Older pieces appear more faded as they approach vanishing
    """)

# Move history
if st.session_state.move_history:
    with st.expander("📝 Move History"):
        st.write("Recent moves (oldest will vanish first):")
        for i, (row, col, player, timestamp) in enumerate(st.session_state.move_history):
            age = len(st.session_state.move_history) - i
            vanish_in = (st.session_state.vanish_after * 2) - age + 1
            if vanish_in > 0:
                st.write(f"Move {i+1}: Player {player} → Row {row+1}, Col {col+1} (vanishes in {vanish_in} moves)")
            else:
                st.write(f"Move {i+1}: Player {player} → Row {row+1}, Col {col+1} ⚠️ (will vanish next)")

# Footer
st.markdown("---")
st.markdown("*Made with ❤️ using Streamlit*")