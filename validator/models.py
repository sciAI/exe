"""
    App models
"""

import urllib
import re
import io
from datetime import datetime

from bs4 import BeautifulSoup
from mongoengine import *
from flask import render_template

import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
from nbconvert.preprocessors.execute import CellExecutionError
from nbconvert import HTMLExporter

from validator import db
from validator.utils import get_path_to_file, install_dependencies, \
    generate_id, is_allowed_file, read_csv_file, get_uploads_path


class List(db.Document):
    """
        Entity represents list of urls to papers record
    """
    filename = db.StringField(default='')
    extension = db.StringField(default='csv')
    path = db.StringField(default='')
    date_created = db.DateTimeField(default=datetime.now())
    is_processed = db.BooleanField(default=False)
    list_type = db.StringField(db_field="type")
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
    def create_new_list():
        """
            Returns new list
        """
        new_list = List()
        new_list.save()

        Log.write_log(
            new_list.get_id(),
            None,
            None,
            'Successfully saved file with list of links'
        )

        return new_list


    def update_type(self, list_type):
        """
            Update type of list
        """
        self.list_type = list_type
        self.save()

        Log.write_log(
            self.get_id(),
            None,
            None,
            'Successfully updated type of list of links to {0}'.format(list_type)
        )


    def update_file(self, file):
        """
            Create a new file with list of links
        """
        if not file or not is_allowed_file(file.filename):
            return False
        new_filename = generate_id() + '.csv'
        file.save(get_path_to_file(new_filename))

        self.filename = new_filename
        self.path = get_path_to_file(new_filename)
        self.save()
        Log.write_log(
            self.get_id(),
            None,
            None,
            'Successfully updated file with list of links'
        )
        return True

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

        urls_to_papers = read_csv_file(get_path_to_file(self.filename))

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
    original_url = db.StringField()
    download_url = db.StringField(default='')
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

    @staticmethod
    def create_new_paper(list_id, url_to_paper):
        """
            Returns new paper object
        """
        Log.write_log(
            list_id,
            None,
            None,
            'Process paper url: {0}'.format(url_to_paper)
        )
        new_paper = Paper(
            original_url=url_to_paper,
            list_id=list_id
        )
        new_paper.save()
        return new_paper

    def update_status(self, status):
        """
            Update status of paper
        """
        self.is_processed = status
        self.save()
        Log.write_log(
            self.list_id,
            self.get_id(),
            None,
            'Processed paper url'
        )


    def extract_links_to_notebooks(self):
        """
            Returns list of links to notebooks from paper
        """
        if self.original_url.find('ncbi.nlm.nih.gov') > -1:
            res = re.findall(r'articles\/(.*)\/?', self.original_url)
            if res:
                pub_id = res[0]
                self.download_url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id={0}'.format(
                    pub_id)
        r = urllib.urlopen(self.download_url).read()
        soup = BeautifulSoup(r)

        notebooks_urls = []
        for url in soup.find_all(['a', 'ext-link']):
            current_url = url.get('href') if url.get(
                'href') else url.get('xlink:href')
            if current_url and current_url.endswith('ipynb'):
                notebooks_urls.append(current_url)

        notebooks_urls = list(set(notebooks_urls))
        return notebooks_urls



class Notebook(db.Document):
    """
        Entity represents notebook record
    """
    original_url = db.StringField()
    download_url = db.StringField(default='')
    filename = db.StringField(default='')
    path = db.StringField()
    output_path = db.StringField(default='')
    output_html_path = db.StringField(default='')
    list_id = db.StringField()
    paper_id = db.StringField()
    date_created = db.DateTimeField(default=datetime.now())
    is_failed = db.BooleanField(default=False)
    is_processed = db.BooleanField(default=False)
    is_downloaded = db.BooleanField(default=False)
    message = db.StringField(default='')
    kernel = db.StringField(default='')
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
    def create_new_notebook(list_id, paper_id, notebook_url):
        """
            Returns new notebook object
        """
        notebook_filename = generate_id() + '.ipynb'
        new_notebook = Notebook(
            original_url=notebook_url,
            filename=notebook_filename,
            path=get_path_to_file(notebook_filename),
            output_path=get_path_to_file(
                'v_output_{0}'.format(notebook_filename)),
            output_html_path=get_path_to_file(
                '{0}.html'.format(notebook_filename)),
            list_id=list_id,
            paper_id=paper_id
        )
        new_notebook.save()
        return new_notebook


    def download_notebook(self):
        """
            Download notebook to uploads folder
        """       
        if self.original_url.find('github.com') > -1:
            self.download_url = self.original_url.replace('/blob/', '/raw/')
        elif self.original_url.find('nbviewer.jupyter.org/github') > -1:
            self.download_url = self.original_url.replace(
                'nbviewer.jupyter.org/github',
                'raw.githubusercontent.com'
            ).replace(
                '/blob/',
                '/'
            )
        elif self.original_url.find('nbviewer.ipython.org/github') > -1:
            self.download_url = self.original_url.replace(
                'nbviewer.ipython.org/github',
                'raw.githubusercontent.com'
            ).replace(
                '/blob/',
                '/'
            )
        else:
            self.download_url = self.original_url

        print(self.download_url)
        print(self.path)

        urllib.urlretrieve(
            self.download_url,
            self.path
        )
        self.is_downloaded = True
        self.save()


    def process_notebook(self):
        """
            Process notebook
        """
        Log.write_log(
            self.list_id,
            self.paper_id,
            self.get_id(),
            'Start process notebook'
        )
        try:
            notebook_file = io.open(self.path, encoding='utf-8')
            notebook_content = nbformat.read(notebook_file, as_version=4)
            # clear outputs
            notebook_content = Notebook.clear_outputs(notebook_content)
            # get kernel name
            kernel_name = notebook_content['metadata']['kernelspec']['name']
            status, tmp_log = install_dependencies(
                str(notebook_content),
                kernel_name
            )

            Log.write_log(
                self.list_id,
                self.paper_id,
                self.get_id(),
                'Install dependencies log: {0}'.format(tmp_log)
            )

            ep = ExecutePreprocessor(
                timeout=60,
                kernel_name=kernel_name
            )
            ep.preprocess(
                notebook_content,
                {'metadata': {'path': get_uploads_path()}}
            )
            message = 'Successfully processed'
            is_failed = False
        except Exception as e:
            message = str(e)
            kernel_name = None if 'kernel_name' not in locals() else kernel_name
            is_failed = True
            notebook_content = False if 'notebook_content' not in locals() else notebook_content
        finally:
            self.kernel = kernel_name
            self.message = message
            self.is_failed = is_failed
            self.is_processed = True
            self.save()
            if notebook_content:
                Log.write_log(
                    self.list_id,
                    self.paper_id,
                    self.get_id(),
                    'Try to write HTML output to file'
                )
                html_exporter = HTMLExporter()
                html_exporter.template_file = 'basic'
                (body, resources) = html_exporter.from_notebook_node(notebook_content)
                f = open(self.output_html_path, 'w')
                rendered_template = render_template('output.html', body=body)
                f.write(rendered_template.encode('utf-8'))
                f.close()
                with io.open(self.output_path, mode='wt', encoding='utf-8') as f:
                    nbformat.write(notebook_content, f)
        return self.get_id()

    @staticmethod
    def clear_outputs(notebook, clear_prompt_numbers=True):
        """
            Clears the output of all cells in an ipython notebook
        """
        for cell in notebook.cells:
            if cell.get('cell_type', None) == 'code':
                cell.outputs = []
                if clear_prompt_numbers is True:
                    cell.execution_count = None
                    cell.pop('prompt_number', None)

        return notebook


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
