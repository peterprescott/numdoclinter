"""
Tests for classes to parse functions, annotations, and docstrings.
"""

from typing import Optional, Union, List, Dict
import ast
from inspect import getsource

import pandas as pd

from numdoclinter import parse


def func1(
    a: int,
    b: str,
    c: Union[float, int],
    d: Dict[str, List[int]],
    e: Optional[pd.DataFrame],
) -> Optional[Union[dict, List[Union[float, int]]]]:
    """
    This is a Numpy style docstring.

    Parameters
    ----------
    a : int
        An integer.
    b : str
        A string.
    c : Union[float, int]
        Can be either a float or an int.
    d : Dict[str, List[int]]
        A dict with keys that are strings, and values that are lists of
        ints.
    e : Optional[pd.DataFrame]
        An optional dataframe.

    Returns
    -------
    Optional[Union[dict, List[Union[float, int]]]
        A weirdly complicated return type.
    """
    return None


def get_func_ast(func):
    [func_ast] = ast.parse(getsource(func)).body
    return func_ast


def get_DocstringInfo(func):
    func_ast = get_func_ast(func)
    docstring_ast = ast.get_docstring(func_ast)
    docstring_info = parse.DocstringInfo(docstring_ast)
    return docstring_info


def test_AnnotationInfo():

    func_ast = get_func_ast(func1)
    parsed_annotations = [
        parse.AnnotationInfo(arg.annotation).txt
        for arg in func_ast.args.args
    ]
    assert parsed_annotations[0] == "int"
    assert parsed_annotations[1] == "str"
    assert parsed_annotations[2] == "Union[float, int]"
    assert parsed_annotations[3] == "Dict[str, List[int]]"
    assert parsed_annotations[4] == "Optional[pd.DataFrame]"


def test_DocstringInfo_description():
    docstring_info = get_DocstringInfo(func1)
    assert (
        docstring_info.description == "This is a Numpy style docstring."
    )


def test_DocstringInfo_param_descriptions():
    docstring_info = get_DocstringInfo(func1)
    assert docstring_info.params[0]["desc"] == "An integer."


def test_DocstringInfo_type_hinting():
    docstring_info = get_DocstringInfo(func1)
    hints = {d["name"]: d["hint"] for d in docstring_info.params}
    assert hints["a"] == "int"
    assert hints["b"] == "str"
    assert hints["c"] == "Union[float, int]"
    assert hints["d"] == "Dict[str, List[int]]"
    assert hints["e"] == "Optional[pd.DataFrame]"


def test_DocstringInfo_returns():
    docstring_info = get_DocstringInfo(func1)
    r = docstring_info.returns
    assert r["hint"] == "Optional[Union[dict, List[Union[float, int]]]"
    assert r["desc"] == "A weirdly complicated return type."


def test_FunctionInfo():
    func_ast = get_func_ast(func1)
    fi = parse.FunctionInfo(func_ast, None, None)
    assert fi.name == "func1"
    assert fi.args == ["a", "b", "c", "d", "e"]
