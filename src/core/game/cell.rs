#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum CellState {
    Red,
    Yellow,
}

impl CellState {
    #[inline]
    pub const fn other(&self) -> Self {
        match self {
            CellState::Red => CellState::Yellow,
            CellState::Yellow => CellState::Red,
        }
    }

    #[inline]
    pub const fn to_bit(&self) -> u64 {
        match self {
            CellState::Red => 1,
            CellState::Yellow => 0,
        }
    }
}
