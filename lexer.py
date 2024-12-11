import re

# Define regex patterns for tokens
TOKENS = {
    "STRING": r"'[^']*'|\"[^\"]*\"",
    "ID": r"[a-zA-Z_][a-zA-Z_0-9]*",
    "INT": r"\d+",
    "FLOAT": r"\d+\.\d+",  # Handle floating-point numbers
    "SEMICOLON": r";",
    "DRUM_PART": r"(kick|snare|hihat|tom|cymbal|floor_tom)",
    "DURATION": r"(quarter|eighth|sixteenth|whole)",
    "TAB_PATTERN": r"\[[x\-o]{1,16}\]",  # Matches patterns up to 16 characters
    "COMMAND": r"(SHOW|LOAD_TRACK|GENERATE_TABS|ERROR|RANDOM_PATTERN)",
    "CONTROL": r"(IF_Groove|PLAY|ENDIF_Groove|WHILE_Groove|ENDWHILE_Groove|REPEAT_Groove|TIMES|ENDREPEAT_Groove)",
    "OPERATOR": r"[+\-*/%]",
    "COMPARATOR": r"(==|!=|<=|>=|<|>|AND|OR)",
    "ASSIGN": r"=",
    "PUNCTUATION": r"[()]",
    "NUMBER": r"\d+(\.\d+)?",  # This should cover both integer and floating-point numbers
    "WHITESPACE": r"[ \t]+",
    "NEWLINE": r"\n",
    "COMMENT": r"#.*",
    "DOT": r"\.",  # Explicitly match the period as a separate token
    "INVALID": r"[^\w\s\[\]()]",  # Catch all invalid characters excluding specific ones
}

# Combine regex patterns into a single regex
MASTER_PATTERN = re.compile(
    "|".join(f"(?P<{name}>{pattern})" for name, pattern in TOKENS.items())
)

# Tokenizer function with preprocessing for period (.)
def tokenize(input_text):
    # Step 1: Preprocess input to separate the period (.)
    input_text = input_text.replace(".", " . ")

    tokens = []
    for match in MASTER_PATTERN.finditer(input_text):
        kind = match.lastgroup
        value = match.group(kind)
        
        if kind == "WHITESPACE" or kind == "COMMENT":
            continue  # Ignores whitespace and comments
        elif kind == "INVALID":
            raise ValueError(f"Unexpected token: {value}")
        tokens.append((kind, value))
    
    return tokens