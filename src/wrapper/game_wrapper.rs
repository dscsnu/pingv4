use crate::core::game::{state, Board, CellState, TurnResult};

pub enum GameWrapper<const R: usize, const C: usize> {
    InProgress(Board<R, C, state::InProgress>),
    Victory(Board<R, C, state::Victory>),
    Draw(Board<R, C, state::Draw>),
}

impl<const R: usize, const C: usize> GameWrapper<R, C> {
    #[inline]
    pub const fn column_heights(&self) -> &[usize; C] {
        match self {
            Self::InProgress(b) => b.column_heights(),
            Self::Victory(b) => b.column_heights(),
            Self::Draw(b) => b.column_heights(),
        }
    }

    #[inline]
    pub const fn hash(&self) -> u64 {
        match &self {
            GameWrapper::InProgress(b) => b.hash(),
            GameWrapper::Victory(b) => b.hash(),
            GameWrapper::Draw(b) => b.hash(),
        }
    }

    #[inline]
    pub fn get_cell(&self, row: usize, col: usize) -> Option<CellState> {
        let cell_states = match self {
            Self::InProgress(b) => b.cell_states(),
            Self::Victory(b) => b.cell_states(),
            Self::Draw(b) => b.cell_states(),
        };
        cell_states[col][row]
    }
}

impl<const R: usize, const C: usize> From<TurnResult<R, C>> for GameWrapper<R, C> {
    #[inline]
    fn from(turn_result: TurnResult<R, C>) -> Self {
        match turn_result {
            TurnResult::InProgress(board) => GameWrapper::InProgress(board),
            TurnResult::Victory(board) => GameWrapper::Victory(board),
            TurnResult::Draw(board) => GameWrapper::Draw(board),
        }
    }
}
