//! Unfuckin-Slop as an MCP server.
//!
//! Exposes the design-knowledge layer (cards, packs, lint, mode detection) and
//! inspiration-gallery entry points over the Model Context Protocol. Browsing
//! the galleries themselves (collectui.com, pixlpin.com, Mobbin, Refero) is
//! delegated to the official Playwright MCP server, which handles JavaScript
//! rendering and user login via storage state.

use rmcp::{
    ServerHandler,
    handler::server::{router::tool::ToolRouter, wrapper::Parameters},
    model::{ServerCapabilities, ServerConfig},
    schemars, tool, tool_handler, tool_router,
    transport::stdio,
    ServiceExt,
};
use schemars::JsonSchema;
use serde::Deserialize;

use crate::cards::Library;
use crate::index;
use crate::lint;
use crate::pack;

#[derive(Clone)]
pub struct InspoServer {
    #[allow(dead_code)]
    tool_router: ToolRouter<Self>,
}

impl Default for InspoServer {
    fn default() -> Self {
        Self {
            tool_router: Self::tool_router(),
        }
    }
}

// ---------- arg structs ----------

#[derive(Debug, Deserialize, JsonSchema)]
pub struct SearchCardsArgs {
    #[schemars(description = "Query, e.g. \"draggable sheet snap\" or \"contrast focus rings\".")]
    pub query: String,
    #[schemars(description = "Max results (1-20).")]
    #[serde(default = "d10")]
    pub limit: usize,
}

#[derive(Debug, Deserialize, JsonSchema)]
pub struct GetCardArgs {
    #[schemars(description = "Card id, e.g. \"apple.springs\" or \"imp.craft-floor\".")]
    pub id: String,
}

#[derive(Debug, Deserialize, JsonSchema)]
pub struct PackArgs {
    #[schemars(description = "Task description in plain language.")]
    pub task: String,
    #[schemars(description = "Token budget for the pack (default 2000).")]
    #[serde(default = "d2000")]
    pub budget: usize,
    #[schemars(description = "Card ceiling (default 6).")]
    #[serde(default = "d6")]
    pub limit: usize,
    #[schemars(description = "Force a mode: build, motion, gesture, critique, polish, system, a11y, native, inspire.")]
    pub mode: Option<String>,
}

#[derive(Debug, Deserialize, JsonSchema)]
pub struct LintArgs {
    #[schemars(description = "Source code or markup to lint.")]
    pub code: String,
    #[schemars(description = "Virtual filename, e.g. \"Hero.tsx\" or \"styles.css\", used to pick rules.")]
    #[serde(default = "dfile")]
    pub filename: String,
}

#[derive(Debug, Deserialize, JsonSchema)]
pub struct InspirationArgs {
    #[schemars(description = "What you are looking for, e.g. \"pricing page hero\" or \"empty state\".")]
    pub query: String,
    #[schemars(description = "Gallery: collectui, pixlpin, mobbin, refero, or all.")]
    #[serde(default = "dall")]
    pub site: String,
}

fn d10() -> usize {
    10
}
fn d2000() -> usize {
    2000
}
fn d6() -> usize {
    6
}
fn dfile() -> String {
    "snippet.tsx".into()
}
fn dall() -> String {
    "all".into()
}

// ---------- tool impl ----------

#[tool_router]
impl InspoServer {
    #[tool(description = "Search the 29 Unfuckin-Slop design cards by keyword. Returns id, title, token cost and score. Use before writing UI.")]
    async fn search_cards(&self, Parameters(args): Parameters<SearchCardsArgs>) -> String {
        let lib = Library::load();
        let hits = index::search(&lib.cards, &args.query);
        let limit = args.limit.clamp(1, 20);
        let out: Vec<_> = hits
            .into_iter()
            .take(limit)
            .map(|h| {
                serde_json::json!({
                    "id": h.card.id,
                    "title": h.card.title,
                    "tokens": h.card.tokens,
                    "score": (h.score * 100.0).round() / 100.0,
                })
            })
            .collect();
        serde_json::to_string_pretty(&out).unwrap_or_default()
    }

    #[tool(description = "Fetch one design card in full (rules, numbers, code).")]
    async fn get_card(&self, Parameters(args): Parameters<GetCardArgs>) -> String {
        let lib = Library::load();
        match lib.cards.iter().find(|c| c.id == args.id) {
            Some(c) => format!(
                "# {} · ~{} tok\n\n{}",
                c.title, c.tokens, c.body
            ),
            None => format!("error: no card \"{}\". Try search_cards.", args.id),
        }
    }

    #[tool(description = "List all 29 cards with token costs (no bodies).")]
    async fn list_cards(&self) -> String {
        let lib = Library::load();
        let out: Vec<_> = lib
            .cards
            .iter()
            .map(|c| serde_json::json!({"id": c.id, "title": c.title, "tokens": c.tokens}))
            .collect();
        serde_json::to_string_pretty(&out).unwrap_or_default()
    }

    #[tool(description = "Build a context pack for a task: ranked cards that fit the token budget. Returns markdown bodies.")]
    async fn pack(&self, Parameters(args): Parameters<PackArgs>) -> String {
        let lib = Library::load();
        let mode = args.mode.clone();
        let packed = pack::build(&lib.cards, &args.task, args.budget, args.limit, mode.as_deref(), false);
        let mut out = format!(
            "mode: {} · {} cards · {} tok · budget {}\n\n",
            packed.mode, packed.cards.len(), packed.tokens, args.budget
        );
        for c in &packed.cards {
            out.push_str(&format!("## {}\n\n{}\n\n", c.title, c.body));
        }
        if packed.omitted > 0 {
            out.push_str(&format!(
                "({} matching cards left out to keep context clean)\n",
                packed.omitted
            ));
        }
        out
    }

    #[tool(description = "Detect the design mode for a task: build, motion, gesture, critique, polish, system, a11y, native, or inspire.")]
    async fn detect_mode(&self, Parameters(args): Parameters<SearchCardsArgs>) -> String {
        pack::detect_mode(&args.query)
    }

    #[tool(description = "Run the 18 deterministic anti-slop lint rules on a code snippet. Returns findings with rule, severity, line and fix.")]
    async fn lint(&self, Parameters(args): Parameters<LintArgs>) -> String {
        let dir = std::env::temp_dir().join(format!("slop-lint-{}", std::process::id()));
        let _ = std::fs::create_dir_all(&dir);
        let path = dir.join(&args.filename);
        if std::fs::write(&path, &args.code).is_err() {
            return "error: could not write temp file".into();
        }
        let report = match lint::run(&[path.to_string_lossy().to_string()], &[]) {
            Ok(r) => r,
            Err(e) => {
                let _ = std::fs::remove_dir_all(&dir);
                return format!("error: {e}");
            }
        };
        let _ = std::fs::remove_dir_all(&dir);
        let warns = report.findings.iter().filter(|f| f.severity == lint::Severity::Warn).count();
        let infos = report.findings.iter().filter(|f| f.severity == lint::Severity::Info).count();
        let mut out = format!(
            "{} findings · {} error · {} warn · {} info\n",
            report.findings.len(),
            report.errors,
            warns,
            infos
        );
        for f in &report.findings {
            out.push_str(&format!(
                "{}:{} {} {} — {}\n  fix: {}\n",
                f.path, f.line, f.severity.as_str(), f.rule, f.message, f.fix
            ));
        }
        out
    }

    #[tool(description = "Return search URLs and access notes for inspiration galleries (collectui.com, pixlpin.com, Mobbin, Refero). Use these with the Playwright MCP server to browse, render and capture designs. Login via Playwright storage state when required.")]
    async fn inspiration_sources(&self, Parameters(args): Parameters<InspirationArgs>) -> String {
        let q = urlencoding(&args.query);
        let mut sources: Vec<serde_json::Value> = Vec::new();
        let site = args.site.to_lowercase();
        let include = |s: &str| site == "all" || site == s;

        if include("collectui") {
            sources.push(serde_json::json!({
                "name": "CollectUI",
                "url": format!("https://collectui.com/search?q={}", q),
                "access": "free, public, client-rendered SPA (use Playwright MCP to render)",
                "notes": "Curated Dribbble UI shots. Copyrighted; use for inspiration/reference only.",
            }));
        }
        if include("pixlpin") {
            sources.push(serde_json::json!({
                "name": "Pixlpin",
                "url": format!("https://pixlpin.com/search?q={}", q),
                "access": "free, public (use Playwright MCP)",
                "notes": "Real app screens, flows, motion, graphics.",
            }));
        }
        if include("mobbin") {
            sources.push(serde_json::json!({
                "name": "Mobbin",
                "url": format!("https://mobbin.com/search?q={}", q),
                "access": "paid (Pro/Team/Enterprise), official MCP at https://api.mobbin.com/mcp (OAuth)",
                "notes": "621k+ real screens/flows. Use the official Mobbin MCP server for full access.",
            }));
        }
        if include("refero") {
            sources.push(serde_json::json!({
                "name": "Refero",
                "url": format!("https://refero.design/search?q={}", q),
                "access": "paid, official MCP at https://api.refero.design/mcp (OAuth/Bearer)",
                "notes": "Real product screens + styles; DESIGN.md extraction available.",
            }));
        }
        let out = serde_json::json!({
            "query": args.query,
            "sources": sources,
            "workflow": [
                "1. Open the returned URL with Playwright MCP (browser_navigate).",
                "2. Wait for render, then snapshot (browser_snapshot) and extract image URLs/designer.",
                "3. For login-gated galleries, save storage state via Playwright MCP and reuse.",
                "4. Cross-check choices against Unfuckin-Slop cards (craft-floor, bans, modes).",
                "5. Run slop lint on the resulting code.",
            ],
        });
        serde_json::to_string_pretty(&out).unwrap_or_default()
    }
}

#[tool_handler]
impl ServerHandler for InspoServer {
    fn get_info(&self) -> ServerConfig {
        ServerConfig::new(ServerCapabilities::builder().enable_tools().build())
            .with_instructions(
                "Unfuckin-Slop MCP: design knowledge (cards, packs, lint, mode detection) plus \
                 inspiration-gallery entry points. Browse galleries via the Playwright MCP server. \
                 Cards stay the thin layer; pull only what the task needs.",
            )
    }
}

pub async fn run() -> std::io::Result<()> {
    let service = InspoServer::default()
        .serve(stdio())
        .await
        .map_err(|e| std::io::Error::new(std::io::ErrorKind::Other, format!("{e}")))?;
    service
        .waiting()
        .await
        .map_err(|e| std::io::Error::new(std::io::ErrorKind::Other, format!("{e}")))?;
    Ok(())
}

fn urlencoding(s: &str) -> String {
    let mut out = String::with_capacity(s.len());
    for b in s.bytes() {
        match b {
            b'a'..=b'z' | b'A'..=b'Z' | b'0'..=b'9' | b'-' | b'_' | b'.' | b'~' => {
                out.push(b as char)
            }
            b' ' => out.push('+'),
            _ => out.push_str(&format!("%{:02X}", b)),
        }
    }
    out
}
