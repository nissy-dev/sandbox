// /// Adds one to the number given.
// /// 与えられた数値に1を足す。
// ///
// /// # Examples
// ///
// /// ```
// /// let five = 5;
// ///
// /// assert_eq!(6, my_crate::add_one(5));
// /// ```
// pub fn add_one(x: i32) -> i32 {
//   x + 1
// }

//! # Art
//!
//! A library for modeling artistic concepts.

// 再エクスポート（APIの階層を隠蔽できる）
pub use kinds::PrimaryColor;
pub use kinds::SecondaryColor;
pub use utils::mix;

pub mod kinds {
  /// The primary colors according to the RYB color model.
  pub enum PrimaryColor {
    Red,
    Yellow,
    Blue,
  }

  /// The secondary colors according to the RYB color model.
  pub enum SecondaryColor {
    Orange,
    Green,
    Purple,
  }
}

pub mod utils {
  use crate::kinds::*;

  /// Combines two primary colors in equal amounts to create a secondary color.
  pub fn mix(c1: PrimaryColor, c2: PrimaryColor) {
    // --snip--
  }
}
