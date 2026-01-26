use pyo3::prelude::*;

use crate::core::game::{state, Board};

const NUM_ROWS: usize = 6;
const NUM_COLS: usize = 7;
type ConnectFourBoard<S> = Board<NUM_ROWS, NUM_COLS, S>;

enum GameWrapper {
    Playing(ConnectFourBoard<state::InProgress>),
    Victory(ConnectFourBoard<state::Victory>),
    Draw(ConnectFourBoard<state::Draw>),
}

#[pyclass]
pub struct ConnectFour {
    inner: GameWrapper,
}

#[pymethods]
impl ConnectFour {
    // REMOVE later
    #[staticmethod]
    fn test_string() -> String {
        "Hello from rust".into()
    }
}
