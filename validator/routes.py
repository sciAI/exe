"""
    App routes
"""

import re
from flask import Blueprint, render_template, request, redirect, url_for, render_template, jsonify

from validator.models import Log, List, Paper, Notebook
from validator import queue

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
        if request.form['text']:
            list_type = 'text'
            urls_to_papers = request.form['text'].splitlines()
            urls_to_papers = [x.strip()
                              for x in urls_to_papers if not x.strip().isspace()]
        elif 'file' in request.files:
            list_type = 'file'
            file = request.files['file']
            urls_to_papers = []
            if file.filename == '':
                return render_template('upload.html', error="Please paste some URLs/DOIs or attach .csv/.txt file")
        else:
            return render_template('upload.html', error="Please paste some URLs/DOIs or attach .csv/.txt file")
        # Step 2. Add processing in queue
        task = queue.enqueue(
            List.create_list,
            list_type,
            content
        )
        return jsonify(task)
        return redirect(url_for('app_routes.render_results', list_id=11))
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
            "notebooks": tmp_list,
            "url_type": paper.url_type
        })
    return render_template('results.html', results=results)
