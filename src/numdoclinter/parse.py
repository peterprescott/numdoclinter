"""
A module that uses the Python abstract syntax grammar to parse the
necessary information (which should be more robust that using regular
expressions).
"""

import ast
from typing import Union, Optional

from sphinx.ext.napoleon import NumpyDocstring


class FunctionInfo:
    def __init__(
        self,
        function_def: ast.FunctionDef,
        module: str,
        context: str,
        class_name: Optional[str] = None,
    ):

        self.ast = function_def
        self.module = module
        self.context = context
        self.class_name = class_name
        if self.class_name:
            self.class_ = f"{class_name}::"
        else:
            self.class_ = ""

        self.name = f"{self.class_}{self.ast.name}"

        self.args = [a.arg for a in self.ast.args.args]
        self.annotations = [
            AnnotationInfo(a.annotation) for a in self.ast.args.args
        ]

        vararg, kwarg = self.ast.args.vararg, self.ast.args.kwarg
        for a in vararg, kwarg:
            if a:
                self.args.append(a.arg)
                self.annotations.append(AnnotationInfo(a.annotation))

        self.argdict = dict(
            zip(self.args, [x.txt for x in self.annotations])
        )

        self.docstring = ast.get_docstring(self.ast)
        self.returns = AnnotationInfo(self.ast.returns).txt

        if self.docstring:
            self.docinfo = DocstringInfo(self.docstring)
        else:
            self.docinfo = None

    def __repr__(self):

        return self.name


class AnnotationInfo:
    def __init__(
        self,
        annotation_info: Union[
            ast.Name,
            ast.Str,
            ast.Attribute,
            ast.Tuple,
            ast.List,
            ast.Subscript,
            ast.NameConstant,
            ast.Ellipsis,
        ],
    ):
        self.ast = annotation_info
        self.annotation_error = None
        try:
            if type(self.ast) == ast.Name:
                self.txt = self.ast.id
            elif type(self.ast) == ast.Str:
                self.txt = self.ast.s
            elif type(self.ast) == ast.Attribute:
                self.annotation_error = AnnotationInfo(
                    self.ast.value
                ).annotation_error

                self.txt = f"{AnnotationInfo(self.ast.value).txt}.{self.ast.attr}"
            elif (type(self.ast) == ast.Tuple) or (
                type(self.ast) == ast.List
            ):
                error_list = [
                    AnnotationInfo(x).annotation_error
                    for x in self.ast.elts
                    if AnnotationInfo(x).annotation_error
                ]
                if error_list:
                    self.annotation_error = ",".join([error_list])

                self.txt = ", ".join(
                    [
                        AnnotationInfo(x).txt
                        for x in self.ast.elts
                        if AnnotationInfo(x).txt
                    ]
                )

            elif type(self.ast) == ast.Subscript:
                if hasattr(self.ast.slice, "value"):
                    self.annotation_error = AnnotationInfo(
                        self.ast.slice.value
                    ).annotation_error

                    self.txt = (
                        f"{self.ast.value.id}"
                        f"[{AnnotationInfo(self.ast.slice.value).txt}]"
                    )
                else:
                    self.txt = (
                        f"{self.ast.value.id}"
                        f"[{AnnotationInfo(self.ast.slice.lower).txt}:"
                        f"{AnnotationInfo(self.ast.slice.upper).txt}]"
                    )
            elif type(self.ast) == ast.NameConstant:
                self.txt = "None"  # this is true in one case, not sure about the others
            elif type(self.ast) == type(None):
                self.txt = None
            elif type(self.ast) == ast.Ellipsis:
                self.txt = "..."
            else:
                # unknown type
                self.txt = f"?!{type(self.ast)}"
        except Exception as e:
            self.txt = None
            self.annotation_error = e


class DocstringInfo:
    def __init__(self, raw_docstring: str):
        self.raw = raw_docstring
        self.sphinx = NumpyDocstring(self.raw).lines()
        self.sphinx_sections = "\n".join(self.sphinx).split("\n\n")
        self._get_description()
        self._get_parameters()
        self._get_returns()

    def _get_description(self):
        try:
            self.description = self.sphinx_sections[0]
            assert self.description[0] != ":"
        except:
            self.description = None

    def _get_parameters(self):
        self.params = []
        self._param_section = [
            section
            for section in self.sphinx_sections
            if section.split(" ")[0] == ":param"
        ]
        if len(self._param_section) == 1:
            self._param_lines = self._param_section[0].split(":param ")[
                1:
            ]
            for p in self._param_lines:
                splits = p.split(":")
                name = splits[0]
                desc = splits[1].strip()
                hint = splits[-1].strip()
                self.params.append(
                    {"name": name, "desc": desc, "hint": hint}
                )

    def _get_returns(self):
        self._returns = [
            section
            for section in self.sphinx_sections
            if section.split(" ")[0] == ":returns:"
        ]
        if self._returns:
            self._returns = self._returns[0]
            hint = self._returns.split(":")[-1].strip()
            desc = self._returns.split(":")[2].strip()
            self.returns = {"hint": hint, "desc": desc}
        else:
            self._returns, self.returns = None, None
