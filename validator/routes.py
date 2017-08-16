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
        # check if the post request has the file part
        if 'file' not in request.files:
            Log.write_log(
                None,
                None,
                None,
                'Someone try to upload not allowed file format'
            )
            return render_template('upload.html', error="Please attach CSV or TXT file")
        file = request.files['file']
        if file.filename == '':
            Log.write_log(
                None,
                None,
                None,
                'Someone try to upload not allowed file format'
            )
            return render_template('upload.html', error="Please attach CSV or TXT file")
        # Step 0. Create a new list file
        new_list = List.create_new_list(file)
        if new_list:            
            # Step 1. Extract links to papers
            urls_to_papers = new_list.extract_list_of_links()
            # Step 2. Extract links to notebooks
            for url_to_paper in urls_to_papers:
                Log.write_log(
                    new_list.get_id(),
                    None,
                    None,
                    'Process paper url: {0}'.format(url_to_paper)
                )
                new_paper = Paper(
                    paper_url=url_to_paper,
                    list_id=new_list.get_id()
                )
                new_paper.save()
                # get NB urls for paper
                notebooks_urls = new_paper.extract_links_to_notebooks()
                for notebook_url in notebooks_urls:
                    # download and process notebook
                    notebook_id = Notebook.process_new_notebook(
                        new_paper.get_id(),
                        notebook_url
                    )
                    print(notebook_id)
            Log.write_log(
                new_list.get_id(),
                new_paper.get_id(),
                None,
                'Processed paper url'
            )
            new_list.is_processed = True
            new_list.save()
            return redirect(url_for('app_routes.render_results', list_id=new_list.get_id()))
        render_template('upload.html', error="Allowed only TXT files")
    return render_template('upload.html')


@app_routes.route('/results/<list_id>', methods=['GET'])
def render_results(list_id):
    """
        Render results of analysis
    """
    papers = Paper.objects(list_id=list_id)
    print('Found {0} processed papers'.format(len(papers)))
    results = []
    for paper in papers:
        notebooks = Notebook.objects(paper_id=paper.get_id())
        print('Found {0} processed notebooks'.format(len(notebooks)))
        tmp_list = []
        for notebook in notebooks:
            tmp_list.append(
                {
                    "id": notebook.get_id(),
                    "filename": notebook.filename,
                    "url": notebook.url,
                    "is_failed": notebook.is_failed,
                    "message": re.sub(r'(\\n)+', '\n', notebook.message).replace('\\n', '<br>')
                }
            )
        results.append({
            "paper_url": paper.paper_url,
            "notebooks": tmp_list
        })
    return render_template('results.html', papers=results)
