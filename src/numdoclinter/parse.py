"""
A module that uses the Python abstract syntax grammar to parse the
necessary information (which should be more robust that using regular
expressions).
"""

import ast
from typing import Union


def get_func_name_list(module_filepath, context):
    with open(module_filepath, "r") as file:
        tree = ast.parse(file.read())

    module = module_filepath.split('.')[0]

    functions = [FunctionInfo(f, module, context) 
            for f in tree.body if isinstance(f, ast.FunctionDef)]
    classes = [c for c in tree.body if isinstance(c, ast.ClassDef)]
    methods = [FunctionInfo(f, module, context, c.name) 
            for c in classes for f in c.body if isinstance(f, ast.FunctionDef)]

    functions.extend(methods)

    return functions


class FunctionInfo:
    def __init__(self, function_def: ast.FunctionDef, module:str,
            context:str, class_name:str = None):

        if class_name:
            class_ = f'{class_name}::'
        else:
            class_ = ''

        self.ast = function_def
        self.name = f'{context}.{module}::{class_}{self.ast.name}'
        self.args = [a.arg for a in self.ast.args.args]
        self.annotations = [
            AnnotationInfo(a.annotation) for a in self.ast.args.args
        ]
        self.argdict = dict(zip(self.args, [x.txt for x in self.annotations]))
        self.docstring = ast.get_docstring(self.ast)
        self.returns = AnnotationInfo(self.ast.returns).txt

    def __repr__(self):

        return self.name


class AnnotationInfo:
    def __init__(self, annotation_info: Union[ast.Name, ast.Attribute, ast.Subscript]):
        self.ast = annotation_info
        try:
            if type(self.ast) == ast.Subscript:
                if hasattr(self.ast.slice, "dims"):
                    self.txt = f"""{self.ast.value.id}[{', '.join([
                        AnnotationInfo(x).txt for x in self.ast.slice.dims]
                    )}]"""
                else:
                    self.txt = f"{self.ast.value.id}[{self.ast.slice.id}]"
            elif type(self.ast) == ast.Name:
                self.txt = self.ast.id
            elif type(self.ast) == ast.Attribute:
                self.txt = f"{self.ast.value.id}.{self.ast.attr}"
            else:
                self.txt = None
        except:
            self.txt = None
