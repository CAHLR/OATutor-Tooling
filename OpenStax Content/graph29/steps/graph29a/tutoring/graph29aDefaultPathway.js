var hints = [{id: "graph29a-h1", type: "hint", dependencies: [], title: "Factoring Expressions", text: "Factor out $$x^3$$ out of the expression.", variabilization: {}}, {id: "graph29a-h2", type: "scaffold", problemType: "TextBox", answerType: "arithmetic", hintAnswer: ["x^3(4x^2 - 12x+ 9)"], dependencies: ["graph29a-h1"], title: "Simplifying Expressions", text: "What is the simplified expression?", variabilization: {}}, {id: "graph29a-h3", type: "scaffold", problemType: "TextBox", answerType: "arithmetic", hintAnswer: ["(2x-3)^2"], dependencies: ["graph29a-h2"], title: "Factoring Expressions", text: "What is the factorization of $$\\left(4\\right) x^2$$ - 12x + 9?", variabilization: {}}, {id: "graph29a-h4", type: "scaffold", problemType: "TextBox", answerType: "arithmetic", hintAnswer: ["0, 3/2"], dependencies: ["graph29a-h3"], title: "Finding Zeroes", text: "What are the values of x that make the expression 0?", variabilization: {}}, {id: "graph29a-h5", type: "hint", dependencies: ["graph29a-h4"], title: "Definition of Multiplicity", text: "The multiplicity is the power to which each part of the expression is raised", variabilization: {}}, ]; export {hints};