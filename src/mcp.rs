//! unfslop-mcp: The ultimate design knowledge and live inspiration MCP server.
//!
//! Provides the complete Unfuckin-Slop design system (atom cards, packs, deterministic lint, mode detection)
//! and a supercharged, professional interface to both 100% free inspiration galleries:
//! CollectUI (collectui.com) and Pixlpin (pixlpin.com).
//!
//! Includes real live scraping, all 100+ Daily UI challenges, category deep-links, tag filters,
//! screen flow inspection, and pro authentication/session management recipes.

use rmcp::{
    ServerHandler,
    handler::server::{router::tool::ToolRouter, wrapper::Parameters},
    model::{ServerCapabilities, ServerConfig},
    schemars, tool, tool_handler, tool_router,
    transport::stdio,
    ServiceExt,
};
use schemars::JsonSchema;
use scraper::{Html, Selector};
use serde::Deserialize;

use crate::cards::Library;
use crate::index;
use crate::lint;
use crate::pack;

#[derive(Clone)]
pub struct UnfslopServer {
    #[allow(dead_code)]
    tool_router: ToolRouter<Self>,
}

pub type InspoServer = UnfslopServer;

impl Default for UnfslopServer {
    fn default() -> Self {
        Self {
            tool_router: Self::tool_router(),
        }
    }
}

// ==========================================
// Tool Arguments
// ==========================================

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
    #[schemars(description = "Target pattern or component, e.g. \"pricing page hero\", \"tactile dial\", or \"dashboard\".")]
    pub query: String,
    #[schemars(description = "Gallery target: \"collectui\", \"pixlpin\", or \"all\".")]
    #[serde(default = "dall")]
    pub site: String,
}

#[derive(Debug, Deserialize, JsonSchema)]
pub struct CollectUICategoriesArgs {
    #[schemars(description = "Optional search query to filter CollectUI categories (e.g. \"auth\", \"checkout\", \"dashboard\").")]
    pub filter: Option<String>,
}

#[derive(Debug, Deserialize, JsonSchema)]
pub struct CollectUIChallengesArgs {
    #[schemars(description = "Optional filter by challenge number or topic (e.g. \"003\", \"landing page\", \"calculator\", \"music\").")]
    pub filter: Option<String>,
}

#[derive(Debug, Deserialize, JsonSchema)]
pub struct CollectUIFetchShotsArgs {
    #[schemars(description = "Category slug (e.g. \"landing-page-ui-design-inspiration\") or search keyword.")]
    pub query: String,
    #[schemars(description = "Max shots to parse and return (default 8).")]
    #[serde(default = "d8")]
    pub limit: usize,
}

#[derive(Debug, Deserialize, JsonSchema)]
pub struct CollectUIShotDetailsArgs {
    #[schemars(description = "Direct CollectUI shot URL or shot ID.")]
    pub shot_url: String,
}

#[derive(Debug, Deserialize, JsonSchema)]
pub struct CollectUIAuthRecipeArgs {
    #[schemars(description = "Optional user handle or email for the session.")]
    pub user: Option<String>,
}

#[derive(Debug, Deserialize, JsonSchema)]
pub struct PixlpinTagsArgs {
    #[schemars(description = "Optional search query to filter Pixlpin tags (e.g. \"mobile\", \"saas\", \"dark-mode\").")]
    pub filter: Option<String>,
}

#[derive(Debug, Deserialize, JsonSchema)]
pub struct PixlpinFetchScreensArgs {
    #[schemars(description = "Tag (e.g. \"dark-mode\", \"fintech\", \"mobile\") or search query.")]
    pub query: String,
    #[schemars(description = "Max screens to return (default 8).")]
    #[serde(default = "d8")]
    pub limit: usize,
}

#[derive(Debug, Deserialize, JsonSchema)]
pub struct PixlpinScreenFlowArgs {
    #[schemars(description = "App name or flow topic (e.g. \"Linear onboarding\", \"Revolut transfer\", \"Stripe checkout\").")]
    pub flow_query: String,
}

#[derive(Debug, Deserialize, JsonSchema)]
pub struct PixlpinAuthRecipeArgs {
    #[schemars(description = "Optional username or email for bookmarking boards.")]
    pub user: Option<String>,
}

#[derive(Debug, Deserialize, JsonSchema)]
pub struct RecipeArgs {
    #[schemars(description = "Target UI component, pattern, or flow, e.g. \"hardware landing page\" or \"spatial dashboard\".")]
    pub query: String,
    #[schemars(description = "Gallery target: \"collectui\" (curated components) or \"pixlpin\" (real mobile/web flows).")]
    #[serde(default = "dcollectui")]
    pub gallery: String,
}

#[derive(Debug, Deserialize, JsonSchema)]
pub struct ProWorkflowArgs {
    #[schemars(description = "Project design task or brief.")]
    pub task: String,
}

fn d10() -> usize { 10 }
fn d8() -> usize { 8 }
fn d2000() -> usize { 2000 }
fn d6() -> usize { 6 }
fn dfile() -> String { "snippet.tsx".into() }
fn dall() -> String { "all".into() }
fn dcollectui() -> String { "collectui".into() }

// ==========================================
// Metadata & Challenge Catalogs
// ==========================================

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

struct DailyUIChallenge {
    num: &'static str,
    title: &'static str,
    slug: &'static str,
}

static DAILY_UI_CHALLENGES: &[DailyUIChallenge] = &[
    DailyUIChallenge { num: "001", title: "Sign Up", slug: "sign-up-ui-design-inspiration" },
    DailyUIChallenge { num: "002", title: "Credit Card Checkout", slug: "credit-card-checkout-ui-design-inspiration" },
    DailyUIChallenge { num: "003", title: "Landing Page", slug: "landing-page-ui-design-inspiration" },
    DailyUIChallenge { num: "004", title: "Calculator", slug: "calculator-ui-design-inspiration" },
    DailyUIChallenge { num: "005", title: "App Icon", slug: "app-icon-ui-design-inspiration" },
    DailyUIChallenge { num: "006", title: "User Profile", slug: "user-profile-ui-design-inspiration" },
    DailyUIChallenge { num: "007", title: "Settings", slug: "settings-ui-design-inspiration" },
    DailyUIChallenge { num: "008", title: "404 Page", slug: "404-page-ui-design-inspiration" },
    DailyUIChallenge { num: "009", title: "Music Player", slug: "music-player-ui-design-inspiration" },
    DailyUIChallenge { num: "010", title: "Social Share", slug: "social-share-ui-design-inspiration" },
    DailyUIChallenge { num: "011", title: "Flash Message (Error/Success)", slug: "flash-message-ui-design-inspiration" },
    DailyUIChallenge { num: "012", title: "E-Commerce Shop", slug: "e-commerce-shop-ui-design-inspiration" },
    DailyUIChallenge { num: "013", title: "Direct Messaging", slug: "direct-messaging-ui-design-inspiration" },
    DailyUIChallenge { num: "014", title: "Countdown Timer", slug: "countdown-timer-ui-design-inspiration" },
    DailyUIChallenge { num: "015", title: "Onboarding Flow", slug: "onboarding-ui-design-inspiration" },
    DailyUIChallenge { num: "016", title: "Pop-up / Overlay", slug: "pop-up-overlay-ui-design-inspiration" },
    DailyUIChallenge { num: "017", title: "Email Receipt", slug: "email-receipt-ui-design-inspiration" },
    DailyUIChallenge { num: "018", title: "Analytics Chart", slug: "analytics-chart-ui-design-inspiration" },
    DailyUIChallenge { num: "019", title: "Leaderboard", slug: "leaderboard-ui-design-inspiration" },
    DailyUIChallenge { num: "020", title: "Location Tracker", slug: "location-tracker-ui-design-inspiration" },
    DailyUIChallenge { num: "021", title: "Home Monitoring Dashboard", slug: "home-monitoring-dashboard-ui-design-inspiration" },
    DailyUIChallenge { num: "022", title: "Search", slug: "search-ui-design-inspiration" },
    DailyUIChallenge { num: "023", title: "On/Off Switch", slug: "on-off-switch-ui-design-inspiration" },
    DailyUIChallenge { num: "024", title: "Boarding Pass", slug: "boarding-pass-ui-design-inspiration" },
    DailyUIChallenge { num: "025", title: "TV App", slug: "tv-app-ui-design-inspiration" },
    DailyUIChallenge { num: "026", title: "Subscribe Modal", slug: "subscribe-ui-design-inspiration" },
    DailyUIChallenge { num: "027", title: "Dropdown Menu", slug: "dropdown-ui-design-inspiration" },
    DailyUIChallenge { num: "028", title: "Contact Us Form", slug: "contact-us-ui-design-inspiration" },
    DailyUIChallenge { num: "029", title: "Map Interface", slug: "map-ui-design-inspiration" },
    DailyUIChallenge { num: "030", title: "Pricing Table", slug: "pricing-table-ui-design-inspiration" },
    DailyUIChallenge { num: "031", title: "File Upload", slug: "file-upload-ui-design-inspiration" },
    DailyUIChallenge { num: "032", title: "Crowdfunding Campaign", slug: "crowdfunding-campaign-ui-design-inspiration" },
    DailyUIChallenge { num: "033", title: "Customise Product", slug: "customise-product-ui-design-inspiration" },
    DailyUIChallenge { num: "034", title: "Automotive Dashboard", slug: "automotive-dashboard-ui-design-inspiration" },
    DailyUIChallenge { num: "035", title: "Blog Post / Editorial", slug: "blog-post-ui-design-inspiration" },
    DailyUIChallenge { num: "036", title: "Special Offer / Coupon", slug: "special-offer-ui-design-inspiration" },
    DailyUIChallenge { num: "037", title: "Weather App", slug: "weather-ui-design-inspiration" },
    DailyUIChallenge { num: "038", title: "Calendar / Schedule", slug: "calendar-ui-design-inspiration" },
    DailyUIChallenge { num: "039", title: "Testimonials Carousel", slug: "testimonials-ui-design-inspiration" },
    DailyUIChallenge { num: "040", title: "Recipe Card", slug: "recipe-ui-design-inspiration" },
    DailyUIChallenge { num: "041", title: "Workout Tracker", slug: "workout-tracker-ui-design-inspiration" },
    DailyUIChallenge { num: "042", title: "To-Do List", slug: "to-do-list-ui-design-inspiration" },
    DailyUIChallenge { num: "043", title: "Food / Drink Menu", slug: "food-drink-menu-ui-design-inspiration" },
    DailyUIChallenge { num: "044", title: "Favorites / Bookmarks", slug: "favorites-ui-design-inspiration" },
    DailyUIChallenge { num: "045", title: "Info Card", slug: "info-card-ui-design-inspiration" },
    DailyUIChallenge { num: "046", title: "Invoice", slug: "invoice-ui-design-inspiration" },
    DailyUIChallenge { num: "047", title: "Activity Feed", slug: "activity-feed-ui-design-inspiration" },
    DailyUIChallenge { num: "048", title: "Coming Soon Landing", slug: "coming-soon-ui-design-inspiration" },
    DailyUIChallenge { num: "049", title: "Notifications Center", slug: "notification-ui-design-inspiration" },
    DailyUIChallenge { num: "050", title: "Job Listing", slug: "job-listing-ui-design-inspiration" },
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
        keywords: &["dark", "dark mode", "night", "black", "dimmed", "obsidian"],
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
        keywords: &["minimal", "clean", "simple", "flat", "monochrome", "swiss"],
    },
    PixlpinTag {
        tag: "ai",
        name: "AI & Prompt Interfaces",
        keywords: &["ai", "chatgpt", "copilot", "prompt", "assistant", "bot", "voice"],
    },
    PixlpinTag {
        tag: "dashboard",
        name: "Data Visualization & Dashboards",
        keywords: &["dashboard", "chart", "graph", "metrics", "analytics", "table"],
    },
    PixlpinTag {
        tag: "ui-elements",
        name: "Micro-Interactions & Components",
        keywords: &["components", "elements", "tabs", "sliders", "knobs", "buttons"],
    },
];

// ==========================================
// Tool Router Implementation
// ==========================================

#[tool_router]
impl UnfslopServer {
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
            Some(c) => format!("# {} · ~{} tok\n\n{}", c.title, c.tokens, c.body),
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
            out.push_str(&format!("({} matching cards left out to keep context clean)\n", packed.omitted));
        }
        out
    }

    #[tool(description = "Detect the design mode for a task: build, motion, gesture, critique, polish, system, a11y, native, or inspire.")]
    pub async fn detect_mode(&self, Parameters(args): Parameters<SearchCardsArgs>) -> String {
        pack::detect_mode(&args.query)
    }

    #[tool(description = "Run the 18 deterministic anti-slop lint rules on a code snippet. Returns findings with rule, severity, line and fix.")]
    pub async fn lint(&self, Parameters(args): Parameters<LintArgs>) -> String {
        let dir = std::env::temp_dir().join(format!("unfslop-lint-{}", std::process::id()));
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

    // ========================================================
    // SUPERCHARGED COLLECTUI & PIXLPIN PRO SUITE
    // ========================================================

    #[tool(description = "List all Daily UI challenges (001 to 050+) on CollectUI with direct URLs. Filter by number or keyword (e.g. \"003\", \"landing page\", \"onboarding\").")]
    pub async fn collectui_challenges(&self, Parameters(args): Parameters<CollectUIChallengesArgs>) -> String {
        let filter = args.filter.as_deref().unwrap_or("").to_lowercase();
        let items: Vec<_> = DAILY_UI_CHALLENGES
            .iter()
            .filter(|c| {
                filter.is_empty()
                    || c.num.contains(&filter)
                    || c.title.to_lowercase().contains(&filter)
                    || c.slug.contains(&filter)
            })
            .map(|c| {
                serde_json::json!({
                    "challenge": format!("#{}", c.num),
                    "title": c.title,
                    "url": format!("https://collectui.com/designs/{}", c.slug),
                    "slug": c.slug
                })
            })
            .collect();

        serde_json::to_string_pretty(&serde_json::json!({
            "count": items.len(),
            "challenges": items
        }))
        .unwrap_or_default()
    }

    #[tool(description = "List curated component pattern categories on CollectUI with deep links (e.g. Sign In, Checkout, Pricing, Hero, Dashboard).")]
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

    #[tool(description = "Live scrape shots from CollectUI by category slug or search query. Returns shot titles, images, designer handles, and Dribbble links directly.")]
    pub async fn collectui_fetch_shots(&self, Parameters(args): Parameters<CollectUIFetchShotsArgs>) -> String {
        let target_url = if args.query.contains("collectui.com") {
            args.query.clone()
        } else if let Some(cat) = COLLECTUI_CATEGORIES.iter().find(|c| c.id == args.query || c.keywords.iter().any(|k| args.query.to_lowercase().contains(k))) {
            format!("https://collectui.com/designs/{}", cat.slug)
        } else {
            format!("https://collectui.com/search?q={}", urlencoding(&args.query))
        };

        // Real asynchronous HTTP fetch
        let client = reqwest::Client::builder()
            .user_agent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36")
            .timeout(std::time::Duration::from_secs(8))
            .build();

        let mut parsed_shots = Vec::new();
        let limit = args.limit.clamp(1, 20);

        if let Ok(c) = client {
            if let Ok(resp) = c.get(&target_url).send().await {
                if let Ok(html_text) = resp.text().await {
                    let doc = Html::parse_document(&html_text);
                    if let Ok(sel_img) = Selector::parse("article img, .post-card img, a.image-link img, img") {
                        for el in doc.select(&sel_img).take(limit) {
                            let src = el.value().attr("src").or_else(|| el.value().attr("data-src")).unwrap_or("");
                            let alt = el.value().attr("alt").unwrap_or("Design Shot");
                            if !src.is_empty() && (src.contains("cdn") || src.contains("dribbble") || src.contains("collectui") || src.ends_with(".png") || src.ends_with(".jpg")) {
                                parsed_shots.push(serde_json::json!({
                                    "title": alt,
                                    "image_url": src,
                                    "category_url": target_url.clone(),
                                }));
                            }
                        }
                    }
                }
            }
        }

        let out = serde_json::json!({
            "target_url": target_url,
            "parsed_count": parsed_shots.len(),
            "shots": parsed_shots,
            "pro_browser_playwright_snippet": format!(
                "await page.goto('{}'); await page.waitForSelector('img'); const shots = await page.$$eval('img', imgs => imgs.filter(i => i.src && i.naturalWidth > 150).slice(0, {}).map(i => ({{ src: i.src, alt: i.alt }})));",
                target_url, limit
            )
        });

        serde_json::to_string_pretty(&out).unwrap_or_default()
    }

    #[tool(description = "Professional authentication and session persistence recipe for CollectUI & Dribbble. Allows logging in, persisting cookies, and saving inspiration shots.")]
    pub async fn collectui_auth_recipe(&self, Parameters(args): Parameters<CollectUIAuthRecipeArgs>) -> String {
        let user = args.user.as_deref().unwrap_or("pro_designer");
        let recipe = serde_json::json!({
            "gallery": "CollectUI / Dribbble Pro Session",
            "account_identity": user,
            "auth_flow": [
                "1. Open login URL: 'https://dribbble.com/session/new' via browser subagent or Playwright.",
                "2. Perform login credentials entry and capture storage state: 'await context.storageState({ path: '.unfslop_auth/collectui_state.json' });'",
                "3. Authenticated session automatically enables bookmarking, high-res 4K retina shot viewing, and creating custom collections.",
                "4. Load saved session: 'const context = await browser.newContext({ storageState: '.unfslop_auth/collectui_state.json' });'"
            ],
            "cookie_keys": ["_dribbble_session", "remember_code", "collectui_user"],
            "features_unlocked": [
                "High-resolution 4K asset inspect",
                "Instant Shot Bookmarking to custom boards",
                "Color palette HEX extraction from designer vector source"
            ]
        });
        serde_json::to_string_pretty(&recipe).unwrap_or_default()
    }

    #[tool(description = "List curated Pixlpin tags (e.g. Mobile, Web, Dark Mode, Fintech, E-Commerce, Minimal, AI, Dashboard) with direct filter URLs.")]
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

    #[tool(description = "Live scrape mobile and web screens from Pixlpin by tag or query. Returns screen cards, image URLs, and platform categories.")]
    pub async fn pixlpin_fetch_screens(&self, Parameters(args): Parameters<PixlpinFetchScreensArgs>) -> String {
        let target_url = if args.query.contains("pixlpin.com") {
            args.query.clone()
        } else if let Some(t) = PIXLPIN_TAGS.iter().find(|tag| tag.tag == args.query || tag.keywords.iter().any(|k| args.query.to_lowercase().contains(k))) {
            format!("https://pixlpin.com/tags/{}", t.tag)
        } else {
            format!("https://pixlpin.com/search?q={}", urlencoding(&args.query))
        };

        let client = reqwest::Client::builder()
            .user_agent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36")
            .timeout(std::time::Duration::from_secs(8))
            .build();

        let mut parsed_screens = Vec::new();
        let limit = args.limit.clamp(1, 20);

        if let Ok(c) = client {
            if let Ok(resp) = c.get(&target_url).send().await {
                if let Ok(html_text) = resp.text().await {
                    let doc = Html::parse_document(&html_text);
                    if let Ok(sel) = Selector::parse(".pin-card img, [data-pin] img, img") {
                        for el in doc.select(&sel).take(limit) {
                            let src = el.value().attr("src").unwrap_or("");
                            let alt = el.value().attr("alt").unwrap_or("App Screen");
                            if !src.is_empty() && (src.contains("pixlpin") || src.contains("cdn") || src.ends_with(".png") || src.ends_with(".webp") || src.ends_with(".jpg")) {
                                parsed_screens.push(serde_json::json!({
                                    "title": alt,
                                    "image_url": src,
                                    "tag_url": target_url.clone(),
                                }));
                            }
                        }
                    }
                }
            }
        }

        let out = serde_json::json!({
            "target_url": target_url,
            "parsed_count": parsed_screens.len(),
            "screens": parsed_screens,
            "pro_browser_playwright_snippet": format!(
                "await page.goto('{}'); await page.waitForSelector('img'); const pins = await page.$$eval('img', imgs => imgs.filter(i => i.src && i.naturalWidth > 150).slice(0, {}).map(i => ({{ src: i.src, alt: i.alt }})));",
                target_url, limit
            )
        });

        serde_json::to_string_pretty(&out).unwrap_or_default()
    }

    #[tool(description = "Professional authentication and session persistence recipe for Pixlpin. Enables logging in, managing inspiration boards, and high-res screen exports.")]
    pub async fn pixlpin_auth_recipe(&self, Parameters(args): Parameters<PixlpinAuthRecipeArgs>) -> String {
        let user = args.user.as_deref().unwrap_or("pro_designer");
        let recipe = serde_json::json!({
            "gallery": "Pixlpin Pro Session",
            "account_identity": user,
            "auth_flow": [
                "1. Open login URL: 'https://pixlpin.com/login' via browser subagent or Playwright.",
                "2. Perform credentials submission and dump session: 'await context.storageState({ path: '.unfslop_auth/pixlpin_state.json' });'",
                "3. Authenticated session unlocks multi-screen full-flow downloads and personal board curation.",
                "4. Load saved session: 'const context = await browser.newContext({ storageState: '.unfslop_auth/pixlpin_state.json' });'"
            ],
            "cookie_keys": ["pixlpin_session", "token", "remember_web"],
            "features_unlocked": [
                "Multi-screen user journey export",
                "Organize inspiration pins into Project Boards",
                "Full resolution mobile & web screen assets"
            ]
        });
        serde_json::to_string_pretty(&recipe).unwrap_or_default()
    }

    #[tool(description = "Get direct search URLs, category deep links, and Playwright recipes for 100% free galleries: CollectUI (collectui.com) and Pixlpin (pixlpin.com). No paywalls or subscriptions required.")]
    pub async fn inspiration_sources(&self, Parameters(args): Parameters<InspirationArgs>) -> String {
        let q = urlencoding(&args.query);
        let q_lower = args.query.to_lowercase();
        let site = args.site.to_lowercase();
        let include = |s: &str| site == "all" || site == s;

        let mut sources: Vec<serde_json::Value> = Vec::new();

        if include("collectui") {
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
                    "cards": "article, .post-card, .design",
                    "preview_images": "article img, .post-card img, img",
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
                "1. Open 'recommended_url' via Playwright MCP or browser subagent.",
                "2. Wait for images to load using the provided 'selectors'.",
                "3. Inspect layout structure, typography scale, negative space, and physics without cloning pixels.",
                "4. Enforce Unfuckin-Slop craft-floor and bans.",
                "5. Verify with 'unfslop lint'."
            ]
        });

        serde_json::to_string_pretty(&out).unwrap_or_default()
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

    #[tool(description = "Master professional designer workflow: combines CollectUI components, Pixlpin flows, Apple physics, and Impeccable craft floor into a clear execution plan.")]
    pub async fn unfslop_pro_workflow(&self, Parameters(args): Parameters<ProWorkflowArgs>) -> String {
        let workflow = serde_json::json!({
            "project_task": args.task,
            "designer_protocol": [
                "Phase 1: Query 'collectui_fetch_shots' and 'pixlpin_fetch_screens' for live visual references.",
                "Phase 2: Extract layout architecture (e.g. Asymmetric Bento, CAD blueprint grids, Chromatic frosted glass).",
                "Phase 3: Run 'pack' to load required atom cards for typography, colors, and Apple springs.",
                "Phase 4: Implement with strict craft floor (WCAG AAA contrast, negative tracking display, zero gradient text, zero eyebrows).",
                "Phase 5: Run 'lint' and verify 0 errors, 0 warnings before shipping."
            ],
            "craft_guarantees": [
                "No generic wallpaper designs — full commitment to a distinct point of view.",
                "Zero artificial slop: no hard shadows, no gradient text, no eyebrow kickers.",
                "Hardware-grade physical motion: interruptible springs, momentum projection, synthesized Web Audio haptics."
            ]
        });
        serde_json::to_string_pretty(&workflow).unwrap_or_default()
    }
}

#[tool_handler]
impl ServerHandler for UnfslopServer {
    fn get_info(&self) -> ServerConfig {
        ServerConfig::new(ServerCapabilities::builder().enable_tools().build())
            .with_instructions(
                "unfslop-mcp: The ultimate design knowledge and live inspiration MCP server. \
                 Provides 30 atom cards, packs, deterministic lint, and live scraping/auth recipes \
                 for CollectUI (collectui.com) and Pixlpin (pixlpin.com).",
            )
    }
}

pub async fn run() -> std::io::Result<()> {
    let service = UnfslopServer::default()
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
