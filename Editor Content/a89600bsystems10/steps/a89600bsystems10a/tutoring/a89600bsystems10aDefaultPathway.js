var hints = [{id: "a89600bsystems10a-h1", type: "hint", dependencies: [], title: "Subsituting Possible Values", text: "The substitution method we used for linear systems is the same method we will use for nonlinear systems. We solve one equation for one variable and then substitute the result into the second equation to solve for another variable, and so on.", variabilization: {}}, {id: "a89600bsystems10a-h2", type: "hint", dependencies: ["a89600bsystems10a-h1"], title: "Common Terms between Equations", text: "What is the common term between the two equations that can be used for substitution?", variabilization: {}}, {id: "a89600bsystems10a-h3", type: "hint", dependencies: ["a89600bsystems10a-h2"], title: "Substitution", text: "What is the equation that we are trying to solve for after substituting the second equation into the first?", variabilization: {}}, {id: "a89600bsystems10a-h4", type: "hint", dependencies: ["a89600bsystems10a-h3"], title: "Factorization", text: "Factorize $$\\left(2\\right) x^3-x^2+x-\\frac{1}{2}=0$$ so that we can find the x coordinates.", variabilization: {}}, {id: "a89600bsystems10a-h5", type: "scaffold", problemType: "TextBox", answerType: "arithmetic", hintAnswer: ["$$\\left(x-\\frac{1}{2}\\right) \\left(\\left(2\\right) x^2+\\left(1\\right)\\right)$$"], dependencies: ["a89600bsystems10a-h4"], title: "Factorization", text: "One of the zeros to $$f(x)=\\left(2\\right) x^3-x^2+x-\\frac{1}{2}$$ is $$\\frac{1}{2}$$. We can use synthetic division to divide $$x-\\frac{1}{2}$$ from the expression. What is the factored expression?", variabilization: {}}, {id: "a89600bsystems10a-h6", type: "scaffold", problemType: "MultipleChoice", answerType: "string", hintAnswer: ["No"], dependencies: ["a89600bsystems10a-h5"], title: "Factorization", text: "Does $$f(x)=\\left(2\\right) x^2+\\left(1\\right)$$ have any zeros? Consider that it is a quadratic curve above the x-axis.", choices: ["Yes", "No"], variabilization: {}}, {id: "a89600bsystems10a-h7", type: "hint", dependencies: ["a89600bsystems10a-h6"], title: "Solving for y", text: "There is only one real solution to the equation, $$\\left(2\\right) x^3-x^2+x-\\frac{1}{2}=0$$. We now want to find the y coordinate that correspond to this x coordinate.", variabilization: {}}, {id: "a89600bsystems10a-h8", type: "scaffold", problemType: "TextBox", answerType: "arithmetic", hintAnswer: ["0"], dependencies: ["a89600bsystems10a-h7"], title: "Solving for y", text: "Substituting $$x=\\frac{1}{2}$$ into y=1/2-x/ What is the corresponding y coordinate?", variabilization: {}}, {id: "a89600bsystems10a-h9", type: "hint", dependencies: ["a89600bsystems10a-h8"], title: "Verifying the Number Of Intersections", text: "We have found the coordinates of all intersections. How many are there?", variabilization: {}}, ]; export {hints};