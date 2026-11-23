//! Install: write the thin SKILL.md, the cards, and a copy of this binary so
//! the skill keeps working on a machine with no Cargo toolchain.

use std::fs;
use std::io;
use std::path::Path;

use crate::cards::{self, Library};

pub const NOTICE: &str = include_str!("../NOTICE.md");

pub fn install(lib: &Library, target: &Path, force: bool) -> io::Result<usize> {
    let skill_path = target.join("SKILL.md");
    if skill_path.exists() && !force {
        return Err(io::Error::new(
            io::ErrorKind::AlreadyExists,
            format!(
                "{} already exists; rerun with --force to overwrite",
                skill_path.display()
            ),
        ));
    }

    fs::create_dir_all(target.join("cards"))?;
    for card in &lib.cards {
        fs::write(
            target.join("cards").join(format!("{}.md", card.id)),
            &card.raw,
        )?;
    }
    fs::write(target.join("NOTICE.md"), NOTICE)?;

    fs::write(target.join("LICENSE"), include_str!("../LICENSE"))?;
    crate::design::install_library(target)?;
    let exe = std::env::current_exe()?.canonicalize()?;
    let bin_dir = target.join("bin");
    fs::create_dir_all(&bin_dir)?;
    for name in ["unfslop", "slop"] {
        let binary = bin_dir.join(format!("{name}{}", std::env::consts::EXE_SUFFIX));
        if !binary.exists() || binary.canonicalize()? != exe {
            fs::copy(&exe, binary)?;
        }
    }
    fs::write(&skill_path, cards::SKILL_MD)?;
    Ok(lib.cards.len())
}
