var hints = [{id: "add29a-h1", type: "hint", dependencies: [], title: "Simplify Both Sides", text: "We want to start by simplifying both sides and comparing the simplified value."}, {id: "add29a-h2", type: "scaffold", problemType: "TextBox", answerType: "arithmetic", hintAnswer: ["9"], dependencies: ["add29a-h1"], title: "Left Hand Side", text: "What does $$|-\\left(9\\right)|$$ evaluate to?", subHints: [{id: "add29a-h2-s1", type: "hint", dependencies: [], title: "Left Hand Side", text: "The $$absolute$$ value of a number is its distance from 0 on the number line. Distance is never negative, so the $$absolute$$ value is never negative."}]}, {id: "add29a-h3", type: "scaffold", problemType: "TextBox", answerType: "arithmetic", hintAnswer: ["-9"], dependencies: ["add29a-h1"], title: "Right Hand Side", text: "What does $$-|-\\left(9\\right)|$$ evaluate to?", subHints: [{id: "add29a-h3-s1", type: "hint", dependencies: [], title: "Right Hand Side", text: "We know that $$|-\\left(9\\right)|=9$$ so the opposite of $$|-\\left(9\\right)|$$ is -9."}]}, {id: "add29a-h4", type: "hint", dependencies: ["add29a-h2", "add29a-h3"], title: "Comparing Numbers", text: "Now we are left to compare 9 and -9. Since 9 is to the right of -9 on the number line, we say $$9>-\\left(9\\right)$$ Therefore, abs(-9)>-abs(-9)."}, ]; export {hints};