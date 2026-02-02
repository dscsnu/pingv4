use crate::core::game::{
    error::GameplayError,
    state::{Draw, GameState, InProgress, Victory},
    CellState,
};

#[derive(Debug, Clone)]
pub enum TurnResult<const R: usize, const C: usize> {
    InProgress(Board<R, C, InProgress>),
    Victory(Board<R, C, Victory>),
    Draw(Board<R, C, Draw>),
}

#[derive(Debug, Clone)]
pub struct Board<const R: usize, const C: usize, S: GameState> {
    // column-major for cache optimization
    // row-idx 0 is bottom row-idx R-1 is top
    cell_states: [[Option<CellState>; R]; C],
    column_heights: [usize; C],
    game_state: S,
    hash: u64,
}

impl<const R: usize, const C: usize, S: GameState> Board<R, C, S> {
    #[inline]
    pub const fn cell_states(&self) -> &[[Option<CellState>; R]; C] {
        &self.cell_states
    }

    #[inline]
    pub const fn column_heights(&self) -> &[usize; C] {
        &self.column_heights
    }

    #[inline]
    pub const fn get_column_height(&self, col_idx: usize) -> usize {
        self.column_heights[col_idx]
    }

    #[inline]
    pub const fn hash(&self) -> u64 {
        self.hash
    }
}

impl<const R: usize, const C: usize> Board<R, C, Victory> {
    #[inline]
    pub const fn winner(&self) -> CellState {
        self.game_state.winner()
    }
}

impl<const R: usize, const C: usize> Board<R, C, InProgress> {
    #[inline]
    pub fn get_valid_moves(&self) -> Vec<usize> {
        self.column_heights
            .iter()
            .enumerate()
            .filter(|&(_, &height)| height < R)
            .map(|(idx, _)| idx)
            .collect()
    }

    #[inline]
    pub const fn player(&self) -> CellState {
        self.game_state.player()
    }

    pub fn make_move(&self, col_idx: usize) -> Result<TurnResult<R, C>, GameplayError> {
        if col_idx >= C {
            return Err(GameplayError::ColumnOutOfBounds);
        }

        let current_col_height = self.column_heights[col_idx];
        if current_col_height >= R {
            return Err(GameplayError::ColumnFull);
        }

        let current_player = self.game_state.player();

        let mut new_cell_states = self.cell_states.clone();
        new_cell_states[col_idx][current_col_height] = Some(current_player);

        let mut new_column_heights = self.column_heights.clone();
        new_column_heights[col_idx] += 1;

        let hash = compute_board_hash(&new_cell_states, &new_column_heights);

        // victory
        let row_idx = current_col_height;
        if self.check_win(&new_cell_states, row_idx, col_idx, current_player) {
            let victory_state = Victory::new(current_player);
            let victory_board = Board {
                cell_states: new_cell_states,
                column_heights: new_column_heights,
                game_state: victory_state,
                hash,
            };
            return Ok(TurnResult::Victory(victory_board));
        }

        // draw
        if is_board_full::<R, C>(&new_column_heights) {
            let draw_state = Draw {};
            let draw_board = Board {
                cell_states: new_cell_states,
                column_heights: new_column_heights,
                game_state: draw_state,
                hash,
            };
            return Ok(TurnResult::Draw(draw_board));
        }

        // game continues
        let next_player = current_player.other();
        let in_progress_state = InProgress::new(next_player);
        let in_progress_board = Board {
            cell_states: new_cell_states,
            column_heights: new_column_heights,
            game_state: in_progress_state,
            hash,
        };
        Ok(TurnResult::InProgress(in_progress_board))
    }

    const fn check_win(
        &self,
        cell_states: &[[Option<CellState>; R]; C],
        row_idx: usize,
        col_idx: usize,
        player: CellState,
    ) -> bool {
        // check horizontal
        if self.check_direction(cell_states, row_idx, col_idx, player, 0, 1) {
            return true;
        }

        // check vertical
        if self.check_direction(cell_states, row_idx, col_idx, player, 1, 0) {
            return true;
        }

        // check diagonal (bottom-left to top-right)
        if self.check_direction(cell_states, row_idx, col_idx, player, 1, 1) {
            return true;
        }

        // check diagonal (top-left to bottom-right)
        if self.check_direction(cell_states, row_idx, col_idx, player, 1, -1) {
            return true;
        }

        false
    }

    const fn check_direction(
        &self,
        cell_states: &[[Option<CellState>; R]; C],
        row_idx: usize,
        col_idx: usize,
        player: CellState,
        dr: isize,
        dc: isize,
    ) -> bool {
        let mut count = 1;

        // count in +ve dirn
        count += self.count_consecutive(cell_states, row_idx, col_idx, player, dr, dc);

        // count in -ve dirn
        count += self.count_consecutive(cell_states, row_idx, col_idx, player, -dr, -dc);

        count >= 4
    }

    const fn count_consecutive(
        &self,
        cell_states: &[[Option<CellState>; R]; C],
        row_idx: usize,
        col_idx: usize,
        player: CellState,
        dr: isize,
        dc: isize,
    ) -> usize {
        let mut count = 0;
        let mut r = row_idx as isize + dr;
        let mut c = col_idx as isize + dc;

        while r >= 0 && r < R as isize && c >= 0 && c < C as isize {
            match cell_states[c as usize][r as usize] {
                Some(cell_state) => {
                    if matches_player(cell_state, player) {
                        count += 1;
                        r += dr;
                        c += dc;
                    } else {
                        break;
                    }
                }
                None => break,
            }
        }

        count
    }
}

const fn is_board_full<const R: usize, const C: usize>(column_heights: &[usize; C]) -> bool {
    let mut i = 0;
    while i < C {
        if column_heights[i] < R {
            return false;
        }
        i += 1;
    }

    true
}

#[inline]
const fn matches_player(cell_state: CellState, player: CellState) -> bool {
    match (cell_state, player) {
        (CellState::Red, CellState::Red) => true,
        (CellState::Yellow, CellState::Yellow) => true,
        _ => false,
    }
}

pub(super) const fn compute_column_hash<const R: usize>(
    column: &[Option<CellState>; R],
    height: usize,
) -> u64 {
    let mut bit_pattern = 0;
    let mut row_idx = 0;

    // bit_pattern of column
    // ex: RYRY -> 1010
    while row_idx < height {
        match column[row_idx] {
            Some(cell_state) => match cell_state {
                CellState::Red => bit_pattern |= 1 << row_idx,
                CellState::Yellow => {}
            },
            None => {}
        }

        row_idx += 1;
    }

    // (2^col_height - 1)
    let offset = if height > 0 { (1u64 << height) - 1 } else { 0 };

    let hash = bit_pattern + offset;
    hash
}

const fn make_radix_weights<const R: usize, const C: usize>() -> [u64; C] {
    // 2^(R+1)-1
    let base: u64 = (1 << (R + 1)) - 1;

    let mut powers = [0; C];
    let mut i = 0;

    while i < C {
        powers[i] = if i == 0 { 1 } else { powers[i - 1] * base };
        i += 1;
    }

    powers
}

const fn compute_board_hash<const R: usize, const C: usize>(
    cell_states: &[[Option<CellState>; R]; C],
    column_heights: &[usize; C],
) -> u64 {
    let radix_weights: [u64; C] = make_radix_weights::<R, C>();

    let mut hash = 0u64;
    let mut col_idx = 0;

    while col_idx < C {
        let column_hash = compute_column_hash::<R>(&cell_states[col_idx], column_heights[col_idx]);

        hash += column_hash * radix_weights[C - col_idx - 1];
        col_idx += 1;
    }

    hash
}

impl<const R: usize, const C: usize> Default for Board<R, C, InProgress> {
    fn default() -> Self {
        let cell_states = [[None; R]; C];
        let column_heights = [0; C];
        let game_state = InProgress::new(CellState::Red);

        Board {
            cell_states,
            column_heights,
            game_state,
            hash: 0,
        }
    }
}
