var hints = [{id: "other9a-h1", type: "hint", dependencies: [], title: "Adding 1 to Both Sides", text: "The first step is to add 1 to both sides of the equation: $$|\\left(1\\right)-\\left(4\\right) x|=6$$"}, {id: "other9a-h2", type: "hint", dependencies: ["other9a-h1"], title: "Creating Two Equations", text: "Create two equations setting 1-4x equal to 6 and -6."}, {id: "other9a-h3", type: "scaffold", problemType: "TextBox", answerType: "arithmetic", hintAnswer: ["-5/4"], dependencies: ["other9a-h2"], title: "Solving $$\\left(1\\right)-\\left(4\\right) x=6$$", text: "What is x when 1-4x=6?", subHints: [{id: "other9a-h3-s1", type: "hint", dependencies: [], title: "Solving $$\\left(1\\right)-\\left(4\\right) x=6$$", text: "To solve $$\\left(1\\right)-\\left(4\\right) x=6$$ start by subtracting 1 from both sides of the equation: $$-\\left(4\\right) x=5$$ Then, divide both sides by -4 to get $$x=\\frac{-\\left(5\\right)}{4}$$"}]}, {id: "other9a-h4", type: "scaffold", problemType: "TextBox", answerType: "arithmetic", hintAnswer: ["2020-07-04 00:00:00"], dependencies: ["other9a-h2"], title: "Solving $$\\left(1\\right)-\\left(4\\right) x=-\\left(6\\right)$$", text: "What is x when 1-4x=-6?", subHints: [{id: "other9a-h4-s1", type: "hint", dependencies: [], title: "Solving $$\\left(1\\right)-\\left(4\\right) x=-\\left(6\\right)$$", text: "For $$\\left(1\\right)-\\left(4\\right) x=-\\left(6\\right)$$ subtract 1 from both sides of the equation: $$-\\left(4\\right) x=-\\left(7\\right)$$ Then, divide both sides by -4 to get $$x=\\frac{7}{4}$$"}]}, {id: "other9a-h5", type: "hint", dependencies: ["other9a-h3", "other9a-h4"], title: "Final Answer", text: "So, the only values of x that would satisfy $$|\\left(1\\right)-\\left(4\\right) x|-\\left(1\\right)=5$$ are $$\\frac{-\\left(5\\right)}{4}$$ and $$\\frac{7}{4}$$"}, ]; export {hints};