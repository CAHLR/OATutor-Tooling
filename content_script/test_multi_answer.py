import json
import sys
import types
import unittest

# Keep this schema test independent of the optional LaTeX converter.
sys.modules["process_text"] = types.SimpleNamespace(
    preprocess_text_to_latex=lambda value, *args, **kwargs: (value, False)
)
from create_content import create_step


class MultiAnswerContentTests(unittest.TestCase):
    def step(self, layout, first_type="numeric", second_type="string", **config):
        answer = json.dumps({
            **config,
            "layout": layout,
            "parts": [
                {"label": "Value", "answerType": first_type, "answer": "12"},
                {"label": "Unit", "answerType": second_type,
                 "answers": ["cm", "centimeters"]},
            ],
        })
        return json.loads(create_step("test", "Value and unit", "Enter both parts",
                                      answer, "multi", 1))

    def test_both_layouts_produce_two_typed_parts(self):
        for layout in ("combined", "sideBySide"):
            with self.subTest(layout=layout):
                step = self.step(layout)
                self.assertEqual(step["problemType"], "MultiAnswer")
                self.assertEqual(step["multiAnswer"]["layout"], layout)
                self.assertEqual([part["answerType"] for part in
                                  step["multiAnswer"]["parts"]], ["arithmetic", "string"])
                self.assertEqual(step["multiAnswer"]["parts"][1]["answers"],
                                 ["cm", "centimeters"])

    def test_legacy_partial_credit_setting_does_not_change_generated_content(self):
        self.assertEqual(self.step("sideBySide", creditMode="perPart"),
                         self.step("sideBySide"))

    def test_unit_type_survives_generation_in_both_layouts(self):
        for layout in ("combined", "sideBySide"):
            with self.subTest(layout=layout):
                step = self.step(layout, second_type="unit")
                self.assertEqual(step["multiAnswer"]["parts"][1], {
                    "label": "Unit", "answerType": "unit",
                    "answers": ["cm", "centimeters"],
                })

    def test_combined_layout_rejects_an_unparseable_type_pair(self):
        with self.assertRaisesRegex(ValueError, "numeric part followed by a unit or string"):
            self.step("combined", first_type="algebra")

    def test_three_parts_generate_one_step_only_with_separate_fields(self):
        parts = [
            {"label": "Value", "answerType": "numeric", "answer": "12"},
            {"label": "Unit", "answerType": "unit", "answer": "cm"},
            {"label": "Direction", "answerType": "string", "answer": "east"},
        ]
        answer = json.dumps({"layout": "sideBySide", "parts": parts})
        step = json.loads(create_step("test", "Displacement", "Enter all parts",
                                      answer, "multi", 1))
        self.assertEqual(step["problemType"], "MultiAnswer")
        self.assertEqual([part["answers"] for part in step["multiAnswer"]["parts"]],
                         [["12"], ["cm"], ["east"]])

        answer = json.dumps({"layout": "combined", "parts": parts})
        with self.assertRaisesRegex(ValueError, "Combined layout requires exactly two parts"):
            create_step("test", "Displacement", "Enter all parts", answer, "multi", 1)

    def test_malformed_multi_answer_is_rejected_before_content_is_written(self):
        with self.assertRaisesRegex(ValueError, "valid JSON"):
            create_step("test", "Question", "Body", "12|cm", "multi", 1)
        with self.assertRaisesRegex(ValueError, "at least two parts"):
            create_step("test", "Question", "Body",
                        json.dumps({"layout": "sideBySide", "parts": []}), "multi", 1)

    def test_unsupported_precision_is_rejected(self):
        answer = json.dumps({"layout": "sideBySide", "parts": [
            {"label": "Value", "answerType": "numeric", "answer": "12", "precision": 2},
            {"label": "Unit", "answerType": "string", "answer": "cm"},
        ]})
        with self.assertRaisesRegex(ValueError, "precision is not supported"):
            create_step("test", "Question", "Body", answer, "multi", 1)

    def test_existing_single_answer_format_is_unchanged(self):
        step = json.loads(create_step("test", "Old question", "Answer it",
                                      "12", "numeric", 1))
        self.assertEqual(step["problemType"], "TextBox")
        self.assertNotIn("multiAnswer", step)

if __name__ == "__main__":
    unittest.main()
