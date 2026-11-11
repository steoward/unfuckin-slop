//! Ranking. BM25 over title, triggers, id and body, plus phrase boosts.
//! Small enough to score from scratch every run; no index to keep in sync.

use crate::cards::Card;

const STOPWORDS: &[&str] = &[
    "the", "a", "an", "of", "to", "and", "for", "with", "in", "on", "at", "by", "my", "our",
    "this", "that", "it", "is", "are", "be", "make", "build", "page", "screen", "ui", "ux",
    "should", "need", "want", "how", "do", "i", "me", "we", "you", "can", "when", "what",
    "which", "from", "into", "but", "or", "not", "no", "if", "then", "than", "so", "just",
    "really", "very", "using", "use", "get", "got", "add", "new", "some", "look", "looks",
    "make", "made", "app", "site", "design", "designing",
];

pub struct Hit<'a> {
    pub card: &'a Card,
    pub score: f64,
}

/// Lowercase, split on non-alphanumerics, drop noise, strip common suffixes.
/// Both the query and the documents go through the same function, so an
/// imperfect stemmer is still consistent.
pub fn tokenize(text: &str) -> Vec<String> {
    text.split(|c: char| !c.is_alphanumeric())
        .filter(|t| !t.is_empty())
        .map(|t| stem(&t.to_lowercase()))
        .filter(|t| t.len() > 1 && !STOPWORDS.contains(&t.as_str()))
        .collect()
}

fn stem(word: &str) -> String {
    let mut s = word.to_string();
    let suffixes = [
        "ingly", "edly", "ability", "ments", "ment", "able", "ible", "ions", "ion", "ing",
        "ers", "er", "ed", "es", "s",
    ];
    // Strip repeatedly so "animations" reaches the same root as "animation".
    loop {
        let mut changed = false;
        for suffix in suffixes {
            if s.len() > suffix.len() + 2 && s.ends_with(suffix) {
                s.truncate(s.len() - suffix.len());
                changed = true;
                break;
            }
        }
        if !changed {
            break;
        }
    }
    if s.len() > 4 && s.ends_with('e') {
        s.pop();
    }
    // "dragg" and "drag" must agree.
    let bytes = s.as_bytes();
    if bytes.len() > 4 {
        let (last, prev) = (bytes[bytes.len() - 1], bytes[bytes.len() - 2]);
        if last == prev && !b"aeiou".contains(&last) {
            s.pop();
        }
    }
    s
}

pub fn search<'a>(cards: &'a [Card], query: &str) -> Vec<Hit<'a>> {
    let raw_query = query.to_lowercase();
    let mut terms = tokenize(query);
    terms.sort();
    terms.dedup();

    // Title, triggers and id count more than prose; repeat them into the token
    // stream rather than carrying a separate field weight.
    let docs: Vec<(Vec<String>, f64)> = cards
        .iter()
        .map(|card| {
            let mut tokens = Vec::new();
            for _ in 0..3 {
                tokens.extend(tokenize(&card.title));
                for trigger in &card.triggers {
                    tokens.extend(tokenize(trigger));
                }
            }
            for _ in 0..2 {
                tokens.extend(tokenize(&card.id.replace(['.', '-'], " ")));
            }
            tokens.extend(tokenize(&card.body));
            let len = tokens.len() as f64;
            (tokens, len)
        })
        .collect();

    let n = cards.len() as f64;
    let avgdl = if docs.is_empty() {
        1.0
    } else {
        (docs.iter().map(|(_, len)| *len).sum::<f64>() / n).max(1.0)
    };
    let (k1, b) = (1.2_f64, 0.75_f64);

    let mut hits: Vec<Hit<'a>> = cards
        .iter()
        .enumerate()
        .map(|(i, card)| {
            let (tokens, dl) = &docs[i];
            let mut score = 0.0;
            for term in &terms {
                let tf = tokens.iter().filter(|t| *t == term).count() as f64;
                if tf == 0.0 {
                    continue;
                }
                let df = docs
                    .iter()
                    .filter(|(doc, _)| doc.iter().any(|t| t == term))
                    .count() as f64;
                let idf = (1.0 + (n - df + 0.5) / (df + 0.5)).ln();
                score += idf * (tf * (k1 + 1.0)) / (tf + k1 * (1.0 - b + b * dl / avgdl));
            }
            for trigger in &card.triggers {
                if trigger.contains(' ') && raw_query.contains(&trigger.to_lowercase()) {
                    score += 3.0;
                }
            }
            let readable_id = card.id.replace(['.', '-'], " ");
            if raw_query.contains(&readable_id) || raw_query.contains(&card.id) {
                score += 4.0;
            }
            // Weight only breaks ties; it must not outrank a real match.
            score += card.weight as f64 * 0.01;
            Hit { card, score }
        })
        .collect();

    hits.sort_by(|a, b| {
        b.score
            .partial_cmp(&a.score)
            .unwrap_or(std::cmp::Ordering::Equal)
            .then_with(|| b.card.weight.cmp(&a.card.weight))
            .then_with(|| a.card.id.cmp(&b.card.id))
    });
    hits
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn tokenizer_drops_stopwords_and_stems() {
        let tokens = tokenize("Building the draggable sheets");
        assert!(tokens.contains(&"drag".to_string()));
        assert!(tokens.contains(&"sheet".to_string()));
        assert!(!tokens.contains(&"the".to_string()));
    }

    #[test]
    fn stem_is_consistent_between_query_and_doc() {
        assert_eq!(tokenize("springs"), tokenize("spring"));
        assert_eq!(tokenize("gestures"), tokenize("gesture"));
        assert_eq!(tokenize("draggable"), tokenize("drag"));
        assert_eq!(tokenize("animations"), tokenize("animation"));
    }
}
