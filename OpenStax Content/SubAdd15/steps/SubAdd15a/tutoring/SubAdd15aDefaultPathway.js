var hints = [{id: "SubAdd15a-h1", type: "hint", dependencies: [], title: "Addition property of equality", text: "When you add the same quantity to both sides of an equation, you still have equality."}, {id: "SubAdd15a-h2", type: "scaffold", problemType: "TextBox", answerType: "arithmetic", hintAnswer: ["b-0.47+0.47=-2.1+0.47"], dependencies: ["SubAdd15a-h1"], title: "Addition", text: "Add 0.47 to each side of the equation."}, {id: "SubAdd15a-h3", type: "scaffold", problemType: "TextBox", answerType: "arithmetic", hintAnswer: ["b=-1.63"], dependencies: ["SubAdd15a-h2"], title: "Simplification", text: "Simplify the equation."}, {id: "SubAdd15a-h4", type: "hint", dependencies: ["SubAdd15a-h3"], title: "Verification", text: "Check whether the result is a solution of the equation."}, {id: "SubAdd15a-h5", type: "scaffold", problemType: "MultipleChoice", answerType: "string", hintAnswer: ["True"], dependencies: ["SubAdd15a-h4"], title: "Verification", text: "Check whether -1.63-0.47 equals -2.1.", choices: ["TRUE", "FALSE"]}, ]; export {hints};