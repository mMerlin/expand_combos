#!bin/python
# coding=utf-8

'''
Generate 'merge' data from input nested dictionaries and lists
'''
# Generate xml data for families of related Fritzing parts

# !/usr/bin/python3
# for virtualenv
#   !bin/python
# using virtualenv
#   source bin/activate  # . b/a «tab»
# coverage run expand_combinations.py
# coverage report -m
# coverage run tests/test_expand.py
# coverage report -m

# https://www.hackerearth.com/practice/python/iterators-and-generators/iterators-and-generators-1/tutorial/
# https://anandology.com/python-practice-book/iterators.html
#  python 2


# if passed a dictionary, keep string or number values as is, processing any list (and tuple?)
# values as combinations
# if passed a list, yield one (str, number) element at a time. processing any list (or tuple?)
# value as another layer of combinations
# ??can a list hold a nested dict element?
#  yield simple element or dict
#  post process yielded element to handle insert (@index) or (key) merge/cascade
# ??reserve?? tuple in ?both? cases for command tags
#  ie. take value from ancestor value (explicit named cascade inherit)

# Base design: Pass a dictionary object with string keys and string or list values.
# Generate (and yield) a new dictionary for each combination of values in the lists.
# a list with string elements will set the value for the associated key in the
# output dictionary.  A dictionary in a list will be processed recursively, and the
# resulting dictionary will be merged (cascaded) into the parent of the list.
# * possible use of tuple keys and values for special processing control
# * a dict key with generated dict values will be removed from the combination
#   (before merging the child dictionary).
# ** this class could seriously use some unit test code
class ExpandCombinations(object):
    '''generate sequences of dictionaries with data combinations from nested
    dictionaries and lists'''
    # https://python-3-patterns-idioms-test.readthedocs.io/en/latest/Singleton.html
    # only one instance of a class variable
    # __serial_number = None  # Trace
    __serial_number = 0  # Trace

    def __init__(self, root: object):
        if not ExpandCombinations.nestable_object(root):
            raise TypeError('{} root object not handled by ExpandCombinations'.format(type(root)))
        self._state = {}
        self._nested = []
        self._state['static'] = {}  # content that passes through unprocessed
        # Trace setup a unique id for each created instance, to help track recursion
        # if ExpandCombinations.__serial_number is None:  # Trace
        #     ExpandCombinations.__serial_number = 0  # Trace
        # ExpandCombinations.__serial_number += 1  # Trace
        self._state['id'] = ExpandCombinations.__serial_number  # Trace
        ExpandCombinations.__serial_number += 1  # Trace
        # print('«{}»ExpandCombinations instance __init__: {} elements in {}'.format(
        #     self._state['id'], len(root), type(root)))  # Trace

        self._context = root
        if isinstance(self._context, dict):
            set_iterable = self._context.items()
            # defines order that keys are added as child elements
            self._state['mode'] = 'dict'  # maintain the source keys
        else:
            set_iterable = enumerate(self._context)
            self._state['mode'] = 'list'  # maintain the source sequence
        # other when tuple?  invalid as root?
        # print('«{}»mode {}; set iterable {}'.format(
        #     self._state['id'], self._state['mode'], type(set_iterable)))  # DEBUG

        for idx, element in set_iterable:
            # print('«{}»ele idx {!r}, val {!r}'.format(self._state['id'], idx, element))  # DEBUG
            if ExpandCombinations.nestable_object(element):
                # print('«{}»sub {!r}; {}'.format(
                #     self._state['id'], idx, type(element)))  # DEBUG
                self._populate_nested(idx, element)
            else:
                self._state['static'][idx] = element
        # print('«{}»{} nested child elements {}'.format(
        #     self._state['id'], len(self._nested), self._nested))  # DEBUG
        self._more_iterations = True
        self._state['list_idx'] = 0  # only used for list processing
        self._state['iter_idx'] = 0
        if self._is_list():
            # iteration covers all list elements, not just the nested cases
            self._state['bottom_idx'] = len(self._context) - 1
        else:
            self._state['bottom_idx'] = len(self._nested) - 1
        self._intermediate = [None for layer_number in range(len(self._nested) + 1)]
        self._intermediate[0] = dict(self._state['static'])
    # end def __init__()

    def _populate_nested(self, pos_key, value):
        '''fill in information needed to process a single nested element'''
        # print('«{}»populate nested@{} with (pos)key {!r}={!r}'.format(
        #     self._state['id'], len(self._nested), pos_key, value))  # Trace
        chld = {}  # Nested child element information
        chld['position'] = pos_key
        # Create ExpandCombinations instance for each nested combination entry.
        # Need to keep the source nested elements around, to be able to recreate the
        # iterators later: while doing the yo-yo processing to generate combinations
        chld['combo'] = value
        child_iter = ExpandCombinations(chld['combo'])
        chld['simple'] = child_iter.simple_list()
        chld['mode'] = child_iter.process_mode()
        if chld['simple']:  # no special processing needed, so use standard iter function
            chld['iter'] = iter(chld['combo'])  # keep context info, but throw out child_iter
        else:  # need to use the extended processing provided by the local class
            chld['iter'] = child_iter
        self._nested.append(chld)  # add child information to nested list
        # print('«{}»nested child {} keys {}'.format(
        #     self._state['id'], len(self._nested) - 1, chld.keys()))  # DEBUG
        # print('«{}»nested child pos {!r}; mode {!r}; simple {}'.format(
        #     self._state['id'], chld['position'], chld['mode'], chld['simple']))  # DEBUG
    # end def _populate_nested()

    def _is_list(self):
        '''returns true when the instance is a list'''
        return self._state['mode'] == 'list'

    def simple_list(self):
        '''returns true when no special handling is needed to iterate self._context'''
        # standard iterator breaks when _context is a dictionary: only get keys
        return not self._nested and self._is_list()

    def process_mode(self):
        '''returns the internal processing mode'''
        # print('«{}»ExpandCombinations process_mode: {!r}'.format(
        #     self._state['id'], self._state['mode']))  # Trace
        return self._state['mode']

    @staticmethod
    def nestable_object(obj: object):
        '''check if an object looks like it can be processed by this class'''
        # tuple and str are iterable, but not useful as top level objects
        return not isinstance(obj, (str, tuple)) and \
            (hasattr(obj, '__iter__') or hasattr(obj, '__getitem__'))

    def __iter__(self):
        '''return the iterator object to be accessed by the for loop'''
        # not called when only using next(), which is what is done for the recursive
        # processing done by this class for the nested nodes.  Only gets here when
        # for … in processing is used by an external caller.  Never interally.
        # print('«{}»ExpandCombinations __iter__ for {} of {} elements'.format(
        #     self._state['id'], type(self._context), len(self._context)))  # Trace
        if self.simple_list():
            # use standard iterator when nothing special needs handling
            return iter(self._context)
        # need the full nested/recursive processing this class provides
        return self

    def _next_list_entry(self):
        '''return the next entry for the current list'''
        while True:
            if self._state['list_idx'] in self._state['static']:
                if self._state['list_idx'] >= self._state['bottom_idx']:
                    # This is the final item in the list, so stop at start of next pass
                    self._more_iterations = False
                static_entry = self._state['static'][self._state['list_idx']]
                self._state['list_idx'] += 1  # increment saved index BEFORE returning entry
                return static_entry
            # self._state['list_idx'] not in self._state['static']; process next nested
            try:
                pick = next(self._nested[self._state['iter_idx']]['iter'])
                return pick  # called iter should have handled any needed «deep» copy
            except StopIteration as dummy_exc:  # no more «variant» values for list_idx entry
                self._state['iter_idx'] += 1  # setup to process next nested element, if exists
            if self._state['list_idx'] >= self._state['bottom_idx']:
                # print('«{}»stopping due to list empty'.format(self._state['id']))  # DEBUG
                raise StopIteration()  # done last list entry, so stop right here, right now
            self._state['list_idx'] += 1  # process next list entry, next pass (of while)
        # end while True
    # end def _next_list_entry()

    # def _next_list_entry_trace(self):
    #     '''return the next entry for the current list'''
    #     trc_fmt = '«{}»ExpandCombinations _next_list_entry: index(list,iter) ({}, {})' \
    #         ' len(list,nest) ({}, {})'  # Trace
    #     print(trc_fmt.format(
    #         self._state['id'], self._state['list_idx'], self._state['iter_idx'],
    #         len(self._state['static']), len(self._nested)))  # Trace
    #     while True:
    #         print('«{}»top _next_list_entry while True: (list,iter) ({}, {})'.format(
    #             self._state['id'], self._state['list_idx'], self._state['iter_idx']))  # Trace
    #         if self._state['list_idx'] in self._state['static']:
    #             if self._state['list_idx'] >= self._state['bottom_idx']:
    #                 # This is the final item in the list, so stop at start of next pass
    #                 self._more_iterations = False
    #             dbg_fmt = '«{}»have static list entry {!r} with {!r}, more={}'  # DEBUG
    #             print(dbg_fmt.format(  # better be string¦number
    #                 self._state['id'], self._state['list_idx'],
    #                 type(self._state['static'][self._state['list_idx']]),
    #                 self._more_iterations))  # DEBUG
    #             static_entry = self._state['static'][self._state['list_idx']]
    #             self._state['list_idx'] += 1  # increment BEFORE returning entry
    #             return static_entry
    #         # self._state['list_idx'] not in self._state['static']; process next nested
    #         print('«{}»list try for nested idx {!r}'.format(
    #             self._state['id'], self._state['iter_idx']))  # Trace
    #         try:
    #             pick = next(self._nested[self._state['iter_idx']]['iter'])
    #             print('«{}»list pick {!r} using idx {!r}'.format(
    #                 self._state['id'], pick, self._state['iter_idx']))  # DEBUG
    #             return pick  # called iter should have handled any needed «deep» copy
    #         except StopIteration as dummy_exc:  # no more «variant» values for list_idx entry
    #             self._state['iter_idx'] += 1  # setup to process next nested element, if exists
    #             # processing a list, an iterator/generator never needs to be reset
    #         if self._state['list_idx'] >= self._state['bottom_idx']:
    #             print('«{}»stopping due to list empty'.format(self._state['id']))  # DEBUG
    #             raise StopIteration()  # done last list entry, so stop right now
    #         self._state['list_idx'] += 1  # process next list entry, next pass (of while)
    #     # end while True
    # # end def _next_list_entry()

    def __next__(self):
        '''return the next combination from the root data set'''
        # dbg_fmt = '«{}»ExpandCombinations __next__; mode {!r}; index(list,iter) ({}, {}); more {}'
        # print(dbg_fmt.format(self._state['id'], self._state['mode'], self._state['list_idx'],
        #                      self._state['iter_idx'], self._more_iterations))  # Trace
        if not self._more_iterations:
            # print('«{}»stopping due to no more iterations'.format(self._state['id']))  # DEBUG
            raise StopIteration()

        if not self._nested:
            self._more_iterations = False
            # print('«{}»not nested return for {} {}'.format(
            #     self._state['id'], type(self._intermediate[0]), type(self._context)))  # DEBUG
            # return a **COPY** of the calculated combination
            return dict(self._intermediate[0])  # only a dictionary should get to here

        if self._is_list():
            return self._next_list_entry()

        it_idx = self._state['iter_idx']
        pos = self._nested[it_idx]['position']
        # print('«{}»__next__: before while True with intermediates {}'.format(
        #     self._state['id'], self._intermediate))  # DEBUG
        # print('«{}»positions: {}'.format(
        #     self._state['id'], [chld['position'] for chld in self._nested]))  # DEBUG
        # when merging nested content, maintain original sequence «where squence makes any sense»
        while True:  # ref: def custom_iter
            # print('«{}»top __next__ while True: iter {}; pos {!r}; bottom {}'.format(
            #     self._state['id'], it_idx, pos, self._state['bottom_idx']))  # Trace
            # if type(self._nested[it_idx]['iter']) != type(iter([])):  # DEBUG trace
            #     print('{}'.format(type(self._nested[it_idx]['iter'])))  # DEBUG
            #     print('{}'.format(self._nested[it_idx]['iter']))  # DEBUG
            try:
                pick = next(self._nested[it_idx]['iter'])
                # print('«{}»dict pick {!r} {!r} for pos {!r} using idx {!r}'.format(
                #     self._state['id'], pick, type(pick), pos, it_idx))  # DEBUG
                self._intermediate[it_idx + 1] = self._intermediate[it_idx].copy()
                if isinstance(pick, dict):
                    # print('«{}»merge dict base\n{}; cascade with\n{}'.format(
                    #     self._state['id'], self._intermediate[it_idx + 1], pick))  # DEBUG
                    # del self._intermediate[it_idx + 1][pos]
                    # print('«{}»updated base\n{}'.format(
                    #     self._state['id'], self._intermediate[it_idx + 1]))  # DEBUG
                    self._intermediate[it_idx + 1].update(pick)
                else:
                    self._intermediate[it_idx + 1][pos] = pick
                # print('«{}»intermediate with pick content\n{}'.format(
                #     self._state['id'], self._intermediate[it_idx + 1]))  # DEBUG

                if it_idx == self._state['bottom_idx']:  # yo-yo spin in place
                    self._state['iter_idx'] = it_idx  # save (no change) for next call
                    # print('«{}»ready to send combo'.format(self._state['id']))  # DEBUG
                    # print('«{}»One raw combo: {}'.format(
                    #     self._state['id'], self._intermediate[it_idx+1]))  # DEBUG
                    # Use a «deep» copy of the combination to send: prevent unintended
                    # linkages between generated combinations.  Simple clone **should**
                    # work, since the result should be flat, with simple values
                    # Process already created a unique working copy so **SHOULD** be ok
                    # return dict(self._intermediate[it_idx + 1])
                    return self._intermediate[it_idx + 1]
                # print('«{}»yo-yo down'.format(self._state['id']))  # DEBUG
                it_idx += 1  # yo-yo down on non-final pick
                pos = self._nested[it_idx]['position']
            except StopIteration as dummy_exc:
                # no more values for the current (it_idx) iterator
                if it_idx <= 0:  # nothing more in the TOP (0) layer/list
                    raise  # all done
                # reset the iterator on the current (just emptied) layer (depth)
                if self._nested[it_idx]['simple']:
                    # print('«{}»use base iter'.format(self._state['id']))  # DEBUG
                    self._nested[it_idx]['iter'] = iter(self._nested[it_idx]['combo'])
                else:
                    # print('«{}»use this instance'.format(self._state['id']))  # DEBUG
                    self._nested[it_idx]['iter'] = ExpandCombinations(self._nested[it_idx]['combo'])
                # print('«{}»yo-yo up'.format(self._state['id']))  # DEBUG
                it_idx -= 1  # yo-yo up after handling (non terminal) exception
                pos = self._nested[it_idx]['position']
    # end def __next__()
# end class ExpandCombinations()


def mymain():
    '''wrapper for test/start code so that variables do not look like constants'''
    smpl_keys = ['sub1', 'sub2', 'sub3', ]

    samples = {
        'sub1': {
            'family': 'bjt',
            'footprint': '',
            'package': ['TO220', {
                'footprint': ['SIL', 'triangle'],
                'package': 'TO92',
                }, 'SOT23'],
        },
        'sub2': {
            'footprint': '',
            'mounting': 'THT',
            'package': [
                {
                    'package': 'TO92',
                    'footprint': ['SIL', 'triangle'],
                }, {
                    'package': 'SOT23',
                    'mounting': 'SMD',
                },
                'TO220', ],
            'label': ['pin', ''],
            'type': ['NPN', 'PNP'],
            'pinout': ['BCE', 'BEC', 'CBE', 'CEB', 'EBC', 'ECB'],
        },
        'sub3': {
            'footprint': '',
            'mounting': 'THT',
            'package': ['TO220', {
                'package': 'TO92',
                'footprint': ['SIL', 'triangle'],
                }, {
                    'package': 'SOT23',
                    'mounting': 'SMD',
                }, ],
            'label': ['pin', ''],
            'type': ['NPN', 'PNP'],
            'pinout': ['BCE', 'BEC', 'CBE', 'CEB', 'EBC', 'ECB'],
        },
    }

    for smpl in smpl_keys:
        bjt_data = samples[smpl]
        print(bjt_data)  # DEBUG
        test_iter = ExpandCombinations(bjt_data)
        print('{} before iterate'.format(smpl))
        test_rslt = []
        for cmb in test_iter:
            test_rslt.append(cmb)
            print('live result case: {}'.format(cmb))
        print('{} final content ='.format(smpl))
        for cmb in test_rslt:
            print(cmb)
        print('{} combinations'.format(len(test_rslt)), end='\n\n')


# Standalone module execution
if __name__ == "__main__":
    mymain()
