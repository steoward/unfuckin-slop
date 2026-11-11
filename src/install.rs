//! Install: write the thin SKILL.md, the cards, and a copy of this binary so
//! the skill keeps working on a machine with no Cargo toolchain.

use std::fs;
use std::io;
use std::path::Path;

use crate::cards::{self, Library};

pub const NOTICE: &str = "\
# Attribution

Unfuckin-Slop is an independent distillation, rewritten for retrieval. It is
not a copy of either source skill, and neither author endorses it.

- **Apple Design** by Emil Kowalski (github.com/emilkowalski/skills), which
  translates Apple's WWDC interface talks, chiefly *Designing Fluid Interfaces*
  (WWDC 2018), *The Details of UI Typography* (WWDC 2020), and *Principles of
  Great Design* (WWDC 2026), to the web. Apple's underlying material remains
  Apple's copyright.
- **Impeccable** by Paul Bakaus (github.com/pbakaus/impeccable), Apache-2.0,
  itself started from Anthropic's frontend-design skill.

To read either in full, install them at their source. This project exists so
an agent does not have to load them both to answer one question.
";

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
    fs::write(&skill_path, cards::SKILL_MD)?;
    for card in &lib.cards {
        fs::write(
            target.join("cards").join(format!("{}.md", card.id)),
            &card.raw,
        )?;
    }
    fs::write(target.join("NOTICE.md"), NOTICE)?;

    // Copies of the running binaries, so the installed skill is self-contained.
    if let Ok(exe) = std::env::current_exe() {
        let bin_dir = target.join("bin");
        if fs::create_dir_all(&bin_dir).is_ok() {
            let slop_name = if cfg!(windows) { "slop.exe" } else { "slop" };
            let _ = fs::copy(&exe, bin_dir.join(slop_name));
            // If slop-mcp sits next to this binary, copy it too.
            if let Some(dir) = exe.parent() {
                let mcp_name = if cfg!(windows) {
                    "slop-mcp.exe"
                } else {
                    "slop-mcp"
                };
                let mcp_src = dir.join(mcp_name);
                if mcp_src.exists() {
                    let _ = fs::copy(&mcp_src, bin_dir.join(mcp_name));
                }
            }
        }
    }

    Ok(lib.cards.len())
}
