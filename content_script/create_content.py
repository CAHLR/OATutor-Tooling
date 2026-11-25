import json
import re
import numpy as np
from PIL import Image
import hashlib

from process_text import preprocess_text_to_latex


def create_image_md5(image_path):
    md5hash = hashlib.md5(Image.open(image_path).tobytes())
    return md5hash.hexdigest()


def create_variabilization(variabilization):
    if variabilization:
        var_list = variabilization.split("\n")

        def var_str_pair_to_tuple (var_str_pair):
            [var_name, var_value_str] = var_str_pair.split(":")
            var_values = var_value_str.split("|")
            return var_name, var_values
        var_dict = dict(map(var_str_pair_to_tuple, var_list))
    else:
        var_dict = {}
    return var_dict


def create_problem_json(name,title,body,oer,license,images=[],var_str='',latex=True,verbosity=False,course_name="",sheet_name="",lesson_id="",figure_alts=None):
    if type(body) == float or type(body) == np.float64:
        body= ""
    for image in images:
        body += "\\n##{0}##".format(image)
    if type(title) == float or type(title) == np.float64:
        title = ""
    if type(oer) == float or type(oer) == np.float64:
        oer = ""
    if type(license) == float or type(license) == np.float64:
        license = ""

    title, title_latex = preprocess_text_to_latex(title, render_latex=latex, verbosity=verbosity)
    body, body_latex = preprocess_text_to_latex(body, render_latex=latex, verbosity=verbosity)

    # TODO: fix "create_variabilization"
    variabilization = create_variabilization(var_str)

    problem_dict = {
        "id": name,
        "title": title,
        "body": body,
        "variabilization": variabilization,
        "oer": oer,
        "license": license,
        "lesson": sheet_name,
        "lessonId": lesson_id,
        "courseName": course_name
    }
    if figure_alts:
        problem_dict["figureAlts"] = figure_alts
    
    return json.dumps(problem_dict, indent=4)


def create_hint(step, hint_id, title, body, oer, license, dependencies="", images=[], subhints=[], hint_dic={}, var_str='',latex=True,verbosity=False,figure_alts=None):
    if type(body) == float or type(body) == np.float64:
        body = ""
    if type(title) == float or type(title) == np.float64:
        title = ""
    
    title, title_latex = preprocess_text_to_latex(title, True, render_latex=latex, verbosity=verbosity)
    body, body_latex = preprocess_text_to_latex(body, True, render_latex=latex, verbosity=verbosity)

    variabilization = create_variabilization(var_str)
    
    try:
        hint_id = step + "-" + hint_id
    except TypeError:
        raise Exception("Hint ID is missing")
    for image in images:
        body += "\\n##{0}##".format(image)
    if type(dependencies) == str and dependencies != 'None' and dependencies != '':
        try:
            dependencies = [hint_dic[hint_id] for hint_id in dependencies.split(",")]
        except Exception as e:
            raise Exception("Hint key error (might be cause by errors in the rows above)")
    else:
        dependencies = []

    hint_dict = {
        "id": hint_id,
        "type": "hint",
        "dependencies": dependencies,
        "title": title,
        "text": body,
        "variabilization": variabilization,
        "oer": oer, 
        "license": license
    }
    if figure_alts:
        hint_dict["figureAlts"] = figure_alts

    if len(subhints) > 0:
        hint_dict.update({
            "subHints": subhints
        })

    return hint_dict, hint_id


scaff_dic = {"mc": "string", "numeric": "TextBox", "algebra": "TextBox", "string": "string", "sa": "sa"}


def handle_answer_type(answer_type):
    if answer_type == "mc":
        return "string", "MultipleChoice"
    elif answer_type == "string":
        return answer_type, "TextBox"
    elif answer_type == "algebra" or answer_type == "algebraic" or answer_type == "numeric":
        return "arithmetic", "TextBox"
    elif answer_type == "sa":
        return "sa", "sa"
    elif type(answer_type) != str:
        raise Exception("Answer type is missing")
    else:
        raise Exception('Answer type not correct: ' + answer_type)


def create_multi_answer(answer, latex=True, verbosity=False):
    """Parse a multi-answer step stored as JSON in the existing Answer cell."""
    try:
        config = json.loads(answer)
    except (TypeError, ValueError) as error:
        raise ValueError("Multi-answer Answer must be valid JSON") from error

    if not isinstance(config, dict) or config.get("layout") not in ("combined", "sideBySide"):
        raise ValueError("Multi-answer layout must be combined or sideBySide")
    layout = config["layout"]
    raw_parts = config.get("parts")
    if not isinstance(raw_parts, list) or len(raw_parts) < 2:
        raise ValueError("Multi-answer requires at least two parts")
    if layout == "combined" and len(raw_parts) != 2:
        raise ValueError("Combined layout requires exactly two parts")

    parts = []
    for index, raw in enumerate(raw_parts):
        if not isinstance(raw, dict) or not isinstance(raw.get("label"), str) or not raw["label"].strip():
            raise ValueError("Multi-answer part {} needs a label".format(index + 1))
        if raw.get("answerType") not in ("numeric", "algebra", "algebraic", "string", "unit"):
            raise ValueError("Multi-answer part {} has an unsupported answerType".format(index + 1))
        answers = raw.get("answers", raw.get("answer"))
        answers = answers if isinstance(answers, list) else [answers]
        if not answers or any(value is None or not str(value).strip() for value in answers):
            raise ValueError("Multi-answer part {} needs an answer".format(index + 1))
        answer_type = raw["answerType"]
        if answer_type != "unit":
            answer_type, _ = handle_answer_type(answer_type)
        formatted = [preprocess_text_to_latex(str(value), render_latex=latex,
                     verbosity=verbosity)[0] if answer_type == "arithmetic" else str(value)
                     for value in answers]
        part = {"label": raw["label"].strip(), "answerType": answer_type,
                "answers": formatted}
        if "precision" in raw:
            raise ValueError("Multi-answer precision is not supported by the arithmetic checker")
        parts.append(part)

    if layout == "combined" and (
            raw_parts[0]["answerType"] != "numeric" or
            raw_parts[1]["answerType"] not in ("unit", "string")):
        raise ValueError("Combined layout requires a numeric part followed by a unit or string part")

    return {"layout": layout, "parts": parts}


def create_scaffold(step, hint_id, title, body, answer_type, answer, mc_answers, oer, license, dependencies=0.0, images="", subhints=[], hint_dic={}, var_str="",latex=True,verbosity=False,figure_alts=None):
    if type(body) == float or type(body) == np.float64:
        body = ""
    if type(title) == float or type(title) == np.float64:
        title = ""
    
    title, title_latex = preprocess_text_to_latex(title, True, render_latex=latex, verbosity=verbosity)
    body, body_latex = preprocess_text_to_latex(body, True, render_latex=latex, verbosity=verbosity)

    variabilization = create_variabilization(var_str)

    # getting rid of timestamp format for fractions
    try:
        if answer_type != "sa" and len(answer) > 8 and answer[-8:] == '00:00:00':
            li = re.split('-| ', answer)
            answer = str(int(li[1])) + '/' + str(int(li[2]))
    except TypeError:
        raise Exception("Scaffold answer missing")
    
    try:
        scaffold_id = step + "-" + hint_id
    except TypeError:
        raise Exception("Scaffold ID is missing")
    for image in images:
        body += "\\n##{0}##".format(image)

    if type(dependencies) == str and dependencies != 'None' and dependencies != '':
        try:
            dependencies = [hint_dic[hint_id] for hint_id in dependencies.split(",")]
        except Exception as e:
            raise Exception("Hint key error (might be cause by errors in the rows above)")
    else:
        dependencies = []

    if answer_type == "mc" and (type(mc_answers) == float or type(mc_answers) == np.float64):
        raise Exception("Scaffold mc question contains no options")
    
    answer_type, problem_type = handle_answer_type(answer_type)
    if answer_type == "arithmetic":
        if "," in answer and not "/mat" in answer:
            raise Exception("Scaffold arithmetic answer contains comma")
        answer = preprocess_text_to_latex(answer, render_latex=latex, verbosity=verbosity)[0]
    scaff_ans = [answer]
    
    if type(mc_answers) != float and type(mc_answers) != np.float64:
        choice_list = [choice for choice in mc_answers.split('|') if choice]
        if answer not in choice_list:
            choice_list.append(answer)
            choice_list.sort()

        mc_answers = [preprocess_text_to_latex(mc_answer, True, True, render_latex=latex, verbosity=verbosity)[0] for mc_answer in choice_list]
        answer = preprocess_text_to_latex(answer, True, True, render_latex=latex, verbosity=verbosity)[0]
        scaff_ans = [answer]

    scaff_dict = {
        "id": scaffold_id,
        "type": "scaffold",
        "problemType": problem_type,
        "answerType": answer_type,
        "hintAnswer": scaff_ans,
        "dependencies": dependencies,
        "title": title,
        "text": body,
        "variabilization": variabilization, 
        "oer": oer, 
        "license": license
    }
    if figure_alts:
        scaff_dict["figureAlts"] = figure_alts

    if type(mc_answers) is list:
        scaff_dict.update({
            "choices": mc_answers
        })
    if len(subhints) > 0:
        scaff_dict.update({
            "subHints": subhints
        })

    return scaff_dict, scaffold_id


def create_step(name, title, body, answer, answer_type, number, choices="", image="", var_str="",latex=True, verbosity=False, figure_alts=None):
    step_id = name + chr(ord('a')+number-1)
    if type(body) == float or type(body) == np.float64:
        body = ""
    if type(title) == float or type(title) == np.float64:
        title = ""
    
    title, title_latex = preprocess_text_to_latex(title, render_latex=latex, verbosity=verbosity)
    body, body_latex = preprocess_text_to_latex(body, render_latex=latex, verbosity=verbosity)

    variabilization = create_variabilization(var_str)

    if answer_type == "multi":
        multi_answer = create_multi_answer(answer, latex=latex, verbosity=verbosity)
        for img in image:
            body += "##" + img + "## "
        step_dict = {
            "id": step_id,
            "stepAnswer": [" ".join(part["answers"][0] for part in multi_answer["parts"])],
            "problemType": "MultiAnswer",
            "stepTitle": title,
            "stepBody": body,
            "answerType": "multi",
            "multiAnswer": multi_answer,
            "variabilization": variabilization,
        }
        if figure_alts:
            step_dict["figureAlts"] = figure_alts
        return json.dumps(step_dict, indent=4)

    # getting rid of timestamp format for fractions
    try:
        if answer_type != "sa" and len(answer) > 8 and answer[-8:] == '00:00:00':
            li = re.split('-| ', answer)
            answer = str(int(li[1])) + '/' + str(int(li[2]))
    except TypeError:
        raise Exception("Step answer missing")

    if answer_type == "mc" and not choices:
        raise Exception("Step mc question contains no options")

    answer_latex = False

    new_answer, answer_latex = preprocess_text_to_latex(answer, render_latex=latex, verbosity=verbosity)

    for img in image:
        body += "##" + img + "## "
    if choices and type(choices) != float:
        choice_list = [choice for choice in choices.split('|') if choice]
        if answer not in choice_list:
            choice_list.append(answer)
            choice_list.sort()

        choices = [preprocess_text_to_latex(mc_answer, True, True, render_latex=latex, verbosity=verbosity)[0] for mc_answer in choice_list]
        answer = preprocess_text_to_latex(answer, True, True, render_latex=latex, verbosity=verbosity)[0]
    
    answer_type, problem_type = handle_answer_type(answer_type)
    if answer_type == "arithmetic":
        if "," in new_answer:
            raise Exception("Step arithmetic answer contains comma")
        answer = new_answer

    step_dict = {
        "id": step_id,
        "stepAnswer": [answer],
        "problemType": problem_type,
        "stepTitle": title,
        "stepBody": body,
        "answerType": answer_type,
        "variabilization": variabilization
    }

    if figure_alts:
        step_dict["figureAlts"] = figure_alts

    if answer_latex:
        step_dict.update({
            "answerLatex": new_answer
        })

    if type(choices) is list:
        step_dict.update({
            "choices": choices
        })

    return json.dumps(step_dict, indent=4)
