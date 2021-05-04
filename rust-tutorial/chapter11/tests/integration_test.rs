extern crate chapter11;

mod common;

#[test]
fn integrate_it_adds_two() {
  common::setup();
  assert_eq!(4, chapter11::add_two(2));
}
