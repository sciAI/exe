$(function () {
    var timerId = null;

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
                var container = $('body .container .row');
                container.html('');

                // create timer
                timerId = setInterval(checkResults, 3000, task_id);
            }
        });

        function checkResults(task_id) {
            $.ajax({
                url: '/check-results',
                data: {task_id: task_id},
                type: 'POST',
                success: function(data) {
                    console.log(data);
                    if (data.is_processed) {
                        console.log('IS PROCESSED');
                        clearInterval(timerId);
                    } else {
                        console.log('IS NOT PROCESSED');
                        updateLog(data.results);
                    }
                }
            })
        }

        function updateLog(messages) {
            var container = $('body .container .row');
            for (var i = 0; i < messages.length; i++) {
                container.append('<p>' + messages[i]['message'] + '</p>');
            }
        }

    })
});
