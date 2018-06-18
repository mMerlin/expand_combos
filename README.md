# Expand Combinations

A python3 class to generate all valid combinations from a (relatively) simple description based on nested lists and dictionaries.

Design limitations and features.  While dictionaries and lists are processed recursively, a list that is an element of a tuple will not be processed.  Any tuple is treated as a single 'simple' element.  The contents are never examined.

## Example expansions

It is fairly easy to create sample inputs and the corresponding expected outputs.  A lot easier than creating a good generic description of the processing rules.

Input dictionary s1
```python
{'key1': 'constant value', 'key2': ['option 1', 'option 2']}
```
should generate (yield) 2 outputs:
```python
{'key1': 'constant value', 'key2': 'option 1'}
{'key1': 'constant value', 'key2': 'option 2'}
```
Input dictionary key1 has a simple (not dictionary or list) value.  That is simply passed through unmodified to each of the expanded output solutions.  key2 is a list, so each output sets key2 to a different value from the list.

Input Dictionary s2
```python
{'key1': 'constant value', 'key2': ['option 1', 'option 2'], 'key3': ['option 3', 'option 4']}
```
should generate (yield) 4 outputs:
```python
{'key1': 'constant value', 'key2': 'option 1', 'key3': 'option 3'}
{'key1': 'constant value', 'key2': 'option 1', 'key3': 'option 4'}
{'key1': 'constant value', 'key2': 'option 2', 'key3': 'option 3'}
{'key1': 'constant value', 'key2': 'option 2', 'key3': 'option 4'}
```
key3 is another list, so for each expanded key2 value, each value of key3 is also expanded to each possible value.

Any or all list elements could be another dictionary.  At the point where that list element would be assigned as the value for the parent dictionary key, the dictionary is expanded (recursively).  Each of the expanded combinations for that dictionary (each of which will be a dictionary), will be merged into the the parent dictionary.

Input Dictionary s3
```python
{'key1': 'default value', 'key2': [
  'option 1',
  {'key3': 'fixed value', 'key4': ['option 2', 'option 3']},
  {'key1': 'override', 'key2': 'keep key'}]}
```
should generate (yield) 4 outputs:
```python
{'key1': 'default value', 'key2': 'option 1'}
{'key1': 'default value', 'key3': 'fixed value', 'key4': 'option 2'}
{'key1': 'default value', 'key3': 'fixed value', 'key4': 'option 3'}
{'key1': 'override', 'key2': 'keep key'}
```
The first case is the same as an element with a simple list.  key2 is set to the first element (which is a simple string) of the input list.  In the second and third expansions, there is no key2.  The expansion of the nested dictionary "{'key3': 'fixed value', 'key4': ['option 2', 'option 3']}]}" does not include a key2.  The final solution modifies (overrides, or cascades) the initial value of key1 with the value returned by the "{'key1': 'override', 'key2': 'keep key'}" expansion (which is a single dictionary).

Here is a sample that might be easier to wrap your head around.  Although anyone with a real interest in food will cringe at the data used.  Show all the possible combinations of meals by picking an appetizer, entrée, and desert.  To make it a little more interesting, a couple of the entrées add a wine, and one has sub entries.
Input Dictionary meals
```python
{
  'appetizer': ['calamari', 'potatoe skins', 'cheesy nachos', 'escargot', ],
  'entrée': [
    'chicken',
    {'entrée': ['white fish', 'rainbow trout'], 'wine': 'white'},
    {'entrée': 'steak', 'wine': 'red'}, ],
  'desert': ['pie', 'tiramisu', 'ice cream', 'apple crisp', ],
},
```
Not listing them all here, but `python3 samples.py meals` shows the 64 meal combinations that describes.

Or how about building random pizzas?
```python
cheeses = ['cheddar', 'goat', 'feta', 'parmesan']
vegetables = ['avocado', 'mushrooms', 'onions', 'spinach']
meats = ['bacon', 'beef', 'pepperoni']
seafood = ['shrimp', 'anchovies', 'prawns']
[
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
```
That simple looking description generates 2954 pizzas.  However, they are not all unique.  The same ingredients can picked for different toppings (first, second, third), in different orders.  There is no difference between shrimp, feta, and feta, shrimp.  Duplicated ingredients are valid unique combinations.  Double cheese, or double shrimp are fine.  To get the 679 unique topping combinations is not difficult, but it does mean storing the previous combinations, instead of being able to simply iterate and process directly.

```python
pizza_keys = ['first', 'second', 'third']
dedup = []
for cmb in ExpandCombinations(input_dict):
  cmb_toppings = []
  for pkey in pizza_keys:
    if pkey in cmb:
      cmb_toppings.append(cmb[pkey])
  cmb_toppings.sort()
  if cmb_toppings not in dedup:
    dedup.append(cmb_toppings)
for cmb in dedup:
  print(cmb)
print('{} unique pizza topping combinations'.format(len(dedup)))
```
`python3 samples.py pizza` shows both the raw and unique combinations and counts.

## A somewhat more formal description of expansion

* The expansion of anything other than a list or a dictionary is the source item itself
* The expansion of a list is the «set¦sequence» of expansions of the elements in the list
* The expansion of a dictionary is a «set¦sequence» of dictionaries containing the cascaded (merge) of the expansion of the elements in the (input) dictionary. [«¹»](#fn1)
* The expansion of a dictionary element (key, value pair) is a dictionary.
  * The expansion of a dictionary element with a value that is an empty list, is an empty dictionary.
  * The value of the element is expanded
  * If an instance of the expansion is NOT a dictionary, the source element expansion instance is a dictionary with a single element: the key of the source element, with a value of the expansion instance.
  * If an instance of the expansion is a dictionary, the source element expansion instance is that dictionary.  The source element key is not used.
  * All elements with values that expand to themselves (everything except lists and dictionary) are collected first.  That reduces the processing of those elements to a single dictionary with those key value pairs.  That combined dictionary is then the base for merges from the expansion cases. [«²»](#fn2)
* The (css style) cascade is implemented as a dictionary merge, of child dictionaries into (copies of) the parent dictionary.  Copies are needed to prevent 'bleed' from one expansion instance to the next. [«³»](#fn3)
* The expansion of each successive element of a dictionary is cascaded into each expansion instance for the previous key.  That can be represented as an expanding 'tree'.  A more condensed form, is to represent it as a 'network', where the multiple expansions of an element all connect to the expansion of the next element.  When all possible paths through the (directed) network are followed, the result is the same as the path from the root to each leaf of the tree representation.

### graphs

A list creates a sibling (not child) node for each element

list expansion.
```text
list: —┬— «node1»
       ├— «node2»
       ├— «node3»
       └— «node…»
```
Each node is the expansion of one element of the list.

dictionary expansion.
```text
dictionary: — «node1» —— «node2» —— «node3» —— «node…»
```
Each node is the expansion of one element (key:value pair) of the dictionary.

dictionary element expansion: the value (from key:value pair) is expanded.

When the value expansion instance is NOT a dictionary:</br>
element expansion.
```python
{element_key: «expansion instance»}
```

When the value expansion instance IS a dictionary:</br>
element expansion.
```text
«expansion instance»
```

expanded intermediate dictionary node with list as value
```text
         ┌— «node2.1» —┐
         ├— «node2.2» —┤
«node1» —┼— «node2.3» —┼—«node3»
         ├— «node2.4» —┤
         └— «node2.5» —┘
```

Every path through the graph, from leaf to the (null) root, generates a separate result.  That result is the (CSS style) cascade of the expanded values of the nodes traversed.

### equivalent inputs

```python
{'key': 'value', }
{'key': ['value', ], }
{'key': [{'key': 'value', }, ], }
```
* NOTE: the only difference between the static value, and the list with a single static value, is that the standalone static value will be collected first, instead of being processed in key order.

Due to the recursive nature of the processing, it should be clear that the following input also produces the same result.
```python
{'key': [{'key': [{'key': 'value', }, ], }, ], }
```

What may not be so obvious, is that so do these.
```python
{'other': [{'key': 'value'}, ], }
{'key': [{'other': [{'key': 'value', }, ], }, ], }
{'other1': [{'other2': [{'key': 'value', }, ], }, ], }
```

Samples equiv1 through equiv7 demonstrate those cases, each of which creates a single output of
```python
{'key': 'value'}
```

### Expansion Detail Footnotes
<a name="fn1">«¹»</a> Standard python dictionary element processing order is undefined.  That means that the cascade can have expansion instances of one element overriding the elements of expansion instanced of a different element.  When that is possible, use collections.OrderedDict instead of a standard dict, and specify the key order as needed to get the desired results.

<a name="fn2">«²»</a> Handling the non-expanding dictionary elements first is important.  The way the cascade works, these become the default values that expansion instances can override.  If these were not handled first, they could override cascaded values from the expansion instances instead.  An unlikely intended outcome.

<a name="fn3">«³»</a> The cascade is (effectively) implemented as a recursive  `parent_dictionary.copy().update(child_node_expansion_instance)`, starting from each leaf (as child node), back to the root.
