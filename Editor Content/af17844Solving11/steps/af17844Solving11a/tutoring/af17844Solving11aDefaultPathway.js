var hints = [{id: "af17844Solving11a-h1", type: "hint", dependencies: [], title: "Setup", text: "Assume numbers are x, $$x+2$$, $$x+4$$ (x is an even integer)", variabilization: {}}, {id: "af17844Solving11a-h2", type: "hint", dependencies: ["af17844Solving11a-h1"], title: "Setup", text: "Write an equation based on the condition: $$x+x+2+x+4=102$$", variabilization: {}}, {id: "af17844Solving11a-h3", type: "hint", dependencies: ["af17844Solving11a-h2"], title: "Organizing", text: "Rewrite the equation as $$3x=102-6$$", variabilization: {}}, {id: "af17844Solving11a-s1", type: "scaffold", problemType: "TextBox", answerType: "arithmetic", hintAnswer: ["96"], dependencies: ["af17844Solving11a-h3"], title: "Subtraction", text: "What is 102-6?", variabilization: {}}, {id: "af17844Solving11a-h4", type: "hint", dependencies: ["af17844Solving11a-h3"], title: "Division", text: "Dividing the coefficient on x to get the answer", variabilization: {}}, ]; export {hints};