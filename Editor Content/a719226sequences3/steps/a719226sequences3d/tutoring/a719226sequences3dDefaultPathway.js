var hints = [{id: "a719226sequences3d-h1", type: "hint", dependencies: [], title: "Substitution", text: "Substitute $$n=4$$ into the formula", variabilization: {}}, {id: "a719226sequences3d-h2", type: "hint", dependencies: ["a719226sequences3d-h1"], title: "Simplification", text: "Calculate the expression $$\\frac{{\\left(-1\\right)}^4 {\\left(4\\right)}^2}{\\left(4\\right)+\\left(1\\right)}$$", variabilization: {}}, {id: "a719226sequences3d-h3", type: "scaffold", problemType: "TextBox", answerType: "arithmetic", hintAnswer: ["16"], dependencies: ["a719226sequences3d-h2"], title: "Calculate the numerator", text: "What is $${\\left(-1\\right)}^4 {\\left(4\\right)}^2$$", variabilization: {}}, {id: "a719226sequences3d-h4", type: "scaffold", problemType: "TextBox", answerType: "arithmetic", hintAnswer: ["5"], dependencies: ["a719226sequences3d-h3"], title: "Calculate the denominator", text: "What is $$\\left(4\\right)+\\left(1\\right)$$", variabilization: {}}, {id: "a719226sequences3d-h5", type: "hint", dependencies: ["a719226sequences3d-h4"], title: "Putting It Together", text: "Put the numerator and denominator together to create a fraction", variabilization: {}}, ]; export {hints};