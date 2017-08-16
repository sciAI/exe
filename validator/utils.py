"""
    Different utils functions
"""

import os
import uuid
import re
import pip
import subprocess
import csv

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


def read_csv_file(path_to_file):
    """
        Simple reader for both txt and csv files
    """
    urls = []
    with open(path_to_file, 'rb') as csvfile:
        content = csv.reader(csvfile, delimiter=',')
        # skip header
        next(content, None)
        for row in content:
            urls.append(row[0])
    return urls

def install_dependencies(nb_string, kernel_name):
    """
        Install necessary dependencies to run notebook
    """
    # log string
    log_string = ''
    # regex to find imports
    modules = re.findall(r'(?<!#)\s?(?<=\\n)(import|from)\s(\w*)', nb_string)
    if kernel_name == 'python2':
        log_string += 'Install dependencies for Python2\n'
        for module in modules:
            log_string += 'Try to install: {0}\n'.format(module[1])
            if is_module_installed(module[1], kernel_name):
                log_string += 'Module: {0} installed\n'.format(module[1])
                continue
            try:
                process = subprocess.Popen([app.config['PYTHON2_PIP'], 'install', module[1]],
                           stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT)
                returncode = process.wait()
                log_string += 'PIP install returned: {0}\n'.format(returncode)
                log_string += process.stdout.read()
            except Exception as e:
                log_string += 'Error occured: {0}\n'.format(str(e))
                return False, log_string
    elif kernel_name == 'python3':
        log_string += 'Install dependencies for Python3\n'
        for module in modules:
            log_string += 'Try to install: {0}\n'.format(module[1])
            if is_module_installed(module[1], kernel_name):
                log_string += 'Module: {0} installed\n'.format(module[1])
                continue
            try:
                process = subprocess.Popen([app.config['PYTHON3_PIP'], 'install', module[1]],
                           stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT)
                returncode = process.wait()
                log_string += 'PIP install returned: {0}\n'.format(returncode)
                log_string += process.stdout.read()
            except Exception as e:
                log_string += 'Error occured: {0}\n'.format(str(e))
                return False, log_string
    return True, log_string


def is_module_installed(module_name, kernel_name):
    """
        Check if module with specified name already installed
    """
    try:
        if kernel_name == 'python2':
            output = subprocess.check_output(
                ["{0} -c 'import pkgutil; print(1 if pkgutil.find_loader(\"{1}\") else 0)'".format(
                    app.config['PYTHON2_PYTHON'],
                    module_name)],
                shell=True
            )
        elif kernel_name == 'python3':
            output = subprocess.check_output(
                ["{0} -c 'import pkgutil; print(1 if pkgutil.find_loader(\"{1}\") else 0)'".format(
                    app.config['PYTHON3_PYTHON'],
                    module_name)],
                shell=True
            )
        if output.strip() == '1':
            return True
    except subprocess.CalledProcessError as e:
        print(str(e))
        return False
    return False
