from lexer import tokenize
from parser import parse_input
from interpreter import DrumScriptInterpreter

with open('examples/example2.drum') as file:
    script = file.read()

tokens = tokenize(script)

ast = parse_input(script)

interpreter = DrumScriptInterpreter()
interpreter.interpret(ast)