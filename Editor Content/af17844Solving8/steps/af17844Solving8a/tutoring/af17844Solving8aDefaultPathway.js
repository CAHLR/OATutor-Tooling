var hints = [{id: "af17844Solving8a-h1", type: "hint", dependencies: [], title: "Setup", text: "Assume one number is x and another is $$x+40$$, based on the second condition", variabilization: {}}, {id: "af17844Solving8a-h2", type: "hint", dependencies: ["af17844Solving8a-h1"], title: "Setup", text: "Write an equation based on the first condition: $$x+x+40=-18$$", variabilization: {}}, {id: "af17844Solving8a-h3", type: "hint", dependencies: ["af17844Solving8a-h2"], title: "Organizing", text: "Rewrite the equation as $$2x=-18-40$$", variabilization: {}}, {id: "af17844Solving8a-s1", type: "scaffold", problemType: "TextBox", answerType: "arithmetic", hintAnswer: ["-58"], dependencies: ["af17844Solving8a-h3"], title: "Subtraction", text: "What is -18-40?", variabilization: {}}, {id: "af17844Solving8a-h4", type: "hint", dependencies: ["af17844Solving8a-h3"], title: "Division", text: "Dividing the coefficient on x to get the answer", variabilization: {}}, ]; export {hints};