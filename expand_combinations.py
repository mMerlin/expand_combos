#!bin/python
# coding=utf-8

'''
Generate combination 'merge' data from input nested dictionaries and lists
'''

# !/usr/bin/python3
# for virtualenv
#   !bin/python
# using virtualenv
#   source bin/activate  # . b/a «tab»
# coverage run expand_combinations.py
# coverage report -m
# coverage run tests/test_expand.py
# coverage report -m

# if passed a dictionary, keep string or number values as is, processing any list
# (and tuple?) values as combination variations
# if passed a list, yield one (str, number) element at a time. processing any list
# (or tuple?) value as another layer of combinations
# ??reserve?? tuple in ?both? cases for command tags
#  ie. take value from ancestor value (explicit named cascade inherit)


# Base design: Pass a dictionary object with member elements that have either simple or list
# values.  Generate (and yield) a new dictionary for each combination of values in the lists.
# A dictionary element that has a list value, will set that key to each list value in
# in the output dictionary (multiple output entries).  A dictionary in a list will be
# processed recursively, and the resulting dictionary(s) will be merged (cascaded)
# into the parent of the list.
# * possible use of tuple keys and values for special processing control
# * a dict key with generated dict values will be removed from the combination
#   (before merging the child dictionary).
class ExpandCombinations(object):
    '''generate sequences of dictionaries with unique data combinations from
    nested dictionaries and lists'''

    def __init__(self, root: object):
        if not ExpandCombinations.nestable_object(root):
            raise TypeError('{} root object not handled by ExpandCombinations'.format(type(root)))
        self._state = {}
        self._nested = []
        self._state['static'] = {}  # content that passes through unprocessed

        self._context = root
        if isinstance(self._context, dict):
            set_iterable = self._context.items()
            # defines order that keys are added as child elements
            self._state['mode'] = 'dict'  # maintain the source keys
        else:
            set_iterable = enumerate(self._context)
            self._state['mode'] = 'list'  # maintain the source sequence
        # IDEA other processing when tuple?  tuple invalid as root?

        for idx, element in set_iterable:
            if ExpandCombinations.nestable_object(element):
                self._populate_nested(idx, element)
            else:
                self._state['static'][idx] = element
        self._state['more_iterations'] = True
        self._state['list_idx'] = 0  # only used for list processing
        # self._state['iter_idx'] = 0  # nested elements that need to be expanded/cascaded
        self._nst_idx = 0  # nested elements that need to be expanded/cascaded
        if self._is_list():
            # iteration covers all list elements, not just the nested cases
            self._bottom_idx = len(self._context) - 1
        else:
            # iterate over only the nested elements
            self._bottom_idx = len(self._nested) - 1
        self._intermediate = [None for layer_number in range(len(self._nested) + 1)]
        self._intermediate[0] = dict(self._state['static'])
    # end def __init__()

    def _populate_nested(self, pos_key, value):
        '''fill in information needed to process a single nested element'''
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
    # end def _populate_nested()

    def _is_list(self):
        '''returns true when the input to the instance is a list'''
        return self._state['mode'] == 'list'

    def simple_list(self):
        '''returns true when no special handling is needed to iterate self._context'''
        # standard iterator breaks when _context is a dictionary: only get keys
        return not self._nested and self._is_list()

    def process_mode(self):
        '''returns the internal processing mode'''
        return self._state['mode']

    @staticmethod
    def nestable_object(obj: object):
        '''check if an object looks like it can be processed by this class'''
        # tuple and str are iterable, but not useful as top level objects
        return not isinstance(obj, (str, tuple)) and \
            (hasattr(obj, '__iter__') or hasattr(obj, '__getitem__'))

    def __iter__(self):
        '''return the iterator object to be accessed by (an external) for loop'''
        # not called when only using next(), which is what is done for the recursive
        # processing done by this class for the nested nodes.  Only gets here when
        # for … in processing is used by an external caller.  Never interally.
        if self.simple_list():
            # use standard iterator when nothing special needs handling
            return iter(self._context)
        # need the full nested/recursive processing this class provides
        return self

    def _next_list_entry(self):
        '''return the next entry for the current list'''
        while True:
            if self._state['list_idx'] in self._state['static']:
                if self._state['list_idx'] >= self._bottom_idx:
                    # This is the final item in the list, so stop at start of next pass
                    self._state['more_iterations'] = False
                static_entry = self._state['static'][self._state['list_idx']]
                self._state['list_idx'] += 1  # increment saved index BEFORE returning entry
                return static_entry
            try:
                # called iter should have handled any needed «deep» copy
                return next(self._nested[self._nst_idx]['iter'])
            except StopIteration as dummy_exc:  # no more «variant» values for list_idx entry
                self._nst_idx += 1  # setup to process next nested element, if exists
                if self._state['list_idx'] >= self._bottom_idx:
                    raise  # done last list entry, so stop right here, right now
            self._state['list_idx'] += 1  # process next list entry, next pass (of while)
        # end while True
    # end def _next_list_entry()

    def __next__(self):
        '''return the next combination from the root data set'''
        if not self._state['more_iterations']:
            raise StopIteration()

        if not self._nested:
            self._state['more_iterations'] = False
            return self._intermediate[0]  # copy cone when created
            # return a **COPY** of the calculated combination
            # return dict(self._intermediate[0])  # only a dictionary should get to here

        if self._is_list():
            return self._next_list_entry()

        # when merging nested content, maintain original sequence «where squence makes any sense»
        while True:  # keep going, until have complete combination to return
            next_nest_idx = self._nst_idx + 1
            try:
                element_value = next(self._nested[self._nst_idx]['iter'])
                # Fresh copy of current partial expanded combination
                self._intermediate[next_nest_idx] = self._intermediate[self._nst_idx].copy()
                if isinstance(element_value, dict):
                    # merge (casade) element_value into existing dictionary
                    self._intermediate[next_nest_idx].update(element_value)
                else:
                    # set the existing entry to the calculated value
                    self._intermediate[next_nest_idx][
                        self._nested[self._nst_idx]['position']] = element_value

                if self._nst_idx == self._bottom_idx:  # yo-yo spin in place
                    # already created a unique working copy so **SHOULD** be
                    # safe to return directly (without another (deep) copy)
                    return self._intermediate[next_nest_idx]
                self._nst_idx += 1  # yo-yo down on non-final element_value for combination
            except StopIteration as dummy_exc:
                # no more values for the current (self._nst_idx) iterator
                if self._nst_idx <= 0:  # nothing more in the TOP (0) layer/list
                    raise  # all done
                # reset the iterator on the current (just emptied) layer (depth)
                if self._nested[self._nst_idx]['simple']:
                    self._nested[self._nst_idx]['iter'] = iter(
                        self._nested[self._nst_idx]['combo'])
                else:
                    self._nested[self._nst_idx]['iter'] = ExpandCombinations(
                        self._nested[self._nst_idx]['combo'])
                self._nst_idx -= 1  # yo-yo up after handling (non terminal) exception
    # end def __next__()
# end class ExpandCombinations()


# Standalone module execution
if __name__ == "__main__":
    print('see "samples.py" for code to exercise the class')
