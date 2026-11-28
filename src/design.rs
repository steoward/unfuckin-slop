//! Assemble catalog evidence and two complementary craft lenses for a design agent.

use std::fs;
use std::io;
use std::path::{Path, PathBuf};
use std::process::Command;

use serde_json::{json, Value};

use crate::{cards::Library, index};

const SCRIPT: &str = "search_design_showcases.py";
const BUILD_LIBRARY: &str = "build_library.py";
const LIBRARY_FILES: &[&str] = &[
    SCRIPT, BUILD_LIBRARY, "semantic_index.py", "visual_annotations.py", "source_material.py", "source_bundle.py", "delivery_packet.py", "prepare_catalog.py", "requirements.txt",
];


fn library_root() -> Option<PathBuf> {
    if let Some(path) = std::env::var_os("UNFSLOP_DESIGN_LIBRARY") {
        return Some(PathBuf::from(path)).filter(|p| p.join(SCRIPT).is_file());
    }
    let exe = std::env::current_exe().ok()?;
    let dir = exe.parent()?;
    // Installed skill/bin, or the normal Cargo checkout/target/{release,debug}.
    let installed = dir.join("../design-library");
    if dir.ends_with("bin") && installed.join(SCRIPT).is_file() {
        return Some(installed);
    }
    // Support Cargo target directories nested in a checkout, not only target/debug.
    if dir.ends_with("release") || dir.ends_with("debug") {
        for checkout in dir.ancestors().skip(1) {
            if checkout.join("Cargo.toml").is_file()
                && checkout.join("skills/unfuckin-slop/SKILL.md").is_file()
                && checkout.join(SCRIPT).is_file() {
                return Some(checkout.to_path_buf());
            }
        }
    }
    None
}

pub(crate) fn install_library(target: &Path) -> io::Result<()> {
    let Some(root) = library_root() else { return Ok(()) };
    let destination = target.join("design-library");
    if destination.is_dir() && destination.canonicalize()? == root.canonicalize()? {
        return Ok(());
    }
    for relative in LIBRARY_FILES {
        let output = destination.join(relative);
        fs::create_dir_all(output.parent().expect("file has a parent"))?;
        fs::copy(root.join(relative), output)?;
    }
    for obsolete in [
        "design_showcases/design_embeddings.npy",
        "design_showcases/component_embeddings.npy",
        "design_showcases/encoder/model.onnx",
        "design_showcases/encoder/tokenizer.json",
        "design_showcases/encoder/encoder_config.json",
    ] {
        match fs::remove_file(destination.join(obsolete)) {
            Ok(()) => (),
            Err(error) if error.kind() == io::ErrorKind::NotFound => (),
            Err(error) => return Err(error),
        }
    }
    Ok(())
}

fn retrieve(script: &str, args: &[&str]) -> Result<Value, String> {
    let root = library_root().ok_or("Install from the source checkout or set UNFSLOP_DESIGN_LIBRARY to its root.")?;
    let python = std::env::var_os("UNFSLOP_PYTHON")
        .unwrap_or_else(|| if cfg!(windows) { "python" } else { "python3" }.into());
    let output = Command::new(python)
        .arg(root.join(script))
        .args(args)
        .output()
        .map_err(|e| format!("Cannot start Python ({e}). Set UNFSLOP_PYTHON to a Python executable."))?;
    if !output.status.success() {
        let stderr = String::from_utf8_lossy(&output.stderr);
        let detail = stderr.lines().last().unwrap_or("retriever exited without a diagnostic");
        if output.status.code() == Some(2) {
            return Err(detail.to_owned());
        }
        return Err(format!("{detail}. Check the installed design-library/requirements.txt."));
    }
    serde_json::from_slice(&output.stdout).map_err(|e| format!("Invalid reference packet: {e}"))
}

pub fn record(id: &str, pool: &str) -> Result<Value, String> {
    retrieve(SCRIPT, &["--pool", pool, "--record", id])
}

pub fn build_library(args: &[&str]) -> Result<Value, String> {
    retrieve(BUILD_LIBRARY, args)
}

pub fn brief(lib: &Library, query: &str, pool: &str, source: Option<&str>) -> Value {
    let mut args = vec!["--pool", pool, "--evidence"];
    if let Some(source) = source {
        args.extend(["--source", source]);
    }
    args.extend(["--", query]);
    let evidence = retrieve(SCRIPT, &args).unwrap_or_else(|reason| {
        json!({"status":"unavailable", "backend":null, "references":[], "reason":reason})
    });
    let hits = index::search(&lib.cards, query);
    let mut lenses = Vec::new();
    for (prefix, fallback) in [("imp.", "imp.modes"), ("apple.", "apple.principles")] {
        let matched = hits.iter().find(|h| h.score > 0.0 && h.card.id.starts_with(prefix)
            && h.card.id != "imp.inspiration");
        if let Some(card) = matched.map(|h| h.card).or_else(|| lib.get(fallback)) {
            lenses.push(json!({"id":card.id, "title":card.title, "guidance":card.body, "related":card.pulls}));
        }
    }
    json!({"task":query, "pool":pool, "evidence":evidence, "craft":lenses})
}
