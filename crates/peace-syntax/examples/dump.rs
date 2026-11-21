//! Print the syntax tree and errors for a Peace file.
//!
//! cargo run -p peace-syntax --example dump -- path/to/file.peace

fn main() {
    let path = std::env::args().nth(1).expect("usage: dump <file.peace>");
    let src = std::fs::read_to_string(&path).unwrap_or_else(|e| panic!("{path}: {e}"));
    let parse = peace_syntax::parse(&src);
    println!("{}", parse.debug_tree());
    if !parse.errors().is_empty() {
        eprintln!("{}", parse.render_errors(&src));
        std::process::exit(1);
    }
}
