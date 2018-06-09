"""
Add parent directory to the path, to allow importing modules to test
"""

# ref: https://stackoverflow.com/questions/61151/where-do-the-python-unit-tests-go#answer-23386287

import sys
import os

# append module root directory to sys.path
sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)
