import re
import sys
from tkinter import WORD
sys.path.insert(0, "../textToLatex")
from pytexit import py2tex
import io

sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding='utf-8')

supported_operators = ["**", "/", "*", "+", ">", "<", "=", "_", "~"]
supported_word_operators = ["sqrt", "abs(", "inf", "log{", "ln{", 'log(', 'sum{', '\\theta', '/mat', '/tab', '/lim', '/int']
answer_only_operators = ["-"]
skip_braces_operators = ["ln{", "log{", "/mat", "sum{", "_{", "/tab", "/lim", "/int"]
trig_operators = ["sin", "cos", "tan", "csc", "sec", "cot"]
replace = {
    "⋅": "*",
    "−": "-",
    "^": "**",
    "𝑥": "x",
    "𝑎": "a",
    "𝑏": "b",
    "𝑦": "y",
    "–": "-",
    "≥": ">=",
    "≤": "<=",
    "∪": "U",
    "\\cap": "∩",
    "π": "pi",
    "µ": "\\mu",
    "α": "\\alpha",
    "≠": "!="
}
conditionally_replace = {"[": "(", "]": ")"}
regex = re.compile("|".join(map(re.escape, replace.keys())))
force_latex = 0.0
match = {'(': ')', '{': '}', '[': ']', '\\left(': '\\right)'}

# Figure out way to deal with equal signs
def preprocess_text_to_latex(text, tutoring=False, stepMC=False, render_latex="TRUE", verbosity=False):
    global force_latex
    render_latex = render_latex == "TRUE"

    if render_latex:
        text = str(text)
        text = regex.sub(lambda m: replace[m.group(0)], text)
        if not re.findall(r"[\[|\(][-\d\s\w/]+,[-\d\s\w/]+[\)|\]]", text):
            text = regex.sub(lambda m: conditionally_replace[m.group(0)], text)

        # Account for space in sqrt(x, y)
        text = re.sub(r"sqrt\s*\(([^,]+),\s*([^\)]+)\)", r"sqrt(\g<1>,\g<2>)", text)
        text = re.sub(r"sqrt(?:\s*)?\(", r"sqrt(", text)
        text = re.sub(r"abs(?:\s*)?\(", r"abs(", text)
        text = re.sub(r"\([\s]*([-\d]+)[\s]*,[\s]*([-\d]+)[\s]*\)", r"(\g<1>,\g<2>)", text)
        text = re.sub(r"\s\\\"\s", " ", text)
        text = re.sub(r"\\\\pipe", "|", text)
        text = re.sub(r"\\/", r"\\\\slash\\\\", text)
        text = re.sub(r"@{(\d+|\w+)}", r"aaa\g<1>ttt", text)
        text = re.sub(r"_\{([\w]+),([\w]+)\}", r"_\g<1>_\g<2>", text)
        text = re.sub(r"_\(([^)]+)\)", r"_\g<1>", text)
        text = re.sub(r"_{2,}", r"___", text)

    # Handle newline
    text = re.sub(r"\n", " |newline| ", text)

    words = text.split()
    latex = False
    for i in range(len(words)):
        word = words[i]
        word = re.sub(r"(\d)(?<![a-zA-Z])pi", r"\g<1>*pi", word)
        if use_latex(word, render_latex, stepMC):
            if not re.findall(r"[\[|\(][\+\-\*/\(\)\d\s\w]+,[\+\-\*/\(\)\d\s\w]+[\)|\]]", word):
                word = re.sub(r",(\S)", r", \g<1>", word)

            strip_punc = word[-1] in "?.,:"
            quote = False
            open_braces = closing_braces = False
            if (word[:2] == r'\\"' and word[-2:] == r'\\"') or (word[0] == r"\'" and word[-1] == r"\'"):
                word = word[2:-2]
                quote = True
            punctuation = word[-1] if strip_punc else ""
            if strip_punc:
                word = word[:-1]
            if word[:1] == "{":
                open_braces = True
                word = word[1:]
            if word[-1:] == "}" and all([op not in word for op in skip_braces_operators]):
                closing_braces = True
                word = word[:-1]
            if word[:2] == "$$" and word[-2:] == "$$":
                word = word[2:-2]
            elif word[:2] == "$$":
                word = word[2:]
            elif word[-2:] == "$$":
                word = word[:-2]

            try:
                sides = re.split(r"((?<!\\)`|=|U|∩|<=|>=|!=|_{3})", word)
                sides = [handle_word(side) for side in sides]
                new_word = ""
                if tutoring and stepMC:
                    new_word = "$$" + "".join(sides) + "$$"
                else:
                    if quote:
                        new_word = "$$\\\"" + "".join([side.replace("\\", "\\") for side in sides]) + "\\\"" + "$$"
                    else:
                        new_word = "$$" + "".join([side.replace("\\", "\\") for side in sides]) + "$$"
                    new_word = re.sub(r"\\\\\"\$\$", r"\"$$", new_word)
                    new_word = re.sub(r"\$\$\\\\\"", r"$$\"", new_word)
                if strip_punc:
                    new_word += punctuation
                if open_braces:
                    new_word = "{" + new_word
                if closing_braces:
                    new_word = new_word + "}"
                new_word = re.sub(r"\\operatorname{or}", r"|", new_word)
                latex = True
                words[i] = new_word
            except Exception as e:
                if verbosity:
                    print("This failed:", word)
                    print(e)
                pass

        if word[:2] == '##' and word[-2:] == '##':
            words[i] = word[2:-2]
        elif word[:2] == '##':
            words[i] = word[2:]
        elif word[-2:] == '##':
            words[i] = word[:-2]

    text = " ".join(words)
    text = re.sub(r"\\\\slash\\\\", "/", text)
    text = re.sub(r"aaa(\w+|\d+)ttt", r"@{\g<1>}", text)
    text = re.sub(r"\s*\|newline\|\s*", r"\\n", text)
    force_latex = 0.0
    return text, latex
