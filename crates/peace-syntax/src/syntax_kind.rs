//! Token and node kinds for the Peace concrete syntax tree.

macro_rules! syntax_kinds {
    ($($name:ident),* $(,)?) => {
        /// Every token and node kind. Tokens come first, then nodes.
        #[allow(non_camel_case_types, clippy::upper_case_acronyms)]
        #[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
        #[repr(u16)]
        pub enum SyntaxKind { $($name),* }

        impl SyntaxKind {
            const ALL: &'static [SyntaxKind] = &[$(SyntaxKind::$name),*];

            pub(crate) fn from_raw(raw: u16) -> SyntaxKind {
                Self::ALL[usize::from(raw)]
            }
        }
    };
}

syntax_kinds! {
    // ---- trivia ----
    WHITESPACE, COMMENT, LINE_BREAK,
    // ---- layout (NEWLINE is a significant line end; INDENT/DEDENT are zero-width) ----
    NEWLINE, INDENT, DEDENT, EOF,
    // ---- literals and names ----
    IDENT, NUMBER, STRING, FSTRING, SUPERSCRIPT, ERROR_TOKEN,
    // ---- punctuation ----
    L_PAREN, R_PAREN, L_BRACK, R_BRACK, L_BRACE, R_BRACE,
    COMMA, COLON, SEMICOLON, DOT, DOT2, DOT2EQ, DOT3, AT, ARROW, TILDE,
    EQ, EQ2, NEQ, LT, LTEQ, GT, GTEQ,
    PLUS, MINUS, STAR, STAR2, SLASH, SLASH2, BACKSLASH, PERCENT, CARET, PIPE, PIPE_GT, PLUS_MINUS,
    DOT_PLUS, DOT_MINUS, DOT_STAR, DOT_SLASH, DOT_BACKSLASH, DOT_CARET,
    PLUS_EQ, MINUS_EQ, STAR_EQ, SLASH_EQ, SLASH2_EQ, PERCENT_EQ, CARET_EQ,
    // not Peace operators: lexed only so the parser can give a hint (`&&`, `||`, `!`)
    AMP2, PIPE2, BANG,
    // ---- hard keywords (RFC 0001): never names ----
    AND_KW, AS_KW, ASSERT_KW, ATTEMPT_KW, ALWAYS_KW, BREAK_KW, CONTINUE_KW, DEF_KW, ELIF_KW,
    ELSE_KW, FALSE_KW, FOR_KW, FROM_KW, IF_KW, IMPORT_KW, IN_KW, IS_KW, LEARN_KW, NONE_KW,
    NOT_KW, OR_KW, PASS_KW, RAISE_KW, REMEMBER_KW, RETURN_KW, TRUE_KW, WHILE_KW,
    // ---- soft keywords: lexed as IDENT, re-tagged by the parser where they act as keywords ----
    GENE_KW, FITNESS_KW, MODULE_KW, SCHEMA_KW, WITH_KW,
    // ---- nodes: file and statements ----
    SOURCE_FILE, ERROR, BLOCK,
    FN_DEF, GENE_DEF, PARAM_LIST, PARAM, RET_TYPE, DECORATOR,
    MODULE_DEF, SCHEMA_DEF, FIELD_DECL, FITNESS_DEF, FITNESS_CLAUSE, SCORE_CLAUSE, INVARIANT_CLAUSE,
    IF_STMT, ELIF_CLAUSE, ELSE_CLAUSE, FOR_STMT, WHILE_STMT,
    ATTEMPT_STMT, LEARN_CLAUSE, ALWAYS_CLAUSE, WITH_STMT, WITH_ITEM,
    RETURN_STMT, RAISE_STMT, ASSERT_STMT, REMEMBER_STMT, IMPORT_STMT, IMPORT_ITEM, PASS_STMT, BREAK_STMT, CONTINUE_STMT,
    EXPR_STMT, ASSIGN_STMT, AUG_ASSIGN_STMT, TARGET_LIST,
    // ---- nodes: types ----
    TYPE_REF, TYPE_ARGS, UNION_TYPE,
    // ---- nodes: expressions ----
    LAMBDA, CONDITIONAL_EXPR, BIN_EXPR, PREFIX_EXPR, STARRED_EXPR, CALL_EXPR, BCAST_CALL_EXPR, INDEX_EXPR, FIELD_EXPR,
    ARG_LIST, ARG, NAMED_ARG, SLICE_LIST, SLICE,
    NAME_REF, LITERAL, STRING_MACRO, SYMBOL, PAREN_EXPR, TUPLE_EXPR, LIST_EXPR, DICT_EXPR,
    SET_EXPR, DICT_ENTRY, LIST_COMP, SET_COMP, DICT_COMP, GENERATOR_EXPR, COMP_FOR, COMP_IF,
    EVOLVABLE, UNIT_EXPR, UNIT_SUFFIX,
}

impl SyntaxKind {
    /// Whitespace, comments, and non-significant line breaks.
    pub fn is_trivia(self) -> bool {
        matches!(
            self,
            SyntaxKind::WHITESPACE | SyntaxKind::COMMENT | SyntaxKind::LINE_BREAK
        )
    }

    /// Hard keywords and soft keywords the parser has re-tagged.
    pub fn is_keyword(self) -> bool {
        (SyntaxKind::AND_KW..=SyntaxKind::WITH_KW).contains(&self)
    }

    /// Hard keywords only: the words that can never be names (RFC 0001 "Keywords").
    pub fn is_hard_keyword(self) -> bool {
        (SyntaxKind::AND_KW..=SyntaxKind::WHILE_KW).contains(&self)
    }

    /// The hard keyword spelled `word`. Soft keywords return `None`: they lex as IDENT.
    pub(crate) fn from_keyword(word: &str) -> Option<SyntaxKind> {
        use SyntaxKind::*;
        Some(match word {
            "and" => AND_KW,
            "as" => AS_KW,
            "assert" => ASSERT_KW,
            "attempt" => ATTEMPT_KW,
            "always" => ALWAYS_KW,
            "break" => BREAK_KW,
            "continue" => CONTINUE_KW,
            "def" => DEF_KW,
            "elif" => ELIF_KW,
            "else" => ELSE_KW,
            "false" => FALSE_KW,
            "for" => FOR_KW,
            "from" => FROM_KW,
            "if" => IF_KW,
            "import" => IMPORT_KW,
            "in" => IN_KW,
            "is" => IS_KW,
            "learn" => LEARN_KW,
            "none" => NONE_KW,
            "not" => NOT_KW,
            "or" => OR_KW,
            "pass" => PASS_KW,
            "raise" => RAISE_KW,
            "remember" => REMEMBER_KW,
            "return" => RETURN_KW,
            "true" => TRUE_KW,
            "while" => WHILE_KW,
            _ => return None,
        })
    }
}

impl From<SyntaxKind> for rowan::SyntaxKind {
    fn from(kind: SyntaxKind) -> Self {
        rowan::SyntaxKind(kind as u16)
    }
}

/// The rowan language tag for Peace trees.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum PeaceLanguage {}

impl rowan::Language for PeaceLanguage {
    type Kind = SyntaxKind;

    fn kind_from_raw(raw: rowan::SyntaxKind) -> SyntaxKind {
        SyntaxKind::from_raw(raw.0)
    }

    fn kind_to_raw(kind: SyntaxKind) -> rowan::SyntaxKind {
        kind.into()
    }
}
