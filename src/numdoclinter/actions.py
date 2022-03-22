import ast
from parse import FunctionInfo


def list_files_recursively(start, folder, func_list):

    os.chdir(os.path.join(start,folder))
    location = os.getcwd()

    modules = [m for m in os.listdir() if 
            (os.path.isfile(m) and m.split('.')[-1] == 'py')]

    for m in modules:
        func_list.extend(parse.get_func_name_list(m, location))
    

    folders = [f for f in os.listdir()
            if os.path.isdir(f)]

    for f in folders:
        list_files_recursively(location, f, func_list)

    return func_list 


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
