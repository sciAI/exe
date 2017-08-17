$(function () {
    console.log('Ready to go!');
    $(document).on('change', '.custom-file-input', function () {
        console.log('Changed value of file input');
        $(this).parent().find('.custom-file-control').attr('data-content', $(this).val().replace(/C:\\fakepath\\/i, '').substring(0, 40));
    });
});