pub mod connect_four;

use pyo3::prelude::*;

#[pymodule]
fn _core(_m: &Bound<'_, PyModule>) -> PyResult<()> {
    Ok(())
}
