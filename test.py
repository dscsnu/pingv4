from pingv4._core import ConnectFourBoard, CellState


def test_initial_board():
    """Test initial board state."""
    board = ConnectFourBoard()
    assert board.num_rows == 6
    assert board.num_cols == 7
    assert board.column_heights == [0, 0, 0, 0, 0, 0, 0]
    assert board.hash == 0
    # All cells should be empty
    # Access is column-major: board[col, row]
    for col in range(7):
        for row in range(6):
            assert board[col, row] is None


def test_make_move_returns_new_board():
    """Test that make_move returns a new board (immutability)."""
    board1 = ConnectFourBoard()
    board2 = board1.make_move(3)

    # Original board unchanged (col=3, row=0)
    assert board1[3, 0] is None
    assert board1.column_heights[3] == 0

    # New board has the move (col=3, row=0)
    assert board2[3, 0] == CellState.Red
    assert board2.column_heights[3] == 1


def test_alternating_players():
    """Test that players alternate Red -> Yellow -> Red."""
    board = ConnectFourBoard()

    board = board.make_move(0)  # Red in col 0
    assert board[0, 0] == CellState.Red  # col=0, row=0

    board = board.make_move(1)  # Yellow in col 1
    assert board[1, 0] == CellState.Yellow  # col=1, row=0

    board = board.make_move(2)  # Red in col 2
    assert board[2, 0] == CellState.Red  # col=2, row=0


def test_stacking_pieces():
    """Test that pieces stack in the same column."""
    board = ConnectFourBoard()

    board = board.make_move(0)  # Red at row 0
    board = board.make_move(0)  # Yellow at row 1
    board = board.make_move(0)  # Red at row 2

    # Access as board[col, row] - all in column 0
    assert board[0, 0] == CellState.Red  # col=0, row=0
    assert board[0, 1] == CellState.Yellow  # col=0, row=1
    assert board[0, 2] == CellState.Red  # col=0, row=2
    assert board.column_heights[0] == 3


def test_column_full_error():
    """Test that filling a column raises ValueError."""
    board = ConnectFourBoard()

    # Fill column 0 (6 rows)
    for _ in range(6):
        board = board.make_move(0)

    # Should raise ValueError on 7th move
    try:
        board.make_move(0)
        assert False, "Expected ValueError"
    except ValueError as e:
        assert "column is at max capacity" in str(e)


def test_column_out_of_bounds_error():
    """Test that invalid column index raises ValueError."""
    board = ConnectFourBoard()

    try:
        board.make_move(7)  # Valid columns are 0-6
        assert False, "Expected ValueError"
    except ValueError as e:
        assert "column index is out of bounds" in str(e)

    try:
        board.make_move(100)
        assert False, "Expected ValueError"
    except ValueError as e:
        assert "column index is out of bounds" in str(e)


def test_hash_changes_with_moves():
    """Test that board hash changes after moves."""
    board1 = ConnectFourBoard()
    board2 = board1.make_move(0)
    board3 = board2.make_move(1)

    # Different board states should have different hashes
    assert board1.hash != board2.hash
    assert board2.hash != board3.hash


def test_cell_state_enum():
    """Test CellState enum values."""
    assert CellState.Red != CellState.Yellow

    board = ConnectFourBoard()
    board = board.make_move(0)

    cell = board[0, 0]  # col=0, row=0
    assert cell == CellState.Red
    assert cell != CellState.Yellow


def test_getitem_bounds():
    """Test __getitem__ with various indices."""
    board = ConnectFourBoard()

    # Valid indices return None on empty board (col, row)
    assert board[0, 0] is None
    assert board[6, 5] is None  # Corner: col=6, row=5

    # Make a move and verify access
    board = board.make_move(3)  # Drop in col 3
    assert board[3, 0] == CellState.Red  # col=3, row=0


def test_column_heights_tracking():
    """Test column_heights updates correctly."""
    board = ConnectFourBoard()

    board = board.make_move(0)
    assert board.column_heights == [1, 0, 0, 0, 0, 0, 0]

    board = board.make_move(0)
    assert board.column_heights == [2, 0, 0, 0, 0, 0, 0]

    board = board.make_move(3)
    assert board.column_heights == [2, 0, 0, 1, 0, 0, 0]


def test_game_not_in_progress_error():
    """Test that making a move after victory raises ValueError."""
    board = ConnectFourBoard()

    # Create a horizontal win for Red (4 in a row)
    # Red plays cols 0,1,2,3 with Yellow playing cols 0,1,2 in between
    board = board.make_move(0)  # Red
    board = board.make_move(0)  # Yellow
    board = board.make_move(1)  # Red
    board = board.make_move(1)  # Yellow
    board = board.make_move(2)  # Red
    board = board.make_move(2)  # Yellow
    board = board.make_move(3)  # Red wins with 4 in a row

    # Should raise ValueError when trying to move on finished game
    try:
        board.make_move(4)
        assert False, "Expected ValueError"
    except ValueError as e:
        assert "game is not in progress" in str(e)


def test_draw_game_error():
    """Test that making a move after draw raises ValueError."""
    board = ConnectFourBoard()

    # fmt: off
    draw_sequence = [
        2, 0, 3, 1, 5, 4, 2, 6, 3, 0, 6, 5, 5, 4, 4, 1,
        0, 2, 1, 3, 2, 6, 3, 5, 4, 0, 6, 1, 0, 0, 1, 1,
        2, 2, 4, 3, 3, 4, 5, 5, 6, 0
    ]
    # fmt: on

    for move in draw_sequence:
        # print(board)
        board = board.make_move(move)

    # Board is now full (draw state)
    # Should raise ValueError "game is not in progress"
    try:
        board.make_move(3)
        assert False, "Expected ValueError for move on drawn game"
    except ValueError as e:
        assert "game is not in progress" in str(e), (
            f"Expected 'game is not in progress', got: {e}"
        )


def run_all_tests():
    """Run all tests and report results."""
    tests = [
        test_initial_board,
        test_make_move_returns_new_board,
        test_alternating_players,
        test_stacking_pieces,
        test_column_full_error,
        test_column_out_of_bounds_error,
        test_hash_changes_with_moves,
        test_cell_state_enum,
        test_getitem_bounds,
        test_column_heights_tracking,
        test_game_not_in_progress_error,
        # test_draw_game_error,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            print(f"✓ {test.__name__}")
            passed += 1
        except Exception as e:
            print(f"✗ {test.__name__}: {e}")
            failed += 1

    print(f"\n{passed}/{passed + failed} tests passed")
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
