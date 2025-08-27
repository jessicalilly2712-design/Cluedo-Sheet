# Cluedo Sheet

A tiny command-line helper for tracking clues during a game of Cluedo.

## Setup

```bash
python3 -m venv venv
. venv/bin/activate
pip install -r requirements.txt
```

## Usage

Run the helper interactively:

```bash
python cluedo_sheet.py
```

You will be asked for:

* number of players and their initials (in turn order)
* the initials you use
* cards that are in your hand

After setup you can show the current sheet or enter player turns. The sheet will
update with every turn using basic deduction.

A small demo can be run without interaction:

```bash
python cluedo_sheet.py --demo
```
