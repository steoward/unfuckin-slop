//! Unfuckin-Slop: design knowledge that costs only what the current moment needs.
//!
//! The library is a set of atom cards distilled from two skills, Apple Design
//! (Emil Kowalski, after Apple's WWDC interface talks) and Impeccable (Paul
//! Bakaus, Apache-2.0). `SKILL.md` is the thin always-on layer; this crate is
//! the router that pulls one or two cards into context instead of all of them.

pub mod cards;
pub mod cli;
pub mod index;
pub mod install;
pub mod lint;
pub mod pack;
pub mod render;
pub mod mcp;

pub fn run(args: &[String]) -> i32 {
    cli::run(args)
}
