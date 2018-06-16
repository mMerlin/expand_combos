#!bin/python
# coding=utf-8

"""
Application description docstring
"""

# !/usr/bin/python3
# for virtualenv
# !bin/python
# using virtualenv
#   source bin/activate

# standard library imports
import sys

# local application/library specific imports
from expand_combinations import ExpandCombinations


def mymain(*supplied_keys):
    '''wrapper for test/start code so that variables do not look like constants'''
    smpl_keys = supplied_keys
    samples = {
        's1': {'key1': 'constant value', 'key2': ['option 1', 'option 2', ], },
        's2': {'key1': 'constant value', 'key2': ['option 1', 'option 2', ],
               'key3': ['option 3', 'option 4', ], },
        's3': {'key1': 'default value', 'key2': [
            'option 1',
            {'key3': 'fixed value', 'key4': ['option 2', 'option 3'], },
            {'key1': 'override', 'key2': 'keep key'}, ], },
        'list1': ['first', 'second', 'third', ],
        'list2': ['dup', 'dup', 'third', ],
        'l1': ['a', ['b', 'c'], 'd', ],
        'l2': [
            'a',
            {'k1': [1, 2, ], 'k2': 'c'},
            {'k3': ['a', 'b', ], 'k4': 5}, ],
        'dup1': {
            'cmn': 'always',
            'hasdup': ['dup', 'dup', 'other'],
        },
        'equiv1': {'key': 'value', },
        'equiv2': {'key': ['value', ], },
        'equiv3': {'key': [{'key': 'value', }, ], },
        'equiv4': {'key': [{'key': [{'key': 'value', }, ], }, ], },
        'equiv5': {'other': [{'key': 'value'}, ], },
        'equiv6': {'key': [{'other': [{'key': 'value', }, ], }, ], },
        'equiv7': {'other1': [{'other2': [{'key': 'value', }, ], }, ], },
        'sub1': {
            'family': 'bjt',
            'footprint': '',
            'package': ['TO220', {
                'footprint': ['SIL', 'triangle', ],
                'package': 'TO92',
                }, 'SOT23', ],
        },
        'sub2': {
            'footprint': '',
            'mounting': 'THT',
            'package': [
                {
                    'package': 'TO92',
                    'footprint': ['SIL', 'triangle', ],
                }, {
                    'package': 'SOT23',
                    'mounting': 'SMD',
                },
                'TO220', ],
            'label': ['pin', '', ],
            'type': ['NPN', 'PNP', ],
            'pinout': ['BCE', 'BEC', 'CBE', 'CEB', 'EBC', 'ECB', ],
        },
        'sub3': {
            'footprint': '',
            'mounting': 'THT',
            'package': ['TO220', {
                'package': 'TO92',
                'footprint': ['SIL', 'triangle', ],
                }, {
                    'package': 'SOT23',
                    'mounting': 'SMD',
                }, ],
            'label': ['pin', '', ],
            'type': ['NPN', 'PNP', ],
            'pinout': ['BCE', 'BEC', 'CBE', 'CEB', 'EBC', 'ECB', ],
        },
        'meals': {
            'appetizer': ['calamari', 'potatoe skins', 'cheesy nachos', 'escargot', ],
            'entrée': [
                'chicken',
                {'entrée': ['white fish', 'rainbow trout'], 'wine': 'white'},
                {'entrée': 'steak', 'wine': 'red'}, ],
            'desert': ['pie', 'tiramisu', 'ice cream', 'apple crisp', ],
        },
    }
    cheeses = ['cheddar', 'goat', 'feta', 'parmesan']
    vegetables = ['avocado', 'mushrooms', 'onions', 'spinach']
    meats = ['bacon', 'beef', 'pepperoni']
    seafood = ['shrimp', 'anchovies', 'prawns']
    samples['pizza'] = [
        {'first': [cheeses, vegetables, meats, seafood, ], },
        {
            'first': [cheeses, vegetables, meats, seafood, ],
            'second': [cheeses, vegetables, meats, seafood, ],
        },
        {
            'first': [cheeses, vegetables, meats, seafood, ],
            'second': [cheeses, vegetables, meats, seafood, ],
            'third': [cheeses, vegetables, meats, seafood, ],
        },
    ]
    # print(samples['pizza'])  # DEBUG
    samples['pizza2'] = {
        'toppings': (cheeses, meats)
    }
    # print(samples['pizza2'])  # DEBUG

    if len(sys.argv) > 1:
        smpl_keys = sys.argv[1:]

    pizza_keys = ['first', 'second', 'third']
    for smpl in smpl_keys:
        if smpl not in samples:
            print('sample {!r} does not exist'.format(smpl))
            continue
        print('\nsample {} input data:'.format(smpl))
        print(samples[smpl])
        test_iter = ExpandCombinations(samples[smpl])
        dedup = []  # only used for pizza
        print('sample {} expanded outputs:'.format(smpl))
        expansion_count = 0
        for cmb in test_iter:
            expansion_count += 1
            print(cmb)
            # pizza is special.  Get the unique topping Combinations
            if smpl == 'pizza':
                cmb_toppings = []
                for pkey in pizza_keys:
                    if pkey in cmb:
                        cmb_toppings.append(cmb[pkey])
                cmb_toppings.sort()
                if cmb_toppings not in dedup:
                    dedup.append(cmb_toppings)
        print('{} expanded combinations'.format(expansion_count))
        if smpl == 'pizza':
            for cmb in dedup:
                print(cmb)
            print('{} unique pizza topping combinations'.format(len(dedup)))


# Specify the sample(s) to show on the command line, or hard-code string value
# arguments.  Any command line arguments override the hard-coded strings
# mymain()
# mymain('dup1')
mymain('sub1', 'sub2', 'sub3')
