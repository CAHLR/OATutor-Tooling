var hints = [{id: "measure29a-h1", type: "hint", dependencies: [], title: "Conversion Formula", text: "Recall that the formula converting Fahrenheit into Celsius is $$C=\\frac{5}{9} \\left(F-\\left(32\\right)\\right)$$ where C is the temperature in Celsius and F is the temperature in Fahrenheit."}, {id: "measure29a-h2", type: "hint", dependencies: ["measure29a-h1"], title: "Applying the Conversion", text: "To use the formula, all we need to do is substitute 86 for the F, so we get the equation C=(5/9)*(86-32)."}, {id: "measure29a-h3", type: "scaffold", problemType: "TextBox", answerType: "arithmetic", hintAnswer: ["30"], dependencies: ["measure29a-h2"], title: "Evaluating the Expression", text: "What is (5/9)*(86-32)?", subHints: [{id: "measure29a-h3-s1", type: "scaffold", problemType: "TextBox", answerType: "arithmetic", hintAnswer: ["54"], dependencies: [], title: "Evaluating the Expression", text: "To evaluate $$\\frac{5}{9} \\left(\\left(86\\right)-\\left(32\\right)\\right)$$ we evaluate what's inside the parenthesis first. What is 86-32?"}, {id: "measure29a-h3-s2", type: "scaffold", problemType: "TextBox", answerType: "arithmetic", hintAnswer: ["30"], dependencies: ["measure29a-h3-s1"], title: "Evaluating the Expression", text: "Then, we evaluate $$\\frac{5}{9} \\left(54\\right)$$ What is this value?"}]}, ]; export {hints};