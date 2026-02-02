mod game_wrapper;
use game_wrapper::GameWrapper;
pub use game_wrapper::PyCellState;

use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;

use crate::core::game::{Board, CellState};

const R: usize = 6;
const C: usize = 7;

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

    #[getter]
    const fn is_in_progress(&self) -> bool {
        match self.inner {
            GameWrapper::InProgress(_) => true,
            _ => false,
        }
    }

    #[getter]
    fn current_player(&self) -> Option<PyCellState> {
        match &self.inner {
            GameWrapper::InProgress(b) => Some(PyCellState::from(b.player())),
            _ => None,
        }
    }

    #[getter]
    const fn is_victory(&self) -> bool {
        match self.inner {
            GameWrapper::Victory(_) => true,
            _ => false,
        }
    }

    #[getter]
    fn winner(&self) -> Option<PyCellState> {
        match &self.inner {
            GameWrapper::Victory(b) => Some(PyCellState::from(b.winner())),
            _ => None,
        }
    }

    #[getter]
    const fn is_draw(&self) -> bool {
        match self.inner {
            GameWrapper::Draw(_) => true,
            _ => false,
        }
    }

    fn make_move(&self, col_idx: usize) -> PyResult<ConnectFourBoard> {
        match self.inner.make_move(col_idx) {
            Ok(new_state) => Ok(ConnectFourBoard { inner: new_state }),
            Err(e) => Err(PyValueError::new_err(e.to_string())),
        }
    }

    fn get_valid_moves(&self) -> Vec<usize> {
        self.inner.get_valid_moves()
    }

    #[getter]
    fn cell_states(&self) -> [[Option<PyCellState>; R]; C] {
        self.inner
            .get_cell_states()
            .clone()
            .map(|col| col.map(|c| c.map(PyCellState::from)))
    }

    fn __getitem__(&self, idx: (usize, usize)) -> Option<PyCellState> {
        let (col, row) = idx;
        self.inner.get_cell(col, row).map(|c| c.into())
    }

    const fn __hash__(&self) -> u64 {
        self.hash()
    }

    const fn __eq__(&self, other: &ConnectFourBoard) -> bool {
        self.hash() == other.hash()
    }

    fn __str__(&self) -> String {
        let cell_states = self.inner.get_cell_states();
        let mut s = String::new();

        // Rows: top to bottom (highest row index first)
        for r in (0..R).rev() {
            s.push_str(&format!("{:>2} |", r));

            for c in 0..C {
                let ch = match cell_states[c][r] {
                    Some(CellState::Red) => 'R',
                    Some(CellState::Yellow) => 'Y',
                    None => '.',
                };

                s.push(ch);
                s.push(' ');
            }

            s.push_str("|\n");
        }

        // Bottom border
        s.push_str("   +");
        for _ in 0..C {
            s.push_str("--");
        }
        s.push_str("+\n");

        // Column indices
        s.push_str("    ");
        for c in 0..C {
            s.push_str(&format!("{} ", c));
        }
        s.push('\n');

        s
    }
}
