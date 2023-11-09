import requests
import os
from PIL import Image, UnidentifiedImageError

from create_dir import *
from create_content import *


def image_timeout(signum, frame):
    raise Exception("Image retrieval timeout")

# Register timeout for image retrieval
# signal.signal(signal.SIGALRM, image_timeout)
# signal.alarm(10)

def validate_image(image, checksum, old_path):
    images = image.split()
    name = ".figure.gif"
    for i in images:
        # if checksum is there, can avoid re-downloading
        if type(checksum) != float and checksum and old_path:
            stored_md5 = checksum
            figures_dir = old_path + "/figures"
            if os.path.isdir(figures_dir):
                if any([create_image_md5(figures_dir + "/" + figure_name) == stored_md5 for figure_name in os.listdir(figures_dir)]):
                    continue
        try:
            i = re.sub(r"https://imgur\.com/([\d\w]+)", r"https://i.imgur.com/\g<1>.png", i)
            r = requests.get(i, headers={ "user-agent": "OATutor/1.0.0" })
        except:
            raise Exception("Image retrieval error")
        with open(name, 'wb') as outfile:
            outfile.write(r.content)
        # check if image is valid
        try:
            Image.open(name)
        except UnidentifiedImageError:
            os.remove(name)
            raise Exception("Downloaded image cannot be opened")
        os.remove(name)


def validate_step(row, variabilization, latex, verbosity, old_path):
    # check images and create figure path if necessary
    if type(row["Images (space delimited)"]) == str:
        validate_image(row["Images (space delimited)"], row["Image Checksum"], old_path)
    choices = type(row["mcChoices"]) == str and row["mcChoices"]
    if variabilization:
        create_step(row['Problem Name'], row['Title'], row["Body Text"], row["Answer"], row["answerType"],
                    1, choices, "", var_str=row["Variabilization"], latex=latex,
                    verbosity=verbosity)
    else:
        create_step(row['Problem Name'], row['Title'], row["Body Text"], row["Answer"], row["answerType"],
                    1, choices, "", latex=latex, verbosity=verbosity)


def validate_hint_with_parent(row, scaff_lst, row_type, hint_dic, previous_tutor, variabilization, latex, verbosity, old_path):
    current_step_name = ""

    if row['Parent'] not in scaff_lst:
        raise Exception("{} is hint so should not have subhint(s)".format(row["Parent"]))

    hint_images = ""
    if type(row["Images (space delimited)"]) == str and type(
            row["Images (space delimited)"]) != np.float64:
        validate_image(row["Images (space delimited)"], row["Image Checksum"], old_path)
    try:
        hint_id = row['Parent'] + "-" + row['HintID']
    except TypeError:
        raise Exception("Hint ID is missing")
    if row_type == 'hint':
        if variabilization:
            subhint, subhint_id = create_hint(current_step_name, hint_id, row["Title"],
                                                row["Body Text"], "", "", row["Dependency"], hint_images,
                                                hint_dic=hint_dic, var_str=row["Variabilization"],
                                                latex=latex, verbosity=verbosity)
        else:
            subhint, subhint_id = create_hint(current_step_name, hint_id, row["Title"],
                                                row["Body Text"], "", "", row["Dependency"], hint_images,
                                                hint_dic=hint_dic, latex=latex, verbosity=verbosity)
    else:
        scaff_lst.append(hint_id)
        if variabilization:
            subhint, subhint_id = create_scaffold(current_step_name, hint_id, row["Title"],
                                                    row["Body Text"], row["answerType"], row["Answer"],
                                                    row["mcChoices"], "", "", row["Dependency"], hint_images,
                                                    hint_dic=hint_dic,
                                                    var_str=row["Variabilization"], latex=latex,
                                                    verbosity=verbosity)
        else:
            subhint, subhint_id = create_scaffold(current_step_name, hint_id, row["Title"],
                                                    row["Body Text"], row["answerType"], row["Answer"],
                                                    row["mcChoices"], "", "", row["Dependency"], hint_images,
                                                    hint_dic=hint_dic, latex=latex, verbosity=verbosity)
    hint_dic[row["HintID"]] = subhint_id
    if previous_tutor['Row Type'] == 'hint':
        if variabilization:
            previous, hint_id = create_hint(current_step_name, previous_tutor["HintID"],
                                            previous_tutor["Title"], previous_tutor["Body Text"], "", "", 
                                            previous_tutor["Dependency"], "",
                                            subhints=[], hint_dic=hint_dic,
                                            var_str=previous_tutor["Variabilization"],
                                            latex=latex, verbosity=verbosity)
        else:
            previous, hint_id = create_hint(current_step_name, previous_tutor["HintID"],
                                            previous_tutor["Title"], previous_tutor["Body Text"], "", "", 
                                            previous_tutor["Dependency"], "",
                                            subhints=[], hint_dic=hint_dic, latex=latex,
                                            verbosity=verbosity)
    else:
        if variabilization:
            previous, hint_id = create_scaffold(current_step_name, previous_tutor["HintID"],
                                                previous_tutor["Title"], previous_tutor["Body Text"],
                                                previous_tutor["answerType"], previous_tutor["Answer"],
                                                previous_tutor["mcChoices"], "", "", 
                                                previous_tutor["Dependency"], "",
                                                subhints=[], hint_dic=hint_dic,
                                                var_str=previous_tutor["Variabilization"],
                                                latex=latex, verbosity=verbosity)
        else:
            previous, hint_id = create_scaffold(current_step_name, previous_tutor["HintID"],
                                                previous_tutor["Title"], previous_tutor["Body Text"],
                                                previous_tutor["answerType"], previous_tutor["Answer"],
                                                previous_tutor["mcChoices"], "", "", 
                                                previous_tutor["Dependency"], "",
                                                subhints=[], hint_dic=hint_dic,
                                                latex=latex, verbosity=verbosity)

    return scaff_lst, hint_dic


def validate_hint_without_parent(row, scaff_lst, row_type, hint_dic, variabilization, latex, verbosity, old_path):
    current_step_name = ""
    if row_type == "hint":
        hint_images = ""
        if type(row["Images (space delimited)"]) == str:
            validate_image(row["Images (space delimited)"], row["Image Checksum"], old_path)
        if variabilization:
            hint, full_id = create_hint(current_step_name, row["HintID"], row["Title"],
                                        row["Body Text"], "", "", row["Dependency"], hint_images,
                                        hint_dic=hint_dic, var_str=row["Variabilization"],
                                        latex=latex, verbosity=verbosity)
        else:
            hint, full_id = create_hint(current_step_name, row["HintID"], row["Title"],
                                        row["Body Text"], "", "", row["Dependency"], hint_images,
                                        hint_dic=hint_dic, latex=latex, verbosity=verbosity)
        hint_dic[row["HintID"]] = full_id
    if row_type == "scaffold":
        scaff_lst.append(row["HintID"])
        scaff_images = ""
        if type(row["Images (space delimited)"]) == str:
            validate_image(row["Images (space delimited)"], row["Image Checksum"], old_path)
        if variabilization:
            scaff, full_id = create_scaffold(current_step_name, row["HintID"], row["Title"],
                                                row["Body Text"], row["answerType"], row["Answer"],
                                                row["mcChoices"], "", "", row["Dependency"], scaff_images,
                                                hint_dic=hint_dic, var_str=row["Variabilization"],
                                                latex=latex, verbosity=verbosity)
        else:
            scaff, full_id = create_scaffold(current_step_name, row["HintID"], row["Title"],
                                                row["Body Text"], row["answerType"], row["Answer"],
                                                row["mcChoices"], "", "", row["Dependency"], scaff_images,
                                                hint_dic=hint_dic, latex=latex, verbosity=verbosity)
        hint_dic[row["HintID"]] = full_id

    return row, hint_dic
