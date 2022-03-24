from sphinx.ext.napoleon import NumpyDocstring
from numdoclinter import parse, actions, linter

start = '/home/peterprescott/90poe/data-science-common'
folder = 'data_science_common'

funcs = actions.list_files_recursively(start, folder, [])

len([f for f in funcs if linter.Linter(f).problems])
