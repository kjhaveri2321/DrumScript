import librosa
import numpy as np
import os
from parser import parse_input
from parser import IfGroove, WhileGroove, RepeatPhrase, RandomPatternCommand
import random

class DrumScriptInterpreter:
    def __init__(self):
        self.variables = {}
        self.output = {}

    def interpret(self, ast):
        for beat in ast.beats:
            self.execute(beat)

    def execute(self, beat, debug=False):
        if isinstance(beat, RandomPatternCommand):
            # Handle the RANDOM_PATTERN command
            drum_part = beat.drumPart
            length = beat.length
            density = beat.density if hasattr(beat, 'density') else 0.5  # Default density is 0.5
            self.generate_random_pattern(drum_part, length, density)  # Ensure pattern is saved
            print(f"{drum_part}: {self.rhythm_to_tab(self.variables[drum_part])}")  # Print the generated pattern
        
        if hasattr(beat, 'file') and beat.__class__.__name__ == 'LoadAudioCommand':
            # Load and process audio file
            self.process_audio_file(beat.file)

        if debug:
            print(f"Debugging Beat Object: {beat}")

        # Calculate the maximum drum part length dynamically
        max_drum_part_length = max((len(drum_part) for drum_part in self.variables.keys()), default=0)

        # Handle Assignments
        if hasattr(beat, 'drumPart') and hasattr(beat, 'rhythm'):
            # Assignment: Assign a rhythm to a drum part
            drum_part = beat.drumPart
            rhythm = self.extract_rhythm_value(beat.rhythm)  # Extract the actual rhythm value
            self.variables[drum_part] = self.rhythm_to_tab(rhythm)
        # Handle SHOW command 
        elif hasattr(beat, 'command') and beat.command == 'SHOW':
            drum_part = beat.drumPart
            if drum_part in self.variables:
                drum_part_aligned = drum_part.ljust(max_drum_part_length)
                print(f"{drum_part_aligned}: {self.variables[drum_part]}")
            else:
                print(f"Error: {drum_part} is not defined.")

        elif hasattr(beat, 'condition') and hasattr(beat, 'body'):
            # Control structures (IF, WHILE, REPEAT)
            if beat.__class__.__name__ == 'IfGroove':
                if self.evaluate(beat.condition):
                    self.interpret(beat.body)
            elif beat.__class__.__name__ == 'WhileGroove':
                while self.evaluate(beat.condition):
                    self.interpret(beat.body)
            elif beat.__class__.__name__ == 'RepeatPhrase':
                for _ in range(self.evaluate(beat.times)):
                    self.interpret(beat.body)

        elif hasattr(beat, 'file'):
            # Input/Output Commands (LOAD_TRACK, GENERATE_TABS)
            if beat.__class__.__name__ == 'InputCommand':
                file_path = beat.file.strip('"') # Remove quotes from file path
                if os.path.exists(file_path):
                    with open(file_path, 'r') as file:
                        input_text = file.read()
                        print(f"Loading track from {file_path}...")
                        self.parse_and_run(input_text)
                else:
                    print(f"ERROR: File {file_path} does not exist.")
            elif beat.__class__.__name__ == 'GenerateTabs':
                print(f"Generating tabs to {beat.file}")

        elif hasattr(beat, 'drumPart'):
            # Show the current drum part with its tab pattern
            drum_part = beat.drumPart
            rhythm = self.variables.get(drum_part, 'Undefined')
            drum_part_aligned = drum_part.ljust(max_drum_part_length)
            print(f"{drum_part_aligned}: {self.rhythm_to_tab(rhythm)}")

        elif hasattr(beat, 'message'):
            # Error handling
            print(f"ERROR: {beat.message}")

        elif hasattr(beat, 'variable') and hasattr(beat, 'value'):
           # Handle general variable assignments like counter = 3
            variable_name = beat.variable
            value = self.evaluate(beat.value)  # Evaluate the value (e.g., 3)
            self.variables[variable_name] = value
            print(f"Assigned {value} to {variable_name}") 

    def extract_rhythm_value(self, rhythm_expression, debug=False):
        """Extract the actual rhythm value from the AST object."""
        if debug:
            print(f"Debugging RhythmExpression: {rhythm_expression}")
        if hasattr(rhythm_expression, 'value'):
            return rhythm_expression.value
        elif isinstance(rhythm_expression, str):
            return rhythm_expression
        else:
            raise ValueError(f"Unexpected rhythm expression: {rhythm_expression}")

    def parse_and_run(self, input_text):
        ast = parse_input(input_text)
        self.interpret(ast)

    def evaluate(self, expr):
        if hasattr(expr, 'op') and hasattr(expr, 'left') and hasattr(expr, 'right') and expr.op:
            left = self.evaluate(expr.left)
            right = self.evaluate(expr.right)
            print(f"Evaluating: {left} {expr.op} {right}")
            return self.apply_operator(expr.op, left, right)
        elif hasattr(expr, 'value'):
            return expr.value
        elif isinstance(expr, str):
            # Return the variable value if defined, otherwise the string itself
            return self.variables.get(expr, expr)
        elif hasattr(expr, 'drumPart') or hasattr(expr, 'duration'):
            return expr  # For simple Note or Duration
        elif hasattr(expr, 'condition') and hasattr(expr, 'body'):
            # Handle control structures like if, else, while, repeat
            if hasattr(expr, 'elseBody'):
                # If-Else
                if self.evaluate(expr.condition):  # Ensure condition is evaluated correctly
                    self.interpret(expr.body)  # Execute 'if' body
                else:
                    self.interpret(expr.elseBody)  # Execute 'else' body
            elif isinstance(expr, IfGroove):
                if self.evaluate(expr.condition):  # Ensure condition is evaluated correctly
                    self.interpret(expr.body)  # Execute 'if' body
            elif isinstance(expr, WhileGroove):
                while self.evaluate(expr.condition):
                    self.interpret(expr.body)
            elif isinstance(expr, RepeatPhrase):
                for _ in range(self.evaluate(expr.times)):
                    self.interpret(expr.body)
            else:
                raise ValueError(f"Unknown control structure: {expr.__class__.__name__}")
        return expr

    def apply_operator(self, op, left, right):
        if op == '==':
            return left == right
        elif op == 'AND':
            return left and right
        elif op == 'OR':
            return left or right
        elif op == '!=':
            return left != right
        elif op == '>':
            return left > right
        elif op == '<':
            return left < right
        elif op == '>=':
            return left >= right
        elif op == '<=':
            return left <= right
        elif op == '+':
            return left + right
        elif op == '-':
            return left - right
        elif op == '*':
            return left * right
        elif op == '/':
            return left / right
        elif op == '%':
            return left % right
        else:
            raise ValueError(f"Unknown operator: {op}")

    def rhythm_to_tab(self, rhythm):
        """Convert a rhythm expression to a tab pattern."""
        
        # If rhythm is 'default', return a placeholder pattern (e.g., silence)
        if rhythm == 'default':
            return '[--------]'
        
        # Handle predefined rhythms
        if rhythm == 'quarter':
            return '[x---x---]'
        elif rhythm == 'eighth':
            return '[x-x-x-x-]'
        elif rhythm == 'sixteenth':
            return '[xxxxxxxx]'
        elif rhythm == 'whole':
            return '[x-------]'
        
        # Ensure the rhythm is a string and not a list or other type
        if isinstance(rhythm, str):
            # Pad the rhythm to 16 characters if it's shorter
            rhythm = rhythm.ljust(16, '-')  # Fill with dashes if it's less than 16 characters
            return f"[{rhythm}]"
        
        # If none of the conditions match, raise an error
        raise ValueError(f"Invalid rhythm pattern: {rhythm}")

    def drum_parts_order(self):
        """Return the drum parts in the fixed order."""
        return ['cymbal', 'hihat', 'tom', 'snare', 'floor_tom', 'kick']
    
    def rhythm_to_dynamic_tab(self, drum_part, rhythm):
        """Convert rhythm to dynamic tab with X for cymbal and hi-hat, o for others."""
        tab = self.rhythm_to_tab(rhythm)

        if drum_part in ['cymbal', 'hihat']:
            return self.rhythm_to_tab(rhythm).replace('x', 'X')
        else:
            return self.rhythm_to_tab(rhythm).replace('x', 'o')
        
    def process_audio_file(self, file_path):
        try:
            # Load the audio file using Librosa
            y, sr = librosa.load(file_path, sr=None)

            # Apply onset detection to identify drum hits
            onset_env = librosa.onset.onset_strength(y=y, sr=sr)
            onset_times = librosa.onset.onset_detect(onset_envelope=onset_env, sr=sr, units='time')

            # Assume drum parts order as ['kick', 'snare', 'hihat']
            # Classify drum sounds (kick, snare, etc.)
            drum_parts = ['kick', 'snare', 'hihat', 'tom', 'floor_tom', 'cymbal']
            detected_tabs = {part: [] for part in drum_parts}

            # Example classification (will need a more robust classifier)
            for t in onset_times:
                # Simulate a drum classification based on time or frequency (use a model or heuristic)
                detected_tabs['kick'].append(t) # Simulate kick detection
            
            for drum_part, timings in detected_tabs.items():
                drum_tab = self.generate_tab_from_timings(timings)
                self.variables[drum_part] = drum_tab
                print(f"{drum_part}: {drum_tab}")

        except Exception as e:
            print(f"Error processing audio file: {e}")

    def generate_tab_from_timings(self, timings):
        # Create a simple tab pattern based on timings
        rhythm_length = 16 #Assume 16 beats per measure 
        tab = ['-'] * rhythm_length
        for t in timings:
            position = int(t * rhythm_length) % rhythm_length # Map time to tab position
            tab[position] = 'x' # Mark the hit in the tab pattern 
        return ''.join(tab)
    
    def generate_random_pattern(self, drum_part, length, density):
        """Generate a random drum pattern based on density and length."""
        pattern = []
        for i in range(length):
            rand_value = random.random()  # Get random number between 0 and 1
            if rand_value < density:
                pattern.append('x')  # Hit
            elif rand_value < 2 * density:
                pattern.append('o')  # Pause
            else:
                pattern.append('-')  # Rest
        pattern_str = ''.join(pattern)
        self.variables[drum_part] = f"[{pattern_str}]" # Store the pattern in the dictionary

    def test_random_pattern(self):
        self.generate_random_pattern('kick', 16, 0.7)
        # Test with snare drum (16 beats, density 0.4)
        self.generate_random_pattern('snare', 16, 0.4)
        # Test with hihat (8 beats, density 0.6)
        self.generate_random_pattern('hihat', 16, 0.6)
        
    

        # When printing, it should show:
        print(f"kick: {self.rhythm_to_tab(self.variables['kick'])}")
        print(f"snare: {self.rhythm_to_tab(self.variables['snare'])}")
        print(f"hihat: {self.rhythm_to_tab(self.variables['hihat'])}")


interpreter = DrumScriptInterpreter()
interpreter.test_random_pattern()

