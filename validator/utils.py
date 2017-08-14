"""
    Different utils functions
"""

import os
import uuid
import re
import pip
import subprocess

from validator import app

# from validator.models import Log, Paper, Notebook


def is_allowed_file(filename):
    """
        Check if file in allowed list
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower(
           ) in app.config['ALLOWED_EXTENSIONS']


def get_unique_appendix():
    """
        Generate uniquer appendix value
    """
    return uuid.uuid4().hex


def get_path_to_file(filename):
    """
        Returns path fo file in uploads by filename
    """
    if not filename:
        return app.config['UPLOAD_FOLDER']
    return os.path.join(app.config['UPLOAD_FOLDER'], filename)


def install_dependencies(nb_string, kernel_name):
    """
        Install necessary dependencies to run notebook
    """
    # regex to find imports
    modules = re.findall(r'(?<!#)\s?(?<=\\n)(import|from)\s(\w*)', nb_string)
    if kernel_name == 'python2':
        print('Install dependencies for Python2')
        for module in modules:
            print('Try to install: {0}'.format(module[1]))
            try:
                pip.main(['install', module[1]])
            except Exception as e:
                return False, str(e)
    elif kernel_name == 'python3':
        print('Install dependencies for Python3')
        for module in modules:
            print('Try to install: {0}'.format(module[1]))
            if is_module_installed(module[1]):
                print('Module: {0} installed'.format(module[1]))
                continue
            try:
                subprocess.check_output(
                    ['/mnt/c/dev/jupyter-testing/py3env/bin/pip install {0}'.format(
                        module[1])],
                    shell=True
                )
            except Exception as e:
                return False, str(e)
    return True, modules


def is_module_installed(module_name):
    """
        Check if module with specified name already installed
    """
    try:
        output = subprocess.check_output(
            ["/mnt/c/dev/jupyter-testing/py3env/bin/python -c 'import pkgutil; print(1 if pkgutil.find_loader(\"{0}\") else 0)'".format(
                module_name)],
            shell=True
        )
        if output.strip() == '1':
            return True
    except subprocess.CalledProcessError as e:
        print(str(e))
        return False
    return False
