'''
This module includes various linter checks for the docstring.
'''

def no_docstring(func):
    return not bool(func.docstring)

def no_description_in_docstring(func):
    return not bool(func.docinfo.description)

def signature_params_not_all_in_docstring(func):
    pass

def docstring_params_not_all_in_signature(func):
    pass

def not_all_docstring_params_have_desc(func):
    pass

def params_docstring_order_different(func):
    pass

def defaults_not_in_docstring(func):
    pass

def return_missing_from_docstring(func):
    pass

def return_missing_from_signature(func):
    pass

def type_hints_missing_from_signature(func):
    pass

def docstring_type_hints_incorrect_or_missing(func):
    pass


class Linter:

    def __init__(self, func):

        self.func = func
        self.tests = [
                 no_docstring,
                 no_description_in_docstring,
                 signature_params_not_all_in_docstring,
                 docstring_params_not_all_in_signature,
                 not_all_docstring_params_have_desc,
                 params_docstring_order_different,
                 defaults_not_in_docstring,
                 return_missing_from_docstring,
                 return_missing_from_signature,
                 type_hints_missing_from_signature,
                 docstring_type_hints_incorrect_or_missing
                ]
        self.problems = [t.__name__ for t in self.tests
                if not t(self.func)]
