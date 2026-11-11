use std::collections::HashSet;

use unfuckin_slop::cards::Library;
use unfuckin_slop::{lint, pack};

#[test]
fn every_card_parses_with_unique_id_and_metadata() {
    let lib = Library::load();
    assert_eq!(lib.cards.len(), 30, "the library should ship 30 cards");
    let mut ids = HashSet::new();
    for card in &lib.cards {
        assert!(ids.insert(card.id.clone()), "duplicate id {}", card.id);
        assert!(!card.title.trim().is_empty(), "{} has no title", card.id);
        assert!(!card.triggers.is_empty(), "{} has no triggers", card.id);
        assert!(card.tokens > 20, "{} is suspiciously small", card.id);
        assert!(card.body.len() > 200, "{} has no body", card.id);
    }
}

#[test]
fn thin_layer_stays_under_a_fifth_of_the_library() {
    let lib = Library::load();
    let thin = unfuckin_slop::render::estimate_tokens(unfuckin_slop::cards::SKILL_MD);
    assert!(
        thin * 5 < lib.total_tokens(),
        "SKILL.md is {thin} tok against {} in the library; it must stay the thin layer",
        lib.total_tokens()
    );
}

#[test]
fn packs_respect_budget_and_never_pad() {
    let lib = Library::load();
    for (task, mode) in [
        ("draggable bottom sheet that snaps on flick", "gesture"),
        ("critique this dashboard", "critique"),
        ("polish the pricing page", "polish"),
        ("settings page with destructive actions", "build"),
    ] {
        let packed = pack::build(&lib.cards, task, 1600, 6, None, false);
        assert!(!packed.cards.is_empty(), "{task} produced an empty pack");
        assert_eq!(packed.mode, mode, "unexpected mode for {task}");
        if packed.cards.len() > 1 {
            assert!(packed.tokens <= 1600, "{task} packed {} tokens", packed.tokens);
        }
        for card in &packed.cards {
            assert!(
                !card.id.is_empty() && card.tokens <= 1600,
                "a single card exceeded the budget"
            );
        }
    }
}

#[test]
fn lint_finds_the_deliberate_violations() {
    let report = lint::run(&["fixtures".to_string()], &[]).expect("fixtures must be readable");
    assert!(report.errors >= 4, "expected the bans to fire, got {:?}", report.errors);
    let rules: HashSet<&str> = report.findings.iter().map(|f| f.rule).collect();
    for expected in [
        "ban.eyebrow",
        "ban.gradient-text",
        "ban.side-stripe",
        "ban.hard-shadow",
        "ban.transition-all",
    ] {
        assert!(rules.contains(expected), "missing rule {expected}");
    }
}

#[test]
fn ignore_filters_a_whole_group() {
    let report = lint::run(&["fixtures".to_string()], &["ban".to_string()]).unwrap();
    assert!(report.findings.iter().all(|f| !f.rule.starts_with("ban.")));
}

#[test]
fn json_output_is_escaped() {
    assert_eq!(
        unfuckin_slop::render::json_string("a \"b\"\nc"),
        "\"a \\\"b\\\"\\nc\""
    );
}

#[test]
fn doctor_reports_library_status() {
    let lib = Library::load();
    assert_eq!(lib.cards.len(), 30);
    assert!(lib.total_tokens() > 10000);
}
