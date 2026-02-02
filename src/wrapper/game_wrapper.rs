use pyo3::prelude::*;

use crate::core::game::{state, Board, CellState, GameplayError, TurnResult};

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
    pub const fn get_cell_states(&self) -> &[[Option<CellState>; R]; C] {
        match &self {
            GameWrapper::InProgress(b) => b.cell_states(),
            GameWrapper::Victory(b) => b.cell_states(),
            GameWrapper::Draw(b) => b.cell_states(),
        }
    }

    #[inline]
    pub fn get_cell(&self, col: usize, row: usize) -> Option<CellState> {
        let cell_states = self.get_cell_states();
        cell_states[col][row]
    }

    #[inline]
    pub fn make_move(&self, col_idx: usize) -> Result<GameWrapper<R, C>, WrapperError> {
        match self {
            Self::InProgress(board) => {
                let result = board.make_move(col_idx).map_err(WrapperError::Gameplay)?;
                Ok(result.into())
            }
            Self::Victory(_) | Self::Draw(_) => Err(WrapperError::GameNotInProgress),
        }
    }

    #[inline]
    pub fn get_valid_moves(&self) -> Vec<usize> {
        match self {
            Self::InProgress(b) => b.get_valid_moves(),
            _ => vec![],
        }
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

#[pyclass(name = "CellState", eq, eq_int)]
#[derive(Clone, PartialEq, Eq)]
pub enum PyCellState {
    Yellow = 0,
    Red = 1,
}

impl From<CellState> for PyCellState {
    #[inline]
    fn from(value: CellState) -> Self {
        match value {
            CellState::Red => PyCellState::Red,
            CellState::Yellow => PyCellState::Yellow,
        }
    }
}

#[derive(Debug)]
pub enum WrapperError {
    GameNotInProgress,
    Gameplay(GameplayError),
}

impl std::fmt::Display for WrapperError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Self::GameNotInProgress => write!(f, "game is not in progress"),
            Self::Gameplay(e) => write!(f, "{}", e),
        }
    }
}
impl std::error::Error for WrapperError {}
