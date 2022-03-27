import os

from numdoclinter import actions


def test_get_func_name_list():

    location = os.path.dirname(os.path.abspath(__file__))
    [f] = actions.get_func_name_list('dir0/module01.py', location)
    assert f.name == 'func01'

def test_list_funcs_recursively():

    location = os.path.dirname(os.path.abspath(__file__))
    funcs = actions.list_funcs_recursively(location,'dir0')

    fnames = sorted([f.name for f in funcs])
    assert fnames == ['func01', 'func02', 'func11', 'func12']

    fmodules = sorted([f.module for f in funcs])
    assert fmodules == ['module01', 'module02', 'module11', 'module12']

    fcontexts = sorted([f.context.replace(location,'') for f in funcs])
    assert fcontexts == ['/dir0', '/dir0', '/dir0/dir1', '/dir0/dir1']

    return


def test_get_docstring_problems():

    location = os.path.dirname(os.path.abspath(__file__))
    df = actions.get_docstring_problems('dir0', location)

    assert list(df.columns) == ['problem', 'function', 'module', 'context']

    df['fname'] = df['function'].apply(lambda x: x.name)
    df = df.sort_values('fname')

    assert df[['fname', 'module', 'problem']].to_dict('list') == {'fname': ['func01', 'func02', 'func11', 'func12'],
            'module': ['module01', 'module02', 'module11', 'module12'],
            'problem': ['no_docstring']*4}
