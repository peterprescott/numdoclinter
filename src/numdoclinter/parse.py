"""
A module that uses the Python abstract syntax grammar to parse the
necessary information (which should be more robust that using regular
expressions).
"""

import ast
from typing import Union


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


class DocstringInfo:
    def __init__(self, raw_docstring:str):
        self.raw = raw_docstring
        self.sphinx = NumpyDocstring(self.raw).lines()
        self.sphinx_sections = '\n'.join(self.sphinx).split('\n\n')
        self._get_description()
        self._get_parameters()
        self._get_returns()

    def _get_description(self):
        self.description = self.sphinx_sections[0]
        assert self.description[0] != ':'

    def _get_parameters(self):
        self._param_section = [section for section 
                in self.sphinx_sections 
                if section.split(' ')[0]==':param']
        if len(self._p0)==1:
            self._param_lines = self._param_section[0].split('\n')
            self._odd = [line for i, line in
                    enumerate(self._param_lines) if i%2==1]
            self._even = [line for i, line in
                    enumerate(self._param_lines) if i%2==0]
            self._pairs = zip(self._odd, self._even)

    def _get_returns(self):
        self._returns = [section for section 
                in self.sphinx_sections
                        if section.split(' ')[0]==':returns:']

