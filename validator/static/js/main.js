/*
##############################################################################
#
#   sci.AI EXE
#   Copyright(C) 2017 sci.AI
#
#   This program is free software: you can redistribute it and / or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or(at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY
#   without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.If not, see < http://www.gnu.org/licenses/ >.
#
##############################################################################
*/

$(function () {
    var timerId = null;
    var body = $("html, body");
    var container = $('.main-block .row');
    var logContainer = $('.logs-block .row').hide();
    var latestLogId = '000000000000000000000000';

    console.log('Ready to go!');
    // update placeholder for file input
    $(document).on('change', '.custom-file-input', function () {
        console.log('Changed value of file input');
        $(this).parent().find('.custom-file-control').attr(
            'data-content',
            $(this).val().replace(/C:\\fakepath\\/i, '').substring(0, 40)
        );
    });

    // upload form button listener
    $('.main-form button').click(function (e) {
        console.log('Submit main form');
        e.preventDefault();
        var fd = new FormData($('.main-form')[0]);

        $.ajax({
            url: '/upload',
            data: fd,
            processData: false,
            contentType: false,
            type: 'POST',
            success: function (data) {
                if (data['error']) {
                    $('.form-control-feedback').html(data['error']);
                    return;
                }
                var task_id = data.task_id;
                container.hide();
                logContainer.show();

                // create timer
                timerId = setInterval(checkResults, 3000, task_id);
            }
        });

        function checkResults(taskId) {
            $.ajax({
                url: '/check-results',
                data: { task_id: taskId, latest_log_id: latestLogId},
                type: 'POST',
                success: function(data) {
                    console.log(data);
                    if (data.is_processed) {
                        console.log('IS PROCESSED');
                        clearInterval(timerId);
                        updateLog([
                            {message: '<a style="color:red" target="_blank" href="/results/' + taskId + '">Click here to open your report</a>',
                            date_created: data.date_updated}]);
                    } else {
                        console.log('IS NOT PROCESSED');
                        if (data.error) {
                            updateLog([
                                {
                                    message: data.error,
                                    date_created: (new Date()).toString()
                                }
                            ]);
                            clearInterval(timerId);
                            return;
                        } if (data.warning) {
                            updateLog([
                                {
                                    message: data.warning,
                                    date_created: (new Date()).toString()
                                }
                            ]);
                            clearInterval(timerId);
                            // re-run interval after 30 seconds
                            setTimeout(function() {
                                timerId = setInterval(checkResults, 3000, taskId);
                            }, 30000);
                        } else if (data.logs.length) {
                            latestLogId = data.logs[data.logs.length - 1]['id'];
                            updateLog(data.logs);
                        }
                    }
                }
            })
        }

        function updateLog(messages) {
            for (var i = 0; i < messages.length; i++) {
                var msg = messages[i];
                logContainer.append('<p>[' + msg['date_created'] + ']:' + msg['message'] + '</p>');
                body.animate({ scrollTop: $(document).height() }, 100)
            }
        }

    })
});
