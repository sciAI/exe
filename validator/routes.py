"""
    App routes
"""

import re
from flask import Blueprint, render_template, request, redirect, url_for, render_template, jsonify

from validator.models import Task, Log, List, Paper, Notebook

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
            urls = request.form['text'].splitlines()
            urls = [x.strip() for x in urls if not x.strip().isspace()]
        elif 'file' in request.files:
            list_type = 'file'
            urls = request.files['file']
            if urls.filename == '':
                return jsonify({'error': 'Please paste some URLs/DOIs or attach .csv/.txt file'}), \
                    200, {'ContentType': 'application/json'}
                # return render_template('upload.html', error="Please paste some URLs/DOIs or attach .csv/.txt file")
        else:
            return jsonify({'error': 'Please paste some URLs/DOIs or attach .csv/.txt file'}), \
                200, {'ContentType': 'application/json'}
            # return render_template('upload.html', error="Please paste some URLs/DOIs or attach .csv/.txt file")
        # Step 2. Add processing in queue
        task_id = Task.create_task(list_type, urls)
        return jsonify({'task_id': task_id, 'error': ''}), \
            200, {'ContentType': 'application/json'}
        # return redirect(url_for('app_routes.render_results', task_id=task_id))
    return render_template('upload.html')


@app_routes.route('/check-results', methods=['POST'])
def check_results():
    """
        Check results by task ID
    """
    if request.form['task_id']:
        task_id = request.form['task_id']
        papers_list = List.objects(task_id=task_id).first()
        if not papers_list:
            return jsonify({'error': 'No list of papers for this task ID'}), \
                200, {'ContentType': 'application/json'}

        # if still processing return logs
        if not papers_list.is_processed:
            logs = Log.objects(list_id=papers_list.get_id()).order_by('date_created')
            results = {'is_processed': False, 'logs':[]}
            for log in logs:
                results['logs'].append({
                    'id': log.get_id(),
                    'date_created': log.date_created,
                    'message': log.message
                })
            return jsonify(results), 200, {'ContentType': 'application/json'}
        # if processed return results
        papers = Paper.objects(list_id=papers_list.get_id())
        results = {
            
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
        return jsonify(results), 200, {'ContentType': 'application/json'}
    return jsonify({'error': 'No task ID specified in query'}), \
        200, {'ContentType': 'application/json'}


@app_routes.route('/results/<task_id>', methods=['GET'])
def render_results(task_id):
    """
        Render results of analysis
    """
    papers_list = List.objects(task_id=task_id).first()
    if not papers_list or not papers_list.is_processed:
        return 'Still processing or wrong task ID'

    papers = Paper.objects(list_id=papers_list.get_id())
    results = {
        "list_id": papers_list.get_id(), 
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
