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
    cell_states: [[Option<CellState>; C]; R],
    game_state: S,
    hash: u64,
}

impl<const R: usize, const C: usize, S: GameState> Board<R, C, S> {
    #[inline]
    pub const fn dimensions(&self) -> (usize, usize) {
        (R, C)
    }

    #[inline]
    pub const fn cell_states(&self) -> &[[Option<CellState>; C]; R] {
        &self.cell_states
    }

    pub fn get_column_hash(&self, col_idx: usize) -> u64 {
        assert!(col_idx < C, "column index {} out of bounds", col_idx);

        let column = &self.cell_states[col_idx];
        todo!()
    }

    pub fn get_board_hash() -> u64 {
        todo!()
    }
}
