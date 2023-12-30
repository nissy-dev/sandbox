use std::fmt::Display;

trait ToString {
    fn to_string(&self) -> String;
}

// ジェネリックな実装
#[feature(specialization)]
impl<T: Display> ToString for T {
    default fn to_string(&self) -> String {
        todo!("generic implementation");
    }
}

pub struct Sample;

impl Display for Sample {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        todo!("some implementation");
    }
}

// &strに最適化された実装
impl ToString for Sample {
    fn to_string(&self) -> String {
        todo!("specific implementation");
    }
}
