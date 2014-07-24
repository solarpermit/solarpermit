$('.delete_form > a').on("click", function (e) {
    $(e.target).parent().submit();
});
$('.api_button').on("click", function (e) {
    $('.api_button').attr('disabled', 'disabled');
    $(e.target).parent().submit();
});
