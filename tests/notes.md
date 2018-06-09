# notes for unittest of ExpandCombinations class
* and any surrounding utilities

If cwd is the tests folder inside of the expand folder, pylint test_expand.py complains:
```
E: 15, 0: Unable to import 'expand_combinations' (import-error)
```
The error does not occur if the cwd is one level up and use pylint tests/test_expand.py
```
It appears that env.py handles the *actual* needed path to the code under test, but pylint is not seeing that.  Running test_expand.py from either location works.

The error also goes away when (empty) file __init__.py exists in the tests folder.
