//! RFC 0001 test plan: conformance corpus, error corpus, round-trip, and doc samples.

use std::{
    collections::BTreeMap,
    fs,
    path::{Path, PathBuf},
};

use peace_syntax::{SyntaxKind, parse};

fn repo_root() -> PathBuf {
    Path::new(env!("CARGO_MANIFEST_DIR"))
        .join("../..")
        .canonicalize()
        .expect("repo root")
}

fn peace_files(dir: &Path) -> Vec<PathBuf> {
    let mut files: Vec<_> = fs::read_dir(dir)
        .unwrap_or_else(|e| panic!("{}: {e}", dir.display()))
        .map(|e| e.unwrap().path())
        .filter(|p| p.extension().is_some_and(|x| x == "peace"))
        .collect();
    files.sort();
    assert!(!files.is_empty(), "no .peace files in {}", dir.display());
    files
}

#[test]
fn ok_corpus_parses_cleanly_and_round_trips() {
    for path in peace_files(&repo_root().join("tests/syntax/ok")) {
        let src = fs::read_to_string(&path).unwrap();
        let parse = parse(&src);
        assert!(
            parse.errors().is_empty(),
            "{}: unexpected errors:\n{}",
            path.display(),
            parse.render_errors(&src)
        );
        assert_eq!(
            parse.syntax().to_string(),
            src,
            "{}: round-trip",
            path.display()
        );
    }
}

/// Each file in `err/` lists the diagnostics it must produce, exactly, as trailing
/// `# expect: line:col: message` comments (RFC 0001 "Diagnostics"). Expectations sit
/// at the end of the file so they don't shift the positions they describe.
#[test]
fn err_corpus_reports_expected_diagnostics_and_still_round_trips() {
    let mut problems = Vec::new();
    for path in peace_files(&repo_root().join("tests/syntax/err")) {
        let src = fs::read_to_string(&path).unwrap();
        let parse = parse(&src);
        let name = path.file_name().unwrap().to_string_lossy();
        if parse.syntax().to_string() != src {
            problems.push(format!("{name}: round-trip mismatch"));
        }
        let mut expected: Vec<&str> = src
            .lines()
            .filter_map(|l| l.strip_prefix("# expect: "))
            .collect();
        let rendered = parse.render_errors(&src);
        let mut actual: Vec<&str> = rendered.lines().collect();
        if expected.is_empty() {
            problems.push(format!("{name}: add `# expect: line:col: message` lines"));
        }
        expected.sort_unstable();
        actual.sort_unstable();
        if expected != actual {
            problems.push(format!(
                "{name}:\n  expected:\n    {}\n  actual:\n    {}",
                expected.join("\n    "),
                actual.join("\n    ")
            ));
        }
    }
    assert!(problems.is_empty(), "\n{}", problems.join("\n\n"));
}

#[test]
fn recovery_keeps_parsing_after_an_unspecified_construct() {
    let src = fs::read_to_string(repo_root().join("tests/syntax/err/unspecified_construct.peace"))
        .unwrap();
    let parse = parse(&src);
    let stmts: Vec<_> = parse.syntax().children().map(|n| n.kind()).collect();
    assert_eq!(
        stmts,
        [SyntaxKind::ERROR, SyntaxKind::ASSIGN_STMT],
        "tree:\n{}",
        parse.debug_tree()
    );
}

/// Every ```peace block in README.md, docs/ and rfcs/. Blocks listed in
/// tests/syntax/docs-allowlist.txt use constructs no RFC specifies yet: they must
/// still round-trip, and must still fail (so the allowlist never goes stale).
#[test]
fn doc_samples_parse() {
    let root = repo_root();
    let allow = load_allowlist(&root.join("tests/syntax/docs-allowlist.txt"));
    let mut md_files = vec![root.join("README.md")];
    for dir in ["docs", "rfcs"] {
        let mut more: Vec<_> = fs::read_dir(root.join(dir))
            .unwrap()
            .map(|e| e.unwrap().path())
            .filter(|p| p.extension().is_some_and(|x| x == "md"))
            .collect();
        more.sort();
        md_files.extend(more);
    }

    let (mut clean, mut problems, mut seen) = (0, Vec::new(), Vec::new());
    for md in &md_files {
        let rel = md
            .strip_prefix(&root)
            .unwrap()
            .to_string_lossy()
            .replace('\\', "/");
        for (n, block) in peace_blocks(&fs::read_to_string(md).unwrap())
            .into_iter()
            .enumerate()
        {
            let id = format!("{rel}#{}", n + 1);
            let parse = parse(&block);
            if parse.syntax().to_string() != block {
                problems.push(format!("{id}: round-trip mismatch"));
            }
            match (parse.errors().is_empty(), allow.contains_key(&id)) {
                (true, false) => clean += 1,
                (false, false) => problems.push(format!(
                    "{id}: errors (fix the sample, the parser, or allowlist it with a reason):\n{}",
                    parse.render_errors(&block)
                )),
                (true, true) => problems.push(format!(
                    "{id}: parses now, remove it from docs-allowlist.txt"
                )),
                (false, true) => {}
            }
            seen.push(id);
        }
    }
    for id in allow.keys().filter(|id| !seen.contains(id)) {
        problems.push(format!("{id}: in docs-allowlist.txt but no such block"));
    }
    eprintln!(
        "doc samples: {clean} parse cleanly, {} allowlisted, {} total",
        allow.len(),
        seen.len()
    );
    assert!(problems.is_empty(), "\n{}", problems.join("\n\n"));
}

fn load_allowlist(path: &Path) -> BTreeMap<String, String> {
    fs::read_to_string(path)
        .unwrap_or_default()
        .lines()
        .map(str::trim)
        .filter(|l| !l.is_empty() && !l.starts_with('#'))
        .map(|l| {
            let (id, reason) = l.split_once(char::is_whitespace).unwrap_or((l, ""));
            assert!(
                !reason.trim().is_empty(),
                "allowlist entry {id} needs a reason"
            );
            (id.to_string(), reason.trim().to_string())
        })
        .collect()
}

/// Extracts ```peace fenced blocks, removing the fence's own indentation.
fn peace_blocks(md: &str) -> Vec<String> {
    let mut blocks = Vec::new();
    let mut current: Option<(usize, String)> = None;
    for line in md.lines() {
        let trimmed = line.trim_start();
        let indent = line.len() - trimmed.len();
        match &mut current {
            None if trimmed == "```peace" => current = Some((indent, String::new())),
            Some(_) if trimmed == "```" => blocks.push(current.take().unwrap().1),
            Some((fence_indent, text)) => {
                text.push_str(
                    line.get(*fence_indent..)
                        .unwrap_or("")
                        .trim_end_matches('\r'),
                );
                text.push('\n');
            }
            None => {}
        }
    }
    blocks
}

/// Error tolerance: every prefix of every corpus file parses without panicking
/// and round-trips. Truncation produces unclosed strings, brackets, and blocks.
#[test]
fn every_prefix_parses_and_round_trips() {
    let root = repo_root();
    let mut checked = 0;
    for dir in ["tests/syntax/ok", "tests/syntax/err"] {
        for path in peace_files(&root.join(dir)) {
            let src = fs::read_to_string(&path).unwrap();
            for (cut, _) in src.char_indices() {
                let prefix = &src[..cut];
                assert_eq!(
                    parse(prefix).syntax().to_string(),
                    prefix,
                    "{} cut at {cut}",
                    path.display()
                );
                checked += 1;
            }
        }
    }
    eprintln!("prefixes checked: {checked}");
}
