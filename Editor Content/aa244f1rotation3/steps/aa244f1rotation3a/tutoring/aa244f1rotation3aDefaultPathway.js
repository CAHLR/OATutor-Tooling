var hints = [{id: "aa244f1rotation3a-h1", type: "hint", dependencies: [], title: "Cot(2*\theta)", text: "To transform the equation of a conic given in the form $$A x^2+B x y+C y^2+D x+E y+F=0$$ into standard form by rotating the axes, we will rewrite the general form as an equation in the x' and y' coordinate system without the x'y' term, by rotating the axes by a measure of \theta that satisfies cot(2*\theta)=(A-C)/B. \\n If cot(2*\theta)>0, then 2*\theta is in the first quadrant, and \theta is between $$(0^o,{45}^o)$$. \\n If cot(2*\theta)<0, then 2*\theta is in the second quadrant, and \theta is between $$({45}^o,{90}^o)$$. \\n If $$A=C$$, then $$\\theta={45}^o$$.", variabilization: {}}, {id: "aa244f1rotation3a-h2", type: "hint", dependencies: ["aa244f1rotation3a-h1"], title: "Equations of Rotation", text: "If a point (x,y) on the Cartesian plane is represented on a new coordinate plane where the axes of rotation are formed by rotating an angle \theta from the positive x-axis, then the coordinates of the point with respect to the new axes are (x′,y′). We can use the following equations of rotation to define the relationship between (x,y) and (x′,y′): \\n x=x′*cos(\theta)-y′*sin(\theta) \\n and \\n y=x′*sin(\theta)+y′*cos(\theta)", variabilization: {}}, {id: "aa244f1rotation3a-h3", type: "hint", dependencies: ["aa244f1rotation3a-h2"], title: "Finding Cot(2*\theta)", text: "We want to find sin(\theta) and cos(\theta) so that we can use them for substitution later on. To do so, we would start by finding cot(2*\theta)=(A-C)/B.", variabilization: {}}, {id: "aa244f1rotation3a-h4", type: "scaffold", problemType: "TextBox", answerType: "arithmetic", hintAnswer: ["8"], dependencies: ["aa244f1rotation3a-h3"], title: "Finding Cot(2*\theta)", text: "What is A?", variabilization: {}}, {id: "aa244f1rotation3a-h5", type: "scaffold", problemType: "TextBox", answerType: "arithmetic", hintAnswer: ["-12"], dependencies: ["aa244f1rotation3a-h4"], title: "Finding Cot(2*\theta)", text: "What is B?", variabilization: {}}, {id: "aa244f1rotation3a-h6", type: "scaffold", problemType: "TextBox", answerType: "arithmetic", hintAnswer: ["17"], dependencies: ["aa244f1rotation3a-h5"], title: "Finding Cot(2*\theta)", text: "What is C?", variabilization: {}}, {id: "aa244f1rotation3a-h7", type: "scaffold", problemType: "TextBox", answerType: "arithmetic", hintAnswer: ["$$\\frac{3}{4}$$"], dependencies: ["aa244f1rotation3a-h6"], title: "Finding Cot(2*\theta)", text: "What is cot(2*\theta)=(A-C)/B?\n##figure1.gif##", variabilization: {}}, {id: "aa244f1rotation3a-h8", type: "hint", dependencies: ["aa244f1rotation3a-h7"], title: "Hypotenuse", text: "For the angle 2*\theta, the adjacent is of length 3 unit and the opposite side is of length 4 unit. What is the length of the hypotenuse? You can use the Pythagorean Theorem to calculate.", variabilization: {}}, {id: "aa244f1rotation3a-h9", type: "hint", dependencies: ["aa244f1rotation3a-h8"], title: "Finding Sin(\theta)", text: "Since we have the angle 2*\theta, we will use the trigonometry identity, sin(\theta)=sqrt((1-cos(2*\theta)/2). We can calculate cos(2*\theta) from the diagram as $$\\frac{adjacent}{hypotenuse}$$ for an angle 2*\theta. What is sin(\theta)?\n##figure2.gif##", variabilization: {}}, {id: "aa244f1rotation3a-h10", type: "hint", dependencies: ["aa244f1rotation3a-h9"], title: "Finding Cos(\theta)", text: "Since we have the angle 2*\theta, we will use the trigonometry identity, cos(\theta)=sqrt((1+cos(2*\theta)/2). We can calculate cos(2*\theta) from the diagram as $$\\frac{adjacent}{hypotenuse}$$ for an angle 2*\theta. What is cos(\theta)?\n##figure4.gif##", variabilization: {}}, {id: "aa244f1rotation3a-h11", type: "hint", dependencies: ["aa244f1rotation3a-h10"], title: "Substitution", text: "We want to substitute x=x′*cos(\theta)-y′*sin(\theta) and y=x′*sin(\theta)+y′*cos(\theta) into the equation so that we can manipulate the equation into the new representation.", variabilization: {}}, {id: "aa244f1rotation3a-h12", type: "scaffold", problemType: "TextBox", answerType: "arithmetic", hintAnswer: ["$$\\frac{2x'-y'}{\\sqrt{5}}$$"], dependencies: ["aa244f1rotation3a-h11"], title: "Substitution", text: "Simplifying the equation of rotation for the x term where x=x′*cos(\theta)-y′*sin(\theta), what is x equals to after substituting in sin(\theta) and cos(\theta)?", variabilization: {}}, {id: "aa244f1rotation3a-h13", type: "scaffold", problemType: "TextBox", answerType: "arithmetic", hintAnswer: ["$$\\frac{x'+2y'}{\\sqrt{5}}$$"], dependencies: ["aa244f1rotation3a-h12"], title: "Substitution", text: "Simplifying the equation of rotation for the y term where y=x′*sin(\theta)+y′*cos(\theta), what is y equals to after substituting in sin(\theta) and cos(\theta)?", variabilization: {}}, {id: "aa244f1rotation3a-h14", type: "scaffold", problemType: "MultipleChoice", answerType: "string", hintAnswer: ["$$8{\\left(\\frac{2x'-y'}{\\sqrt{5}}\\right)}^2-12\\frac{2x'-y'}{\\sqrt{5}} \\frac{x'+2y'}{\\sqrt{5}}+17{\\left(\\frac{x'+2y'}{\\sqrt{5}}\\right)}^2=20$$"], dependencies: ["aa244f1rotation3a-h13"], title: "Substitution", text: "Substituting $$x=\\frac{2x'-y'}{\\sqrt{5}}$$ and $$y=\\frac{x'+2y'}{\\sqrt{5}}$$ into $$8x^2-12x y+17y^2=20$$, what is the expression?", choices: ["$$8{\\left(\\frac{2x'-y'}{\\sqrt{5}}\\right)}^2-12\\frac{2x'-y'}{\\sqrt{5}} \\frac{x'+2y'}{\\sqrt{5}}+17{\\left(\\frac{x'+2y'}{\\sqrt{5}}\\right)}^2=20$$", "$$8{\\left(\\frac{x'+2y'}{\\sqrt{5}}\\right)}^2-12\\frac{2x'-y'}{\\sqrt{5}} \\frac{x'+2y'}{\\sqrt{5}}+17{\\left(\\frac{2x'-y'}{\\sqrt{5}}\\right)}^2=20$$"], variabilization: {}}, {id: "aa244f1rotation3a-h15", type: "hint", dependencies: ["aa244f1rotation3a-h14"], title: "Simplification", text: "We can start our simplification by first squaring the denominators,. What is the equation?", variabilization: {}}, {id: "aa244f1rotation3a-h16", type: "scaffold", problemType: "MultipleChoice", answerType: "string", hintAnswer: ["$$8\\left(4{x'}^2-4x' y'+{y'}^2\\right)-12\\left(2{x'}^2+3x' y'-2{y'}^2\\right)+17\\left({x'}^2+4x' y'+4{y'}^2\\right)=100$$"], dependencies: ["aa244f1rotation3a-h15"], title: "Simplification", text: "Next, we will multiply by 5 on both sides so that we can remove the denominators and expand out the binomials using the FOIL method. What is the equation now?", choices: ["$$8\\left(4{x'}^2-4x' y'+{y'}^2\\right)-12\\left(2{x'}^2+3x' y'-2{y'}^2\\right)+17\\left({x'}^2+4x' y'+4{y'}^2\\right)=100$$", "$$8\\left(4{x'}^2+4x' y'+{y'}^2\\right)-12\\left(2{x'}^2-3x' y'-2{y'}^2\\right)+17\\left({x'}^2-4x' y'+4{y'}^2\\right)=100$$"], variabilization: {}}, {id: "aa244f1rotation3a-h17", type: "scaffold", problemType: "MultipleChoice", answerType: "string", hintAnswer: ["$$25{x'}^2+100{y'}^2=100$$"], dependencies: ["aa244f1rotation3a-h16"], title: "Simplification", text: "Next we will distribute the scalar multiples and combine like terms. What is the current equation?", choices: ["$$25{x'}^2+100{y'}^2=100$$", "$$100{x'}^2+25{y'}^2=100$$"], variabilization: {}}, {id: "aa244f1rotation3a-h18", type: "scaffold", problemType: "MultipleChoice", answerType: "string", hintAnswer: ["$$\\frac{{x'}^2}{4}+\\frac{{y'}^2}{1}=1$$"], dependencies: ["aa244f1rotation3a-h17"], title: "Simplification", text: "Set the RHS to 1 by dividing by 100. We can write the equation with x' and y' in the standard form by dividing each term by the constant in the denominator. What is the equation now? The equation is an ellipse.\n##figure8.gif##", choices: ["$$\\frac{{x'}^2}{4}+\\frac{{y'}^2}{1}=1$$", "$$\\frac{{x'}^2}{1}+\\frac{{y'}^2}{4}=1$$"], variabilization: {}}, ]; export {hints};