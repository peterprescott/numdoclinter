"""
This module includes various linter checks for the docstring.

The design is very simple. Each check is a function, the name of which
specifies the problem a function might have, and which returns a Boolean
value as to whether the particular function has that problem.

So `no_docstring(func)` returns True if `func` has no docstring.
"""

from numdoclinter.parse import FunctionInfo


IGNORED_PARAMS = ("self", "cls", "args", "kwargs")


def no_docstring(func: FunctionInfo) -> bool:
    """
    Check whether the specified function has the problem described in
    this test's name.

    Parameters
    ----------
    func: FunctionInfo
        Parsed FunctionInfo.

    Returns
    -------
    bool
        Whether the function has the problem described in this
        function's name.
    """
    return not bool(func.docstring)


def no_description_in_docstring(func: FunctionInfo) -> bool:
    """
    Check whether the specified function has the problem described in
    this test's name.

    Parameters
    ----------
    func: FunctionInfo
        Parsed FunctionInfo.

    Returns
    -------
    bool
        Whether the function has the problem described in this
        function's name.
    """
    if func.docinfo:
        return not bool(func.docinfo.description)
    else:
        return False


def docstring_blank_line_missing(func: FunctionInfo) -> bool:
    """
    Check whether the specified function has the problem described in
    this test's name.

    Parameters
    ----------
    func: FunctionInfo
        Parsed FunctionInfo.

    Returns
    -------
    bool
        Whether the function has the problem described in this
        function's name.
    """
    # TODO
    pass


def signature_params_not_same_as_docstring(func: FunctionInfo) -> bool:
    """
    Check whether the specified function has the problem described in
    this test's name.

    Parameters
    ----------
    func: FunctionInfo
        Parsed FunctionInfo.

    Returns
    -------
    bool
        Whether the function has the problem described in this
        function's name.
    """
    if func.docinfo:
        signature_params = [p for p in func.args if p not in IGNORED_PARAMS]
        docstring_params = [
            d["name"]
            for d in func.docinfo.params
            if d["name"] not in IGNORED_PARAMS
        ]
        return not bool(signature_params == docstring_params)
    else:
        return False


def not_all_docstring_params_have_desc(func: FunctionInfo) -> bool:
    """
    Check whether the specified function has the problem described in
    this test's name.

    Parameters
    ----------
    func: FunctionInfo
        Parsed FunctionInfo.

    Returns
    -------
    bool
        Whether the function has the problem described in this
        function's name.
    """
    if func.docinfo:
        return not all([bool(d["desc"]) for d in func.docinfo.params])
    else:
        return False


def defaults_not_in_docstring(func: FunctionInfo) -> bool:
    """
    Check whether the specified function has the problem described in
    this test's name.

    Parameters
    ----------
    func: FunctionInfo
        Parsed FunctionInfo.

    Returns
    -------
    bool
        Whether the function has the problem described in this
        function's name.

    """
    # TODO:
    # will require parsing defaults from signature ast
    # and from docstring
    pass


def return_in_signature_missing_from_docstring(func: FunctionInfo) -> bool:
    """
    Check whether the specified function has the problem described in
    this test's name.

    Parameters
    ----------
    func: FunctionInfo
        Parsed FunctionInfo.

    Returns
    -------
    bool
        Whether the function has the problem described in this
        function's name.

    """
    if func.returns:
        return not (
            hasattr(func.docinfo, "returns") and bool(func.docinfo.returns)
        )
    else:
        return False


def return_in_docstring_missing_from_signature(func: FunctionInfo) -> bool:
    """
    Check whether the specified function has the problem described in
    this test's name.

    Parameters
    ----------
    func: FunctionInfo
        Parsed FunctionInfo.

    Returns
    -------
    bool
        Whether the function has the problem described in this
        function's name.

    """
    if hasattr(func.docinfo, "returns") and bool(func.docinfo.returns):
        return not bool(func.returns)
    else:
        return False


def type_hints_missing_from_signature(func: FunctionInfo) -> bool:
    """
    Check whether the specified function has the problem described in
    this test's name.

    Parameters
    ----------
    func: FunctionInfo
        Parsed FunctionInfo.

    Returns
    -------
    bool
        Whether the function has the problem described in this
        function's name.

    """

    return not all(
        [bool(v) for k, v in func.argdict.items() if k not in IGNORED_PARAMS]
    )


def docstring_type_hints_not_match_signature(func: FunctionInfo) -> bool:
    """
    Check whether the specified function has the problem described in
    this test's name.

    Parameters
    ----------
    func: FunctionInfo
        Parsed FunctionInfo.

    Returns
    -------
    bool
        Whether the function has the problem described in this
        function's name.

    """

    if func.docinfo and all(
        [bool(v) for k, v in func.argdict.items() if k not in IGNORED_PARAMS]
    ):
        return not (
            [v for k, v in func.argdict.items() if k not in IGNORED_PARAMS]
            == [d["hint"] for d in func.docinfo.params]
        )
    else:
        return False


class Linter:
    def __init__(self, func: FunctionInfo):
        """
        Initialize Linter.

        Parameters
        ----------
        func: FunctionInfo
            Parsed FunctionInfo.
        """

        self.func = func
        self.run_tests()

    def run_tests(self):
        """
        Run tests to assess whether signature and docstring conform to
        Numpy style.
        """
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
