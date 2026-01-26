use crate::connect_four::CellState;

// marker trait
pub trait GameState {}

#[derive(Debug, Clone)]
pub struct InProgress {
    player: CellState,
}
impl GameState for InProgress {}

impl InProgress {
    #[inline]
    pub const fn new(player: CellState) -> Self {
        Self { player }
    }

    #[inline]
    pub const fn player(&self) -> CellState {
        self.player
    }
}

#[derive(Debug, Clone)]
pub struct Victory {
    winner: CellState,
}
impl GameState for Victory {}

impl Victory {
    #[inline]
    pub const fn new(winner: CellState) -> Self {
        Self { winner }
    }

    #[inline]
    pub const fn winner(&self) -> CellState {
        self.winner
    }
}

#[derive(Debug, Clone)]
pub struct Draw {}
impl GameState for Draw {}
