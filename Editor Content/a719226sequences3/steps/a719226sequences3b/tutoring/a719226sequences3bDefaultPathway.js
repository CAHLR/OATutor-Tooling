var hints = [{id: "a719226sequences3b-h1", type: "hint", dependencies: [], title: "Substitution", text: "Substitute $$n=2$$ into the formula", variabilization: {}}, {id: "a719226sequences3b-h2", type: "hint", dependencies: ["a719226sequences3b-h1"], title: "Simplification", text: "Calculate the expression $$\\frac{{\\left(-1\\right)}^2 {\\left(2\\right)}^2}{\\left(2\\right)+\\left(1\\right)}$$", variabilization: {}}, {id: "a719226sequences3b-h3", type: "scaffold", problemType: "TextBox", answerType: "arithmetic", hintAnswer: ["4"], dependencies: ["a719226sequences3b-h2"], title: "Calculate the numerator", text: "What is $${\\left(-1\\right)}^2 {\\left(2\\right)}^2$$", variabilization: {}}, {id: "a719226sequences3b-h4", type: "scaffold", problemType: "TextBox", answerType: "arithmetic", hintAnswer: ["3"], dependencies: ["a719226sequences3b-h3"], title: "Calculate the denominator", text: "What is $$\\left(2\\right)+\\left(1\\right)$$", variabilization: {}}, {id: "a719226sequences3b-h5", type: "hint", dependencies: ["a719226sequences3b-h4"], title: "Putting It Together", text: "Put the numerator and denominator together to create a fraction", variabilization: {}}, ]; export {hints};