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
    

def without_desc_for_all_docstring_params(x:int, y:int):
    """
    Parameters
    ----------
    x: int
        Only this parameter has docstring description.
    y: int
    """
    pass


def return_not_in_docstring(x:int) -> int:
    """
    Function with return in signature but not docstring.

    Parameters
    ----------
    x: int
        Some integer.
    """
    return 1



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

    
def test_not_all_docstring_params_have_desc():
    func_without_desc_for_all_docstring_params = get_FunctionInfo_object(
            without_desc_for_all_docstring_params)
    assert linter.not_all_docstring_params_have_desc(
            func_without_desc_for_all_docstring_params)
    func_with_desc_for_all_docstring_params = get_FunctionInfo_object(
            with_signature_params_different_from_docstring)
    assert not linter.not_all_docstring_params_have_desc(
            func_with_desc_for_all_docstring_params)


def test_return_in_signature_missing_from_docstring():
    func_with_no_docstring_return = get_FunctionInfo_object(
            return_not_in_docstring)
    assert linter.return_in_signature_missing_from_docstring(
            func_with_no_docstring_return)
