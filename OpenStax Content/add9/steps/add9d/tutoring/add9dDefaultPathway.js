var hints = [{id: "add9d-h1", type: "hint", dependencies: [], title: "Finding the Value of $$|q|$$", text: "The first step is to find the value of abs(q)."}, {id: "add9d-h2", type: "scaffold", problemType: "TextBox", answerType: "arithmetic", hintAnswer: ["49"], dependencies: ["add9d-h1"], title: "Calculating $$|q|$$", text: "$$q=-\\left(49\\right)$$ What is abs(-49)?", subHints: [{id: "add9d-h2-s1", type: "hint", dependencies: [], title: "Evaluating the Absolute Value of Negative Numbers", text: "If a is negative, then abs(a)=-a. For example, $$|-\\left(11\\right)|=11$$"}]}, {id: "add9d-h3", type: "hint", dependencies: ["add9d-h2"], title: "Finding the Value of $$-|q|$$", text: "Multiply $$|q|$$ by -1 to find -abs(q)."}, {id: "add9d-h4", type: "scaffold", problemType: "TextBox", answerType: "arithmetic", hintAnswer: ["-49"], dependencies: ["add9d-h3"], title: "Calculating $$-|q|$$ with the Substituted Value of q", text: "What is -1*49?"}, ]; export {hints};