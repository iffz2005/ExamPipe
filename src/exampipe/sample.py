"""Synthetic demo data.

Everything here is invented for this repository: simple arithmetic, number
series and widely known general facts. No real exam content is used anywhere.
``clean_rows`` is a valid paper for configs/demo_exam.yaml; ``broken_text``
takes the same paper and plants one defect per validation rule, so the
validator can be demonstrated (and tested) against known-bad input.
"""

from __future__ import annotations

from .schema import Row

M, R, G = "Mathematics", "Reasoning", "General Knowledge"

# (section, sub_section, question, [4 options], correct_answer, explanation, difficulty)
_RAW = [
    # ---- Mathematics (1-10) ---------------------------------------------------
    (M, "Percentage", r"What is $20\%$ of $150$?", [r"$20$", r"$25$", r"$30$", r"$35$"], "3",
     r"The percentage $20\%$ means $\frac{20}{100}$. Multiplying this by the number gives $\frac{20}{100}\times150=30$.<br><br>Hence <b>$30$</b> is the required value.", "Easy"),
    (M, "Percentage", r"A price rises from $200$ to $250$. What is the percentage increase?", [r"$20\%$", r"$25\%$", r"$30\%$", r"$50\%$"], "2",
     r"The increase is $250-200=50$. The percentage increase is $\frac{50}{200}\times100=25\%$.<br><br>Therefore the price rose by <b>$25\%$</b>.", "Medium"),
    (M, "Percentage", r"If $40\%$ of a number is $60$, what is the number?", [r"$120$", r"$150$", r"$180$", r"$240$"], "2",
     r"Let the number be $x$. Then $\frac{40}{100}x=60$, so $x=\frac{60\times100}{40}=150$.<br><br>The number is therefore <b>$150$</b>.", "Medium"),
    (M, "Ratio and Proportion", r"Divide $60$ in the ratio $2:3$. What is the larger part?", [r"$24$", r"$30$", r"$36$", r"$40$"], "3",
     r"The total number of parts is $2+3=5$. One part equals $\frac{60}{5}=12$.<br><br>The larger part has $3$ parts, so it is <b>$36$</b>.", "Easy"),
    (M, "Ratio and Proportion", r"If $a:b=3:4$ and $b:c=2:5$, what is $a:c$?", [r"$3:10$", r"$3:5$", r"$6:5$", r"$2:5$"], "1",
     r"Make the value of $b$ equal in both ratios. Rewriting $b:c=2:5$ as $4:10$ gives $a:b:c=3:4:10$.<br><br>Hence the required ratio is <b>$3:10$</b>.", "Hard"),
    (M, "Ratio and Proportion", r"The ratio of boys to girls in a class is $3:2$. If there are $15$ boys, how many girls are there?", [r"$8$", r"$10$", r"$12$", r"$15$"], "2",
     r"Each part of the ratio equals $\frac{15}{3}=5$ students. The girls make up $2$ parts, so there are $2\times5=10$ girls.<br><br>The class therefore has <b>$10$</b> girls.", "Easy"),
    (M, "Time and Work", r"A can finish a job in $10$ days and B in $15$ days. Working together, in how many days will they finish it?", [r"$5$", r"$6$", r"$7$", r"$8$"], "2",
     r"In one day A does $\frac{1}{10}$ of the job and B does $\frac{1}{15}$. Together they do $\frac{1}{10}+\frac{1}{15}=\frac{1}{6}$ of the job per day.<br><br>They will therefore finish it in <b>$6$</b> days.", "Medium"),
    (M, "Time and Work", r"A tap fills a tank in $12$ hours. How much of the tank does it fill in $3$ hours?", [r"$\frac{1}{3}$", r"$\frac{1}{4}$", r"$\frac{1}{6}$", r"$\frac{1}{2}$"], "2",
     r"The tap fills $\frac{1}{12}$ of the tank every hour. In $3$ hours it fills $3\times\frac{1}{12}=\frac{1}{4}$ of the tank.<br><br>The answer is therefore <b>$\frac{1}{4}$</b>.", "Easy"),
    (M, "Simple Interest", r"What is the simple interest on $\text{Rs. }1000$ at $5\%$ per annum for $2$ years?", [r"$\text{Rs. }50$", r"$\text{Rs. }100$", r"$\text{Rs. }150$", r"$\text{Rs. }200$"], "2",
     r"Simple interest is given by $SI=\frac{P\times R\times T}{100}$. Substituting the values gives $SI=\frac{1000\times5\times2}{100}=100$.<br><br>The interest earned is therefore <b>$\text{Rs. }100$</b>.", "Easy"),
    (M, "Simple Interest", r"At what rate of simple interest per annum will $\text{Rs. }800$ earn $\text{Rs. }160$ in $2$ years?", [r"$5\%$", r"$8\%$", r"$10\%$", r"$12\%$"], "3",
     r"From $SI=\frac{P\times R\times T}{100}$ we get $R=\frac{SI\times100}{P\times T}$. Substituting gives $R=\frac{160\times100}{800\times2}=10$.<br><br>The required rate is <b>$10\%$</b> per annum.", "Medium"),
    # ---- Reasoning (11-20) ------------------------------------------------------
    (R, "Number Series", r"Find the next number in the series: $2$, $4$, $8$, $16$, ?", [r"$24$", r"$30$", r"$32$", r"$64$"], "3",
     r"Each term is double the previous term. Following this rule, the term after $16$ is $16\times2=32$.<br><br>The next number is therefore <b>$32$</b>.", "Easy"),
    (R, "Number Series", r"Find the next number in the series: $3$, $6$, $11$, $18$, $27$, ?", [r"$36$", r"$38$", r"$40$", r"$42$"], "2",
     r"The differences between consecutive terms are $3$, $5$, $7$ and $9$. This is a run of consecutive odd numbers, so the next difference is $11$. Adding it to the last term gives $27+11=38$.<br><br>The next number is therefore <b>$38$</b>.", "Medium"),
    (R, "Number Series", r"Find the missing letter: A, C, E, G, ?", ["H", "I", "J", "K"], "2",
     r"The letters move forward by two places each time. After G, skipping H, the next letter is I.<br><br>The missing letter is therefore <b>I</b>.", "Easy"),
    (R, "Analogies", r"Book is to Reading as Fork is to ?", ["Eating", "Drawing", "Writing", "Cooking"], "1",
     r"A book is an object used for reading. In the same way, a fork is an object used for eating.<br><br>The correct pair is therefore <b>Eating</b>.", "Easy"),
    (R, "Analogies", r"Doctor is to Hospital as Teacher is to ?", ["School", "Student", "Pen", "Library"], "1",
     r"A doctor works in a hospital. Similarly, a teacher works in a school.<br><br>The correct answer is therefore <b>School</b>.", "Easy"),
    (R, "Coding and Decoding", r"If CAT is coded as DBU, how is DOG coded?", ["EPH", "EOH", "FPH", "DPH"], "1",
     r"Each letter in CAT is shifted one place forward: $C\rightarrow D$, $A\rightarrow B$, $T\rightarrow U$. Applying the same rule to DOG gives $D\rightarrow E$, $O\rightarrow P$, $G\rightarrow H$.<br><br>The code for DOG is therefore <b>EPH</b>.", "Medium"),
    (R, "Coding and Decoding", r"In a certain code, $A=1$, $B=2$, $C=3$ and so on. What is the sum of the values of the letters in the word BAD?", [r"$6$", r"$7$", r"$8$", r"$9$"], "2",
     r"The values are $B=2$, $A=1$ and $D=4$. Adding them gives $2+1+4=7$.<br><br>The required sum is therefore <b>$7$</b>.", "Easy"),
    (R, "Syllogism", r"Statements:<br>All pens are books.<br>All books are tables.<br><br>Conclusion: All pens are tables.<br><br>Which of the following is correct?", ["Definitely true", "Definitely false", "Cannot be determined", "Only some pens are tables"], "1",
     r"Pens are a subset of books, and books are a subset of tables. Therefore every pen must also belong to the set of tables.<br><br>The conclusion is <b>definitely true</b>.", "Medium"),
    (R, "Syllogism", r"Statements:<br>Some cats are dogs.<br>All dogs are animals.<br><br>Conclusion: Some cats are animals.<br><br>Which of the following is correct?", ["Definitely true", "Definitely false", "Cannot be determined", "No cat is an animal"], "1",
     r"Some cats are dogs, and every dog is an animal. So those cats that are dogs are also animals.<br><br>The conclusion is therefore <b>definitely true</b>.", "Medium"),
    (R, "Number Series", r"Find the next number in the series: $1$, $4$, $9$, $16$, ?", [r"$20$", r"$24$", r"$25$", r"$36$"], "3",
     r"The terms are the squares of consecutive natural numbers: $1^2$, $2^2$, $3^2$, $4^2$. The next term is $5^2=25$.<br><br>The answer is therefore <b>$25$</b>.", "Easy"),
    # ---- General Knowledge (21-30) -----------------------------------------------
    (G, "Geography", "Which is the largest continent by area?", ["Africa", "Asia", "Europe", "North America"], "2",
     "Asia covers about 44.6 million square kilometres. This makes it the largest continent by area, well ahead of Africa.<br><br>The correct answer is therefore <b>Asia</b>.", "Easy"),
    (G, "Geography", "Which is the largest ocean on Earth?", ["Atlantic Ocean", "Indian Ocean", "Arctic Ocean", "Pacific Ocean"], "4",
     "The Pacific Ocean covers more area than all of Earth's land combined. It is larger than the Atlantic, Indian and Arctic Oceans.<br><br>The correct answer is therefore the <b>Pacific Ocean</b>.", "Easy"),
    (G, "Geography", "Which line of latitude divides the Earth into the Northern and Southern Hemispheres?", ["Tropic of Cancer", "Equator", "Tropic of Capricorn", "Prime Meridian"], "2",
     "The Equator is the line at 0 degrees latitude. It lies midway between the poles and splits the Earth into two hemispheres.<br><br>The correct answer is therefore <b>the Equator</b>.", "Easy"),
    (G, "History", "In which year did World War II end?", ["1943", "1945", "1947", "1950"], "2",
     "The war in Europe ended in May 1945 and the war in Asia ended in September 1945. Hence the war as a whole ended in 1945.<br><br>The correct answer is therefore <b>1945</b>.", "Easy"),
    (G, "History", "Who was the first President of the United States?", ["Thomas Jefferson", "George Washington", "Abraham Lincoln", "John Adams"], "2",
     "George Washington took office in 1789 after the Constitution was ratified. He served two terms before stepping down in 1797.<br><br>The correct answer is therefore <b>George Washington</b>.", "Easy"),
    (G, "General Science", "What is the chemical formula of water?", [r"$CO_2$", r"$H_2O$", r"$O_2$", r"$NaCl$"], "2",
     r"A water molecule contains two hydrogen atoms and one oxygen atom. This is written as $H_2O$.<br><br>The correct answer is therefore <b>$H_2O$</b>.", "Easy"),
    (G, "General Science", "Which gas do plants absorb from the atmosphere for photosynthesis?", ["Oxygen", "Nitrogen", "Carbon dioxide", "Hydrogen"], "3",
     "Plants take in carbon dioxide through small pores called stomata. They combine it with water, using sunlight, to make glucose.<br><br>The correct answer is therefore <b>carbon dioxide</b>.", "Easy"),
    (G, "General Science", "What is the SI unit of force?", ["Joule", "Watt", "Newton", "Pascal"], "3",
     "Force is measured in newtons in the SI system. One newton is the force needed to accelerate a mass of 1 kilogram by 1 metre per second squared.<br><br>The correct answer is therefore <b>Newton</b>.", "Medium"),
    (G, "Computers", "What does CPU stand for?", ["Central Processing Unit", "Computer Personal Unit", "Central Program Utility", "Core Processing Utility"], "1",
     "The CPU is the component that executes program instructions. Its full form is Central Processing Unit.<br><br>The correct answer is therefore <b>Central Processing Unit</b>.", "Easy"),
    (G, "Computers", "Which of the following is an operating system?", ["Linux", "Python", "Excel", "HTTP"], "1",
     "An operating system manages hardware and runs other software. Linux is a widely used example of one.<br><br>The others are a programming language, a spreadsheet program and a network protocol, so the correct answer is <b>Linux</b>.", "Medium"),
]


def clean_rows() -> list[Row]:
    """A valid 30-question paper for configs/demo_exam.yaml."""
    rows = []
    for no, (sec, sub, q, opts, ans, expl, diff) in enumerate(_RAW, start=1):
        rows.append(Row(no=no, section=sec, sub_section=sub, question=q, options=list(opts),
                        correct_answer=ans, explanation=expl, difficulty=diff))
    return rows


def clean_text() -> str:
    return "\n".join(r.to_pipe_line() for r in clean_rows()) + "\n"


def broken_text() -> str:
    """The same paper with one planted defect per rule (see tests/test_sample.py)."""
    rows = {r.no: r for r in clean_rows()}

    rows[2].question = r"A price rises from $20<br>0$ to $250$. What is the percentage increase?"   # KATEX_BR
    rows[3].sub_section = "Percentge"                                                           # SUBSECTION_UNKNOWN (typo)
    rows[4].sub_section = "Geography"                                                           # SECTION_MISMATCH
    rows[6].options[0] = "A) " + rows[6].options[0]                                             # OPTION_PREFIX
    rows[8].options[2] = rows[8].options[0]                                                     # OPTION_DUPLICATE
    rows[9].correct_answer = "5"                                                                # ANSWER_INVALID
    rows[12].question = rows[12].question.replace("$3$", "$ 3$")                                # KATEX_SPACE
    rows[14].explanation = "The answer is the first option. Option 1 is correct because a fork is used for eating.<br><br>Hence it is Eating."  # EXPL_OPTION_REF
    rows[20].question = rows[20].question.replace("$9$", "$9")                                  # KATEX_UNBALANCED
    rows[25].no = 24                                                                            # NUMBER_DUPLICATE (+ missing 25)
    rows[28].explanation = "Force is measured in newtons."                                      # EXPL_SENTENCES (warning)
    rows[30].question = "{{Image}} " + rows[30].question                                        # IMAGE_PLACEHOLDER (warning)

    lines = [r.to_pipe_line() for r in rows.values()]
    # Row 16 loses its last column: PARSE_COLUMNS (and that number then goes missing).
    lines[15] = lines[15].rsplit(" | ", 1)[0]
    return "\n".join(lines) + "\n"
