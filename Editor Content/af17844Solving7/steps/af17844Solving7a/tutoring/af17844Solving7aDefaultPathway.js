var hints = [{id: "af17844Solving7a-h1", type: "hint", dependencies: [], title: "Setup", text: "Assume one number is x and another is x-7, based on the second condition", variabilization: {}}, {id: "af17844Solving7a-h2", type: "hint", dependencies: ["af17844Solving7a-h1"], title: "Setup", text: "Write an equation based on the first condition: $$x+x-7=-23$$", variabilization: {}}, {id: "af17844Solving7a-h3", type: "hint", dependencies: ["af17844Solving7a-h2"], title: "Organizing", text: "Rewrite the equation as $$2x=-23-(-7)$$", variabilization: {}}, {id: "af17844Solving7a-s1", type: "scaffold", problemType: "TextBox", answerType: "arithmetic", hintAnswer: ["-16"], dependencies: ["af17844Solving7a-h3"], title: "Subtraction", text: "What is -23-(-7)?", variabilization: {}}, {id: "af17844Solving7a-h4", type: "hint", dependencies: ["af17844Solving7a-h3"], title: "Division", text: "Dividing the coefficient on x to get the answer", variabilization: {}}, ]; export {hints};