# numdoclinter

Inspired by [`numdoclint`](https://github.com/simon-ritchie/numdoclint), but wanting to try a slightly different approach...

Basically, we need to:

1. recurse through folders to parse modules and list functions,
2. parse function signatures and type annotations,
3. parse function docstrings,
4. check that the signature and docstring are consistent and contain everything required.
