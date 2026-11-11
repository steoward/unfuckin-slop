//! The mechanical half of the craft floor: checks a text model reliably skips.
//! Every rule is deterministic, cites a card, and names the fix. No auto-fix.

use std::fs;
use std::path::{Path, PathBuf};

#[derive(Clone, Copy, PartialEq, Eq, Debug)]
pub enum Severity {
    Info,
    Warn,
    Error,
}

impl Severity {
    pub fn as_str(self) -> &'static str {
        match self {
            Severity::Info => "info",
            Severity::Warn => "warn",
            Severity::Error => "error",
        }
    }
}

pub struct Finding {
    pub path: String,
    pub line: usize,
    pub rule: &'static str,
    pub severity: Severity,
    pub message: String,
    pub fix: &'static str,
}

pub struct LintReport {
    pub findings: Vec<Finding>,
    pub files: usize,
    pub errors: usize,
    pub warnings: usize,
}

const SKIP_DIRS: &[&str] = &[
    ".git", "node_modules", "target", "dist", "build", ".next", "vendor", "coverage",
    "attic", ".turbo", ".cache", "out", ".venv",
];

const CSS_EXTS: &[&str] = &["css", "scss", "sass", "less"];
const SOURCE_EXTS: &[&str] = &[
    "css", "scss", "sass", "less", "html", "htm", "jsx", "tsx", "js", "mjs", "cjs", "ts",
    "vue", "svelte", "astro",
];
const MARKUP_EXTS: &[&str] = &["html", "htm", "jsx", "tsx", "vue", "svelte", "astro"];

pub fn run(paths: &[String], ignore: &[String]) -> std::io::Result<LintReport> {
    let skips = read_skips();
    let mut files: Vec<PathBuf> = Vec::new();
    for raw in paths {
        let path = Path::new(raw);
        if !path.exists() {
            return Err(std::io::Error::new(
                std::io::ErrorKind::NotFound,
                format!("path not found: {raw}"),
            ));
        }
        collect(path, &mut files, &skips);
    }
    files.sort();
    files.dedup();

    let sources: Vec<(PathBuf, String)> = files
        .iter()
        .filter_map(|path| {
            let meta = fs::metadata(path).ok()?;
            if meta.len() > 2_000_000 {
                return None;
            }
            let text = fs::read_to_string(path).ok()?;
            Some((path.clone(), text))
        })
        .collect();

    let any_pointer = sources.iter().any(|(_, text)| {
        let lower = text.to_lowercase();
        lower.contains("pointerdown") || lower.contains("onpointerdown")
    });

    let mut findings = Vec::new();
    for (path, text) in &sources {
        let display = path.to_string_lossy().replace('\\', "/");
        findings.extend(scan(&display, text, any_pointer));
    }

    findings.retain(|f| {
        !ignore.iter().any(|rule| {
            f.rule == rule
                || f.rule.starts_with(&format!("{rule}."))
                || f.rule.split('.').next() == Some(rule.as_str())
        })
    });
    findings.sort_by(|a, b| {
        a.path
            .cmp(&b.path)
            .then(a.line.cmp(&b.line))
            .then(a.rule.cmp(b.rule))
    });

    let errors = findings
        .iter()
        .filter(|f| f.severity == Severity::Error)
        .count();
    let warnings = findings
        .iter()
        .filter(|f| f.severity == Severity::Warn)
        .count();

    Ok(LintReport {
        findings,
        files: sources.len(),
        errors,
        warnings,
    })
}

fn collect(path: &Path, out: &mut Vec<PathBuf>, skips: &[String]) {
    if skipped(path, skips) {
        return;
    }
    if path.is_dir() {
        if let Ok(entries) = fs::read_dir(path) {
            for entry in entries.flatten() {
                let child = entry.path();
                let name = child
                    .file_name()
                    .unwrap_or_default()
                    .to_string_lossy()
                    .to_lowercase();
                if child.is_dir() {
                    if SKIP_DIRS.contains(&name.as_str()) {
                        continue;
                    }
                    collect(&child, out, skips);
                } else if is_source(&child) {
                    out.push(child);
                }
            }
        }
    } else if is_source(path) {
        out.push(path.to_path_buf());
    }
}

/// `.slopignore` in the working directory: one path prefix per line, `#` for
/// comments. Keeps unrelated tool state out of the scan without a config system.
fn read_skips() -> Vec<String> {
    let mut skips = Vec::new();
    if let Ok(text) = fs::read_to_string(".slopignore") {
        for line in text.lines() {
            let line = line.trim();
            if line.is_empty() || line.starts_with('#') {
                continue;
            }
            skips.push(line.to_string());
        }
    }
    skips
}

fn skipped(path: &Path, skips: &[String]) -> bool {
    if skips.is_empty() {
        return false;
    }
    let normalized = path.to_string_lossy().replace('\\', "/").to_lowercase();
    skips.iter().any(|skip| {
        let skip = skip.trim_matches('/').to_lowercase();
        !skip.is_empty()
            && (normalized == skip
                || normalized.starts_with(&format!("{skip}/"))
                || normalized.contains(&format!("/{skip}/")))
    })
}

fn is_source(path: &Path) -> bool {
    path.extension()
        .and_then(|e| e.to_str())
        .map(|e| SOURCE_EXTS.contains(&e.to_lowercase().as_str()))
        .unwrap_or(false)
}

fn push(
    findings: &mut Vec<Finding>,
    seen: &mut Vec<&'static str>,
    path: &str,
    line: usize,
    rule: &'static str,
    severity: Severity,
    message: impl Into<String>,
    fix: &'static str,
    once: bool,
) {
    if once {
        if seen.contains(&rule) {
            return;
        }
        seen.push(rule);
    }
    findings.push(Finding {
        path: path.to_string(),
        line,
        rule,
        severity,
        message: message.into(),
        fix,
    });
}

fn scan(path: &str, text: &str, any_pointer: bool) -> Vec<Finding> {
    let ext = Path::new(path)
        .extension()
        .and_then(|e| e.to_str())
        .unwrap_or("")
        .to_lowercase();
    let is_css = CSS_EXTS.contains(&ext.as_str());
    let is_markup = MARKUP_EXTS.contains(&ext.as_str());
    let lower = text.to_lowercase();
    let has_reduced = lower.contains("prefers-reduced-motion");
    let has_focus_visible = lower.contains("focus-visible");
    let has_hover = lower.contains(":hover");

    let mut findings: Vec<Finding> = Vec::new();
    let mut seen: Vec<&'static str> = Vec::new();
    let mut selector = String::new();
    let mut has_transform_transition = false;

    for (index, raw) in text.lines().enumerate() {
        let line_no = index + 1;
        let line = raw.trim();
        if line.is_empty() {
            continue;
        }
        let low = line.to_lowercase();

        if line.contains('{') {
            selector = low.split('{').next().unwrap_or("").trim().to_string();
        }
        let decls = declarations(line);
        let value = |prop: &str| -> Option<&str> {
            decls
                .iter()
                .rev()
                .find(|(key, _)| key.eq_ignore_ascii_case(prop))
                .map(|(_, val)| *val)
        };

        // A kicker above a heading is the one permanent ban.
        if ["eyebrow", "kicker", "overline"].iter().any(|w| low.contains(w))
            && (low.contains("class") || line.starts_with('.') || line.starts_with('#'))
        {
            push(
                &mut findings,
                &mut seen,
                path,
                line_no,
                "ban.eyebrow",
                Severity::Error,
                "kicker/eyebrow label above a heading: a permanent ban, no brief earns it back",
                "Delete the label; let the heading carry the section.",
                false,
            );
        }

        if (low.contains("background-clip") && low.contains("text"))
            || (low.contains("-webkit-text-fill-color") && low.contains("transparent"))
        {
            push(
                &mut findings,
                &mut seen,
                path,
                line_no,
                "ban.gradient-text",
                Severity::Error,
                "gradient-clipped text",
                "Use weight, size, or a real colour; emphasis is not a gradient.",
                false,
            );
        }

        for prop in ["border-left", "border-right", "border-inline-start", "border-inline-end"] {
            if let Some(val) = value(prop) {
                if let Some(px) = first_length(val) {
                    if px > 1.0 {
                        push(
                            &mut findings,
                            &mut seen,
                            path,
                            line_no,
                            "ban.side-stripe",
                            Severity::Error,
                            format!("{prop} of {px}px is a coloured side stripe"),
                            "Rewrite the element: no side-stripe callouts, cards, or alerts.",
                            false,
                        );
                    }
                }
            }
        }
        for prop in ["border-left-width", "border-right-width"] {
            if let Some(val) = value(prop) {
                if let Some(px) = first_length(val) {
                    if px > 1.0 {
                        push(
                            &mut findings,
                            &mut seen,
                            path,
                            line_no,
                            "ban.side-stripe",
                            Severity::Error,
                            format!("{prop} of {px}px is a coloured side stripe"),
                            "Rewrite the element instead of softening the stripe.",
                            false,
                        );
                    }
                }
            }
        }

        if let Some(val) = value("box-shadow") {
            let lens = lengths(val);
            if lens.len() >= 3 {
                let (x, y, blur) = (lens[0], lens[1], lens[2]);
                if blur == 0.0 && (x != 0.0 || y != 0.0) {
                    push(
                        &mut findings,
                        &mut seen,
                        path,
                        line_no,
                        "ban.hard-shadow",
                        Severity::Error,
                        format!("zero-blur offset shadow ({x}px {y}px 0)"),
                        "Use a depth system with offset and soft blur, or drop the shadow.",
                        false,
                    );
                } else if x == 0.0 && y == 0.0 {
                    push(
                        &mut findings,
                        &mut seen,
                        path,
                        line_no,
                        "ban.zero-offset-shadow",
                        Severity::Warn,
                        "zero-offset halo is decoration, not depth",
                        "Give the shadow an offset and a blur, or remove it.",
                        false,
                    );
                }
            }
        }

        for prop in ["transition", "transition-property"] {
            if let Some(val) = value(prop) {
                let lval = val.to_lowercase();
                if lval.trim() == "all" || lval.trim_start().starts_with("all ") {
                    push(
                        &mut findings,
                        &mut seen,
                        path,
                        line_no,
                        "ban.transition-all",
                        Severity::Error,
                        "transition: all animates properties you did not choose",
                        "List the properties, usually transform and opacity.",
                        false,
                    );
                }
                if lval.contains("transform") {
                    has_transform_transition = true;
                }
                if [
                    "width", "height", "top", "left", "right", "margin", "padding", "font-size",
                ]
                .iter()
                .any(|p| lval.contains(p))
                {
                    push(
                        &mut findings,
                        &mut seen,
                        path,
                        line_no,
                        "perf.layout-property",
                        Severity::Warn,
                        "animating a layout property costs frames",
                        "Animate transform and opacity; reserve space instead of animating size.",
                        false,
                    );
                }
            }
        }
        if let Some(val) = value("animation") {
            if val.to_lowercase().contains("transform") {
                has_transform_transition = true;
            }
        }

        if let Some(val) = value("letter-spacing") {
            if let Some(em) = em_length(val) {
                if em < -0.04 {
                    push(
                        &mut findings,
                        &mut seen,
                        path,
                        line_no,
                        "type.tracking-floor",
                        Severity::Warn,
                        format!("letter-spacing {em}em is below the -0.04em floor"),
                        "Loosen the tracking; below the floor letters touch.",
                        false,
                    );
                }
            }
        }

        if (selector.contains(":root") || selector == "html" || selector == "body")
            && value("font-size").and_then(first_length).is_some()
        {
            push(
                &mut findings,
                &mut seen,
                path,
                line_no,
                "type.fixed-root-font",
                Severity::Warn,
                "root font-size in px ignores the user's text size setting",
                "Use 100% or a rem value so the layout scales with the user's setting.",
                false,
            );
        }

        if is_markup && low.contains("<img") && !low.contains("alt=") {
            push(
                &mut findings,
                &mut seen,
                path,
                line_no,
                "a11y.img-alt",
                Severity::Warn,
                "image without alt text",
                "Add informative alt, or alt=\"\" when decorative.",
                false,
            );
        }

        if is_markup
            && low.contains("<div")
            && (low.contains("onclick") || low.contains("onpress"))
            && !low.contains("role=")
        {
            push(
                &mut findings,
                &mut seen,
                path,
                line_no,
                "a11y.div-click",
                Severity::Warn,
                "click handler on a div with no role or key handling",
                "Use a button, or add role, tabindex, and key handlers.",
                false,
            );
        }

        if let Some(val) = value("outline") {
            if (val == "none" || val == "0") && !has_focus_visible {
                push(
                    &mut findings,
                    &mut seen,
                    path,
                    line_no,
                    "a11y.outline-none",
                    Severity::Warn,
                    "outline removed with no focus-visible replacement in this file",
                    "Style :focus-visible with a visible ring and offset.",
                    false,
                );
            }
        }

        if is_markup && line.contains('—') && line.contains('>') {
            push(
                &mut findings,
                &mut seen,
                path,
                line_no,
                "copy.em-dash",
                Severity::Info,
                "em dash in interface copy",
                "Use a comma, colon, semicolon, period, or parentheses.",
                false,
            );
        }
        if is_markup && low.contains("click here") {
            push(
                &mut findings,
                &mut seen,
                path,
                line_no,
                "copy.click-here",
                Severity::Info,
                "link text \"click here\" names nothing",
                "Name the destination or the action.",
                false,
            );
        }
        if is_markup && low.contains("lorem ipsum") {
            push(
                &mut findings,
                &mut seen,
                path,
                line_no,
                "copy.lorem",
                Severity::Info,
                "placeholder copy left in the interface",
                "Write real copy; lorem hides overflow and rhythm problems.",
                false,
            );
        }
    }

    if is_css && has_hover && !has_focus_visible {
        push(
            &mut findings,
            &mut seen,
            path,
            1,
            "a11y.focus-visible",
            Severity::Warn,
            "hover styles without a focus-visible equivalent",
            "Give keyboard users the same affordance as the pointer.",
            true,
        );
    }
    if is_css && has_transform_transition && !has_reduced {
        push(
            &mut findings,
            &mut seen,
            path,
            1,
            "motion.reduced",
            Severity::Warn,
            "transform motion with no prefers-reduced-motion fallback",
            "Add a cross-fade branch under prefers-reduced-motion: reduce.",
            true,
        );
    }
    if is_css && has_transform_transition && any_pointer {
        push(
            &mut findings,
            &mut seen,
            path,
            1,
            "motion.css-gesture",
            Severity::Warn,
            "gesture surface animates with CSS; it cannot be interrupted mid-flight",
            "Use a spring that starts from the current value and carries release velocity.",
            true,
        );
    }

    findings
}

fn declarations(line: &str) -> Vec<(&str, &str)> {
    let mut out = Vec::new();
    for segment in line.split(';') {
        let segment = segment.rsplit('{').next().unwrap_or(segment).trim();
        if let Some((key, val)) = segment.split_once(':') {
            let key = key.trim();
            let val = val.trim().trim_end_matches('}').trim();
            if !key.is_empty() && key.len() <= 40 && !key.contains(' ') {
                out.push((key, val));
            }
        }
    }
    out
}

fn first_length(value: &str) -> Option<f64> {
    lengths(value).first().copied()
}

fn lengths(value: &str) -> Vec<f64> {
    value
        .split(|c: char| c == ' ' || c == ',')
        .filter_map(|token| {
            let token = token.trim();
            let digits: String = token
                .chars()
                .take_while(|c| c.is_ascii_digit() || *c == '.' || *c == '-')
                .collect();
            if digits.is_empty() {
                return None;
            }
            let unit = &token[digits.len()..];
            if unit.is_empty() || unit.starts_with("px") {
                digits.parse::<f64>().ok()
            } else {
                None
            }
        })
        .collect()
}

fn em_length(value: &str) -> Option<f64> {
    let digits: String = value
        .trim()
        .chars()
        .take_while(|c| c.is_ascii_digit() || *c == '.' || *c == '-')
        .collect();
    if digits.is_empty() {
        return None;
    }
    let unit = &value.trim()[digits.len()..];
    if unit.starts_with("em") || unit.starts_with("rEm") || unit.starts_with("rem") {
        digits.parse().ok()
    } else {
        None
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn findings(text: &str, name: &str) -> Vec<Finding> {
        scan(name, text, false)
    }

    #[test]
    fn catches_side_stripe_but_not_hairline() {
        let bold = findings(".card { border-left: 4px solid #f00; }", "a.css");
        assert!(bold.iter().any(|f| f.rule == "ban.side-stripe"));
        let hairline = findings(".card { border-left: 1px solid #eee; }", "a.css");
        assert!(!hairline.iter().any(|f| f.rule == "ban.side-stripe"));
    }

    #[test]
    fn catches_transition_all_and_gradient_text() {
        let f = findings(
            ".x { transition: all 300ms ease; background-clip: text; color: transparent; }",
            "a.css",
        );
        assert!(f.iter().any(|x| x.rule == "ban.transition-all"));
        assert!(f.iter().any(|x| x.rule == "ban.gradient-text"));
    }

    #[test]
    fn ignores_soft_shadow_and_flags_hard_one() {
        let soft = findings(".x { box-shadow: 0 8px 24px rgba(0,0,0,.2); }", "a.css");
        assert!(!soft.iter().any(|f| f.rule == "ban.hard-shadow"));
        assert!(!soft.iter().any(|f| f.rule == "ban.zero-offset-shadow"));
        let hard = findings(".x { box-shadow: 4px 4px 0 #000; }", "a.css");
        assert!(hard.iter().any(|f| f.rule == "ban.hard-shadow"));
    }

    #[test]
    fn markup_checks_alt_and_div_click() {
        let f = findings("<div onClick={go}><img src=\"a.png\" /></div>", "a.tsx");
        assert!(f.iter().any(|x| x.rule == "a11y.div-click"));
        assert!(f.iter().any(|x| x.rule == "a11y.img-alt"));
    }

    #[test]
    fn file_level_motion_checks_fire_once() {
        let css = ".a { transition: transform 200ms; }\n.b { transition: transform 300ms; }";
        let f = findings(css, "a.css");
        assert_eq!(f.iter().filter(|x| x.rule == "motion.reduced").count(), 1);
    }

    #[test]
    fn em_dash_only_in_markup_text() {
        assert!(findings("<p>Fast — quiet</p>", "a.tsx")
            .iter()
            .any(|f| f.rule == "copy.em-dash"));
        assert!(!findings("/* fast — quiet */", "a.ts")
            .iter()
            .any(|f| f.rule == "copy.em-dash"));
    }
}
