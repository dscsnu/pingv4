use pyo3::prelude::*;

use crate::core::game::{state, Board};

const R: usize = 6;
const C: usize = 7;

enum GameWrapper {
    InProgress(Board<R, C, state::InProgress>),
    Victory(Board<R, C, state::Victory>),
    Draw(Board<R, C, state::Draw>),
}

#[pyclass]
pub struct ConnectFour {
    inner: GameWrapper,
}

impl Default for GameWrapper {
    #[inline]
    fn default() -> Self {
        GameWrapper::InProgress(Board::default())
    }
}

#[pymethods]
impl ConnectFour {
    // REMOVE later
    #[staticmethod]
    fn test_string() -> String {
        "Hello from rust".into()
    }
}
