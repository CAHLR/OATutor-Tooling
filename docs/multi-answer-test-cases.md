# Multi-answer test cases (provisional)

These cases cover a numeric answer and a string answer submitted together in either of two layouts. The same answer data and grading rules should drive both layouts.

The first fixture is a deliberately simple value-and-unit question: expected number `12`, expected unit `cm`. A second fixture uses the real Disc6 Part E pair: Blank 1 is `10000` (`algebra` in the sheet) and Blank 2 is `make_array()` (`string`). The real pair is suitable for the two-field layout; it is not suitable for the combined field until a delimiter or parsing rule is specified for arbitrary expressions.

One Submit checks both parts; both must be correct to complete the step. The first graded attempt sends one overall result to mastery. A correct field remains editable on retry. The combined parser accepts `12 cm` and `12cm`; unit aliases are accepted only when authored explicitly in `answers`.

## Shared behavior

| Case | Student answer(s) | Expected component result | Expected overall result |
| --- | --- | --- | --- |
| Both correct | `12` and `cm` | Number correct; unit correct | Correct; complete the question |
| Number only correct | `12` and `mm` | Number correct; unit incorrect | Incomplete; show which part needs correction |
| Unit only correct | `13` and `cm` | Number incorrect; unit correct | Incomplete; show which part needs correction |
| Both incorrect | `13` and `mm` | Both incorrect | Incomplete |
| Missing number | Empty number, `cm` | Number missing; unit present | Do not silently grade the missing number as zero |
| Missing unit | `12`, empty unit | Number present; unit missing | Do not mark complete |
| Retry | Correct a previously wrong part | Preserve the first attempt's result for mastery and log the new attempt | Complete only when both parts are correct |

For every submission, verify that the saved attempt contains both entered values and both correctness results. Verify that mastery records one first-attempt observation per applicable knowledge component, and that it records an incorrect result if either part is wrong. Existing single-answer questions must continue to render, submit, and score as before.

## One combined field

| Case | Input | Expected behavior |
| --- | --- | --- |
| Standard entry | `12 cm` | Parse number `12` and unit `cm`; both correct |
| Number correct, unit wrong | `12 mm` | Report number correct and unit wrong |
| Number wrong, unit correct | `13 cm` | Report number wrong and unit correct |
| Empty field | Empty | Do not submit or score |
| No parseable number | `cm` | Show a format error; do not turn it into numeric zero |
| No unit | `12` | Show that the unit is missing |
| Whitespace variant | ` 12 cm ` | Trim surrounding whitespace; parse both parts |
| No space | `12cm` | Parse both parts |
| Decimal or negative value | `12.5 cm`, `-12 cm` | Parse as a signed number and unit; compare using the configured numeric rule |
| Unit alias | `12 centimeters` | Follow the sheet's explicitly accepted unit aliases |

Do not infer conversions such as `0.12 m = 12 cm` unless the content format explicitly supports them.

## Two fields side by side

| Case | Inputs | Expected behavior |
| --- | --- | --- |
| Standard entry | Number `12`, unit `cm` | One Submit checks both; both correct |
| Mixed correctness | Number `12`, unit `mm` | Show feedback for each field |
| One field empty | Number `12`, unit empty | Keep Submit disabled; never mark complete |
| Retry | Change only the wrong field | Both fields remain editable; do not create duplicate first-attempt mastery updates |
| Keyboard use | Tab between both fields and Submit; press Enter | Focus order and submission work without a mouse |
| Narrow screen | View at mobile width | Inputs remain labeled and usable, stacking if needed |
| Real mixed-type fixture | Disc6 Part E: `10000` and `make_array()` | Each part uses its own existing answer type and checker |

## Decisions to confirm with the project lead

1. Does a correct field lock after a mixed result, or may the student edit both on retry?
2. Which abbreviations should be accepted as alternatives to the expected unit?
3. Is the combined field limited to a number plus unit, or must it also support arbitrary numeric/algebra and string pairs?
