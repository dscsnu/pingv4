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
    cell_states: [[Option<CellState>; C]; R],
    game_state: S,
    cached_hash: u64,
}

impl<const R: usize, const C: usize, S: GameState> Board<R, C, S> {
    #[inline]
    pub const fn dimensions(&self) -> (usize, usize) {
        (R, C)
    }

    #[inline]
    pub const fn cell_states(&self) -> &[[Option<CellState>; C]; R] {
        &self.cell_states
    }

    #[inline]
    pub fn hash(&self) -> u64 {
        self.cached_hash
    }

    #[inline]
    pub fn update_hash(&mut self) {
        self.cached_hash = self.get_board_hash();
    }

    pub fn get_column_hash(&self, col_idx: usize) -> u64 {
        assert!(col_idx < C, "column index {} out of bounds", col_idx);

        let mut hash = 0u64;
        
        for (pos, row_idx) in (0..R).rev().enumerate() {
            if let Some(cell_state) = self.cell_states[row_idx][col_idx] {
                let bit = match cell_state {
                    CellState::Yellow => 0,
                    CellState::Red => 1,
                };
                hash += bit << pos;
            } else {
                break;
            }
        }

        hash
    }

    fn get_column_height(&self, col_idx: usize) -> usize {
        assert!(col_idx < C, "column index {} out of bounds", col_idx);

        let mut height = 0;
        for row_idx in (0..R).rev() {
            if self.cell_states[row_idx][col_idx].is_some() {
                height += 1;
            } else {
                break;
            }
        }

        height
    }

    pub fn get_board_hash(&self) -> u64 {
        let mut columns: Vec<(usize, u64, usize)> = (0..C)
            .map(|col_idx| {
                let height = self.get_column_height(col_idx);
                let col_hash = self.get_column_hash(col_idx);
                (height, col_hash, col_idx)
            })
            .collect();

        columns.sort_by_key(|&(height, col_hash, _)| (height, col_hash));

        let mut board_hash = 0u64;

        for (height, col_hash, _) in columns {
            let offset = if height > 0 {
                (1u64 << height) - 1
            } else {
                0
            };

            board_hash += offset + col_hash;
        }

        board_hash
    }
}
