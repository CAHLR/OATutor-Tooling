var hints = [{id: "a719226sequences4d-h1", type: "hint", dependencies: [], title: "Substitution", text: "Substitute $$n=4$$ into the formula", variabilization: {}}, {id: "a719226sequences4d-h2", type: "hint", dependencies: ["a719226sequences4d-h1"], title: "Simplification", text: "Calculate the expression $$\\frac{\\left(4\\right) \\left(4\\right)}{{\\left(-2\\right)}^4}$$", variabilization: {}}, {id: "a719226sequences4d-h3", type: "scaffold", problemType: "TextBox", answerType: "arithmetic", hintAnswer: ["16"], dependencies: ["a719226sequences4d-h2"], title: "Calculate the numerator", text: "What is $$\\left(4\\right) \\left(4\\right)$$", variabilization: {}}, {id: "a719226sequences4d-h4", type: "scaffold", problemType: "TextBox", answerType: "arithmetic", hintAnswer: ["16"], dependencies: ["a719226sequences4d-h3"], title: "Calculate the denominator", text: "What is $${\\left(-2\\right)}^4$$", variabilization: {}}, {id: "a719226sequences4d-h5", type: "hint", dependencies: ["a719226sequences4d-h4"], title: "Putting It Together", text: "Put the numerator and denominator together to create a fraction", variabilization: {}}, ]; export {hints};