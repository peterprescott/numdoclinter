import os

from numdoclinter import parse


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

os.chdir('/home/peterprescott/90poe/data-science-common')

x = list_files_recursively('.', 'data_science_common', [])

x[:10]
