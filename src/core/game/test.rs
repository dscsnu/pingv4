use std::collections::HashSet;

use crate::core::game::{board::compute_column_hash, CellState};

#[test]
fn ensure_perfect_column_hashing() {
    const R: usize = 6;

    let mut seen = HashSet::new();

    let colors = [CellState::Red, CellState::Yellow];

    let mut height = 0;
    while height <= R {
        let patterns = 1usize << height;
        let mut mask = 0;

        while mask < patterns {
            let mut column = [None; R];

            let mut row = 0;
            while row < height {
                let bit = (mask >> row) & 1;
                column[row] = Some(colors[bit]);
                row += 1;
            }

            let hash = compute_column_hash::<R>(&column, height);

            assert!(
                seen.insert(hash),
                "Hash collision for column {:?} at height {}",
                column,
                height
            );

            mask += 1;
        }

        height += 1;
    }

    let expected = (1usize << (R + 1)) - 1;

    assert_eq!(
        seen.len(),
        expected,
        "Expected {} unique hashes, found {}",
        expected,
        seen.len()
    );
}
