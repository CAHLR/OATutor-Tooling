var hints = [{id: "a719226sequences4a-h1", type: "hint", dependencies: [], title: "Substitution", text: "Substitute $$n=1$$ into the formula", variabilization: {}}, {id: "a719226sequences4a-h2", type: "hint", dependencies: ["a719226sequences4a-h1"], title: "Simplification", text: "Calculate the expression $$\\frac{\\left(4\\right) \\left(1\\right)}{{\\left(-2\\right)}^1}$$", variabilization: {}}, {id: "a719226sequences4a-h3", type: "scaffold", problemType: "TextBox", answerType: "arithmetic", hintAnswer: ["4"], dependencies: ["a719226sequences4a-h2"], title: "Calculate the numerator", text: "What is $$\\left(4\\right) \\left(1\\right)$$", variabilization: {}}, {id: "a719226sequences4a-h4", type: "scaffold", problemType: "TextBox", answerType: "arithmetic", hintAnswer: ["-2"], dependencies: ["a719226sequences4a-h3"], title: "Calculate the denominator", text: "What is $${\\left(-2\\right)}^1$$", variabilization: {}}, {id: "a719226sequences4a-h5", type: "hint", dependencies: ["a719226sequences4a-h4"], title: "Putting It Together", text: "Put the numerator and denominator together to create a fraction", variabilization: {}}, ]; export {hints};