$(function () {
    var timerId = null;
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
                timerId = setInterval(checkResults, 3000, task_id, latestLogId);
            }
        });

        function checkResults(taskId, latestLogId) {
            $.ajax({
                url: '/check-results',
                data: { task_id: taskId, latest_log_id: latestLogId},
                type: 'POST',
                success: function(data) {
                    console.log(data);
                    if (data.is_processed) {
                        console.log('IS PROCESSED');
                        clearInterval(timerId);
                        updateLog(['<a style="color:red" href="/results/' + taskId + '">Click here to open your report</a>']);
                    } else {
                        console.log('IS NOT PROCESSED');
                        latestLogId = data.logs[data.logs.length-1]['id'];
                        updateLog(data.logs);
                    }
                }
            })
        }

        function updateLog(messages) {
            for (var i = 0; i < messages.length; i++) {
                var msg = messages[i];
                logContainer.append('<p>[' + msg['date_created'] + ']:' + msg['message'] + '</p>');
            }
        }

    })
});
