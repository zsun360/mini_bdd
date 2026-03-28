
# mini_bdd readme.md

## description

Developed a lightweight, Behave-inspired BDD framework using Python's higher-order functions and decorators. It utilizes textX to parse Gherkin (*.feature) files and includes core functionalities for step definition matching, code execution, and result reporting.

## directory structure

mini_bdd/
├─ requirements.txt
├─ gherkin.tx
├─ parser.py
├─ registry.py
├─ runner.py
├─ report.py
├─ main.py
├─ demo_steps.py
└─ demo.feature

## install command

1. python -m venv .venv
2. # Windows
   .venv\Scripts\activate.bat
3. pip install -r requirements.txt
4. python main.py demo.feature demo_steps

## run bdd

behave

## behave's report style

1 feature passed, 0 failed, 0 skipped
5 scenarios passed, 0 failed, 0 skipped
15 steps passed, 0 failed, 0 skipped
Took 0min 0.006s
