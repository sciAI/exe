#!/usr/bin/env python2
# -*- coding: utf-8 -*-
##############################################################################
#
#   sci.AI EXE
#   Copyright(C) 2017 sci.AI
#
#   This program is free software: you can redistribute it and / or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY
#   without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see < http://www.gnu.org/licenses/ >.
#
##############################################################################

"""
    App routes
"""

import re
from flask import Blueprint, render_template, request, redirect, url_for, render_template, jsonify

from validator.models import Task, Log, List, Paper, Notebook
from validator.utils import is_allowed_file, generate_id, get_path_to_file

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
            file = request.files['file']
            if not file or file.filename == '' or not is_allowed_file(file.filename):
                return jsonify({'error': 'Please paste some URLs/DOIs or attach .csv/.txt file'}), \
                    200, {'ContentType': 'application/json'}
                # return render_template('upload.html', error="Please paste some URLs/DOIs or attach .csv/.txt file")
            urls = generate_id() + '.csv'
            file.save(get_path_to_file(urls))
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
    if request.form['task_id'] and request.form['latest_log_id']:
        task_id = request.form['task_id']
        latest_log_id = request.form['latest_log_id']
        papers_list = List.objects(task_id=task_id).first()
        if not papers_list:
            task = Task.objects(task_id=task_id).first()
            if not task:
                return jsonify({'error': 'No task with specified ID: {0}'.format(task_id)}), \
                    200, {'ContentType': 'application/json'}
            return jsonify({'warning': 'Your list is still in the queue. Processing can take some time, so please be patient. The log will be updated every 30 seconds.'}), \
                200, {'ContentType': 'application/json'}

        # if still processing return logs
        if not papers_list.is_processed:
            logs = Log.objects(
                list_id=papers_list.get_id(),
                id__gt=latest_log_id
            ).order_by('date_created')

            # To fix: search by task ID written in list_id
            if not logs:
                logs = Log.objects(
                    list_id=task_id,
                    id__gt=latest_log_id
                ).order_by('date_created')

            results = {'is_processed': False, 'logs':[]}
            for log in logs:
                results['logs'].append({
                    'id': log.get_id(),
                    'date_created': log.date_created,
                    'message': log.message.replace('/opt/jupyter-testing/', './').replace('\n', '<br />')
                })
            return jsonify(results), 200, {'ContentType': 'application/json'}
        # if processed return results
        papers = Paper.objects(list_id=papers_list.get_id())
        results = {
            'is_processed': True,
            'date_updated': papers_list.date_updated
        }
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
                    "message": re.sub(r'(\\n)+', '\n', notebook.message).replace('\n', '<br>')
                }
            )
        results["papers"].append({
            "paper_url": paper.original_url,
            "notebooks": tmp_list,
            "url_type": paper.url_type
        })
    return render_template('results.html', results=results)



@app_routes.route('/logs/<task_id>', methods=['GET'])
def render_logs(task_id):
    """
        Render results of analysis
    """
    papers_list = List.objects(task_id=task_id).first()
    if not papers_list or not papers_list.is_processed:
        return 'Still processing or wrong task ID'

    notebooks = Notebook.objects(list_id=papers_list.get_id())
    
    if not notebooks:
        return 'No notebooks for this task found'

    results = []

    for notebook in notebooks:
        logs = Log.objects(notebook_id=notebook.get_id()).all()
        results.append({
            "id": notebook.get_id(),
            "notebook": notebook,
            "logs": logs
        })
    
    return render_template('logs.html', results=results)
