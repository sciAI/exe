"""
    App models
"""

import urllib
import re
import io
from datetime import datetime

from bs4 import BeautifulSoup
from mongoengine import *
from werkzeug.utils import secure_filename
from flask import render_template

import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
from nbconvert.preprocessors.execute import CellExecutionError
from nbconvert import HTMLExporter

from validator import db
from validator.utils import get_path_to_file, install_dependencies, \
    get_unique_appendix, is_allowed_file


class List(db.Document):
    """
        Entity represents list of urls to papers record
    """
    filename = db.StringField()
    extension = db.StringField(default='csv')
    path = db.StringField()
    date_created = db.DateTimeField(default=datetime.now())
    is_processed = db.BooleanField(default=False)
    # meta info
    meta = {
        'collection': 'lists',
        'db_alias': 'main'
    }

    def get_id(self):
        """
            Returns entity ID
        """
        return str(self.id)

    @staticmethod
    def create_new_list(file):
        """
            Create a new file with list of links
        """
        if not file or not is_allowed_file(file.filename):
            return False
        secured_filename = secure_filename(file.filename)
        secured_filename = '_'.join(secured_filename.split('.'))
        new_filename = '{0}_{1}'.format(
            secured_filename,
            get_unique_appendix()
        )
        file.save(get_path_to_file(new_filename))
        new_list = List(
            filename=new_filename,
            path=get_path_to_file(new_filename),
            is_processed=False
        )
        new_list.save()
        Log.write_log(
            new_list.get_id(),
            None,
            None,
            'Successfully saved file with list of links'
        )
        return new_list

    def extract_list_of_links(self):
        """
            Extract list of links to notebooks from papers
        """
        Log.write_log(
            self.get_id(),
            None,
            None,
            'Starting processing list of urls'
        )

        # read the file with list of links
        urls_to_papers = []
        with open(get_path_to_file(self.filename)) as f:
            urls_to_papers = f.readlines()
        # remove spaces from urls
        urls_to_papers = [x.strip() for x in urls_to_papers]

        Log.write_log(
            self.get_id(),
            None,
            None,
            'Total papers urls extracted: {0}'.format(len(urls_to_papers))
        )

        return urls_to_papers


class Paper(db.Document):
    """
        Entity represents paper record
    """
    paper_url = db.StringField()
    list_id = db.StringField()
    date_created = db.DateTimeField(default=datetime.now())
    is_processed = db.BooleanField(default=False)
    # meta info
    meta = {
        'collection': 'papers',
        'db_alias': 'main'
    }

    def get_id(self):
        """
            Returns entity ID
        """
        return str(self.id)


    def extract_links_to_notebooks(self):
        """
            Returns list of links to notebooks from paper
        """
        if self.paper_url.find('ncbi.nlm.nih.gov') > -1:
            res = re.findall(r'articles\/(.*)\/?', self.paper_url)
            if res:
                pub_id = res[0]
                paper_url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id={0}'.format(
                    pub_id)
        r = urllib.urlopen(paper_url).read()
        soup = BeautifulSoup(r)

        notebooks_urls = []
        for url in soup.find_all(['a', 'ext-link']):
            current_url = url.get('href') if url.get(
                'href') else url.get('xlink:href')
            if current_url and current_url.endswith('ipynb'):
                print('Jupyter notebook url: {0}'.format(current_url))
                notebooks_urls.append(current_url)

        notebooks_urls = list(set(notebooks_urls))
        return notebooks_urls



class Notebook(db.Document):
    """
        Entity represents notebook record
    """
    url = db.StringField()
    filename = db.StringField()
    path = db.StringField()
    paper_id = db.StringField()
    date_created = db.DateTimeField(default=datetime.now())
    is_failed = db.BooleanField(default=False)
    is_processed = db.BooleanField(default=False)
    message = db.StringField(default='')
    kernel = db.StringField(default='')
    #html_content = db.StringField(default='')
    #html_resources = db.DictField(default={})
    # meta info
    meta = {
        'collection': 'notebooks',
        'db_alias': 'main'
    }


    def get_id(self):
        """
            Returns entity ID
        """
        return str(self.id)

    @staticmethod
    def process_new_notebook(paper_id, notebook_url):
        """
            Download and process new notebook
        """
        # Step 1. Download notebook
        notebook_filename = get_unique_appendix() + '.ipynb'
        if notebook_url.find('github.com') > -1:
            notebook_url = notebook_url.replace('/blob/', '/raw/')
        elif notebook_url.find('nbviewer.jupyter.org/github') > -1:
            notebook_url = notebook_url.replace(
                'nbviewer.jupyter.org/github',
                'raw.githubusercontent.com'
            ).replace(
                '/blob/',
                '/'
            )
        urllib.urlretrieve(notebook_url, get_path_to_file(notebook_filename))

        # Step 2. Process notebook
        new_notebook = Notebook(
            url=notebook_url,
            filename=notebook_filename,
            path=get_path_to_file(notebook_filename),
            paper_id=paper_id
        )
        new_notebook.save()

        notebook_path = get_path_to_file(notebook_filename)
        notebook_out_path = get_path_to_file('validator_output_{0}'.format(notebook_filename))
        # read the file
        Log.write_log(
            None,
            paper_id,
            new_notebook.get_id(),
            'Start process notebook'
        )
        try:
            notebook_file = io.open(notebook_path, encoding='utf-8')
            notebook_content = nbformat.read(notebook_file, as_version=4)
            kernel_name = notebook_content['metadata']['kernelspec']['name']
            status, tmp_log = install_dependencies(
                str(notebook_content), kernel_name)

            Log.write_log(
                None,
                paper_id,
                new_notebook.get_id(),
                tmp_log
            )

            ep = ExecutePreprocessor(
                timeout=150,
                kernel_name=kernel_name
            )
            ep.preprocess(
                notebook_content,
                {'metadata': {'path': get_path_to_file('')}}
            )
            message = 'Successfully processed'
            is_failed = False
        except Exception as e:
            message = str(e)
            kernel_name = None if 'kernel_name' not in locals() else kernel_name
            is_failed = True
            notebook_content = False if 'notebook_content' not in locals() else notebook_content
        finally:
            new_notebook.kernel = kernel_name
            new_notebook.message = message
            new_notebook.is_failed = is_failed
            new_notebook.is_processed = True
            new_notebook.save()
            if notebook_content:
                Log.write_log(
                    None,
                    paper_id,
                    new_notebook.get_id(),
                    'Write output to file'
                )
                html_exporter = HTMLExporter()
                html_exporter.template_file = 'basic'
                (body, resources) = html_exporter.from_notebook_node(notebook_content)
                f = open(get_path_to_file('{0}.html').format(new_notebook.get_id()), 'w')
                rendered_template = render_template('output.html', body=body)
                f.write(rendered_template.encode('utf-8'))
                f.close()

                #print(body)
                #print('<------------------------------>')
                #print(resources)
                # new_notebook.html_content = body
                # new_notebook.html_resources = resources
                new_notebook.save()
                with io.open(notebook_out_path, mode='wt', encoding='utf-8') as f:
                    nbformat.write(notebook_content, f)
        return new_notebook.get_id()

class Log(db.Document):
    """
        Entity representes log record
    """
    date_created = db.DateTimeField(default=datetime.now())
    list_id = db.StringField()
    paper_id = db.StringField()
    notebook_id = db.StringField()
    message = db.StringField()
    # meta info
    meta = {
        'collection': 'logs',
        'db_alias': 'main'
    }

    def get_id(self):
        """
            Returns entity ID
        """
        return str(self.id)


    @staticmethod
    def write_log(list_id, paper_id, notebook_id, message):
        """
            Write log
        """
        new_log = Log(
            list_id=list_id,
            paper_id=paper_id,
            notebook_id=notebook_id,
            message=message
        )
        new_log.save()
        return new_log.get_id()
