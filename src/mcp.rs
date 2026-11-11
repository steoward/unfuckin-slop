//! Unfuckin-Slop as an MCP server.
//!
//! Exposes the design-knowledge layer (cards, packs, lint, mode detection) and
//! specialized free inspiration-gallery entry points (collectui.com, pixlpin.com)
//! over the Model Context Protocol. Browsing the galleries themselves is delegated
//! to the official Playwright MCP server (@playwright/mcp), which handles
//! client-rendered JavaScript SPAs without paywalls or subscriptions.

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
    #[schemars(description = "What you are looking for, e.g. \"pricing page hero\" or \"sign in form\" or \"dashboard\".")]
    pub query: String,
    #[schemars(description = "Free gallery target: \"collectui\", \"pixlpin\", or \"all\" (both are 100% free and open).")]
    #[serde(default = "dall")]
    pub site: String,
}

#[derive(Debug, Deserialize, JsonSchema)]
pub struct CollectUICategoriesArgs {
    #[schemars(description = "Optional search query to filter CollectUI categories (e.g. \"auth\", \"checkout\", \"dashboard\").")]
    pub filter: Option<String>,
}

#[derive(Debug, Deserialize, JsonSchema)]
pub struct PixlpinTagsArgs {
    #[schemars(description = "Optional search query to filter Pixlpin tags (e.g. \"mobile\", \"saas\", \"dark\").")]
    pub filter: Option<String>,
}

#[derive(Debug, Deserialize, JsonSchema)]
pub struct RecipeArgs {
    #[schemars(description = "Target UI component, pattern, or flow, e.g. \"pricing table\" or \"user settings\".")]
    pub query: String,
    #[schemars(description = "Gallery target: \"collectui\" (curated components) or \"pixlpin\" (real flows).")]
    #[serde(default = "dcollectui")]
    pub gallery: String,
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
fn dcollectui() -> String {
    "collectui".into()
}

// ---------- metadata tables ----------

struct CollectUICategory {
    id: &'static str,
    name: &'static str,
    slug: &'static str,
    keywords: &'static [&'static str],
}

static COLLECTUI_CATEGORIES: &[CollectUICategory] = &[
    CollectUICategory {
        id: "sign-in",
        name: "Sign In / Login",
        slug: "sign-in-ui-design-inspiration",
        keywords: &["sign in", "signin", "login", "log in", "auth", "authentication"],
    },
    CollectUICategory {
        id: "sign-up",
        name: "Sign Up / Registration",
        slug: "sign-up-ui-design-inspiration",
        keywords: &["sign up", "signup", "register", "registration", "create account", "auth"],
    },
    CollectUICategory {
        id: "pricing",
        name: "Pricing Table / Plans",
        slug: "pricing-table-ui-design-inspiration",
        keywords: &["pricing", "plans", "tier", "subscription", "price", "billing plan"],
    },
    CollectUICategory {
        id: "checkout",
        name: "Checkout / Payment",
        slug: "checkout-ui-design-inspiration",
        keywords: &["checkout", "payment", "pay", "order summary", "cart checkout"],
    },
    CollectUICategory {
        id: "landing-page",
        name: "Landing Page / Hero",
        slug: "landing-page-ui-design-inspiration",
        keywords: &["landing", "landing page", "hero", "homepage", "marketing page", "showcase"],
    },
    CollectUICategory {
        id: "dashboard",
        name: "Dashboard / Analytics",
        slug: "dashboard-ui-design-inspiration",
        keywords: &["dashboard", "analytics", "stats", "charts", "metrics", "admin"],
    },
    CollectUICategory {
        id: "settings",
        name: "Settings / Preferences",
        slug: "settings-ui-design-inspiration",
        keywords: &["settings", "preferences", "config", "options", "account settings"],
    },
    CollectUICategory {
        id: "user-profile",
        name: "User Profile / Account",
        slug: "user-profile-ui-design-inspiration",
        keywords: &["profile", "user profile", "account", "avatar", "bio"],
    },
    CollectUICategory {
        id: "pop-up-overlay",
        name: "Modal / Pop-up Overlay",
        slug: "pop-up-overlay-ui-design-inspiration",
        keywords: &["modal", "pop-up", "popup", "dialog", "overlay", "sheet"],
    },
    CollectUICategory {
        id: "404-page",
        name: "404 Error Page",
        slug: "404-page-ui-design-inspiration",
        keywords: &["404", "not found", "error page", "empty state 404"],
    },
    CollectUICategory {
        id: "search",
        name: "Search / Autocomplete",
        slug: "search-ui-design-inspiration",
        keywords: &["search", "lookup", "find", "autocomplete", "filter search"],
    },
    CollectUICategory {
        id: "navigation",
        name: "Navigation / Header / Menu",
        slug: "navigation-ui-design-inspiration",
        keywords: &["nav", "navigation", "navbar", "menu", "header", "sidebar"],
    },
    CollectUICategory {
        id: "calculator",
        name: "Calculator",
        slug: "calculator-ui-design-inspiration",
        keywords: &["calculator", "calc", "math", "converter"],
    },
    CollectUICategory {
        id: "music-player",
        name: "Music / Media Player",
        slug: "music-player-ui-design-inspiration",
        keywords: &["music", "audio", "player", "media player", "podcast", "song"],
    },
    CollectUICategory {
        id: "direct-messaging",
        name: "Direct Messaging / Chat",
        slug: "direct-messaging-ui-design-inspiration",
        keywords: &["chat", "message", "messaging", "dm", "inbox", "conversation"],
    },
    CollectUICategory {
        id: "credit-card",
        name: "Credit Card / Payment Form",
        slug: "credit-card-checkout-ui-design-inspiration",
        keywords: &["credit card", "debit card", "card", "stripe form", "card input"],
    },
    CollectUICategory {
        id: "notification",
        name: "Notifications / Alerts",
        slug: "notification-ui-design-inspiration",
        keywords: &["notification", "alerts", "banner", "toast", "bell"],
    },
    CollectUICategory {
        id: "leaderboard",
        name: "Leaderboard / Rankings",
        slug: "leaderboard-ui-design-inspiration",
        keywords: &["leaderboard", "rank", "ranking", "score", "top users"],
    },
    CollectUICategory {
        id: "onboarding",
        name: "Onboarding Flow",
        slug: "onboarding-ui-design-inspiration",
        keywords: &["onboarding", "walkthrough", "welcome", "getting started", "tour"],
    },
    CollectUICategory {
        id: "faq",
        name: "FAQ / Help Center",
        slug: "faq-ui-design-inspiration",
        keywords: &["faq", "help", "questions", "support", "accordion"],
    },
];

struct PixlpinTag {
    tag: &'static str,
    name: &'static str,
    keywords: &'static [&'static str],
}

static PIXLPIN_TAGS: &[PixlpinTag] = &[
    PixlpinTag {
        tag: "mobile",
        name: "Mobile App Screens",
        keywords: &["mobile", "phone", "app", "ios", "android", "touch"],
    },
    PixlpinTag {
        tag: "web",
        name: "Web / SaaS Interfaces",
        keywords: &["web", "desktop", "browser", "saas", "dashboard", "portal"],
    },
    PixlpinTag {
        tag: "dark-mode",
        name: "Dark Mode UIs",
        keywords: &["dark", "dark mode", "night", "black", "dimmed"],
    },
    PixlpinTag {
        tag: "onboarding",
        name: "Onboarding & Walkthroughs",
        keywords: &["onboarding", "welcome", "flow", "signup flow", "intro"],
    },
    PixlpinTag {
        tag: "fintech",
        name: "Fintech & Crypto",
        keywords: &["fintech", "banking", "finance", "crypto", "wallet", "money"],
    },
    PixlpinTag {
        tag: "ecommerce",
        name: "E-Commerce & Shop",
        keywords: &["ecommerce", "shop", "store", "product page", "cart", "catalog"],
    },
    PixlpinTag {
        tag: "minimal",
        name: "Minimalist Design",
        keywords: &["minimal", "clean", "simple", "flat", "monochrome"],
    },
    PixlpinTag {
        tag: "ai",
        name: "AI & Prompt Interfaces",
        keywords: &["ai", "chatgpt", "copilot", "prompt", "assistant", "bot"],
    },
];

// ---------- tool impl ----------

#[tool_router]
impl InspoServer {
    #[tool(description = "Search the 30 Unfuckin-Slop design cards by keyword. Returns id, title, token cost and score. Use before writing UI.")]
    pub async fn search_cards(&self, Parameters(args): Parameters<SearchCardsArgs>) -> String {
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
    pub async fn get_card(&self, Parameters(args): Parameters<GetCardArgs>) -> String {
        let lib = Library::load();
        match lib.cards.iter().find(|c| c.id == args.id) {
            Some(c) => format!(
                "# {} · ~{} tok\n\n{}",
                c.title, c.tokens, c.body
            ),
            None => format!("error: no card \"{}\". Try search_cards.", args.id),
        }
    }

    #[tool(description = "List all 30 cards with token costs (no bodies).")]
    pub async fn list_cards(&self) -> String {
        let lib = Library::load();
        let out: Vec<_> = lib
            .cards
            .iter()
            .map(|c| serde_json::json!({"id": c.id, "title": c.title, "tokens": c.tokens}))
            .collect();
        serde_json::to_string_pretty(&out).unwrap_or_default()
    }

    #[tool(description = "Build a context pack for a task: ranked cards that fit the token budget. Returns markdown bodies.")]
    pub async fn pack(&self, Parameters(args): Parameters<PackArgs>) -> String {
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
    pub async fn detect_mode(&self, Parameters(args): Parameters<SearchCardsArgs>) -> String {
        pack::detect_mode(&args.query)
    }

    #[tool(description = "Run the 18 deterministic anti-slop lint rules on a code snippet. Returns findings with rule, severity, line and fix.")]
    pub async fn lint(&self, Parameters(args): Parameters<LintArgs>) -> String {
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

    #[tool(description = "Get direct search URLs, category deep links, and Playwright recipes for 100% free galleries: CollectUI (collectui.com) and Pixlpin (pixlpin.com). No accounts, paywalls, or paid tokens required.")]
    pub async fn inspiration_sources(&self, Parameters(args): Parameters<InspirationArgs>) -> String {
        let q = urlencoding(&args.query);
        let q_lower = args.query.to_lowercase();
        let site = args.site.to_lowercase();
        let include = |s: &str| site == "all" || site == s;

        let mut sources: Vec<serde_json::Value> = Vec::new();

        if include("collectui") {
            // Check for category deep link match
            let matched_cat = COLLECTUI_CATEGORIES.iter().find(|cat| {
                cat.keywords.iter().any(|kw| q_lower.contains(kw))
            });

            let direct_url = matched_cat.map(|cat| {
                format!("https://collectui.com/designs/{}", cat.slug)
            });

            sources.push(serde_json::json!({
                "gallery": "CollectUI",
                "access": "100% Free & Open (Dribbble curated shots)",
                "recommended_url": direct_url.clone().unwrap_or_else(|| format!("https://collectui.com/search?q={}", q)),
                "direct_category_url": direct_url,
                "matched_category": matched_cat.map(|c| c.name),
                "search_fallback_url": format!("https://collectui.com/search?q={}", q),
                "selectors": {
                    "container": "main, .container",
                    "cards": "article, .post-card",
                    "preview_images": "article img, .post-card img",
                    "titles": "h2, h3, a"
                },
                "playwright_snippet": "await page.goto(url); await page.waitForSelector('img'); const shots = await page.$$eval('img', imgs => imgs.map(i => ({ src: i.src, alt: i.alt })));"
            }));
        }

        if include("pixlpin") {
            let matched_tag = PIXLPIN_TAGS.iter().find(|tag| {
                tag.keywords.iter().any(|kw| q_lower.contains(kw))
            });

            let tag_url = matched_tag.map(|t| format!("https://pixlpin.com/tags/{}", t.tag));

            sources.push(serde_json::json!({
                "gallery": "Pixlpin",
                "access": "100% Free & Open (Production mobile and web app screens)",
                "recommended_url": format!("https://pixlpin.com/search?q={}", q),
                "tag_filter_url": tag_url,
                "matched_tag": matched_tag.map(|t| t.name),
                "selectors": {
                    "cards": ".pin-card, [data-pin], .item",
                    "preview_images": "img[src*='cdn'], .pin-card img, img",
                    "titles": ".title, h3, h4"
                },
                "playwright_snippet": "await page.goto(url); await page.waitForSelector('img'); const pins = await page.$$eval('img', imgs => imgs.map(i => ({ src: i.src, alt: i.alt })));"
            }));
        }

        let out = serde_json::json!({
            "query": args.query,
            "sources": sources,
            "fast_workflow": [
                "1. Open the 'recommended_url' using Playwright MCP ('browser_navigate').",
                "2. Wait for cards/images to load using the provided 'selectors'.",
                "3. Take a focused screenshot or extract reference image URLs with 'browser_snapshot'.",
                "4. Identify the layout structure and spring motion parameters without cloning pixels.",
                "5. Validate implementation against Unfuckin-Slop cards: 'imp.craft-floor' and 'imp.bans'."
            ]
        });

        serde_json::to_string_pretty(&out).unwrap_or_default()
    }

    #[tool(description = "List all 20+ curated UI pattern categories on CollectUI (e.g. Sign In, Checkout, Pricing, Dashboard, Settings, 404) with direct URLs for instant access.")]
    pub async fn collectui_categories(&self, Parameters(args): Parameters<CollectUICategoriesArgs>) -> String {
        let filter = args.filter.as_deref().unwrap_or("").to_lowercase();
        let categories: Vec<_> = COLLECTUI_CATEGORIES
            .iter()
            .filter(|c| {
                filter.is_empty()
                    || c.name.to_lowercase().contains(&filter)
                    || c.id.to_lowercase().contains(&filter)
                    || c.keywords.iter().any(|k| k.contains(&filter))
            })
            .map(|c| {
                serde_json::json!({
                    "id": c.id,
                    "name": c.name,
                    "url": format!("https://collectui.com/designs/{}", c.slug),
                    "keywords": c.keywords
                })
            })
            .collect();

        serde_json::to_string_pretty(&serde_json::json!({
            "count": categories.len(),
            "categories": categories
        }))
        .unwrap_or_default()
    }

    #[tool(description = "List curated Pixlpin tags (e.g. Mobile, Web, Dark Mode, Fintech, E-Commerce, Minimal, AI) with direct filter URLs.")]
    pub async fn pixlpin_tags(&self, Parameters(args): Parameters<PixlpinTagsArgs>) -> String {
        let filter = args.filter.as_deref().unwrap_or("").to_lowercase();
        let tags: Vec<_> = PIXLPIN_TAGS
            .iter()
            .filter(|t| {
                filter.is_empty()
                    || t.name.to_lowercase().contains(&filter)
                    || t.tag.to_lowercase().contains(&filter)
                    || t.keywords.iter().any(|k| k.contains(&filter))
            })
            .map(|t| {
                serde_json::json!({
                    "tag": t.tag,
                    "name": t.name,
                    "url": format!("https://pixlpin.com/tags/{}", t.tag),
                    "keywords": t.keywords
                })
            })
            .collect();

        serde_json::to_string_pretty(&serde_json::json!({
            "count": tags.len(),
            "tags": tags
        }))
        .unwrap_or_default()
    }

    #[tool(description = "Generate a ready-to-execute Playwright automation recipe to find and capture UI design references for a component from CollectUI or Pixlpin.")]
    pub async fn inspiration_recipe(&self, Parameters(args): Parameters<RecipeArgs>) -> String {
        let q = urlencoding(&args.query);
        let gallery = args.gallery.to_lowercase();

        let (target_url, wait_sel, extract_code) = if gallery.contains("pixlpin") {
            (
                format!("https://pixlpin.com/search?q={}", q),
                "img[src*='cdn'], .pin-card img, img",
                "Array.from(document.querySelectorAll('img')).filter(i => i.src && i.naturalWidth > 150).slice(0, 5).map(i => ({ src: i.src, alt: i.alt }))"
            )
        } else {
            let q_lower = args.query.to_lowercase();
            let matched_cat = COLLECTUI_CATEGORIES.iter().find(|cat| {
                cat.keywords.iter().any(|kw| q_lower.contains(kw))
            });
            let url = matched_cat
                .map(|cat| format!("https://collectui.com/designs/{}", cat.slug))
                .unwrap_or_else(|| format!("https://collectui.com/search?q={}", q));
            (
                url,
                "article img, .post-card img, img",
                "Array.from(document.querySelectorAll('article img, .post-card img, img')).filter(i => i.src && i.naturalWidth > 150).slice(0, 5).map(i => ({ src: i.src, alt: i.alt }))"
            )
        };

        let recipe = serde_json::json!({
            "query": args.query,
            "gallery": gallery,
            "target_url": target_url,
            "wait_selector": wait_sel,
            "playwright_mcp_steps": [
                {
                    "step": 1,
                    "tool": "browser_navigate",
                    "args": { "url": target_url }
                },
                {
                    "step": 2,
                    "tool": "browser_wait_for",
                    "args": { "selector": wait_sel }
                },
                {
                    "step": 3,
                    "tool": "browser_snapshot",
                    "args": {}
                }
            ],
            "browser_js_extractor": extract_code,
            "design_quality_rules": [
                "Borrow layout hierarchy and functional contrast ratios.",
                "Never copy exact typography styles without checking 'apple.typography'.",
                "Enforce craft floor: verify keyboard focus, states, and no banned eyebrow tags."
            ]
        });

        serde_json::to_string_pretty(&recipe).unwrap_or_default()
    }
}

#[tool_handler]
impl ServerHandler for InspoServer {
    fn get_info(&self) -> ServerConfig {
        ServerConfig::new(ServerCapabilities::builder().enable_tools().build())
            .with_instructions(
                "Unfuckin-Slop MCP: design knowledge (30 atom cards, packs, lint, mode detection) plus \
                 free, zero-paywall inspiration gallery tools for CollectUI (collectui.com) and Pixlpin (pixlpin.com). \
                 Use 'inspiration_sources' or 'inspiration_recipe' to get direct category deep links and automation steps.",
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
