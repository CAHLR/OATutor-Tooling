var hints = [{id: "DivMul40a-h1", type: "hint", dependencies: [], title: "Translation", text: "We need to find what we are asked to find and which sentence gives the $$information$$ to find it."}, {id: "DivMul40a-h2", type: "hint", dependencies: ["DivMul40a-h1"], title: "Objective", text: "We are asked to find the cost for each person."}, {id: "DivMul40a-h3", type: "hint", dependencies: ["DivMul40a-h2"], title: "Information", text: "The cost for 6 people is $34.98."}, {id: "DivMul40a-h4", type: "hint", dependencies: ["DivMul40a-h3"], title: "Assignment", text: "Assign a variable to what we want to find. For example, let $$c=the$$ cost for each person."}, {id: "DivMul40a-h5", type: "hint", dependencies: ["DivMul40a-h4"], title: "Translation", text: "Translate into an equation."}, {id: "DivMul40a-h6", type: "scaffold", problemType: "TextBox", answerType: "arithmetic", hintAnswer: ["6c=34.98"], dependencies: ["DivMul40a-h5"], title: "Translation", text: "Write the equation."}, {id: "DivMul40a-h7", type: "hint", dependencies: ["DivMul40a-h6"], title: "Division property of equality", text: "When you divide both sides of an equation by any non-zero number, you still have equality."}, {id: "DivMul40a-h8", type: "scaffold", problemType: "TextBox", answerType: "arithmetic", hintAnswer: ["c=5.83"], dependencies: ["DivMul40a-h7"], title: "Division", text: "Divide both sides by 6."}, {id: "DivMul40a-h9", type: "hint", dependencies: ["DivMul40a-h8"], title: "Verification", text: "Check whether the result is a solution of the equation."}, {id: "DivMul40a-h10", type: "scaffold", problemType: "MultipleChoice", answerType: "string", hintAnswer: ["True"], dependencies: ["DivMul40a-h9"], title: "Verification", text: "Check whether $$\\left(6\\right) \\left(5.83\\right)$$ equals 34.98.", choices: ["TRUE", "FALSE"]}, {id: "DivMul40a-h11", type: "hint", dependencies: ["DivMul40a-h10"], title: "Explanation", text: "Since $$c=5.83$$ the cost for each person is $5.83."}, ]; export {hints};