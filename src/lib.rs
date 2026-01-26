#[allow(dead_code)]
mod core;

#[allow(dead_code)]
mod wrapper;

use pyo3::prelude::*;

#[pymodule]
fn _core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<wrapper::ConnectFour>()?;
    Ok(())
}
