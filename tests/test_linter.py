from inspect import getsource
import ast

from numdoclinter import linter, parse, actions


def with_no_docstring():
    pass


def get_FunctionInfo_object(func):
    [func_ast] = ast.parse(getsource(func)).body
    fi = parse.FunctionInfo(func_ast, module=None, context=None)
    return fi


def test_no_docstring():
    func_with_no_docstring = get_FunctionInfo_object(with_no_docstring)
    assert linter.no_docstring(func_with_no_docstring)
