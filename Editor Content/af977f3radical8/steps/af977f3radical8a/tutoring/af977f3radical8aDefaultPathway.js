var hints = [{id: "af977f3radical8a-h1", type: "hint", dependencies: [], title: "Finding the Largest Perfect Square", text: "You must first identify the largest perfect square factor of the variable inside the radical.", variabilization: {}}, {id: "af977f3radical8a-h2", type: "scaffold", problemType: "TextBox", answerType: "arithmetic", hintAnswer: ["$$49v^8$$"], dependencies: ["af977f3radical8a-h1"], title: "Finding the Largest Perfect Square", text: "What is the largest perfect square factor of the variable inside the radical?", variabilization: {}}, {id: "af977f3radical8a-h3", type: "hint", dependencies: ["af977f3radical8a-h2"], title: "Rewriting the Radical", text: "You must now rewrite the radical as the product of two radicals. One of these radicals must include the perfect square. This is possible because of the product rule.", variabilization: {}}, {id: "af977f3radical8a-h4", type: "scaffold", problemType: "TextBox", answerType: "arithmetic", hintAnswer: ["$$\\sqrt{49v^8} \\sqrt{v}$$"], dependencies: ["af977f3radical8a-h3"], title: "Rewriting the Radical", text: "What is the result?", variabilization: {}}, {id: "af977f3radical8a-h5", type: "scaffold", problemType: "TextBox", answerType: "arithmetic", hintAnswer: ["$$7v^4 \\sqrt{v}$$"], dependencies: ["af977f3radical8a-h4"], title: "Simplfying the Radicals", text: "What is the result after simplifying the square root with the perfect square?", variabilization: {}}, ]; export {hints};