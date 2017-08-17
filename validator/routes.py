"""
    App routes
"""

import re
from flask import Blueprint, render_template, request, redirect, url_for, render_template, jsonify

from validator.models import Log, List, Paper, Notebook

app_routes = Blueprint(
    'app_routes',
    __name__,
    template_folder='templates'
)


@app_routes.route('/', methods=['GET', 'POST'])
@app_routes.route('/upload', methods=['GET', 'POST'])
def upload_file():
    """
        Upload file
    """
    if request.method == 'POST':
        # Step 0. Create a new list
        new_list = List.create_new_list()
        if request.form['text']:
            new_list.update_type('text')
            urls_to_papers = request.form['text'].splitlines()
            urls_to_papers = [x.strip()
                              for x in urls_to_papers if not x.strip().isspace()]
        elif 'file' in request.files:
            new_list.update_type('file')
            file = request.files['file']
            if file.filename == '':
                return render_template('upload.html', error="Please paste some URLs/DOIs or attach .csv/.txt file")
            update_status = new_list.update_file(file)    
            if update_status:        
                # Step 1. Extract links to papers
                urls_to_papers = new_list.extract_list_of_links()
            else:
                # in case of not allowed file format
                return render_template('upload.html', error="Unallowed file format. Please attach .csv/.txt file")
        else:
            return render_template('upload.html', error="Please paste some URLs/DOIs or attach .csv/.txt file")
        # Step 2. Extract links to notebooks
        for url_to_paper in urls_to_papers:
            new_paper = Paper.create_new_paper(new_list.get_id(), url_to_paper)
            # get NB urls for paper
            notebooks_urls = new_paper.extract_links_to_notebooks()
            for notebook_url in notebooks_urls:
                # download and process notebook
                notebook = Notebook.create_new_notebook(
                    new_list.get_id(),
                    new_paper.get_id(),
                    notebook_url
                )
                notebook.download_notebook()
                notebook.process_notebook()

            new_paper.update_status(True)
        new_list.is_processed = True
        new_list.save()
        return redirect(url_for('app_routes.render_results', list_id=new_list.get_id()))
    return render_template('upload.html')


@app_routes.route('/results/<list_id>', methods=['GET'])
def render_results(list_id):
    """
        Render results of analysis
    """
    papers = Paper.objects(list_id=list_id)
    results = {
        "list_id": list_id, 
        "papers": []
    }
    for paper in papers:
        notebooks = Notebook.objects(paper_id=paper.get_id())
        tmp_list = []
        for notebook in notebooks:
            tmp_list.append(
                {
                    "id": notebook.get_id(),
                    "filename": notebook.filename,
                    "url": notebook.original_url,
                    "is_failed": notebook.is_failed,
                    "message": re.sub(r'(\\n)+', '\n', notebook.message).replace('\\n', '<br>')
                }
            )
        results["papers"].append({
            "paper_url": paper.original_url,
            "notebooks": tmp_list
        })
    return render_template('results.html', results=results)
