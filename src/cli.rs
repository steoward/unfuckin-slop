//! Argument parsing and the command surface. Hand-rolled: no dependency, no
//! derive macros, and flag errors that say what to do instead.

use std::path::PathBuf;

use crate::cards::Library;
use crate::{index, install, lint, pack, render};

#[derive(Default)]
struct Flags {
    positional: Vec<String>,
    budget: Option<usize>,
    limit: Option<usize>,
    mode: Option<String>,
    fail_on: Option<String>,
    ignore: Vec<String>,
    dir: Option<String>,
    agent: Option<String>,
    json: bool,
    brief: bool,
    all: bool,
    user: bool,
    force: bool,
    help: bool,
}

pub fn run(args: &[String]) -> i32 {
    let Some(command) = args.first() else {
        print_help();
        return 0;
    };
    let flags = match parse(&args[1..]) {
        Ok(flags) => flags,
        Err(message) => {
            eprintln!("error: {message}");
            return 2;
        }
    };
    if flags.help {
        print_help();
        return 0;
    }
    match command.as_str() {
        "context" | "pack" => context(flags),
        "search" | "find" => search(flags),
        "cards" | "list" => cards(flags),
        "get" | "card" => get(flags),
        "lint" => lint_cmd(flags),
        "install" => install_cmd(flags),
        "doctor" => doctor(flags),
        "stats" => stats(flags),
        "help" | "-h" | "--help" => {
            print_help();
            0
        }
        "version" | "-V" | "--version" => {
            println!("unfuckin-slop {}", env!("CARGO_PKG_VERSION"));
            0
        }
        other => {
            eprintln!("unknown command: {other}");
            print_help();
            2
        }
    }
}

fn parse(args: &[String]) -> Result<Flags, String> {
    let mut flags = Flags::default();
    let mut index = 0;
    while index < args.len() {
        let arg = args[index].clone();
        match arg.as_str() {
            "--json" => flags.json = true,
            "--brief" => flags.brief = true,
            "--all" => flags.all = true,
            "--user" => flags.user = true,
            "--force" => flags.force = true,
            "--help" | "-h" => flags.help = true,
            "--budget" => {
                let value = next_value(args, &mut index, "--budget")?;
                flags.budget = Some(parse_number(&value, "--budget")?);
            }
            "--limit" => {
                let value = next_value(args, &mut index, "--limit")?;
                flags.limit = Some(parse_number(&value, "--limit")?);
            }
            "--mode" => flags.mode = Some(next_value(args, &mut index, "--mode")?),
            "--fail-on" => flags.fail_on = Some(next_value(args, &mut index, "--fail-on")?),
            "--ignore" => flags.ignore.push(next_value(args, &mut index, "--ignore")?),
            "--dir" => flags.dir = Some(next_value(args, &mut index, "--dir")?),
            "--agent" => flags.agent = Some(next_value(args, &mut index, "--agent")?),
            other if other.starts_with("--agent=") => flags.agent = Some(other[8..].to_string()),
            other if other.starts_with("--budget=") => {
                flags.budget = Some(parse_number(&other[9..], "--budget")?);
            }
            other if other.starts_with("--limit=") => {
                flags.limit = Some(parse_number(&other[8..], "--limit")?);
            }
            other if other.starts_with("--mode=") => flags.mode = Some(other[7..].to_string()),
            other if other.starts_with("--fail-on=") => {
                flags.fail_on = Some(other[10..].to_string())
            }
            other if other.starts_with("--ignore=") => {
                flags.ignore.push(other[9..].to_string())
            }
            other if other.starts_with("--dir=") => flags.dir = Some(other[6..].to_string()),
            other if other.starts_with("--") => {
                return Err(format!("unknown flag {other}. Run `unfslop help`."))
            }
            value => flags.positional.push(value.to_string()),
        }
        index += 1;
    }
    Ok(flags)
}

fn next_value(args: &[String], index: &mut usize, flag: &str) -> Result<String, String> {
    *index += 1;
    args.get(*index)
        .cloned()
        .ok_or_else(|| format!("{flag} needs a value"))
}

fn parse_number(value: &str, flag: &str) -> Result<usize, String> {
    value
        .parse()
        .map_err(|_| format!("{flag} must be a number, got {value:?}"))
}

fn context(flags: Flags) -> i32 {
    let library = Library::load();
    let task = flags.positional.join(" ");
    if task.trim().is_empty() {
        eprintln!("error: context needs a task, e.g. unfslop context \"bottom sheet that snaps on flick\"");
        return 2;
    }
    let budget = flags.budget.unwrap_or(pack::DEFAULT_BUDGET);
    let limit = flags.limit.unwrap_or(pack::DEFAULT_LIMIT);
    let packed = pack::build(
        &library.cards,
        &task,
        budget,
        limit,
        flags.mode.as_deref(),
        flags.all,
    );
    if flags.json {
        render::print_pack_json(&packed, &task);
    } else {
        render::print_pack(&packed, &task, flags.brief);
    }
    0
}

fn search(flags: Flags) -> i32 {
    let library = Library::load();
    let query = flags.positional.join(" ");
    if query.trim().is_empty() {
        eprintln!("error: search needs a query, e.g. unfslop search \"focus ring\"");
        return 2;
    }
    let limit = flags.limit.unwrap_or(8);
    let hits: Vec<(f64, &crate::cards::Card)> = index::search(&library.cards, &query)
        .into_iter()
        .filter(|hit| hit.score > 0.0)
        .take(limit)
        .map(|hit| (hit.score, hit.card))
        .collect();
    render::print_search(&hits, &query, flags.json);
    0
}

fn cards(flags: Flags) -> i32 {
    let library = Library::load();
    let mut all: Vec<&crate::cards::Card> = library.cards.iter().collect();
    all.sort_by(|a, b| a.id.cmp(&b.id));
    render::print_cards(&all, library.total_tokens(), flags.json);
    0
}

fn get(flags: Flags) -> i32 {
    let Some(id) = flags.positional.first() else {
        eprintln!("error: get needs a card id, e.g. unfslop get apple.springs");
        return 2;
    };
    let library = Library::load();
    match library.get(id) {
        Some(card) => {
            render::print_card(card, flags.json);
            0
        }
        None => {
            eprintln!("error: no card {id:?}. Run `unfslop cards` or `unfslop search \"<topic>\"`.");
            2
        }
    }
}

fn lint_cmd(flags: Flags) -> i32 {
    let paths = if flags.positional.is_empty() {
        vec![".".to_string()]
    } else {
        flags.positional.clone()
    };
    match lint::run(&paths, &flags.ignore) {
        Ok(report) => {
            render::print_lint(&report, flags.json);
            match flags.fail_on.as_deref().unwrap_or("error") {
                "never" | "none" => 0,
                "warn" | "warning" => {
                    if report.warnings + report.errors > 0 {
                        1
                    } else {
                        0
                    }
                }
                "error" | "errors" => {
                    if report.errors > 0 {
                        1
                    } else {
                        0
                    }
                }
                other => {
                    eprintln!("error: --fail-on takes error, warn, or never, got {other:?}");
                    2
                }
            }
        }
        Err(error) => {
            eprintln!("error: {error}");
            2
        }
    }
}

fn install_cmd(flags: Flags) -> i32 {
    let library = Library::load();
    let target = install_target(&flags);
    match install::install(&library, &target, flags.force) {
        Ok(count) => {
            println!(
                "installed {count} cards → {}",
                target.to_string_lossy().replace('\\', "/")
            );
            println!("binary copied to {}/bin", target.to_string_lossy().replace('\\', "/"));
            println!("next: point your agent's skill directory at that folder, then `unfslop context \"<task>\"`.");
            0
        }
        Err(error) => {
            eprintln!("error: {error}");
            1
        }
    }
}

fn install_target(flags: &Flags) -> PathBuf {
    if let Some(dir) = &flags.dir {
        return PathBuf::from(dir);
    }
    let home = std::env::var("USERPROFILE").or_else(|_| std::env::var("HOME")).ok();
    let agent = flags.agent.as_deref().unwrap_or("claude");
    match agent.to_lowercase().as_str() {
        "antigravity" | "gemini" => {
            if flags.user {
                if let Some(h) = home {
                    return PathBuf::from(h).join(".gemini/config/skills/unfuckin-slop");
                }
            }
            PathBuf::from(".agents/skills/unfuckin-slop")
        }
        "codex" => {
            if flags.user {
                if let Some(h) = home {
                    return PathBuf::from(h).join(".agents/skills/unfuckin-slop");
                }
            }
            PathBuf::from(".agents/skills/unfuckin-slop")
        }
        "opencode" => {
            if flags.user {
                if let Some(h) = home {
                    return PathBuf::from(h).join(".config/opencode/skills/unfuckin-slop");
                }
            }
            PathBuf::from(".opencode/skills/unfuckin-slop")
        }
        "cursor" => {
            if flags.user {
                if let Some(h) = home {
                    return PathBuf::from(h).join(".cursor/skills/unfuckin-slop");
                }
            }
            PathBuf::from(".cursor/skills/unfuckin-slop")
        }
        _ => {
            if flags.user {
                if let Some(h) = home {
                    return PathBuf::from(h).join(".claude/skills/unfuckin-slop");
                }
            }
            PathBuf::from(".claude/skills/unfuckin-slop")
        }
    }
}

fn doctor(_flags: Flags) -> i32 {
    let library = Library::load();
    let total = library.total_tokens();
    let thin = render::estimate_tokens(crate::cards::SKILL_MD);
    let pct = if total == 0 { 0.0 } else { thin as f64 * 100.0 / total as f64 };
    println!("unfuckin-slop {}", env!("CARGO_PKG_VERSION"));
    println!(
        "library     {} cards · {} tok · {}",
        library.cards.len(),
        total,
        library.layer()
    );
    if let Some(dir) = &library.dir {
        let shown = std::fs::canonicalize(dir).unwrap_or_else(|_| dir.clone());
        println!("path        {}", shown.display());
    }
    println!("thin layer  SKILL.md · ~{thin} tok ({pct:.0}% of the library)");
    println!("defaults    budget ~{0} tok · at most {1} cards per pack", pack::DEFAULT_BUDGET, pack::DEFAULT_LIMIT);
    println!("lint        18 mechanical checks");

    let home = std::env::var("USERPROFILE").or_else(|_| std::env::var("HOME")).ok();
    let project_checks = [
        ("claude (proj)", PathBuf::from(".claude/skills/unfuckin-slop")),
        ("agent (proj)", PathBuf::from(".agents/skills/unfuckin-slop")),
    ];
    for (label, path) in project_checks {
        println!(
            "{label:<15} {} ({})",
            if path.join("SKILL.md").exists() { "installed" } else { "not installed" },
            path.to_string_lossy().replace('\\', "/")
        );
    }
    if let Some(h) = &home {
        let user_checks = [
            ("claude (user)", PathBuf::from(h).join(".claude/skills/unfuckin-slop")),
            ("antigravity", PathBuf::from(h).join(".gemini/config/skills/unfuckin-slop")),
            ("codex (user)", PathBuf::from(h).join(".agents/skills/unfuckin-slop")),
        ];
        for (label, path) in user_checks {
            println!(
                "{label:<15} {} ({})",
                if path.join("SKILL.md").exists() { "installed" } else { "not installed" },
                path.to_string_lossy().replace('\\', "/")
            );
        }
    }
    0
}

fn stats(_flags: Flags) -> i32 {
    let library = Library::load();
    let mut groups: Vec<(String, usize, usize)> = Vec::new();
    for card in &library.cards {
        let group = card.id.split('.').next().unwrap_or("other").to_string();
        match groups.iter_mut().find(|(name, _, _)| *name == group) {
            Some((_, count, tokens)) => {
                *count += 1;
                *tokens += card.tokens;
            }
            None => groups.push((group, 1, card.tokens)),
        }
    }
    groups.sort_by(|a, b| b.2.cmp(&a.2));
    println!("{} cards · {} tok total\n", library.cards.len(), library.total_tokens());
    for (name, count, tokens) in &groups {
        println!("{name:<8} {count:>2} cards  {tokens:>5} tok");
    }
    let mut largest: Vec<&crate::cards::Card> = library.cards.iter().collect();
    largest.sort_by_key(|card| std::cmp::Reverse(card.tokens));
    println!("\nlargest:");
    for card in largest.iter().take(5) {
        println!("  {:<30} {} tok", card.id, card.tokens);
    }
    0
}

fn print_help() {
    println!(
        "unfuckin-slop · design context that costs only what the moment needs

USAGE
  unfslop context \"<task>\" [--budget N] [--limit N] [--mode M] [--brief] [--all] [--json]
  unfslop search \"<query>\" [--limit N] [--json]
  unfslop get <card-id> [--json]
  unfslop cards [--json]
  unfslop lint [paths...] [--fail-on error|warn|never] [--ignore rule] [--json]
  unfslop install [--dir PATH | --user] [--agent claude|antigravity|codex|cursor|opencode] [--force]
  unfslop doctor | stats | version | help

CONTEXT is the main command: it ranks cards for the task and prints only the
ones that fit the budget (default {} tok, {} cards). Nothing else is loaded.",
        pack::DEFAULT_BUDGET, pack::DEFAULT_LIMIT
    );
}
