"""
    Different utils functions
"""

import os
import uuid
import re
import subprocess
import csv

import jinja2

from threading import Timer
from validator import app


def is_allowed_file(filename):
    """
        Check if file in allowed list
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower(
           ) in app.config['ALLOWED_EXTENSIONS']


def generate_id():
    """
        Generate uniquer appendix value
    """
    return uuid.uuid4().hex


def get_uploads_path():
    return app.config['UPLOAD_FOLDER']

def get_path_to_file(filename):
    """
        Returns path fo file in uploads by filename
    """
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
            if not row or row[0].isspace():
                continue
            possible_url = row[0].strip()
            urls.append(possible_url)
    return urls

def install_dependencies(nb_string, kernel_name):
    """
        Install necessary dependencies to run notebook
    """
    # log string
    log_string = ''
    # regex to find imports
    # re.findall(r'(?<!#)\s?(?<=\\n)(import|from)\s(\w*)', nb_string)
    modules = re.findall(r'(\\n|\')(?<!#)\s?(import|from)\s(\w*)', nb_string)
    modules_names = set([x[2] for x in modules])
    log_string += 'Modules to install: {0}\n'.format(str(modules_names))
    if kernel_name == 'python2':
        log_string += 'Install dependencies for Python2\n'
        for module in modules_names:
            log_string += 'Try to install: {0}\n'.format(module)
            if is_module_installed(module, kernel_name):
                log_string += 'Module: {0} installed\n'.format(module)
                continue
            try:
                process = subprocess.Popen(
                    [app.config['PYTHON2_PIP']],
                    'install',
                    module,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                timer = Timer(300, process.kill)
                timer.start()
                stdout, stderr = process.communicate()
                returncode = process.returncode
                log_string += 'PIP install returned: {0}\n'.format(returncode)
                log_string += 'PIP log: {0}\n'.format(stdout)
                log_string += 'Error: {0}\n'.format(stderr)
                if not timer.is_alive():
                    log_string += 'Timer timeout. Module {0} takes too long to install\n'.format(
                        module)
            except Exception as e:
                log_string += 'Error occured: {0}\n'.format(str(e))
                return False, log_string
            finally:
                if 'timer' in locals():
                    timer.cancel()
    elif kernel_name == 'python3':
        log_string += 'Install dependencies for Python3\n'
        for module in modules_names:
            log_string += 'Try to install: {0}\n'.format(module)
            if is_module_installed(module, kernel_name):
                log_string += 'Module: {0} installed\n'.format(module)
                continue
            try:
                process = subprocess.Popen(
                    [app.config['PYTHON3_PIP']],
                    'install',
                    module,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                timer = Timer(300, process.kill)
                timer.start()
                stdout, stderr = process.communicate()
                returncode = process.returncode
                log_string += 'PIP install returned: {0}\n'.format(returncode)
                log_string += 'PIP log: {0}\n'.format(stdout)
                log_string += 'Error: {0}\n'.format(stderr)
                if not timer.is_alive():
                    log_string += 'Timer timeout. Module {0} takes too long to install'.format(
                        module)
            except Exception as e:
                log_string += 'Error occured: {0}\n'.format(str(e))
                return False, log_string
            finally:
                if 'timer' in locals():
                    timer.cancel()
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

def get_direct_url_to_notebook(original_url):
    """
        Returns direct URL to download notebooks
    """
    download_url = original_url
    if original_url.find('github.com') > -1:
        download_url = original_url.replace('/blob/', '/raw/')
    elif original_url.find('nbviewer.jupyter.org/github') > -1:
        download_url = original_url.replace(
            'nbviewer.jupyter.org/github',
            'raw.githubusercontent.com'
        ).replace(
            '/blob/',
            '/'
        )
    elif original_url.find('nbviewer.ipython.org/github') > -1:
        download_url = original_url.replace(
            'nbviewer.ipython.org/github',
            'raw.githubusercontent.com'
        ).replace(
            '/blob/',
            '/'
        )
    return download_url


def render_without_request(template_name, **template_vars):
    """
    Usage is the same as flask.render_template:

    render_without_request('my_template.html', var1='foo', var2='bar')
    """
    env = jinja2.Environment(
        loader=jinja2.PackageLoader('validator', 'templates')
    )
    template = env.get_template(template_name)
    return template.render(**template_vars)
