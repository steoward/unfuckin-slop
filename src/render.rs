//! Output. Plain text for agents, JSON for hosts that want structure.

use crate::cards::Card;
use crate::lint::{Finding, LintReport, Severity};
use crate::pack::Pack;

/// Rough token estimate. Four characters per token is close enough for
/// budgeting and, unlike a tokenizer, adds no dependency and no latency.
pub fn estimate_tokens(text: &str) -> usize {
    (text.chars().count() + 3) / 4
}

pub fn escape_json(text: &str) -> String {
    let mut out = String::with_capacity(text.len() + 8);
    for ch in text.chars() {
        match ch {
            '"' => out.push_str("\\\""),
            '\\' => out.push_str("\\\\"),
            '\n' => out.push_str("\\n"),
            '\r' => out.push_str("\\r"),
            '\t' => out.push_str("\\t"),
            c if (c as u32) < 0x20 => out.push_str(&format!("\\u{:04x}", c as u32)),
            c => out.push(c),
        }
    }
    out
}

pub fn json_string(text: &str) -> String {
    format!("\"{}\"", escape_json(text))
}

fn thousands(n: usize) -> String {
    let s = n.to_string();
    let mut out = String::new();
    for (i, ch) in s.chars().enumerate() {
        if i > 0 && (s.len() - i) % 3 == 0 {
            out.push(',');
        }
        out.push(ch);
    }
    out
}

pub fn print_pack(pack: &Pack<'_>, task: &str, brief: bool) {
    println!(
        "unfuckin-slop · {} · budget {} tok · {} cards · {} tok",
        pack.mode,
        thousands(pack.budget),
        pack.cards.len(),
        thousands(pack.tokens)
    );
    println!("task: {task}");
    if pack.omitted > 0 {
        println!(
            "{} matching card(s) left out to keep the context clean. Ask for one by id if needed.",
            pack.omitted
        );
    }
    println!();
    for (i, card) in pack.cards.iter().enumerate() {
        println!(
            "[{}] {} · {} · ~{} tok",
            i + 1,
            card.id,
            card.title,
            thousands(card.tokens)
        );
        if !brief {
            println!();
            println!("{}", card.body);
        }
        println!();
    }
    if brief {
        return;
    }
    let next: Vec<&str> = pack
        .cards
        .iter()
        .flat_map(|c| c.pulls.iter().map(|s| s.as_str()))
        .filter(|id| !pack.cards.iter().any(|c| c.id == *id))
        .collect();
    if let Some(id) = next.first() {
        println!("next: unfslop get {id}   (only if the work touches that rule)");
    }
}

pub fn print_pack_json(pack: &Pack<'_>, task: &str) {
    let cards: Vec<String> = pack
        .cards
        .iter()
        .map(|c| {
            format!(
                "{{\"id\":{},\"title\":{},\"tokens\":{},\"body\":{}}}",
                json_string(&c.id),
                json_string(&c.title),
                c.tokens,
                json_string(&c.body)
            )
        })
        .collect();
    println!(
        "{{\"task\":{},\"mode\":{},\"budget\":{},\"tokens\":{},\"omitted\":{},\"cards\":[{}]}}",
        json_string(task),
        json_string(&pack.mode),
        pack.budget,
        pack.tokens,
        pack.omitted,
        cards.join(",")
    );
}

pub fn print_card(card: &Card, json: bool) {
    if json {
        println!(
            "{{\"id\":{},\"title\":{},\"tokens\":{},\"triggers\":[{}],\"pulls\":[{}],\"body\":{}}}",
            json_string(&card.id),
            json_string(&card.title),
            card.tokens,
            card.triggers
                .iter()
                .map(|t| json_string(t))
                .collect::<Vec<_>>()
                .join(","),
            card.pulls
                .iter()
                .map(|t| json_string(t))
                .collect::<Vec<_>>()
                .join(","),
            json_string(&card.body)
        );
        return;
    }
    println!("{} · ~{} tok", card.id, thousands(card.tokens));
    println!("{}", card.title);
    println!();
    println!("{}", card.body);
    if !card.pulls.is_empty() {
        println!("\nnext: unfslop get {}   (only if the work touches that rule)", card.pulls[0]);
    }
}

pub fn print_cards(cards: &[&Card], total_tokens: usize, json: bool) {
    if json {
        let items: Vec<String> = cards
            .iter()
            .map(|c| {
                format!(
                    "{{\"id\":{},\"title\":{},\"tokens\":{},\"weight\":{},\"always\":{}}}",
                    json_string(&c.id),
                    json_string(&c.title),
                    c.tokens,
                    c.weight,
                    c.always
                )
            })
            .collect();
        println!(
            "{{\"count\":{},\"tokens\":{},\"cards\":[{}]}}",
            cards.len(),
            total_tokens,
            items.join(",")
        );
        return;
    }
    let id_width = cards.iter().map(|c| c.id.len()).max().unwrap_or(8);
    let title_width = cards.iter().map(|c| c.title.len()).max().unwrap_or(20).min(58);
    for card in cards {
        let mut title: String = card.title.chars().take(title_width).collect();
        if title.len() < card.title.len() {
            title.push('…');
        }
        println!(
            "{:<id_width$}  {:>5} tok  {:<title_width$}  w{}",
            card.id,
            card.tokens,
            title,
            card.weight,
            id_width = id_width,
            title_width = title_width
        );
    }
    println!(
        "\n{} cards · {} tok in the whole library. Never load it whole; use `unfslop context`.",
        cards.len(),
        thousands(total_tokens)
    );
}

pub fn print_search(hits: &[(f64, &Card)], query: &str, json: bool) {
    if json {
        let items: Vec<String> = hits
            .iter()
            .map(|(score, c)| {
                format!(
                    "{{\"id\":{},\"title\":{},\"score\":{:.2},\"tokens\":{}}}",
                    json_string(&c.id),
                    json_string(&c.title),
                    score,
                    c.tokens
                )
            })
            .collect();
        println!(
            "{{\"query\":{},\"hits\":[{}]}}",
            json_string(query),
            items.join(",")
        );
        return;
    }
    if hits.is_empty() {
        println!("no card matches {query:?}. Try a broader word, or `unfslop cards`.");
        return;
    }
    for (score, card) in hits {
        println!("{:>5.2}  {}  ·  {} (~{} tok)", score, card.id, card.title, card.tokens);
    }
    println!("\nload one: unfslop get <id>");
}

pub fn print_lint(report: &LintReport, json: bool) {
    if json {
        let items: Vec<String> = report
            .findings
            .iter()
            .map(|f| {
                format!(
                    "{{\"path\":{},\"line\":{},\"rule\":{},\"severity\":{},\"message\":{},\"fix\":{}}}",
                    json_string(&f.path),
                    f.line,
                    json_string(f.rule),
                    json_string(f.severity.as_str()),
                    json_string(&f.message),
                    json_string(f.fix)
                )
            })
            .collect();
        println!(
            "{{\"files\":{},\"errors\":{},\"warnings\":{},\"findings\":[{}]}}",
            report.files,
            report.errors,
            report.warnings,
            items.join(",")
        );
        return;
    }
    for f in &report.findings {
        println!(
            "{}:{}  {}  {}",
            f.path,
            f.line,
            f.severity.as_str(),
            f.rule
        );
        println!("    {}", f.message);
        println!("    fix: {}", f.fix);
    }
    if !report.findings.is_empty() {
        println!();
    }
    let info = report
        .findings
        .iter()
        .filter(|f| f.severity == Severity::Info)
        .count();
    println!(
        "{} findings · {} error · {} warn · {} info · {} files scanned",
        report.findings.len(),
        report.errors,
        report.warnings,
        info,
        report.files
    );
}

pub fn print_finding(f: &Finding) -> String {
    format!("{}:{} {} {}", f.path, f.line, f.severity.as_str(), f.rule)
}
