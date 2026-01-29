#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum CellState {
    Yellow,
    Red,
}

impl CellState {
    #[inline]
    pub const fn other(&self) -> Self {
        match self {
            CellState::Red => CellState::Yellow,
            CellState::Yellow => CellState::Red,
        }
    }
}
