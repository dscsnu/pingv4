use crate::core::game::{
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
    pub const fn new<NewState: GameState>(
        cell_states: [[Option<CellState>; R]; C],
        column_heights: [usize; C],
        game_state: NewState,
    ) -> Board<R, C, NewState> {
        let hash = compute_board_hash::<R, C>(&cell_states, &column_heights);

        Board {
            cell_states,
            column_heights,
            game_state,
            hash,
        }
    }

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

pub(super) const fn compute_column_hash<const R: usize>(
    column: &[Option<CellState>; R],
    height: usize,
) -> u64 {
    let mut bit_pattern = 0;
    let mut row_idx = 0;

    // bit_pattern of column
    // ex: RYRY -> 1010
    while row_idx < R {
        match column[row_idx] {
            Some(cell_state) => {
                let bit = cell_state.to_bit();
                bit_pattern |= bit << row_idx;
            }
            None => break,
        }

        row_idx += 1;
    }

    // (2^col_height - 1)
    let offset = if height > 0 { (1u64 << height) - 1 } else { 0 };

    let hash = bit_pattern + offset;
    hash
}

const fn compute_board_hash<const R: usize, const C: usize>(
    cell_states: &[[Option<CellState>; R]; C],
    column_heights: &[usize; C],
) -> u64 {
    todo!()
}
