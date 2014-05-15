
$('#close_sec_dialog').click(function(event) {
	controller.closeSecondDialog();
    return false;
});

$('#accept').click(function(event) {
    {# for forum bridge integration #}
    {% if FORUM_INTEGRATION == True %}
    // LSS:
        controller.submitForm('#form_create_account', function(data) {
            controller.lsslogin1(
                $('#form_create_account_field_username').val(), 
                $('#form_create_account_field_password').val(),
                data
            );
        }, null, true);

    //END LSS:
    
    {% else %}
        controller.submitForm('#form_create_account');
    {% endif %}
    
    controller.closeSecondDialog();
    return false;
});