    var uploader_input = document.getElementById("file-uploader");
    if (uploader_input != null) {
        var uploader = new qq.FileUploader(
            {
                element: document.getElementById("file-uploader"),
                action: "/organization/logo/org_uploadfile/",
                customHeaders: {"X-CSRFToken": js_csrf },
                debug: true,
                multiple: false,
                uploadButtonText: "Upload Logo",
                onComplete: function(id, fileName, response) {
                                if (response.error){
                                		$(".qq-upload-failed-text").html(response.error);
                                    $("#filename").val();
                                    return;
                                } else {
                                    $("#filename").val(fileName);
                                    $("#id_logo").val(fileName).trigger("change");
                                    if($("#error_message").is(":visible"))     $("#error_message").hide();
                                    $("#file_store_name").val(response.store_name);
                                    $("#thum_logo").empty().append("<img src='"+response.thum_path+"' alt='logo' >");
                                }
                            },
                            params: {
                                'csrfmiddlewaretoken': js_csrf,
                              }
        });
    }

$(function() {
$( "#tabs" ).tabs();
});

{% for admin in org_admins %}
$('#id_admin_'+{{admin.id}}).bind('mouseover', function(){controller.postRequest('/account/', {ajax: 'user_profile_short', user_id: {{admin.user.id}}, unique_list_id: 'admin_{{admin.id}}', caller:'dialog' });});
{% endfor %}

function add_to_myprofile(){
	var org_id = {{organization.id}};
	controller.postRequest('/organization/', {ajax: 'add_org_to_myprofile', orgid: org_id});
}

$('#org_members_list').jscroll({
	callback: function () {
		//since the list changed, bind events only to items with unbind class (new)
		
	}
});

$('#org_members_list1').jscroll({
	callback: function () {
		//since the list changed, bind events only to items with unbind class (new)
		
	}
});

$('#org_details_add_my_btn').click(function (){
	var org_name = '{{organization.name}}';
	var org_id = '{{organization.id}}';
	controller.showConfirm({
		title: 'Do you want to add '+org_name+' to your profile?',
		message: 'A request to join will be sent to the company or organization administrators, and you will receive an email when your request has been processed.',
		proceedText: 'Add to My Profile',
		cancelText: 'Cancel',
		callback: add_to_myprofile
	});
	return false;
});

function accept_invite_from_org_details(){
	var member_id = '{{orgmember.id}}';
	controller.postRequest('/organization/', {ajax: 'accept_invite', mid: member_id});
}

$('#fancybox_close').click(function() {
	$.fancybox.close();
});

$('#org_details_accept_btn').click(function (){
	var org_name = '{{organization.name}}';
	var org_id = '{{organization.id}}';
	controller.showConfirm({
		title: 'Do you want to accept the invitation to join  '+org_name+'?',
		message: '<br>',
		proceedText: 'I accept ',
		cancelText: 'Cancel',
		callback: accept_invite_from_org_details
	});
	return false;
});

function decline_invite_from_org_details(){
	var member_id = '{{orgmember.id}}';
	controller.postRequest('/organization/', {ajax: 'decline_invite', mid: member_id});
}

$('#org_details_decline_btn').click(function (){
	var org_name = '{{organization.name}}';
	var org_id = {{organization.id}};
	controller.showConfirm({
		title: 'Do you want to decline the invitation to join  '+org_name+'?',
		message: '<br>',
		proceedText: 'I decline ',
		cancelText: 'Cancel',
		callback: decline_invite_from_org_details
	});
	return false;
});

function remove_org_member_from_org_details(){
	var member_id = '{{orgmember.id}}';
	controller.postRequest('/organization/', {ajax: 'remove_from_my_profile', mid: member_id});
}

$('#remove_org_member_btn').click(function (){
	var org_name = '{{organization.name}}';
	var org_id = {{organization.id}};
	controller.showConfirm({
		title: 'Do you want to remove  '+org_name+' from your profile?',
		message: '<br>',
		proceedText: 'Remove from My Profile ',
		cancelText: 'Cancel',
		callback: remove_org_member_from_org_details
	});
	return false;
});

$('#remove_admin_org_admin_btn').click(function (){
	var org_name = '{{organization.name}}';
	var org_id = {{organization.id}};
	controller.showConfirm({
		title: 'Do you want to remove  '+org_name+' from your profile?',
		message: '<br>',
		proceedText: 'Remove from My Profile ',
		cancelText: 'Cancel',
		callback: remove_org_member_from_org_details
	});
	return false;
});

function cancel_request(){
	var org_id = '{{organization.id}}';
	controller.postRequest('/organization/', {ajax: 'cancel_org_request', orgid: org_id});
}

$('#cancel_request_btn').click(function (){
	var org_name = '{{organization.name}}';
	var org_id = {{organization.id}};
	controller.showConfirm({
		title: 'Do you want to cancel your request to join  '+org_name+'?',
		message: '<br>',
		proceedText: 'Yes, cancel my request',
		cancelText: 'No, do not cancel my request',
		callback: cancel_request
	});
	return false;
});

function delete_org(){
	var org_id = '{{organization.id}}';
	controller.postRequest('/organization/', {ajax: 'delete_org', orgid: org_id});
}

$('#delete_org_btn').click(function (){
	var org_name = '{{organization.name}}';
	var org_id = {{organization.id}};
	controller.showConfirm({
		title: 'Do you want to delete '+org_name+' from the system?',
		message: "Deleting this company or organization will expunge all membbers and administrators, and cannot be undone.<p><input type='checkbox' name='yes_delete' id='yes_delete' value='1'> Yes, I want to delete this company or organization.</p>",
		proceedText: 'Delete',
		cancelText: 'Cancel',
		checkboxSelector: '#yes_delete',
		callback: delete_org
	});
	return false;
});

function change_right(){
	var org_id = {{organization.id}};
	var va = $('#selected_change_member').val();
	var right_value = $('#id_role_'+va).val();
	//controller.postRequest('/organization/', {ajax: 'change_org_right', orgid: org_id, mid:va, value:right_value});
}

function cancel_change_right(){
	var va = $('#selected_change_member').val();
	var old_value = $('#id_role_'+va).data('oldValue');
	$('#id_role_'+va).unbind('change');
	$('#id_role_'+va).val(old_value);
	$('#id_role_'+va).bind('change', function(){
		$('#selected_change_member').val($(this).data('memberId'));
		controller.showConfirm({
			title: 'You have made changes you need to save.',
			message: '<br>',
			proceedText: 'Save',
			cancelText: 'Cancel',
			callback: change_right,
			cancelcallback: cancel_change_right
		});
	});
}

$('#tabs1_a').click(function() {
	orgid = $(this).data('orgid');
	controller.postRequest('/organization/', {ajax: 'org_details', orgid: orgid});
});

$('#tabs2_a').click(function() {
	orgid = $(this).data('orgid');
	controller.postRequest('/organization/', {ajax: 'pending_request', orgid: orgid});
});

$('#org_details_cancel_btn').click(function() {
	return controller.postRequest('/organization/', {ajax: 'choose_org'});
});

$('#org_details_close_btn').click(function() {
	$.fancybox.close();
});

$('#invite_btn').click(function (){
	orgid = $(this).data('orgid');
	controller.postRequest('/organization/', {ajax: 'select_users', orgid: orgid}); 
	return false;
});

$('#save_orgname').click(function() {
	controller.submitForm('#form_org_details_orgname');
	return false;
});

$("#form_org_details_orgname").submit(function (event){
	controller.submitForm('#form_org_details_orgname');
	return false;
})

$('#save_logo').click(function(ev) {
	disabled_save = $(this).attr('disabled');
    if (disabled_save === 'disabled') {
    	return false;
    }
	$('#save_logo').attr('disabled', 'disabled');
	controller.submitForm('#form_org_details_logo');
	return false;
});

$("#form_org_details_logo").submit(function (event){
	//event.preventDefault();
	controller.submitForm('#form_org_details_logo');
	return false;
})

$('#save_website').click(function() {
	controller.submitForm('#form_org_details_website'); 
	return false;
});

$("#form_org_details_website").submit(function (event){
	controller.submitForm('#form_org_details_website');
	return false;
})

	$('#choose_org').click(function() {
		$target = $(event.target);
		controller.postRequest('/organization/', {ajax: 'choose_org'});
		return false;
					
	});	
	
	$('#select_users').click(function() {
		$target = $(event.target);
		var orgId = $target.data('orgid');
		controller.postRequest('/organization/', {ajax: 'select_users', orgid: orgId});
		return false;
					
	});				
