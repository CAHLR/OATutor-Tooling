var hints = [{id: "VarCon1a-h1", type: "hint", dependencies: [], title: "Subtraction property of equality", text: "When you subtract the same quantity from both sides of an equation, you still have equality."}, {id: "VarCon1a-h2", type: "scaffold", problemType: "TextBox", answerType: "arithmetic", hintAnswer: ["7x=-21"], dependencies: ["VarCon1a-h1"], title: "Subtraction", text: "Subtract 8 from each side."}, {id: "VarCon1a-h3", type: "hint", dependencies: ["VarCon1a-h2"], title: "Division property of equality", text: "When you divide both sides of an equation by any non-zero number, you still have equality."}, {id: "VarCon1a-h4", type: "scaffold", problemType: "TextBox", answerType: "arithmetic", hintAnswer: ["x=-3"], dependencies: ["VarCon1a-h3"], title: "Division", text: "Divide 7 from each side."}, {id: "VarCon1a-h5", type: "hint", dependencies: ["VarCon1a-h4"], title: "Verification", text: "Check whether the result is a solution of the equation."}, {id: "VarCon1a-h6", type: "scaffold", problemType: "MultipleChoice", answerType: "string", hintAnswer: ["True"], dependencies: ["VarCon1a-h5"], title: "Verification", text: "Check whether $$\\left(7\\right) -\\left(3\\right)+\\left(8\\right)$$ equals -13.", choices: ["TRUE", "FALSE"]}, ]; export {hints};