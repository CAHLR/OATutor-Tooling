var hints = [{id: "whole11a-h1", type: "hint", dependencies: [], title: "Finding Two Factors Whose Product is the Given Number", text: "The first step is to find two factors whose product is the given number."}, {id: "whole11a-h2", type: "scaffold", problemType: "MultipleChoice", answerType: "string", hintAnswer: ["Yes"], dependencies: ["whole11a-h1"], title: "Finding Two Factors Whose Product is the Given Number", text: "Are 12 and 21 factors of 252 that multiply together to make 252?", choices: ["Yes", "No"]}, {id: "whole11a-h3", type: "hint", dependencies: ["whole11a-h2"], title: "Prime Number Factors", text: "If a factor is prime, that means it can't be divided further. Thus, it is a prime factor of the number."}, {id: "whole11a-h4", type: "scaffold", problemType: "MultipleChoice", answerType: "string", hintAnswer: ["No"], dependencies: ["whole11a-h3"], title: "Verifying if a Factor is Prime", text: "Is 12 prime?", choices: ["Yes", "No"]}, {id: "whole11a-h5", type: "scaffold", problemType: "MultipleChoice", answerType: "string", hintAnswer: ["No"], dependencies: ["whole11a-h4"], title: "Verifying if a Factor is Prime", text: "Is 21 prime?", choices: ["Yes", "No"]}, {id: "whole11a-h6", type: "hint", dependencies: ["whole11a-h5"], title: "Proceeding With a Factor that is Not Prime", text: "The next step is to divide factors that are not prime into two more factors."}, {id: "whole11a-h7", type: "scaffold", problemType: "MultipleChoice", answerType: "string", hintAnswer: ["Yes"], dependencies: ["whole11a-h6"], title: "Finding Two Factors Whose Product is the Given Number", text: "Are 2 and 6 factors of 12 that multiply together to make 12?", choices: ["Yes", "No"]}, {id: "whole11a-h8", type: "scaffold", problemType: "MultipleChoice", answerType: "string", hintAnswer: ["Yes"], dependencies: ["whole11a-h7"], title: "Verifying if a Factor is Prime", text: "Is 2 prime?", choices: ["Yes", "No"]}, {id: "whole11a-h9", type: "scaffold", problemType: "MultipleChoice", answerType: "string", hintAnswer: ["No"], dependencies: ["whole11a-h8"], title: "Verifying if a Factor is Prime", text: "Is 6 prime?", choices: ["Yes", "No"]}, {id: "whole11a-h10", type: "scaffold", problemType: "MultipleChoice", answerType: "string", hintAnswer: ["Yes"], dependencies: ["whole11a-h9"], title: "Finding Two Factors Whose Product is the Given Number", text: "Are 3 and 7 factors of 21 that multiply together to make 21?", choices: ["Yes", "No"]}, {id: "whole11a-h11", type: "scaffold", problemType: "MultipleChoice", answerType: "string", hintAnswer: ["Yes"], dependencies: ["whole11a-h10"], title: "Verifying if a Factor is Prime", text: "Is 3 prime?", choices: ["Yes", "No"]}, {id: "whole11a-h12", type: "scaffold", problemType: "MultipleChoice", answerType: "string", hintAnswer: ["Yes"], dependencies: ["whole11a-h11"], title: "Verifying if a Factor is Prime", text: "Is 7 prime?", choices: ["Yes", "No"]}, {id: "whole11a-h13", type: "hint", dependencies: ["whole11a-h12"], title: "Proceeding With a Factor that is Not Prime", text: "Continue to divide factors that are not prime into two more factors."}, {id: "whole11a-h14", type: "scaffold", problemType: "MultipleChoice", answerType: "string", hintAnswer: ["Yes"], dependencies: ["whole11a-h13"], title: "Finding Two Factors Whose Product is the Given Number", text: "Are 2 and 3 factors of 6 that multiply together to make 6?", choices: ["Yes", "No"]}, {id: "whole11a-h15", type: "scaffold", problemType: "MultipleChoice", answerType: "string", hintAnswer: ["Yes"], dependencies: ["whole11a-h14"], title: "Verifying if a Factor is Prime", text: "Are both 2 and 3 prime?", choices: ["Yes", "No"]}, {id: "whole11a-h16", type: "hint", dependencies: ["whole11a-h15"], title: "Final Step", text: "The final step is to write the composite number as the product of all the prime factors."}, {id: "whole11a-h17", type: "hint", dependencies: ["whole11a-h16"], title: "Answer", text: "The found prime factors of 252 were 2,2,3,3, and 7. and 3. Thus $$\\left(2\\right) \\left(2\\right) \\left(3\\right) \\left(3\\right) \\left(7\\right)=252$$ and $$\\left(2\\right) \\left(2\\right) \\left(3\\right) \\left(3\\right) \\left(7\\right)$$ is the prime factorization of 252."}, ]; export {hints};