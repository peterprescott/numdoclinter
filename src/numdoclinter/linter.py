"""
This module includes various linter checks for the docstring.
"""

IGNORED_PARAMS = ("self", "cls", "args", "kwargs")


def no_docstring(func):
    return not bool(func.docstring)


def no_description_in_docstring(func):
    if func.docinfo:
        return not bool(func.docinfo.description)
    else:
        return False


def docstring_blank_line_missing(func):
    # TODO
    pass


def signature_params_not_same_as_docstring(func):
    if func.docinfo:
        signature_params = [
            p for p in func.args if p not in IGNORED_PARAMS
        ]
        docstring_params = [
            d["name"]
            for d in func.docinfo.params
            if d["name"] not in IGNORED_PARAMS
        ]
        return not bool(signature_params == docstring_params)
    else:
        return False


def not_all_docstring_params_have_desc(func):
    if func.docinfo:
        return not all([bool(d["desc"]) for d in func.docinfo.params])
    else:
        return False


def defaults_not_in_docstring(func):
    # TODO:
    # will require parsing defaults from signature ast
    # and from docstring
    pass


def return_in_signature_missing_from_docstring(func):
    if func.returns:
        return not (
            hasattr(func.docinfo, "returns")
            and bool(func.docinfo.returns)
        )
    else:
        return False


def return_in_docstring_missing_from_signature(func):
    if hasattr(func.docinfo, "returns") and bool(func.docinfo.returns):
        return not bool(func.returns)
    else:
        return False


def type_hints_missing_from_signature(func):
    return not all(
        [
            bool(v)
            for k, v in func.argdict.items()
            if k not in IGNORED_PARAMS
        ]
    )


def docstring_type_hints_not_match_signature(func):
    if func.docinfo and all(
        [
            bool(v)
            for k, v in func.argdict.items()
            if k not in IGNORED_PARAMS
        ]
    ):
        return not (
            [
                v
                for k, v in func.argdict.items()
                if k not in IGNORED_PARAMS
            ]
            == [d["hint"] for d in func.docinfo.params]
        )
    else:
        return False


class Linter:
    def __init__(self, func):

        self.func = func
        self.tests = [
            no_docstring,
            no_description_in_docstring,
            signature_params_not_same_as_docstring,
            not_all_docstring_params_have_desc,
            defaults_not_in_docstring,
            return_in_signature_missing_from_docstring,
            return_in_docstring_missing_from_signature,
            type_hints_missing_from_signature,
            docstring_type_hints_not_match_signature,
        ]
        self.problems = [t.__name__ for t in self.tests if t(self.func)]
