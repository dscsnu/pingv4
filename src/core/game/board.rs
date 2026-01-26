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
    cell_states: [[Option<CellState>; R]; C],
    game_state: S,
}

impl<const R: usize, const C: usize, S: GameState> Board<R, C, S> {
    #[inline]
    pub const fn dimensions(&self) -> (usize, usize) {
        (R, C)
    }

    #[inline]
    pub const fn cell_states(&self) -> &[[Option<CellState>; R]; C] {
        &self.cell_states
    }
}
