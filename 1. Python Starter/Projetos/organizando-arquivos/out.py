import os

cwd = os.getcwd()
folder_list = [i for i in os.listdir(cwd) if os.path.isdir(i)]

for folder in folder_list:
    path = cwd + '/' + folder
    files = os.listdir(path)
    for file in files:
        path_from = path + '/' + file
        path_to = cwd + '/' + file
        os.replace(path_from, path_to)
    os.rmdir(path)