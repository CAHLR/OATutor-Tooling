var hints = [{id: "ser24a-h1", type: "hint", dependencies: [], title: "Explicit Formula", text: "The given formula, $$-\\left({\\left(\\frac{\\left(-1\\right)}{2}\\right)}^{k-\\left(1\\right)}\\right)$$, is exponential with a base of $$\\frac{-\\left(1\\right)}{2}$$.", variabilization: {}}, {id: "ser24a-h2", type: "hint", dependencies: ["ser24a-h1"], title: "Identify r", text: "The series is geometric with a common ratio of $$\\frac{-\\left(1\\right)}{2}$$.", variabilization: {}}, {id: "ser24a-h3", type: "scaffold", problemType: "MultipleChoice", answerType: "string", hintAnswer: ["T"], dependencies: ["ser24a-h2"], title: "Confirm that $$-\\left(1\\right)<r<1$$", text: "Is $$-\\left(1\\right)<\\frac{-\\left(1\\right)}{2}<1$$ True or False?", choices: ["T", "F"], variabilization: {}}, {id: "ser24a-h4", type: "hint", dependencies: ["ser24a-h3"], title: "Sum of Infinite Geometric Series", text: "Since $$-\\left(1\\right)<\\frac{-\\left(1\\right)}{2}<1$$ is F; then sum is defined.", variabilization: {}}, {id: "ser24a-h5", type: "hint", dependencies: ["ser24a-h4"], title: "Identify $$a_1$$ and r", text: "From the given formula, we are given that $$a_1=-1$$ and $$r=\\frac{-\\left(1\\right)}{2}$$", variabilization: {}}, {id: "ser24a-h6", type: "hint", dependencies: ["ser24a-h5"], title: "Formula for the Sum of an Infinite Geometric Series", text: "Substitute values for $$a_1$$ and r into the formula: $$S=\\frac{a_1}{\\left(1\\right)-r}$$.", variabilization: {}}, {id: "ser24a-h7", type: "hint", dependencies: ["ser24a-h6"], title: "Formula for the Sum of an Infinite Geometric Series", text: "The formula of the sum is $$S=\\frac{-\\left(1\\right)}{\\left(1\\right)-\\frac{\\left(-1\\right)}{2}}$$", variabilization: {}}, ]; export {hints};