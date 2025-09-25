# theory-programming-languages

## Grammar Syntax

* Each production rule is written with the head and body separated by ```->```.
* Nonterminals are capitalized (e.g., ```E```, ```T```); terminals are not (e.g., ```id```, ```+```).
* Symbols in the body of the production are separated by spaces. For multi-character symbols, spaces are omitted (e.g.,
  ```id```).
* The choice operator ```|``` can be used to separate alternatives in the body.
* The null symbol is represented by ```^```.

## Grammar File

The grammar should be provided in a text file. Here's an example ```grammar.txt```:

```
E -> E + T
E -> T
T -> T * F | F
F -> ( E )
F -> id
```
