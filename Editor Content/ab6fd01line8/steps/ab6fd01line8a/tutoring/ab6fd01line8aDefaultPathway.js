var hints = [{id: "ab6fd01line8a-h1", type: "scaffold", problemType: "TextBox", answerType: "arithmetic", hintAnswer: ["$$\\frac{1}{6}$$"], dependencies: [], title: "Identify the Slope", text: "What is the value of the slope given in the problem?", variabilization: {}}, {id: "ab6fd01line8a-h2", type: "scaffold", problemType: "MultipleChoice", answerType: "string", hintAnswer: ["(6,1)"], dependencies: ["ab6fd01line8a-h1"], title: "Identify the Point", text: "What is the coordinate of the given point?", choices: ["(-1,6)", "(6,1)", "$$(\\frac{1}{6},1)$$", "$$(6,\\frac{1}{6})$$"], variabilization: {}}, {id: "ab6fd01line8a-h3", type: "hint", dependencies: ["ab6fd01line8a-h2"], title: "Point Slope Form", text: "Substitute the values into the point-slope form, $$y-y_1=m\\left(x-x_1\\right)$$", variabilization: {}}, {id: "ab6fd01line8a-h4", type: "hint", dependencies: ["ab6fd01line8a-h3"], title: "Slope Intercept Form", text: "Simplify the equation and write it in slope intercept form", variabilization: {}}, ]; export {hints};