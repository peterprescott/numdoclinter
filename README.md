# numdoclinter

Inspired by [`numdoclint`](https://github.com/simon-ritchie/numdoclint),
but wanting to try a slightly different approach...

Specifically, instead of trying to parse signatures and docstrings using
regex, `numdoclinter` uses the abstract syntax tree built into Python's
standard library `ast` package.

Basically, all we do is:

1. recurse through folders to parse modules and list functions,
2. parse function signatures and type annotations,
3. parse function docstrings,
4. check that the signature and docstring are consistent and contain
   everything required.

You can clone this repo and then `pip install` it, and then you can run
`numdoclinter` (or just `ndlinter`) from your command line on whatever
folder you like.

```
git clone https://github.com/peterprescott/numdoclinter
cd numdoclinter
pip install .
ndlinter --help
```
