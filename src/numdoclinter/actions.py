import ast
import os
from typing import List, Optional

import pandas as pd
import fire

from numdoclinter.linter import Linter
from numdoclinter.parse import FunctionInfo


def list_funcs_recursively(
    start: str,
    folder: str,
    func_list: Optional[List[FunctionInfo]] = None,
) -> List[FunctionInfo]:

    if func_list == None:
        func_list = []

    os.chdir(start)
    starting_location = os.getcwd()

    os.chdir(os.path.join(start, folder))
    location = os.getcwd()

    modules = [
        m
        for m in os.listdir()
        if (os.path.isfile(m) and m.split(".")[-1] == "py")
    ]

    for m in modules:
        func_list.extend(get_func_name_list(m, location))

    folders = [f for f in os.listdir() if os.path.isdir(f)]

    for f in folders:
        list_funcs_recursively(location, f, func_list)

    os.chdir(starting_location)
    return func_list


def get_func_name_list(module_filepath, context):
    with open(module_filepath, "r") as file:
        tree = ast.parse(file.read())

    module = module_filepath.split(".")[0]

    functions = [
        FunctionInfo(f, module, context)
        for f in tree.body
        if isinstance(f, ast.FunctionDef)
    ]
    classes = [c for c in tree.body if isinstance(c, ast.ClassDef)]
    methods = [
        FunctionInfo(f, module, context, c.name)
        for c in classes
        for f in c.body
        if isinstance(f, ast.FunctionDef)
    ]

    functions.extend(methods)

    return functions


def get_docstring_problems(folder, start=os.getcwd(), ignore_init=True):

    funcs = list_funcs_recursively(start, folder, [])

    if ignore_init:
        funcs = [f for f in funcs if f.ast.name != "__init__"]

    full_list = [
        (p, f, f.module, f.context)
        for f in funcs
        for p in Linter(f).problems
    ]

    df = pd.DataFrame(
        full_list, columns=["problem", "function", "module", "context"]
    )

    return df


def run_from_cli(
    folder: str,
    save_as_csv: bool = False,
    csv_name: str = "DOCSTRING_PROBLEMS.csv",
    echo_problems: bool = True,
):
    """
    Run numdoclinter from CLI.

    Parameters
    ----------
    folder: str
        The folder that you want to search
        (recursively) for modules (and nested subfolders containing
        modules) containing functions, to check if their signatures and
        docstrings conform to Numpy style.
    save_as_csv: bool
        Whether or not to save the list of problems as a CSV.
    csv_name: str
        If you have chosen to `save_as_csv`, the name of the CSV (which
        will be saved in your current working directory).
    echo_problems: bool
        Whether to print the list of problems to your CLI.
    """

    location = os.getcwd()

    funcs = list_funcs_recursively(location, folder, [])

    funcs = [f for f in funcs if f.ast.name != "__init__"]
    print(f"Found {len(funcs)} functions...")

    full_list = [
        (p, f, f.module, f.context.replace(location, ""))
        for f in funcs
        for p in Linter(f).problems
    ]
    print(f"... with {len(full_list)} docstring problems.")

    if echo_problems:
        [
            print(f"{os.path.join(x[3],x[2])}\n{x[1]}()\n{x[0]}\n")
            for x in full_list
        ]

    print(
        f"Summary: {len(funcs)} functions, {len(full_list)} problems."
    )

    if save_as_csv:
        df = pd.DataFrame(
            full_list,
            columns=["problem", "function", "module", "context"],
        )

        df.to_csv(csv_name, index=False)
        print(f"List saved as {csv_name}.")


def main():
    fire.Fire(run_from_cli)



if __name__ == "__main__":

    main()
