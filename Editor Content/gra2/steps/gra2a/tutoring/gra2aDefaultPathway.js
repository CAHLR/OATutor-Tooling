var hints = [{id: "gra2a-h1", type: "hint", dependencies: [], title: "Substitute", text: "We substitute $$x=3$$ and $$y=-3$$ into both inequalities.", variabilization: {}}, {id: "gra2a-h2", type: "hint", dependencies: ["gra2a-h1"], title: "Substitute into First Equation", text: "$$\\left(3\\right) x+y>5$$ \\n $$\\left(3\\right) \\left(3\\right)-\\left(3\\right)>5$$ \\n $$6>5$$", variabilization: {}}, {id: "gra2a-h3", type: "scaffold", problemType: "MultipleChoice", answerType: "string", hintAnswer: ["TRUE"], dependencies: ["gra2a-h2"], title: "Substitute into First Equation", text: "Is the inequality above true?", choices: ["True", "False"], variabilization: {}}, {id: "gra2a-h4", type: "hint", dependencies: ["gra2a-h3"], title: "Substitute into Second Equation", text: "$$\\left(2\\right) x-y \\leq 10$$ \\n $$\\left(2\\right) \\left(3\\right)-\\left(-3\\right) \\leq 10$$ \\n $$9 \\leq 10$$", variabilization: {}}, {id: "gra2a-h5", type: "scaffold", problemType: "MultipleChoice", answerType: "string", hintAnswer: ["TRUE"], dependencies: ["gra2a-h4"], title: "Substitute into Second Equation", text: "Is the inequality above true?", choices: ["True", "False"], variabilization: {}}, {id: "gra2a-h6", type: "hint", dependencies: ["gra2a-h5"], title: "Solutions of a System of Equations", text: "(3,-3) makes both inequalities true. (3,-3) is a solution.", variabilization: {}}, ]; export {hints};