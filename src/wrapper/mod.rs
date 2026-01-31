mod game_wrapper;
use game_wrapper::GameWrapper;

use pyo3::prelude::*;

use crate::core::game::{Board, CellState};

const R: usize = 6;
const C: usize = 7;

#[pyclass(name = "CellState", eq, eq_int)]
#[derive(Clone, PartialEq, Eq)]
pub enum PyCellState {
    Yellow = 0,
    Red = 1,
}

#[pyclass]
pub struct ConnectFourBoard {
    inner: GameWrapper<R, C>,
}

#[pymethods]
impl ConnectFourBoard {
    #[new]
    fn new() -> Self {
        ConnectFourBoard {
            inner: GameWrapper::InProgress(Board::default()),
        }
    }

    #[getter]
    const fn num_rows(&self) -> usize {
        R
    }

    #[getter]
    const fn num_cols(&self) -> usize {
        C
    }

    #[getter]
    fn column_heights(&self) -> [usize; C] {
        self.inner.column_heights().clone()
    }

    #[getter]
    const fn hash(&self) -> u64 {
        self.inner.hash()
    }

    fn __getitem__(&self, idx: (usize, usize)) -> Option<PyCellState> {
        let (row, col) = idx;
        self.inner.get_cell(row, col).map(|c| match c {
            CellState::Red => PyCellState::Red,
            CellState::Yellow => PyCellState::Yellow,
        })
    }

    const fn __hash__(&self) -> u64 {
        todo!()
    }

    const fn __eq__(&self, other: &ConnectFourBoard) -> bool {
        self.hash() == other.hash()
    }
}
