# JSON Grammar Reference

This document provides a visual guide to the JSON grammar, using tokens that match the `TokenType` enum.

## 1. Key

### Diagram Shapes

| Shape          | Meaning                                                     |
| :------------- | :---------------------------------------------------------- |
| `(( ))`        | Start or End of a grammar production                        |
| `[TOKEN]`      | A token emitted by the lexer (e.g., `STRING`, `NUMBER`)     |
| `["char"]`     | A literal character expected in the input (e.g., `{`, `"`)  |
| `-->`          | The path the scanner takes through the characters           |
| `-- label -->` | A specific condition or branch in the flow                  |

### Token Mnemonics

| Mnemonic   | TokenType                   | Literal Character(s) |
| :--------- | :-------------------------- | :------------------- |
| `LBRACE`   | `TokenType.LBRACE`          | `{`                  |
| `RBRACE`   | `TokenType.RBRACE`          | `}`                  |
| `LBRACKET` | `TokenType.LBRACKET`        | `[`                  |
| `RBRACKET` | `TokenType.RBRACKET`        | `]`                  |
| `COLON`    | `TokenType.COLON`           | `:`                  |
| `COMMA`    | `TokenType.COMMA`           | `,`                  |
| `QUOTE`    | `TokenType.STRING` (Marker) | `"`                  |
| `TRUE`     | `TokenType.TRUE`            | `true`               |
| `FALSE`    | `TokenType.FALSE`           | `false`              |
| `NULL`     | `TokenType.NULL`            | `null`               |

## 2. VALUE

A JSON value can be an object, array, string, number, or one of the three literals.

```mermaid
graph LR
    Start(( )) --> OBJECT
    Start --> ARRAY
    Start --> STRING
    Start --> NUMBER
    Start --> TRUE[true]
    Start --> FALSE[false]
    Start --> NULL[null]
    OBJECT --> End(( ))
    ARRAY --> End
    STRING --> End
    NUMBER --> End
    TRUE --> End
    FALSE --> End
    NULL --> End
```

## 3. OBJECT

An object is an unordered set of name/value pairs.

```mermaid
graph LR
    Start(( )) --> LBRACE["{"]
    LBRACE --> RBRACE["}"] --> End(( ))
    LBRACE --> KEY[STRING] --> COLON[":"] --> VAL[VALUE]
    VAL --> RBRACE
    VAL -- COMMA --> KEY
```

## 4. ARRAY

An array is an ordered collection of values.

```mermaid
graph LR
    Start(( )) --> LBRACKET["["]
    LBRACKET --> RBRACKET["]"] --> End(( ))
    LBRACKET --> VAL[VALUE] --> RBRACKET
    VAL -- COMMA --> VAL
```

## 5. STRING

A string is a sequence of zero or more Unicode characters, wrapped in double quotes.

```mermaid
graph LR
    Start(( )) --> QUOTE1[QUOTE]
    QUOTE1 --> CHAR[CHARACTER]
    CHAR --> QUOTE2[QUOTE]
    QUOTE2 --> End(( ))
    CHAR -- BACKSLASH --> ESC[ESCAPED_CHAR]
    ESC --> CHAR
    CHAR --> CHAR
```

## 6. NUMBER

A number is very much like a C or Java number, except that the octal and hexadecimal formats are not used.

```mermaid
graph LR
    Start(( )) --> MINUS["-"] --> POS
    Start --> POS(( ))

    POS --> ZERO["0"] --> NEXT
    POS --> ONENINE["1-9"] --> DIGITS[DIGITS] --> NEXT
    ONENINE --> NEXT(( ))

    NEXT --> DOT["."] --> FRAC_DIGITS[DIGITS] --> NEXT2
    NEXT --> NEXT2(( ))

    NEXT2 --> EXP["e or E"] --> SIGN["+ or -"] --> EXP_DIGITS[DIGITS] --> End(( ))
    EXP --> EXP_DIGITS
    NEXT2 --> End
```

## 7. WHITESPACE

Whitespace can be inserted between any pair of tokens.

```mermaid
graph LR
    WS(( )) --> SPACE --> WS
    WS --> TAB --> WS
    WS --> LF --> WS
    WS --> CR --> WS
    WS --> End(( ))
```
