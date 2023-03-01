# OATutor-Tooling

## Our project
This repository is meant to store content and quality assurance tools used for the OATutor system developed by Computational Approaches to Human Learning at UC Berkeley. The OATutor system was developed to make learning more accessible and provide an open-source tutoring system for researchers, teachers, and students to access, disseminate, and better understand learning materials.

## Structure of README
The README of the repository is composed of two main parts. The first part explains the usage and structure of the content generation script, which is located under the TerminalScript directory, and the second part explains the usage of the Selenium testing and answer validation script, which is located under the selenium directory.

## Content Script General Usage
To run script on one sheet, change directory into TerminalScript, and use the command: 
```
python3 process_sheet.py online <sheet_key> <sheet_name>
```
where `sheet_key` is taken from the google sheet URL, and `sheet_name` is the name of Google sheet tab to be run on. The generated content will appear under OATutor-Tooling/OpenStax1.

To run script over the full content pool (i.e. full content update), use the command:
```
python3 final.py online full
```
This will regenerate content for all books listed in Problem Bank URL (https://docs.google.com/spreadsheets/d/1yyeDxm52Zd__56Y0T3CdoeyXvxHVt0ITDKNKWIoIMkU). 

To run script over contents that have been recently modified, used the command:
```
python3 final.py online
```
This will only update the json content files corresponding to problems that are modified or newly added since the last content script execution.

The script is also responsible for auto-checking the content format, and providing instant feedback to content editors directly through Google sheets. 

## How to structure content
The script in this repo reads in Google Sheets and outputs json files ready to be processed by the system. For every sheet procesed by the system, there are some requirements for headers and notation that ensure the script is read properly. Every sheet must have: "Problem Name", "Row Type", "Title", "Body Text", "Answer", "answerType", "HintID", "Dependency", "mcChoices", "Images (space delimited)", "Parent", "OER src", "openstax KC", "KC", and "Taxonomy", and may optionally include "Variabilization" and "Meta".

## Content Organization
The content in OATutor is organized into different lessons. On a Google Sheets Document, each lesson should have its own sheet (i.e. tab). Each lesson has different KC's, or knowledge components, associated with it, and the OATutor system attempts to ensure that a student has only finished the lesson after demonstrating mastery of each KC within the lesson.

## Problem Organization
The way that content in OATutor is structured is that every row denotes either a problem, step, hint, or scaffold. Problems are generally just headers that tell the student what skill the question is about, meaning that the actual question is asked in the steps of the problem. This also means that every problem must have at least one step. Steps ask the actual questions and as a result, also have corresponding answers that can be formatted in different ways. Since steps themselves are questions, they have associated hints and scaffolds to provide students with help. Hints are sentences (not questions) that provide students with information such that they can answer the step better. Scaffolds on the other hand are questions themselves that have answers so that students can work through part of the problem. 

## Headers and associated values:
Here is an example of a fully finished Google Sheets with content ready to be loaded into the system: https://docs.google.com/spreadsheets/d/1kp-RgMBtw-B5hXrMuMG4J40WYTJrMuF34seTAwaSAl4/edit?usp=sharing

Problem Name: This is a problem name for the system. It is generally abbreviated (e.g. "Linear Inequalities" becomes "LinIneq") and has a number appended to the end to denote which numberproblem it is. For example, the seventh linear inequality problem may be denoted as "LinIneq7". Every problem must have a distinct name, and the problem name field must always be filled in when the row type is "problem."

Row Type: Takes on four values: "problem", "step", "hint", or "scaffold".

Title: Denotes what the problem/step/scaffold.hint is about. Can contain mathematical notation/LaTex.

Body Text: Provides the text of the step, scaffold, or hint. Can contain mathematical notation/LaTex. Generally blank for problem rows.

Answer: The answer for the step/scaffold. Leave this field blank for hints and problems.

answerType: The answer types are "mc", "string", and "algebra". "mc" denotes multiple choice and if a step/scaffold/hint is "mc", then the "mcChoices" field must be filled in. "string" means that the answer the student provides must exactly match the answer that the content creator inputs in the "Answer" field, and is generally used for questions with text answers. "algebra" means that the answer can contain some type of math notation and the OpenITS system will check that the answer that the student provided is mathematically equivalent to the answer provided by the content creator. 

HintID: The id of the hint/scaffold. Leave this field blank if the row is a problem or a step. These are generally denoted "h1", "h2", etc. for the number of hint they are for the step. Every hint/scaffold in a step must have a unique hint ID, but hint IDs don't have to be unique across steps and problems. 

Dependency: This field enables the OATutor to open hints only after certain other hints have already been opened or scaffolds have been correctly answered. The dependency field can also include multiple other hints, and is comma-delimited. An example could be "h1,h2,h3" if the content creator wants students to only access this hint after finishing "h1", "h2", and "h3".

mcChoices: This field is only filled in if the answerType is "mc". One of the choices here must be exactly similar to the answer provided in the answer field. This field is "|" delimited. For example, if the possible answers are "square", "cirle", "triangle", or "octagon", then this field must be "square|circle|triangle|octagon" with the Answer field being either "square", "cirle", "triangle", or "octagon". 

Images (space delimited): If you want to provide images in the questions, you can do so here. Please provide the URL's to the images themselves, not a URL that contains the image but may have other content.

Parent: The OATutor system supports subhints and sub-scaffolds, which are hints and scaffolds provided to help students answer hints and scaffolds. For example, if the hint with id "h3" needs subhints, then that can be expressed here by setting the Parent field to "h3". The hint id for subhint is denoted analogous to regular hint id's, except the "h" is replaced with an "s".

OER src: If the problem comes from an OER source, provide the URL here.

openstax KC: KC denotes knowledge component. If using an openstax textbook, you can provide the KC name provided by the OpenStax textbook here.

KC: A name for the KC. Every problem row must have this field filled in. Questions within the OATutor system are grouped by their KC, so if multiple questions have the same skills, they will appear within the same lesson.

Taxonomy: If it exists, a link to the skill taxonomy which specifies the order of the KC's. This field is optional.

Variabilization: If it exists, each cell in this column will contain group(s) of variable-value matching. Variable that appears in problem or answer text will have one of its possible values selected at random, which will replace the variable name in the problem text. This field is optional.

Meta: It it exists, contains metadata about mode of the problem.

## Text Formatting
OATutor supports mathematical notation so that questions can render properly and more easily for students to see. There are two options when it comes to math notation. First, content creators can use OATutor's mathematical notation itself, but this math notation has specific formatting rules and only supports a limited amount of math operations, which will be explained below. For broader math/symbol support, content creators can write their content directly in LaTex and wrap the LaTex portions of their content in "$$" which tells the system to process it as LaTex. Prepending "##" to the sheet name prevents the content script from rendering mathematical notations in LaTex. 

### OATutor math formatting:
This is the default math formatting that the system uses. If you wish to use the math formatting, please adhere to the following formatting rules:

Leave no spaces within the mathematical expression. This means that "x = 5 + 3 / 4" should be denoted as "x=5+3/4".

When nesting expressions, only use parentheses rather than brackets.

The following math expressions should be denoted using the following symbols:
Addition: +

Subtraction: -

Multiplication: *

Division: /

Exponentiation: **

Square root: sqrt() . For example, the square root of 5 should be denoted "sqrt(5)". If you wish to take the root to another power, denote that as "sqrt(root,base)". For example, the 5th root of y should be denoted "sqrt(5,y)". Make sure to avoid spaces.

Plus or Minus: +/-

Absolute value: The absolute value of x should be denoted as "abs(x)"

Infinity: "inf"

Less than: <

Greater than: >

Less than or equal to: <=

Greater than or equal to: >=

Subscript: _

Matrix: /mat{(a,b,c),(d,e,f),(g,h,i)} . This will give a 3x3 matrix where the first row is (a,b,c), second row is (d,e,f), and third row is (g,h,i). The system supports arbitrary number of rows and columns, and supports math expressions for each element. 

## Selenium Script Intro
The Selenium script is developed with the purpose of answer validation testing. The script connects to the debug tool in the content-staging server, simulates user's behavior of inputting answers, and checks for the correctness of each answer. There are two modes for which the script could be run: testing one problem, or testing all problem contents. For both modes, errors are summarized in a Pandas DataFrame, and reported to the feedback Google sheet. 

## Selenium Script Usage
To test all steps of a particular problem, change directory to selenium, and run the following command:
```
python3 test_page.py <problem_name>
```
or
```
python3 test_page.py <problem_name> <url_prefix>
```
problem_name: the name of problem that you are testing, with hash code included. ex. "af36e21FunNota14".
`url_prefix`: the script tests the webpage with the full URL: `url_prefix + problem_name`. If `url_prefix` is not specified in the function call, it will be default to the CAHLR staging URL "https://cahlr.github.io/OATutor-Staging/#/debug/". 

To test answer for all problems, change directory to selenium, and run the following command:
```
python3 test_all.py <url_prefix>
```
This command loops through the collection of all problems under OpenStax Content, fetches the step answers and types for each problem from the content js files, and runs UI testing for each problem.

## Feedback Submission Check
To test whether feedback submitted through the frontend platform reaches Google firestore, run the file check_feedback.py under selenium with the following command:
```
python3 check_feedback.py <url_prefix>
```
url_prefix: an optional argument that specifies the url domain that the feedback will be submitted from. If not present, we default to the staging branch. 

## OATutor Google App Script Editor Tools Library

A set of tools is currently under development to be incorporated in relevant content Google Spreadsheets.

### Using the Library

1. In a content spreadsheet (e.g., "Openstax: College Algebra"), click on the Extensions menu
2. Click on the App Scripts menu item
3. In the App Scripts editor, If the "OATutorEditorTools" library already exists under the "Libraries" tab, skip to step 6
4. Next to the "Libraries" tab, there is a plus button. Click it then paste in the following script ID: `1l0L7TnKrOHOrRDVOLrO3F0JM1BcUBD1P3ckEPpy7ZbchyO-7t1OuvLIa`
5. Choose the default options
6. To use a library function such as `getProblemId(rawProblemName)`, write a function in any `.gs` file

For example, to generate problem IDs (with hash prepended) in "Openstax: College Algebra", 
`generateProblemId.gs` is created with the following content:
```javascript
function getProblemId(rawProblemName) {
  return OATutorEditorTools.getProblemId(rawProblemName);
}
```  
> Make sure to press ctrl/cmd + s to save!!

Then, in the spreadsheet, it is possible to enter custom formula to access the custom formula.  
For example, putting `= getProblemId("real1")` into a cell returns `a6f9727real1`

### Errors?

This could be because the library project has not been shared with you yet. Message an OATutor dev.

### Updating the Library

1. Write relevant code with relevant function/parameter names
2. Press ctrl/cmd + s to save
3. Press the blue "Deploy" button
4. Choose the library type
5. In the description, roughly describe what feature you added
6. Deploy
