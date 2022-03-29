"""
This module contains the main FunctionInfo class used for handling
functions. This makes use of the AnnotationInfo class for parsing
signature type hints, and the DocstringInfo class for parsing
docstrings. These in turn make use of the built-in ast library, and the
Sphinx Napoleon extension.
"""

import ast
from typing import Union, Optional

from sphinx.ext.napoleon import NumpyDocstring


class FunctionInfo:
    """
    This is how we extract the information we want about the functions
    we are interested in, without running their code (which could be
    unsafe), or trying to do fancy regex on their source (which might
    not be sufficiently robust).
    """

    def __init__(
        self,
        function_def: ast.FunctionDef,
        module: str,
        context: str,
        class_name: Optional[str] = None,
    ):
        """
        Initialize the FunctionInfo object.

        Parameters
        ----------
        function_def: ast.FunctionDef
            The abstract syntax tree object for the function definition.
        module: str
            The name of the module in which the function was found.
        context: str
            The filepath of the module in which the function was found.
        class_name: Optional[str]
            If the function is a method, the name of the class in which
            it is defined.
        """

        self.ast = function_def
        self.module = module
        self.context = context
        self.class_name = class_name

        if self.class_name:
            self.name = f"{class_name}::{self.ast.name}"
        else:
            self.name = self.ast.name

        self._parse_signature()
        self._parse_docstring()

    def _parse_signature(self):
        """
        Parse the signature of the function, and get its type hints using
        the AnnotationInfo object.
        """

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

    def _parse_docstring(self):
        """
        Parse the docstring of the function using the DocstringInfo
        object.
        """
        self.docstring = ast.get_docstring(self.ast)
        self.returns = AnnotationInfo(self.ast.returns).txt

        if self.docstring:
            self.docinfo = DocstringInfo(self.docstring)
        else:
            self.docinfo = None

    def __repr__(self):
        """
        Represent the FunctionInfo object with the function's name.
        """

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
        """
        Recursively unpacks the ast Annotation into the text of its type
        hint, based on the specific behaviour of the annotation type.

        Parameters
        ----------
        annotation_info: Union[
            ast.Name,
            ast.Str,
            ast.Attribute,
            ast.Tuple,
            ast.List,
            ast.Subscript,
            ast.NameConstant,
            ast.Ellipsis,
        ]
        """
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

                self.txt = (
                    f"{AnnotationInfo(self.ast.value).txt}.{self.ast.attr}"
                )
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
                self.txt = "None"
            elif type(self.ast) == type(None):
                self.txt = None
            elif type(self.ast) == ast.Ellipsis:
                self.txt = "..."
            else:
                # ast type not yet dealt with
                self.txt = f"?!{type(self.ast)}"
        except Exception as e:
            self.txt = None
            self.annotation_error = e


class DocstringInfo:
    def __init__(self, raw_docstring: str):
        """
        Uses the sphinx.ext.napoleon.NumpyDocstring to parse the lines
        of the docstring into a somewhat more predictable format, before
        then extracting the information into a form more suitable for
        our use.
        """
        self.raw = raw_docstring
        self.sphinx = NumpyDocstring(self.raw).lines()
        self.sphinx_sections = "\n".join(self.sphinx).split("\n\n")
        self._get_description()
        self._get_parameters()
        self._get_returns()

    def _get_description(self):
        """
        Try to get initial docstring description.
        """
        try:
            self.description = self.sphinx_sections[0]
            assert self.description[0] != ":"
        except:
            self.description = None

    def _get_parameters(self):
        """
        For each docstring parameter, get name, description and type hint.
        """
        self.params = []
        self._param_section = [
            section
            for section in self.sphinx_sections
            if section.split(" ")[0] == ":param"
        ]
        if len(self._param_section) == 1:
            self._param_lines = self._param_section[0].split(":param ")[1:]
            for p in self._param_lines:
                splits = p.split(":")
                name = splits[0]
                desc = splits[1].strip()
                hint = splits[-1].strip()
                self.params.append(
                    {"name": name, "desc": desc, "hint": hint}
                )

    def _get_returns(self):
        """
        Get docstring returns hint and description.
        """
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
