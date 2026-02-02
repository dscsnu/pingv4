use std::fmt::{self, Display, Formatter};

#[derive(Debug)]
pub enum GameplayError {
    ColumnFull,
    ColumnOutOfBounds,
}
impl std::error::Error for GameplayError {}

impl Display for GameplayError {
    fn fmt(&self, f: &mut Formatter<'_>) -> fmt::Result {
        match self {
            Self::ColumnFull => write!(f, "column is at max capacity"),
            Self::ColumnOutOfBounds => write!(f, "column index is out of bounds"),
        }
    }
}
