//! Card loading. Disk library wins when present; otherwise the cards baked
//! into the binary at build time are used, so the tool works with no install.

use std::collections::BTreeMap;
use std::fs;
use std::path::{Path, PathBuf};

mod embedded {
    include!(concat!(env!("OUT_DIR"), "/embedded.rs"));
}

pub use embedded::SKILL_MD;

#[derive(Clone, Debug)]
pub struct Card {
    pub id: String,
    pub title: String,
    pub triggers: Vec<String>,
    pub pulls: Vec<String>,
    pub weight: u32,
    pub always: bool,
    pub body: String,
    pub tokens: usize,
    pub raw: String,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Source {
    Disk,
    Embedded,
}

pub struct Library {
    pub cards: Vec<Card>,
    pub source: Source,
    pub dir: Option<PathBuf>,
}

impl Library {
    pub fn load() -> Library {
        if let Some(dir) = discover_dir() {
            if let Some(cards) = read_cards(&dir) {
                return Library {
                    cards,
                    source: Source::Disk,
                    dir: Some(dir),
                };
            }
        }
        let mut cards: Vec<Card> = embedded::CARDS
            .iter()
            .filter_map(|(id, raw)| {
                let mut c = Card::parse(raw)?;
                if c.id.is_empty() {
                    c.id = (*id).to_string();
                }
                Some(c)
            })
            .collect();
        cards.sort_by(|a, b| b.weight.cmp(&a.weight).then_with(|| a.id.cmp(&b.id)));
        Library {
            cards,
            source: Source::Embedded,
            dir: None,
        }
    }

    pub fn get(&self, id: &str) -> Option<&Card> {
        self.cards.iter().find(|c| c.id.eq_ignore_ascii_case(id))
    }

    pub fn total_tokens(&self) -> usize {
        self.cards.iter().map(|c| c.tokens).sum()
    }

    pub fn layer(&self) -> &'static str {
        match self.source {
            Source::Disk => "disk",
            Source::Embedded => "embedded",
        }
    }
}

impl Card {
    pub fn parse(raw: &str) -> Option<Card> {
        let mut lines = raw.lines();
        if lines.next()?.trim() != "---" {
            return None;
        }
        let mut fields: BTreeMap<String, String> = BTreeMap::new();
        let mut body = String::new();
        let mut in_front = true;
        for line in lines {
            if in_front {
                if line.trim() == "---" {
                    in_front = false;
                    continue;
                }
                if let Some((k, v)) = line.split_once(':') {
                    fields.insert(
                        k.trim().to_ascii_lowercase(),
                        v.trim().trim_matches('"').to_string(),
                    );
                }
            } else {
                body.push_str(line);
                body.push('\n');
            }
        }
        let id = fields.get("id").cloned().unwrap_or_default();
        if id.is_empty() {
            return None;
        }
        let title = fields
            .get("title")
            .cloned()
            .unwrap_or_else(|| id.replace(['.', '-'], " "));
        let body = body.trim().to_string();
        let tokens = crate::render::estimate_tokens(&title) + crate::render::estimate_tokens(&body);
        Some(Card {
            id,
            title,
            triggers: split_list(fields.get("triggers")),
            pulls: split_list(fields.get("pulls")),
            weight: fields
                .get("weight")
                .and_then(|w| w.trim().parse().ok())
                .unwrap_or(5),
            always: fields.get("always").map(|v| v == "true").unwrap_or(false),
            body,
            tokens,
            raw: raw.trim().to_string(),
        })
    }
}

fn split_list(value: Option<&String>) -> Vec<String> {
    value
        .map(|v| {
            v.split(',')
                .map(|s| s.trim().to_string())
                .filter(|s| !s.is_empty())
                .collect()
        })
        .unwrap_or_default()
}

fn discover_dir() -> Option<PathBuf> {
    if let Ok(home) = std::env::var("UNFUCKIN_SLOP_HOME") {
        let base = PathBuf::from(home);
        let nested = base.join("cards");
        if nested.is_dir() {
            return Some(nested);
        }
        if base.is_dir() {
            return Some(base);
        }
    }
    let mut roots: Vec<PathBuf> = Vec::new();
    if let Ok(exe) = std::env::current_exe() {
        if let Some(parent) = exe.parent() {
            roots.push(parent.to_path_buf());
        }
    }
    if let Ok(cwd) = std::env::current_dir() {
        roots.push(cwd);
    }
    for root in roots {
        for rel in [
            "cards",
            "../cards",
            "skills/unfuckin-slop/cards",
            "../skills/unfuckin-slop/cards",
            "../../skills/unfuckin-slop/cards",
        ] {
            let candidate = root.join(rel);
            if candidate.is_dir() {
                return Some(candidate);
            }
        }
    }
    None
}

fn read_cards(dir: &Path) -> Option<Vec<Card>> {
    let mut cards = Vec::new();
    for entry in fs::read_dir(dir).ok()?.flatten() {
        let path = entry.path();
        if path.extension().map(|e| e != "md").unwrap_or(true) {
            continue;
        }
        if let Ok(raw) = fs::read_to_string(&path) {
            if let Some(card) = Card::parse(&raw) {
                cards.push(card);
            }
        }
    }
    if cards.is_empty() {
        return None;
    }
    cards.sort_by(|a, b| a.id.cmp(&b.id));
    Some(cards)
}
