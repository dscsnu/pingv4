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
    hash: u64,
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

    #[inline]
    pub fn hash(&self) -> u64 {
        self.hash
    }

    #[inline]
    fn update_hash(&mut self) {
        self.hash = self.get_board_hash();
    }

    pub fn get_column_hash(column: &[Option<CellState>; R]) -> u64 {
        let mut height = 0;
        let mut hash_pattern = 0u64;
        
        for (pos, row_idx) in (0..R).rev().enumerate() {
            if let Some(cell_state) = column[row_idx] {
                let bit = match cell_state {
                    CellState::Yellow => 0,
                    CellState::Red => 1,
                };
                
                hash_pattern += bit << pos;
                height += 1;
            } else {
                break;
            }
        }

        let offset = if height > 0 {
            (1u64 << height) - 1
        } else {
            0
        };
        
        hash_pattern + offset
    }

    pub fn get_board_hash(&self) -> u64 {
        let mut column_hashes: Vec<u64> = (0..C)
            .map(|col_idx| {
                Self::get_column_hash(&self.cell_states[col_idx])
            })
            .collect();

        column_hashes.sort_unstable();
        column_hashes.iter().sum()
    }
}
