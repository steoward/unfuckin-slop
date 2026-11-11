//! Packing: choose the smallest set of cards that answers the moment, and
//! never exceed the token budget. This is the whole point of the project.

use crate::cards::Card;
use crate::index;

pub const DEFAULT_BUDGET: usize = 2000;
pub const DEFAULT_LIMIT: usize = 6;

pub struct Pack<'a> {
    pub cards: Vec<&'a Card>,
    pub tokens: usize,
    pub budget: usize,
    pub omitted: usize,
    pub mode: String,
    /// A mandated card did not fit; the pack stopped rather than padding.
    pub truncated: bool,
}

pub fn detect_mode(task: &str) -> String {
    let t = task.to_lowercase();
    let has = |words: &[&str]| words.iter().any(|w| t.contains(w));

    if has(&[
        "inspiration", "reference", "example", "gallery", "collectui", "pixlpin", "mobbin", "refero",
        "shot", "dribbble", "pattern", "inspo",
    ]) {
        "inspire".to_string()
    } else if has(&["gesture", "swipe", "drag", "grab", "pointer", "touch", "carousel"]) {
        "gesture".to_string()
    } else if has(&[
        "spring", "sheet", "flick", "interrupt", "momentum", "snap", "rubber", "transition",
        "animation", "motion",
    ]) {
        "motion".to_string()
    } else if has(&[
        "accessib", "a11y", "contrast", "keyboard", "screen reader", "focus",
    ]) {
        "a11y".to_string()
    } else if has(&["critique", "review", "audit", "evaluate", "score", "feedback"]) {
        "critique".to_string()
    } else if has(&["polish", "final pass", "refine", "tighten", "clean up"]) {
        "polish".to_string()
    } else if has(&["token", "design system", "design.md", "theme", "palette"]) {
        "system".to_string()
    } else if has(&["ios", "iphone", "ipad", "macos", "native", "swiftui", "android"]) {
        "native".to_string()
    } else {
        "build".to_string()
    }
}

pub fn mode_cards(mode: &str) -> &'static [&'static str] {
    match mode {
        "motion" => &[
            "apple.springs",
            "apple.interruptibility",
            "apple.velocity-projection",
            "imp.motion",
            "apple.motion-a11y",
        ],
        "gesture" => &[
            "apple.direct-manipulation",
            "apple.gestures",
            "apple.spatial",
            "apple.springs",
            "apple.velocity-projection",
        ],
        "critique" => &["imp.critique", "imp.bans", "imp.slop-test", "imp.craft-floor"],
        "polish" => &["imp.polish", "imp.states", "imp.copy", "imp.craft-floor"],
        "system" => &["imp.system", "imp.typeset", "imp.color"],
        "a11y" => &["imp.a11y", "apple.motion-a11y", "imp.states"],
        "native" => &[
            "apple.principles",
            "apple.materials",
            "apple.typography",
            "apple.motion-a11y",
        ],
        "inspire" => &[
            "imp.inspiration",
            "imp.craft-floor",
            "imp.modes",
            "imp.bans",
            "imp.layout",
        ],
        // Build has no fixed syllabus: the ranking and the floor are enough.
        // Injecting general design advice here is exactly the context stuffing
        // this project exists to avoid.
        _ => &[],
    }
}

fn push_unique<'a>(list: &mut Vec<&'a Card>, seen: &mut Vec<String>, card: &'a Card) {
    if !seen.iter().any(|id| id == &card.id) {
        seen.push(card.id.clone());
        list.push(card);
    }
}

pub fn build<'a>(
    cards: &'a [Card],
    task: &str,
    budget: usize,
    limit: usize,
    mode: Option<&str>,
    all: bool,
) -> Pack<'a> {
    let mode_name = mode
        .map(|m| m.to_string())
        .unwrap_or_else(|| detect_mode(task));

    let mut seen: Vec<String> = Vec::new();
    let mut primary: Vec<&Card> = Vec::new();
    for id in mode_cards(&mode_name) {
        if let Some(card) = cards.iter().find(|c| c.id == *id) {
            // The floor is inserted separately; listing it in a mode must not
            // put it in the pack twice.
            if card.always {
                continue;
            }
            push_unique(&mut primary, &mut seen, card);
        }
    }
    let floor = cards.iter().find(|c| c.always);

    // Only genuinely relevant matches become extras. The top score sets the
    // scale, so a weak hit in a big budget cannot masquerade as knowledge.
    let hits = index::search(cards, task);

    // Inside a mode, the subject of this particular request leads. Without
    // this, "swipe to dismiss" would get the same order as every other motion
    // task and might drop the one card that matches.
    let score_of = |id: &str| {
        hits.iter()
            .find(|h| h.card.id == id)
            .map(|h| h.score)
            .unwrap_or(0.0)
    };
    primary.sort_by(|a, b| {
        score_of(&b.id)
            .partial_cmp(&score_of(&a.id))
            .unwrap_or(std::cmp::Ordering::Equal)
            .then_with(|| b.weight.cmp(&a.weight))
    });
    primary.truncate(4);

    let best = hits.first().map(|h| h.score).unwrap_or(0.0);
    let threshold = (best * 0.25).max(1.0);
    let mut extras: Vec<&Card> = Vec::new();
    for hit in hits {
        if hit.score < threshold {
            continue;
        }
        if primary.iter().any(|c| c.id == hit.card.id)
            || floor.map(|f| f.id == hit.card.id).unwrap_or(false)
        {
            continue;
        }
        push_unique(&mut extras, &mut seen, hit.card);
    }

    // Order: the topic, then the quality gate, then the rest of the topic, then
    // relevant extras. The floor sits second so it is read, not skipped.
    let mut ordered: Vec<&Card> = Vec::new();
    if let Some(first) = primary.first() {
        ordered.push(*first);
        if let Some(card) = floor {
            ordered.push(card);
        }
        for card in primary.iter().skip(1) {
            ordered.push(*card);
        }
    } else if let Some(card) = floor {
        ordered.push(card);
    }
    let mandatory = ordered.len();
    let extra_count = extras.len();
    ordered.extend(extras);

    let effective_budget = if all { usize::MAX } else { budget };
    let effective_limit = if all { usize::MAX } else { limit.max(1) };
    let mut chosen: Vec<&Card> = Vec::new();
    let mut tokens = 0;
    let mut truncated = false;

    for (index, card) in ordered.iter().enumerate() {
        if chosen.len() >= effective_limit {
            truncated = true;
            break;
        }
        if tokens + card.tokens <= effective_budget {
            tokens += card.tokens;
            chosen.push(card);
        } else if chosen.is_empty() {
            // The single most relevant card always gets through.
            tokens += card.tokens;
            chosen.push(card);
        } else if index < mandatory {
            // A mandated card did not fit: stop instead of padding the pack
            // with weaker material that happens to be smaller.
            truncated = true;
            break;
        }
    }

    let omitted = primary.len() + extra_count + usize::from(floor.is_some()) - chosen.len();

    Pack {
        cards: chosen,
        tokens,
        budget: if all { tokens } else { budget },
        omitted,
        mode: mode_name,
        truncated,
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::cards::Library;

    fn library() -> Library {
        Library::load()
    }

    #[test]
    fn pack_never_exceeds_budget_unless_one_card() {
        let lib = library();
        let pack = build(&lib.cards, "draggable bottom sheet with spring snap", 700, 6, None, false);
        if pack.cards.len() > 1 {
            assert!(pack.tokens <= 700, "pack of {} tokens", pack.tokens);
        }
    }

    #[test]
    fn pack_prioritises_the_matching_topic() {
        let lib = library();
        let pack = build(&lib.cards, "spring damping for a draggable sheet", 2000, 6, None, false);
        let ids: Vec<&str> = pack.cards.iter().map(|c| c.id.as_str()).collect();
        assert!(
            ids.iter().any(|id| id.starts_with("apple.")),
            "expected an Apple card, got {ids:?}"
        );
    }

    #[test]
    fn no_filler_when_budget_is_loose() {
        let lib = library();
        let pack = build(&lib.cards, "draggable bottom sheet that snaps on flick", 2000, 6, None, false);
        let allowed = mode_cards(&pack.mode);
        for card in &pack.cards {
            assert!(
                allowed.contains(&card.id.as_str()) || card.always,
                "{} is filler, not a requested rule",
                card.id
            );
        }
    }

    #[test]
    fn pack_has_no_duplicate_cards() {
        let lib = library();
        let pack = build(&lib.cards, "critique this dashboard", 3000, 8, None, false);
        let mut ids: Vec<&str> = pack.cards.iter().map(|c| c.id.as_str()).collect();
        let before = ids.len();
        ids.sort();
        ids.dedup();
        assert_eq!(before, ids.len(), "duplicate card in pack: {:?}", ids);
    }

    #[test]
    fn mode_detection_routes_reviews() {
        assert_eq!(detect_mode("critique this dashboard"), "critique");
        assert_eq!(detect_mode("the swipe gesture feels wrong"), "gesture");
        assert_eq!(detect_mode("slide it in with a spring"), "motion");
        assert_eq!(detect_mode("contrast on the settings page"), "a11y");
    }

    #[test]
    fn every_mode_card_exists() {
        let lib = library();
        for mode in ["build", "motion", "critique", "polish", "system", "a11y", "native"] {
            for id in mode_cards(mode) {
                assert!(lib.get(id).is_some(), "mode {mode} points at missing card {id}");
            }
        }
    }
}
