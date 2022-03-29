from inspect import getsource
import ast

from numdoclinter import linter, parse, actions


def with_no_docstring():
    pass

def with_no_description(x:int):
    """
    Parameters
    ----------
    x: int
        An integer.
    """
    pass

def with_signature_params_different_from_docstring(y:int, z:str):
    """
    Function with y,z as params in signature, but x,y in docstring.

    Parameters
    ----------
    x : str
        x
    y : int
        y
    """
    pass
    



def get_FunctionInfo_object(func):
    [func_ast] = ast.parse(getsource(func)).body
    fi = parse.FunctionInfo(func_ast, module=None, context=None)
    return fi


def test_no_docstring():
    func_with_no_docstring = get_FunctionInfo_object(with_no_docstring)
    assert linter.no_docstring(func_with_no_docstring)
    func_with_no_description = get_FunctionInfo_object(with_no_description)
    assert not linter.no_docstring(func_with_no_description)

def test_no_description_in_docstring():
    func_with_no_description = get_FunctionInfo_object(with_no_description)
    assert linter.no_description_in_docstring(func_with_no_description)
    func_with_description = get_FunctionInfo_object(
            with_signature_params_different_from_docstring)
    assert not linter.no_description_in_docstring(func_with_description)


def test_signature_params_not_same_as_docstring():
    different_signature_and_docstring_params = get_FunctionInfo_object(
        with_signature_params_different_from_docstring)
    assert linter.signature_params_not_same_as_docstring(different_signature_and_docstring_params)
    same_signature_and_docstring_params = get_FunctionInfo_object(with_no_description)
    assert not linter.signature_params_not_same_as_docstring(same_signature_and_docstring_params)

    
