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
