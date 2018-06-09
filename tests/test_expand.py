#!/usr/bin/python3
# coding=utf-8

"""
test the ExpandCombinations recursive combination iteration class
"""

# !/usr/bin/python3
# for virtualenv
#   !bin/python
# using virtualenv
#   source bin/activate  # . b/a «tab»
# coverage run tests/test_expand.py
# coverage report -m

# test_expand.py -b

import unittest
import copy
from collections import OrderedDict as odict
# https://docs.python.org/3/library/collections.html#collections.OrderedDict
# pylint: disable=unused-import
import env  # append parent directory to import path
# pylint: enable=unused-import
# needs both 'env' above, and __init__.py to exist, to import and keep pylint happy
from expand_combinations import ExpandCombinations
# pylint: disable=fixme
# TODO handle todo cases, and remove above fixme message suppression
# pylint: disable=protected-access


# ~/development/workspace/python/fragments/permute.py
def permutations(src_list: list) -> list:
    '''Generate all possible permutations of elements in a list'''
    for idx in range(len(src_list)):
        wrk_list = src_list.copy()
        perm_list = [wrk_list.pop(idx)]
        if wrk_list:
            for sub_perm in permutations(wrk_list):
                yield perm_list + sub_perm
        else:
            yield perm_list


def multiple_key_permutations(allref: list) -> list:
    '''use next method to step each dictionary key permuation independently'''
    # @param allref list of dictionaries
    # @returns list of lists of key str
    d_iterators = [iter(permutations(list(ref.keys()))) for ref in allref]
    bottom_idx = len(d_iterators) - 1
    key_sequence = list(range(len(d_iterators)))  # placeholders
    iter_idx = 0  # start at the 'top' (first) element
    while True:
        try:
            key_sequence[iter_idx] = next(d_iterators[iter_idx])
            if iter_idx == bottom_idx:
                yield key_sequence
                continue  # skip increment when at the bottom (last) element
            # go down(forward) one entry on success for the current entry
            iter_idx += 1  # yo-yo down (forward) one entry after success on next
        except StopIteration as dummy_exc:
            # no more values for the current (iter_idx) iterator
            if iter_idx <= 0:  # nothing more for the top (first) element
                break  # all done
            # reset the iterator on the current (just emptied) element
            d_iterators[iter_idx] = iter(permutations(list(allref[iter_idx].keys())))
            iter_idx -= 1  # yo-yo up, backtracking to higher (previous) element


class TestAllowedNestable(unittest.TestCase):
    '''Directly test nestable_object static method'''
    @classmethod
    def setUpClass(cls):
        # create test dictionaries (that should be accepted)
        cls.test_dicts = [
            {},  # empty dictionary
            {'this': 'that'},  # populated with simple values
            {'some': (0, 1, 'tuple')},  # populated with compound
            {('name1', 0, 'test'): 'value'},  # dictionary with tuple key
            {
                5: 'test',
                10: [0, 3, 'test2'],
                'key1': 4.5,
                'key2': 'another string',
                'key3': [0, ['test', 5], {'nkey1': 'nvalue1'}, ],
                'key4': {'nkey2': 'nvalue2', (0, 1): ['nvalue3', '']},
                ('x', 'y'): 'tuple key value',
            },  # multiple entries with different key, value types
            {
                'key5': [0, 3, 10]
            },
            odict(),  # Ordered Dictionary should be treat as regular dict
            odict([('key5', [0, 3, 10])]),
        ]
        # create test lists (that should be accepted)
        cls.test_lists = [
            [],  # empty list
            [3, None, 'me to', 5.7],  # simple values in list
            [[], [None], {}, [{}], {'key': ['value', 'test']}, ],  # complex/compound values
        ]
        # create test cases that should not be accepted
        cls.test_bad = [
            3,
            'test',
            None,
            (0, 1),  # tuple
            True,
            3.1416,
            object,  # class
            TestAllowedNestable,  # class
            TestAllowedNestable.setUpClass,  # function reference
        ]

    # @classmethod
    # def tearDownClass(cls):
    #     pass

    # @unittest.skip('reduce clutter testing with ordered dictionary')
    def test_accepts_dict(self):
        '''should approve using any dictionary'''
        # The function does not, is not intended to, do a full parse.  It is just
        # an initial smoke test to use before starting.
        for case in self.test_dicts:
            with self.subTest(msg=repr(case)):
                self.assertTrue(
                    ExpandCombinations.nestable_object(case),
                    '{} dict should be accepted'.format(type(case)))

    # @unittest.skip('reduce clutter testing with ordered dictionary')
    def test_accepts_list(self):
        '''should approve using any list'''
        # The function does not, is not intended to do, a full parse.  It is just
        # an initial smoke test to use before starting.
        for case in self.test_lists:
            with self.subTest(msg=repr(case)):
                self.assertTrue(
                    ExpandCombinations.nestable_object(case),
                    '{} list should be accepted'.format(type(case)))

    # @unittest.skip('reduce clutter testing with ordered dictionary')
    def test_rejects_other(self):
        '''should reject anything else'''
        for case in self.test_bad:
            with self.subTest(msg=repr(case)):
                self.assertFalse(
                    ExpandCombinations.nestable_object(case),
                    '{!r} argument should be rejected'.format(type(case)))


class TestIteratorCreation(unittest.TestCase):
    '''test creation of combination iterators for various input cases'''
    @classmethod
    def setUpClass(cls):
        input_keys = {
            'empty_dict': [],
            'flat_dict': ['key1', 5, ('flag', 'here'), 'more', ],
            'flat_odict': ['key1', 5, ('flag', 'here'), 'more', ],
            'd_singl_l': ['varkey0'],
            'd_mix_fl': ['fix1', 'varkey1', ],
            'd_mix_2fl': ['fix2', 'fix3', 'varkey2', ],
            'd_mix_f2l': ['fix4', 'varkey3', 'varkey4', ],
            'd_nest_2fl': ['fix5', 'fix6', 'varkey5', ],
            'd_nest_2fl1a': ['fix6', ],
            'd_nest_2fl1b': ['fix7', 'varkey6'],
            'd_progressive_0': ['footprint', 'mounting', 'package'],
            'd_progressive_1.0': ['package', 'footprint'],
            'd_progressive_2.1': ['package', 'mounting'],
            'd_progressive_4': 'label',  # hpd keys
        }
        input_values = {
            'empty_dict': [],
            'flat_dict': ['value1', False, 'tuple val', None],
            'flat_odict': ['value1', False, 'tuple val', None],
            'var0_vals': ['var0', 'var1', 'var2', ],
            'var1_vals': ['only1', 'in1', 'one1', ],
            'var2_vals': ['only2', 'in2', 'one2', ],
            'var3_vals': ['only3', 'in3', 'one3', ],
            'var4_vals': ['only4', 'in4', 'one4', ],
            'fix1_val': 'in all output1',
            'fix2_val': 'in all2',
            'fix3_val': 'output3',
            'fix4_val': 'in all4',
            'fix5_val': 'common',
            'fix6_val': '',
            'fix6_val1a': 'fix6.1a',
            'fix7_val1b': 'fix7.1b',
            'var5_vals1a': 'val5.1a',
            'var6_vals': ['val6.0', 'val6.1', ],
            'd_progressive_0': ['', 'THT', 'one only'],
            'd_progressive_1.0': ['TO92', ['SIL', 'triangle', ], ],
            'd_progressive_2.1': ['SOT23', 'SMD', ],
            'd_progressive_3.2': 'TO220',
            'd_progressive_4': ['pin', '', ],  # hpd values
        }
        cls.input_case = {
            'bad_string0': '',
            'bad_string`': 'just a string',
            'bad_bool0': True,
            'bad_bool1': False,
            'bad_int0': 0,
            'bad_int1': 10,
            'bad_int2': -999,
            'bad_tuple0': (),
            'bad_tuple1': (['list', 'here'], 23, ),
            'bad_float0': 0e0,
            'bad_float1': 5e-20,
            'bad_float2': -5e20,
            'empty_list': [],
            'flat_strs': ['one', 'two', 'three', ],
            'one_nest': [['four', 'five'], ],
            'two_nest': [[['four', 'five']]],
            'l_mix_f_n': [9, ['six', None], ],
            'l_mix_n_f': [['seven', ('tuple', 'ele')], 10, ],
            'l_mix_n_n': [['zero', 100], [99, False]],
            'l_mix_f_n_n': ['fix', [True, None], ['', 43], ],
            'l_mix_n_f_n': [[True, None], 'fix2', ['', 43], ],
            'l_mix_n_n_f': [[True, None], ['', 43], 'fix3', ],
            'empty_dict': {},
            'flat_dict': dict([
                (input_keys['flat_dict'][0], input_values['flat_dict'][0]),
                (input_keys['flat_dict'][1], input_values['flat_dict'][1]),
                (input_keys['flat_dict'][2], input_values['flat_dict'][2]),
                (input_keys['flat_dict'][3], input_values['flat_dict'][3]),
            ]),
            'flat_odict': odict([
                (input_keys['flat_odict'][0], input_values['flat_odict'][0]),
                (input_keys['flat_odict'][1], input_values['flat_odict'][1]),
                (input_keys['flat_odict'][2], input_values['flat_odict'][2]),
                (input_keys['flat_odict'][3], input_values['flat_odict'][3]),
            ]),
            'd_singl_l': {
                input_keys['d_singl_l'][0]: input_values['var0_vals'],
            },
            'd_mix_fl': {  # flat + list element values
                input_keys['d_mix_fl'][0]: input_values['fix1_val'],
                input_keys['d_mix_fl'][1]: input_values['var1_vals'],
            },
            'd_mix_2fl': {  # 2 flat + 1 list element values
                input_keys['d_mix_2fl'][0]: input_values['fix2_val'],
                input_keys['d_mix_2fl'][1]: input_values['fix3_val'],
                input_keys['d_mix_2fl'][2]: input_values['var2_vals'],
            },
            'd_mix_f2l': {
                input_keys['d_mix_f2l'][0]: input_values['fix4_val'],
                input_keys['d_mix_f2l'][1]: input_values['var3_vals'],
                input_keys['d_mix_f2l'][2]: input_values['var4_vals'],
            },
            'd_nest_2fl': odict([
                (input_keys['d_nest_2fl'][0], input_values['fix5_val']),
                (input_keys['d_nest_2fl'][1], input_values['fix6_val']),
                (input_keys['d_nest_2fl'][2], [
                    input_values['var5_vals1a'],
                    odict([
                        (input_keys['d_nest_2fl1a'][0], input_values['fix6_val1a']),
                    ]),
                    odict([
                        (input_keys['d_nest_2fl1b'][0], input_values['fix7_val1b']),
                        (input_keys['d_nest_2fl1b'][1], input_values['var6_vals']),
                    ]),
                ]),
            ]),
            'd_progressive_0': odict([
                (input_keys['d_progressive_0'][0], input_values['d_progressive_0'][0]),
                (input_keys['d_progressive_0'][1], input_values['d_progressive_0'][1]),
                (input_keys['d_progressive_0'][2], input_values['d_progressive_0'][2]),
            ]),
        }
        cls.input_case['d_progressive_1'] = copy.deepcopy(cls.input_case['d_progressive_0'])
        cls.input_case['d_progressive_1'][input_keys['d_progressive_0'][2]] = [odict([
            (input_keys['d_progressive_1.0'][0], input_values['d_progressive_1.0'][0]),
            (input_keys['d_progressive_1.0'][1], input_values['d_progressive_1.0'][1]),
        ])]
        cls.input_case['d_progressive_2'] = copy.deepcopy(cls.input_case['d_progressive_1'])
        # print('\nclone 2 {}'.format(cls.input_case['d_progressive_2']))
        # print('pkg 2 {}'.format(
        #     cls.input_case['d_progressive_2'][input_keys['d_progressive_0'][2]]))
        # print('typ p {}'.format(
        #     type(cls.input_case['d_progressive_2'][input_keys['d_progressive_0'][2]])))
        cls.input_case['d_progressive_2'][input_keys['d_progressive_0'][2]].append(odict([
            (input_keys['d_progressive_2.1'][0], input_values['d_progressive_2.1'][0]),
            (input_keys['d_progressive_2.1'][1], input_values['d_progressive_2.1'][1]),
        ]))
        cls.input_case['d_progressive_3'] = copy.deepcopy(cls.input_case['d_progressive_2'])
        cls.input_case['d_progressive_3'][input_keys['d_progressive_0'][2]].append(
            input_values['d_progressive_3.2']
        )
        cls.input_case['d_progressive_4'] = copy.deepcopy(cls.input_case['d_progressive_3'])
        cls.input_case['d_progressive_4'][input_keys['d_progressive_4']] = \
            input_values['d_progressive_4']  # hpd input

        cls.expected_out = {
            'one_nest': ['four', 'five'],
            'two_nest': ['four', 'five'],  # same as one_nest case
            'l_mix_f_n': [9, 'six', None],
            'l_mix_n_f': ['seven', ('tuple', 'ele'), 10],
            'l_mix_n_n': ['zero', 100, 99, False],
            'l_mix_f_n_n': ['fix', True, None, '', 43],
            'l_mix_n_f_n': [True, None, 'fix2', '', 43],
            'l_mix_n_n_f': [True, None, '', 43, 'fix3'],
            'empty_dict': [{}],
            'flat_dict': [{
                input_keys['flat_dict'][0]: input_values['flat_dict'][0],
                input_keys['flat_dict'][1]: input_values['flat_dict'][1],
                input_keys['flat_dict'][2]: input_values['flat_dict'][2],
                input_keys['flat_dict'][3]: input_values['flat_dict'][3],
            }],
            'flat_odict': [{  # same as flat_dict (not ordered dictionary)
                input_keys['flat_odict'][0]: input_values['flat_odict'][0],
                input_keys['flat_odict'][1]: input_values['flat_odict'][1],
                input_keys['flat_odict'][2]: input_values['flat_odict'][2],
                input_keys['flat_odict'][3]: input_values['flat_odict'][3],
            }],
            'd_singl_l': [
                {input_keys['d_singl_l'][0]: input_values['var0_vals'][0]},
                {input_keys['d_singl_l'][0]: input_values['var0_vals'][1]},
                {input_keys['d_singl_l'][0]: input_values['var0_vals'][2]},
            ],
            'd_mix_fl': [  # one flat and one list input element
                {
                    input_keys['d_mix_fl'][0]: input_values['fix1_val'],
                    input_keys['d_mix_fl'][1]: input_values['var1_vals'][0],
                },
                {
                    input_keys['d_mix_fl'][0]: input_values['fix1_val'],
                    input_keys['d_mix_fl'][1]: input_values['var1_vals'][1],
                },
                {
                    input_keys['d_mix_fl'][0]: input_values['fix1_val'],
                    input_keys['d_mix_fl'][1]: input_values['var1_vals'][2],
                },
            ],
            'd_mix_2fl': [  # 2 flat and one list input elements
                {
                    input_keys['d_mix_2fl'][0]: input_values['fix2_val'],
                    input_keys['d_mix_2fl'][1]: input_values['fix3_val'],
                    input_keys['d_mix_2fl'][2]: input_values['var2_vals'][0],
                },
                {
                    input_keys['d_mix_2fl'][0]: input_values['fix2_val'],
                    input_keys['d_mix_2fl'][1]: input_values['fix3_val'],
                    input_keys['d_mix_2fl'][2]: input_values['var2_vals'][1],
                },
                {
                    input_keys['d_mix_2fl'][0]: input_values['fix2_val'],
                    input_keys['d_mix_2fl'][1]: input_values['fix3_val'],
                    input_keys['d_mix_2fl'][2]: input_values['var2_vals'][2],
                },
            ],
            'd_mix_f2l': [  # 1 flat and two list input elements
                {
                    input_keys['d_mix_f2l'][0]: input_values['fix4_val'],
                    input_keys['d_mix_f2l'][1]: input_values['var3_vals'][0],
                    input_keys['d_mix_f2l'][2]: input_values['var4_vals'][0],
                },
                {
                    input_keys['d_mix_f2l'][0]: input_values['fix4_val'],
                    input_keys['d_mix_f2l'][1]: input_values['var3_vals'][0],
                    input_keys['d_mix_f2l'][2]: input_values['var4_vals'][1],
                },
                {
                    input_keys['d_mix_f2l'][0]: input_values['fix4_val'],
                    input_keys['d_mix_f2l'][1]: input_values['var3_vals'][0],
                    input_keys['d_mix_f2l'][2]: input_values['var4_vals'][2],
                },
                {
                    input_keys['d_mix_f2l'][0]: input_values['fix4_val'],
                    input_keys['d_mix_f2l'][1]: input_values['var3_vals'][1],
                    input_keys['d_mix_f2l'][2]: input_values['var4_vals'][0],
                },
                {
                    input_keys['d_mix_f2l'][0]: input_values['fix4_val'],
                    input_keys['d_mix_f2l'][1]: input_values['var3_vals'][1],
                    input_keys['d_mix_f2l'][2]: input_values['var4_vals'][1],
                },
                {
                    input_keys['d_mix_f2l'][0]: input_values['fix4_val'],
                    input_keys['d_mix_f2l'][1]: input_values['var3_vals'][1],
                    input_keys['d_mix_f2l'][2]: input_values['var4_vals'][2],
                },
                {
                    input_keys['d_mix_f2l'][0]: input_values['fix4_val'],
                    input_keys['d_mix_f2l'][1]: input_values['var3_vals'][2],
                    input_keys['d_mix_f2l'][2]: input_values['var4_vals'][0],
                },
                {
                    input_keys['d_mix_f2l'][0]: input_values['fix4_val'],
                    input_keys['d_mix_f2l'][1]: input_values['var3_vals'][2],
                    input_keys['d_mix_f2l'][2]: input_values['var4_vals'][1],
                },
                {
                    input_keys['d_mix_f2l'][0]: input_values['fix4_val'],
                    input_keys['d_mix_f2l'][1]: input_values['var3_vals'][2],
                    input_keys['d_mix_f2l'][2]: input_values['var4_vals'][2],
                },
            ],
            'd_nest_2fl': [
                {
                    input_keys['d_nest_2fl'][0]: input_values['fix5_val'],
                    input_keys['d_nest_2fl'][1]: input_values['fix6_val'],
                    input_keys['d_nest_2fl'][2]: input_values['var5_vals1a'],
                }, {
                    input_keys['d_nest_2fl'][0]: input_values['fix5_val'],
                    input_keys['d_nest_2fl1a'][0]: input_values['fix6_val1a'],
                }, {
                    input_keys['d_nest_2fl'][0]: input_values['fix5_val'],
                    input_keys['d_nest_2fl'][1]: input_values['fix6_val'],
                    input_keys['d_nest_2fl1b'][0]: input_values['fix7_val1b'],
                    input_keys['d_nest_2fl1b'][1]: input_values['var6_vals'][0],
                }, {
                    input_keys['d_nest_2fl'][0]: input_values['fix5_val'],
                    input_keys['d_nest_2fl'][1]: input_values['fix6_val'],
                    input_keys['d_nest_2fl1b'][0]: input_values['fix7_val1b'],
                    input_keys['d_nest_2fl1b'][1]: input_values['var6_vals'][1],
                },
            ],
            'd_progressive_0': [
                {
                    input_keys['d_progressive_0'][0]: input_values['d_progressive_0'][0],
                    input_keys['d_progressive_0'][1]: input_values['d_progressive_0'][1],
                    input_keys['d_progressive_0'][2]: input_values['d_progressive_0'][2],
                },
            ],
            'd_progressive_1': [
                {
                    input_keys['d_progressive_0'][0]: input_values['d_progressive_1.0'][1][0],
                    input_keys['d_progressive_0'][1]: input_values['d_progressive_0'][1],
                    input_keys['d_progressive_0'][2]: input_values['d_progressive_1.0'][0],
                }, {
                    input_keys['d_progressive_0'][0]: input_values['d_progressive_1.0'][1][1],
                    input_keys['d_progressive_0'][1]: input_values['d_progressive_0'][1],
                    input_keys['d_progressive_0'][2]: input_values['d_progressive_1.0'][0],
                },
            ],
        }
        cls.expected_out['d_progressive_2'] = copy.deepcopy(cls.expected_out['d_progressive_1'])
        cls.expected_out['d_progressive_2'].append({
            input_keys['d_progressive_0'][0]: input_values['d_progressive_0'][0],
            input_keys['d_progressive_0'][1]: input_values['d_progressive_2.1'][1],
            input_keys['d_progressive_0'][2]: input_values['d_progressive_2.1'][0],
        })
        cls.expected_out['d_progressive_3'] = copy.deepcopy(cls.expected_out['d_progressive_2'])
        cls.expected_out['d_progressive_3'].append({
            input_keys['d_progressive_0'][0]: input_values['d_progressive_0'][0],
            input_keys['d_progressive_0'][1]: input_values['d_progressive_0'][1],
            input_keys['d_progressive_0'][2]: input_values['d_progressive_3.2'],
        })
        cls.expected_out['d_progressive_4'] = []  # hpd expected
        for solution in cls.expected_out['d_progressive_3']:
            for val in input_values['d_progressive_4']:
                a_sol = copy.deepcopy(solution)
                a_sol[input_keys['d_progressive_4']] = val
                cls.expected_out['d_progressive_4'].append(a_sol)

        # print('\nkeys 0   {}'.format(input_keys['d_progressive_0']))  # DEBUG
        # print('keys 1.0 {}'.format(input_keys['d_progressive_1.0']))  # DEBUG
        # print('vals 0   {}'.format(input_values['d_progressive_0']))  # DEBUG
        # print('vals 1.0 {}'.format(input_values['d_progressive_1.0']))  # DEBUG
        # print('test 1   {}'.format(cls.input_case['d_progressive_1']))  # DEBUG
        # print('expect 1 {}'.format(cls.expected_out['d_progressive_1']))  # DEBUG

        # test_case = cls.input_case['d_progressive_1']
        # test_keys = list(test_case.keys())
        # print('\nkeys 1   {}'.format(test_keys))  # DEBUG
        # test_0_keys = list(test_case[test_keys[2]][0].keys())
        # print('keys 1.0 {}'.format(test_0_keys))  # DEBUG
        # print('vals 0   {}'.format(list(cls.input_case['d_progressive_0'].values())))  # DEBUG
        # print('vals 1.0 {}'.format(list(test_case[test_keys[2]][0].values())))

        # print('\nkeys 2.1 {}'.format(input_keys['d_progressive_2.1']))  # DEBUG
        # print('vals 2.1 {}'.format(input_values['d_progressive_2.1']))  # DEBUG
        # test_case = cls.input_case['d_progressive_2']
        # test_keys = list(test_case.keys())
        # print('\nkeys 2   {}'.format(test_keys))  # DEBUG
        # test_0_keys = list(test_case[test_keys[2]][0].keys())
        # print('keys 2.0 {}'.format(test_0_keys))  # DEBUG
        # test_1_keys = list(test_case[test_keys[2]][1].keys())
        # print('keys 2.1 {}'.format(test_1_keys))  # DEBUG
        # print('vals 2.0 {}'.format(list(test_case[test_keys[2]][0].values())))
        # print('vals 2.1 {}'.format(list(test_case[test_keys[2]][1].values())))

        # print('\ntest 1   {}'.format(cls.input_case['d_progressive_1']))  # DEBUG
        # for idx, solution in enumerate(cls.expected_out['d_progressive_1']):
        #     print('expected 1[{}] {}'.format(idx, solution))
        #
        # print('\ntest 2   {}'.format(cls.input_case['d_progressive_2']))  # DEBUG
        # for idx, solution in enumerate(cls.expected_out['d_progressive_2']):
        #     print('expected 2[{}] {}'.format(idx, solution))
        #
        # print('\ntest 3   {}'.format(cls.input_case['d_progressive_3']))  # DEBUG
        # for idx, solution in enumerate(cls.expected_out['d_progressive_3']):
        #     print('expected 3[{}] {}'.format(idx, solution))

        # print('\ntest 4   {}'.format(cls.input_case['d_progressive_4']))  # DEBUG
        # for idx, solution in enumerate(cls.expected_out['d_progressive_4']):
        #     print('expected 4[{}] {}'.format(idx, solution))

        # lists of (groups of) test cases
        cls.bad_cases = [
            'bad_string0',
            'bad_string`',
            'bad_bool0',
            'bad_bool1',
            'bad_int0',
            'bad_int1',
            'bad_int2',
            'bad_tuple0',
            'bad_tuple1',
            'bad_float0',
            'bad_float1',
            'bad_float2',
        ]
        cls.fl_cases = [  # flat lists
            'empty_list',
            'flat_strs',
        ]
        cls.fd_cases = [  # flat dictionaries
            'empty_dict',
            'flat_dict',
            'flat_odict',
            'd_progressive_0',
        ]
        cls.nl_cases = [  # lists with nested list elements
            'one_nest',  # single element that is another list
            'two_nest',  # single element that is another single element list
            'l_mix_f_n',  # 2 elements, second of which is a list
            'l_mix_n_f',  # 2 elements, first of which is a list
            'l_mix_n_n',  # 2 elements, each of which is a list
            'l_mix_f_n_n',  # 3 elements, 1st is simple, others are lists
            'l_mix_n_f_n',  # 3 elements, 2nd is simple, others are lists
            'l_mix_n_n_f',  # 3 elements, 3rd is simple, others are lists
        ]
        cls.vd_cases = [  # dictionaries with list variants and nested dictionaries
            'd_singl_l',
            'd_mix_fl',
            'd_mix_2fl',
            'd_mix_f2l',
            'd_nest_2fl',
            'd_progressive_0',
            'd_progressive_1',
            'd_progressive_2',
            'd_progressive_3',
            'd_progressive_4',  # hpd
        ]

    # @classmethod
    # def tearDownClass(cls):
    #     pass

    # @unittest.skip('reduce clutter testing with ordered dictionary')
    def test_rejects_many(self):
        '''check that disallowed data types really are rejected'''
        for reject_case in self.bad_cases:
            with self.subTest():
                with self.assertRaisesRegex(TypeError,
                                            '.* root object not handled by ExpandCombinations',
                                            msg='for {!r}'.format(self.input_case[reject_case])):
                    ExpandCombinations(self.input_case[reject_case])

    # @unittest.skip('reduce clutter testing with ordered dictionary')
    def test_accepts_flat_list(self):
        '''check that a flat list is valid, and uses standard iterator'''
        for exp_case in self.fl_cases:
            instance = ExpandCombinations(self.input_case[exp_case])
            # print('«{}»mode {}'.format(instance._state['id'], instance._state['mode']))  # DEBUG
            with self.subTest():
                self.assertIsInstance(
                    instance, ExpandCombinations,
                    'for {!r}'.format(self.input_case[exp_case]))
            iterator = iter(instance)
            with self.subTest():
                self.assertNotIsInstance(
                    iterator, ExpandCombinations,
                    'for {!r}, and should not be'.format(self.input_case[exp_case]))
            with self.subTest():
                self.assertIsInstance(
                    iterator, iter([]).__class__,
                    # iterator, list_iterator,  # NameError: name 'list_iterator' is not defined
                    'for {!r}'.format(self.input_case[exp_case]))

    # @unittest.skip('reduce clutter testing with ordered dictionary')
    def test_accepts_flat_dict(self):
        '''check that a flat dictionary is valid, and uses custom iterator'''
        for exp_case in self.fd_cases:
            instance = ExpandCombinations(self.input_case[exp_case])
            # print('«{}»mode {}'.format(instance._state['id'], instance._state['mode']))  # DEBUG
            with self.subTest():
                self.assertIsInstance(
                    instance, ExpandCombinations,
                    'for {!r}'.format(self.input_case[exp_case]))
            iterator = iter(instance)
            with self.subTest():
                self.assertIsInstance(
                    iterator, ExpandCombinations,
                    'for {!r}'.format(self.input_case[exp_case]))

    # @unittest.skip('reduce clutter testing with ordered dictionary')
    def test_uses_copyof_flat_list(self):
        '''check that the content of a flat list is not linked (referenced) by output'''
        for exp_case in self.fl_cases:
            in_obj = self.input_case[exp_case].copy()
            instance = ExpandCombinations(in_obj)
            captured = []
            ele_idx = 0
            for out_ele in instance:
                captured.append(out_ele)
                with self.subTest(msg=repr(self.input_case[exp_case]), ctx='iterate'):
                    # Do an on the fly check
                    self.assertEqual(self.input_case[exp_case][ele_idx], out_ele, 'src != out')
                    self.assertEqual(in_obj[ele_idx], out_ele, 'in != out')  # better be same
                    # now modify the input element, and make sure that the output did not change too
                    # in_obj[ele_idx] = '@'
                    in_obj[ele_idx] = '@'
                    self.assertNotEqual(in_obj[ele_idx], out_ele, 'mod in == out')
                    self.assertEqual(self.input_case[exp_case][ele_idx], out_ele, 'src chg != out')
                ele_idx += 1
            with self.subTest(msg=repr(self.input_case[exp_case]), ctx='post iteration'):
                self.assertEqual(self.input_case[exp_case], captured, 'expected == captured')
                if in_obj:  # only not equal when input was not an empty list
                    self.assertNotEqual(in_obj, captured, 'in != captured')

    # @unittest.skip('reduce clutter testing with ordered dictionary')
    def test_flatten_nested(self):
        '''check that nested lists are flattened on output, and not references'''
        for nest_case in self.nl_cases:
            in_obj = copy.deepcopy(self.input_case[nest_case])
            instance = ExpandCombinations(in_obj)
            captured = []
            ele_idx = 0
            for out_ele in instance:
                captured.append(out_ele)
                with self.subTest(msg=repr(self.input_case[nest_case]), ctx='for'):
                    # Do an on the fly check while iterating
                    self.assertEqual(self.expected_out[nest_case][ele_idx], out_ele)
                ele_idx += 1
            with self.subTest(msg=repr(self.input_case[nest_case]), ctx='captured'):
                self.assertEqual(self.expected_out[nest_case], captured)
                # modify all elements in the input list
                for idx in range(len(self.input_case[nest_case])):
                    in_obj[idx] = 'changed'
                # verify that the caputure ouput has not been changed
                with self.subTest(msg=repr(self.input_case[nest_case]), ctx='detect reference'):
                    self.assertEqual(self.expected_out[nest_case], captured)

    # @unittest.skip('reduce clutter testing with ordered dictionary')
    def test_uses_copy_of_flat_dict(self):
        '''check that content of a dict is copied to output without references to input'''
        for exp_case in self.fd_cases:
            src_obj = self.input_case[exp_case]  # reference to input object
            src_keys = list(src_obj.keys())
            if not src_obj:
                with self.subTest(msg=repr(src_keys), ctx='empty'):
                    # take a (fresh) copy of input case that is safe to modify
                    in_obj = odict(copy.deepcopy(src_obj))
                    instance = ExpandCombinations(in_obj)
                    captured = []
                    for out_ele in instance:
                        captured.append(out_ele)
                    self.assertEqual(1, len(captured), 'should be only single output element')
                    self.assertEqual(self.expected_out[exp_case], captured, 'exp == out list')
                    in_obj['new'] = 'break'
                    self.assertEqual(self.expected_out[exp_case], captured, 'input key added')
                continue
            for perm in permutations(src_keys):
                with self.subTest(msg=repr(perm), ctx='permutation'):
                    # take a (fresh) copy of input case that is safe to modify
                    in_obj = odict(copy.deepcopy(src_obj))
                    for key in perm:  # adjust odict keys to match permutation order
                        in_obj.move_to_end(key)
                    self.assertEqual(perm, list(in_obj.keys()), 'keys should match permutation')
                    instance = ExpandCombinations(in_obj)
                    captured = []
                    for out_ele in instance:
                        captured.append(out_ele)
                        # «single» output should be same as input for this simple case
                        self.assertEqual(src_obj, out_ele, 'src == out ele')
                        self.assertEqual(self.expected_out[exp_case][0], out_ele, 'exp == out ele')
                    self.assertEqual(1, len(captured), 'should be only single output element')
                    self.assertEqual(self.expected_out[exp_case], captured, 'exp == out list')
                    in_obj[perm[0]] = 'changed'
                    self.assertEqual(self.expected_out[exp_case], captured, 'input key changed')
                    del in_obj[perm[-1]]
                    self.assertEqual(self.expected_out[exp_case], captured, 'input key deleted')
                    in_obj['new'] = 'break'
                    self.assertEqual(self.expected_out[exp_case], captured, 'input key added')

    # def _check_dict_variants(self, in_key):
    #     '''verify that variant outputs match expected dictionaries'''
    #     in_obj = dict(self.input_case[in_key])  # take a copy that is safe to modify
    #     instance = ExpandCombinations(in_obj)
    #     ele_idx = 0
    #     captured = []
    #     for out_ele in instance:
    #         captured.append(out_ele)
    #         # do inline check
    #         self.assertEqual(self.expected_out[in_key][ele_idx], out_ele)
    #         ele_idx += 1
    #     # full post iteration check, to make sure nothing got changed one step to the next
    #     self.assertEqual(self.expected_out[in_key], captured)
    #     # make sure that (post iteration) changes to the input do not affect collected data
    #     # in_obj['varkey0'][0] = 'changed'
    #     # self.assertEqual(self.expected_out[in_key], captured)
    #     # in_obj['varkey0'].append('extra')
    #     # self.assertEqual(self.expected_out[in_key], captured)
    #     in_obj['pluskey'] = 'added'
    #     self.assertEqual(self.expected_out[in_key], captured)
    #     # IDEA check that change to captured elements do not affect other elements??

    def _unordered_list_compare(self, expected: list, actual: list) -> bool:
        '''verify that two lists have the same elements (ignoring order)'''
        matched = []
        for ele in actual:
            self.assertIn(ele, expected, 'ele not expected')
            self.assertNotIn(ele, matched, 'ele not unique')
            matched.append(ele)
        self.assertEqual(len(expected), len(matched), 'ele counts not matched')

    # @staticmethod
    # def _walk_expandable(nest_level: int, srcobj: object):  # DEBUG
    #     if isinstance(srcobj, dict):
    #         for (key, val) in srcobj.items():
    #             if isinstance(val, (dict, list)):
    #                 print('«{}»key {!r} contains {}'.format(nest_level, key, type(val)))
    #                 TestIteratorCreation._walk_expandable(nest_level + 1, val)
    #         return
    #     for idx, ele in enumerate(srcobj):
    #         if isinstance(ele, (dict, list)):
    #             print('«{}»idx {} contains {}'.format(nest_level, idx, type(ele)))
    #             TestIteratorCreation._walk_expandable(nest_level + 1, ele)

    @staticmethod
    def _get_dict_from_expandable(srcobj: object) -> dict:
        '''recursively walk dictionaries and lists, collecting references to dictionaries'''
        if isinstance(srcobj, dict):
            yield srcobj
            for (dummy_key, val) in srcobj.items():
                if isinstance(val, (dict, list)):
                    for more in TestIteratorCreation._get_dict_from_expandable(val):
                        yield more
            return
        for ele in srcobj:
            if isinstance(ele, (dict, list)):
                for more in TestIteratorCreation._get_dict_from_expandable(ele):
                    yield more

    # @unittest.skip('reduce clutter testing with ordered dictionary')
    def test_gen_variant_dict(self):
        '''check that list dictionary entries generate a variant per list element'''
        # print('start test_gen_variant_dict for {}'.format(self.vd_cases))  # DEBUG
        for exp_case in self.vd_cases:
            # print('expand test case {!r}'.format(exp_case))  # DEBUG
            expect_ele_cnt = len(self.expected_out[exp_case])
            # print('{} expected output cases'.format(expect_ele_cnt))  # DEBUG
            # for idx, exp in enumerate(self.expected_out[exp_case]):  # DEBUG
            #     print('exp[{}] == {}'.format(idx, exp))  # DEBUG
            src_obj = self.input_case[exp_case]  # reference to input object
            # self._walk_expandable(0, src_obj)  # DEBUG
            # references to the (ordered) dictionaries in the current expand test case
            # d_in_case = [d_ref for d_ref in self._get_dict_from_expandable(src_obj)]
            # print('found {} dictionaries with sizes {}'.format(
            #     len(d_in_case),
            #     [len(ref) for ref in d_in_case]))  # DEBUG
            # for perm_set in multiple_key_permutations(d_in_case):
            for perm_set in multiple_key_permutations([d_ref for d_ref in
                                                       self._get_dict_from_expandable(src_obj)]):
                # for each key permutation (all dictionaries)
                # print('«»key set = {}'.format(perm_set))
                with self.subTest(msg=repr(perm_set), ctx='permutation'):
                    # take a (fresh) copy of the input case that is safe to modify
                    in_obj = odict(copy.deepcopy(src_obj))
                    # get (matching) references to the dictionaries in the copy
                    in_ref = [ref for ref in self._get_dict_from_expandable(in_obj)]
                    for idx, ref in enumerate(in_ref):  # set key order for permutation set
                        for key in perm_set[idx]:
                            ref.move_to_end(key)
                        self.assertEqual(
                            perm_set[idx], list(ref.keys()), 'keys should match permutation')
                    instance = ExpandCombinations(in_obj)  # using adjusted key sequence
                    captured = []  # would prefer set, but dict not hashable
                    for out_ele in instance:
                        with self.subTest(msg=repr(perm_set), ctx='inline'):
                            # print('ele == {}'.format(out_ele))  # DEBUG
                            # inline check; each output element should match a unique expected case
                            with self.subTest(msg=repr(perm_set), ctx='duplicate', dup=out_ele):
                                self.assertNotIn(out_ele, captured, 'generated ele not unique')
                            captured.append(out_ele)
                            self.assertIn(
                                out_ele, self.expected_out[exp_case], 'generated ele not expected')
                    self.assertEqual(expect_ele_cnt, len(captured), 'wrong output element count')
                    # full post iteration check, elements should change one step to the next
                    # print(captured)  # DEBUG
                    with self.subTest(msg=repr(perm_set), ctx='post check'):
                        self._unordered_list_compare(self.expected_out[exp_case], captured)
                        # make sure that (post iteration) input changes do not affect collected data
                        # print('source: {}'.format(in_obj))  # DEBUG
                        for idx, perm in enumerate(perm_set):
                            if isinstance(in_ref[idx][perm[0]], list):
                                in_ref[idx][perm[0]].append('extra')
                                subcase = 'input ele appended'
                            else:
                                in_ref[idx][perm[0]] = 'changed'
                                subcase = 'input ele changed'
                            with self.subTest(msg=repr(perm_set), ctx=subcase, prm=perm, idx=idx):
                                self._unordered_list_compare(self.expected_out[exp_case], captured)
                            # print('chgd: {}'.format(in_obj))  # DEBUG
                            del in_ref[idx][perm[-1]]
                            with self.subTest(msg=repr(perm_set),
                                              ctx='input key deleted', prm=perm, idx=idx):
                                self._unordered_list_compare(self.expected_out[exp_case], captured)
                            in_ref[idx]['pluskey'] = 'added'
                            with self.subTest(msg=repr(perm),
                                              ctx='input key added', prm=perm, idx=idx):
                                self._unordered_list_compare(self.expected_out[exp_case], captured)
                            # print('final: {}'.format(in_ref[idx]))  # DEBUG
            # IDEA check that change to captured elements do not affect other elements??

# py lint: disable=«warnings about accessing private members»
# class TestInternals(unittest.TestCase):
# instance.simple_list
# instance.process_mode
# instance._populate_nested
# instance._next_list_entry
# instance.__iter__
# instance.__next__

# list of valid input data cases
# list of expected output
# for idx, case in enumerate(test_inputs):
# list of «named?»tuples: input case, expected output
# for (sample, expected) in test_inputs:
#     # deep copy case «variants for dict and list?»
#     case = copy.deepcopy(sample)
#     assertTrue(case == sample)
#     new_iterator = ExpandCombinations(case)
#     test_result = []
#     out_idx = 0
#     for itr_out in new_iterator:
#         # deep compare itr_out == expected[out_idx]
#         out_idx += 1
#         test_result.append(itr_out)
#     # make sure input data not modified during processing
#     # deep compare case == sample
#     # deep compare test_result == expected
#     # make sure no reference links between input and output
#     # modify sample
#     # deep compare test_result == expected
#     # make sure no reference links between output data instances
#     # deep_test = copy.deepcopy(test_result)
#     # for mod in mod_cases:
#     #     # modify expected, test_result
#     #     # deep compare test_result == mod_expected
    # def test_correct_result_for_«case_name»
        # likely need unique code for the *modify* tests in above
        # not convenient to loop on them
        # IDEA added list of modification methods to modify input and output


if __name__ == '__main__':
    # print(__name__)  # DEBUG
    # print(__path__)  # «module reference».__path__ ?? not a module ??
    unittest.main()
