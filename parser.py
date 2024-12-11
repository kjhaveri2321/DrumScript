class IfGroove:
    def __init__(self, condition, body, elseBody=None):
        self.condition = condition
        self.body = body
        self.elseBody = elseBody

class WhileGroove:
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

class RepeatPhrase:
    def __init__(self, times, body):
        self.times = times
        self.body = body

class RandomPatternCommand:
    def __init__(self, drumPart, length, density=0.5):
        self.drumPart = drumPart
        self.length = length
        self.density = density

class LoadAudioCommand:
    def __init__(self, file):
        self.file = file

class Assignment:
    def __init__(self, drumPart, rhythm):
        self.drumPart = drumPart
        self.rhythm = rhythm

class ShowCommand:
    def __init__(self, drumPart):
        self.drumPart = drumPart


from textx import metamodel_from_str

# DrumScript grammar (in TextX syntax)
GRAMMAR = """
Model:
    beats*=Beat
;

Beat:
    Assignment | DrumControl | InputCommand | GenerateTabs | ShowCommand | ErrorCommand | RandomPatternCommand
;

Assignment:
    drumPart=ID '=' rhythm=STRING
;

RhythmExpression:
    value=STRING | NUMBER 
;

NUMBER:
    /\d+/ | /\d+\.\d+/
;

Note:
    DRUM_PART | DURATION | TAB_PATTERN | INT | FLOAT | STRING | '(' RhythmExpression ')'
;

DrumControl:
    IfGroove | WhileGroove | RepeatPhrase
;

IfGroove:
    'IF_Groove' condition=Condition 'PLAY' body=Model ('ELSE' elseBody=Model)? 'ENDIF_Groove'
;

WhileGroove:
    'WHILE_Groove' condition=Condition 'PLAY' body=Model 'ENDWHILE_Groove'
;

RepeatPhrase:
    'REPEAT_Groove' times=INT 'TIMES' 'PLAY' body=Model 'ENDREPEAT_Groove'
;

Condition:
    left=RhythmExpression|ID comparator=COMPARATOR right=RhythmExpression|ID
;

InputCommand:
    'LOAD_TRACK' file=STRING
;

GenerateTabs:
    'GENERATE_TABS' '(' file=STRING ')'
;

ShowCommand:
    'SHOW' drumPart=ID
;

ErrorCommand:
    'ERROR' message=STRING
;

RandomPatternCommand:
    'RANDOM_PATTERN' drumPart=DRUM_PART length=INT ( density=FLOAT )?
;

AudioCommand:
    'PROCESS_AUDIO' file=STRING
;

LoadAudioCommand:
    'LOAD_AUDIO' file=STRING
;

Comment:
    /#.*$/ 
;

OPERATOR: '+' | '-' | '*' | '/' | '%';
COMPARATOR: '==' | '!=' | '<' | '>' | '<=' | '>=' | 'AND' | 'OR';

// Token definitions
STRING: /"[^"]*"/ | /'[^']*'/;
DRUM_PART: 'kick' | 'snare' | 'hihat' | 'tom' | 'cymbal' | 'floor_tom';
DURATION: 'quarter' | 'eighth' | 'sixteenth' | 'whole';
TAB_PATTERN: '\\[([x\\-|o]+)\\]'; 
INT: /\d+/;
FLOAT: /\d+\.\d+/;
ID: /[a-zA-Z_][a-zA-Z_0-9]*/;
"""

# Create and return a parser
def create_parser():
    return metamodel_from_str(GRAMMAR)

def parse_input(input_text):
    parser = create_parser()
    return parser.model_from_str(input_text)