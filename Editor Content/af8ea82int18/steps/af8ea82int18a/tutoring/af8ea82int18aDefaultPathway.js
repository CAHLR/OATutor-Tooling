var hints = [{id: "af8ea82int18a-h1", type: "hint", dependencies: [], title: "Simplify the Expression in the Absolute Value", text: "First, simplify what's inside the absolute value, until it is a single number", variabilization: {}}, {id: "af8ea82int18a-h2", type: "scaffold", problemType: "TextBox", answerType: "arithmetic", hintAnswer: ["0"], dependencies: ["af8ea82int18a-h1"], title: "Simplify the Expression in the Absolute Value", text: "What is $$8-4\\left(7-5\\right)$$?", subHints: [{id: "af8ea82int18a-h2-s1", type: "scaffold", problemType: "TextBox", answerType: "arithmetic", hintAnswer: ["2"], dependencies: [], title: "Simplify the Expression in the Absolute Value", text: "What is (7-5)?", variabilization: {}}, {id: "af8ea82int18a-h2-s2", type: "scaffold", problemType: "TextBox", answerType: "arithmetic", hintAnswer: ["8"], dependencies: ["af8ea82int18a-h2-s1"], title: "Simplify the Expression in the Absolute Value", text: "What is $$4\\times2$$?", variabilization: {}}, {id: "af8ea82int18a-h2-s3", type: "scaffold", problemType: "TextBox", answerType: "arithmetic", hintAnswer: ["0"], dependencies: ["af8ea82int18a-h2-s2"], title: "Simplify the Expression in the Absolute Value", text: "What is 8-8?", variabilization: {}}], variabilization: {}}, {id: "af8ea82int18a-h3", type: "hint", dependencies: ["af8ea82int18a-h2"], title: "Simplify the Absolute Value", text: "Replace $$|8-4\\left(7-5\\right)|$$ with the absolute value of 0; remember that the absolute value of 0 is 0", variabilization: {}}, {id: "af8ea82int18a-h4", type: "scaffold", problemType: "TextBox", answerType: "arithmetic", hintAnswer: ["0"], dependencies: ["af8ea82int18a-h3"], title: "Simplify the Absolute Value", text: "What is $$|0|$$?", variabilization: {}}, {id: "af8ea82int18a-h5", type: "hint", dependencies: ["af8ea82int18a-h4"], title: "Finishing the Problem", text: "Once the absolute value is replaced, we can solve the problem like normal", variabilization: {}}, {id: "af8ea82int18a-h6", type: "scaffold", problemType: "TextBox", answerType: "arithmetic", hintAnswer: ["9"], dependencies: ["af8ea82int18a-h5"], title: "Finishing the Problem", text: "What is 9-0?", variabilization: {}}, ]; export {hints};