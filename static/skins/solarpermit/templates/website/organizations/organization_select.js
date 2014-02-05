$('#search_org').bind('keyup', function (event) {
	var $target = $(event.target);
    if ((event.which != 38) &&
    		(event.which != 40) &&
    		(event.which != 13)) {
    	var searchText = $target.val();
    	if (searchText != ''){
    		search_postion = $('#search_org').position();
    		var top = search_postion.top + 2;
    		$('#cleara-dev').css('top', top + 'px');
    		$('#search_org').css('background-image', 'url("/media/images/x.png")');
    		$('#cleara-dev').show();
    	}	else{
    		$('#cleara-dev').hide();
    		$('#search_org').css('background-image', 'url("/media/images/search.png")');
    	}
    	controller.postRequest('/organization/', {ajax: 'search_org', text: searchText});
    }
});

$('#cleara').bind('click', function(){
	$('#cleara-dev').hide();
	$('#search_org').css('background-image', 'url("/media/images/search.png")');
	$('#search_org').val('');
	controller.postRequest('/organization/', {ajax: 'search_org', text: ''});
});

$('#search_org_sort').click(function (event) {
	var searchText = $('#search_org').val()
	var sort_dir = $('#sort_dir').val()
	if (sort_dir == 'desc'){
		$('#sort_dir').val('asc');
		$('#search_org_sort_dir').addClass('sort-down').removeClass('sort-up');
	}else{
		$('#sort_dir').val('desc');
		$('#search_org_sort_dir').addClass('sort-up').removeClass('sort-down');
	}
		 
    $('#search_org_sort_by_date_added_dir').removeClass('sort-up').removeClass('sort-down');
    controller.postRequest('/organization/', {ajax: 'search_org', text: searchText, sort_dir: sort_dir});

});

$('#search_org_sort_by_date_added').click(function (event) {
	var searchText = $('#search_org').val()
	var sort_by_date_added_dir = $('#sort_by_date_added_dir').val()
	if (sort_by_date_added_dir == 'desc'){
		$('#sort_by_date_added_dir').val('asc');
		$('#search_org_sort_by_date_added_dir').addClass('sort-down').removeClass('sort-up');
	}else{
		$('#sort_by_date_added_dir').val('desc');
		$('#search_org_sort_by_date_added_dir').addClass('sort-up').removeClass('sort-down');
	}
		
    $('#search_org_sort_dir').removeClass('sort-up').removeClass('sort-down');
    controller.postRequest('/organization/', {ajax: 'search_org', text: searchText, sort_by_date_added_dir: sort_by_date_added_dir});

});

$('#organization_select_search_form').submit(function (event) {
	//don't really post form
	event.preventDefault();
});

$('#org_new_btn').click(function (event){
	var $target = $(event.target);
	if (!$target.hasClass('disabled')) {
		controller.postRequest('/organization/', {ajax: 'create_org'});
	}
});

$('#org_cancel_btn').click(function () {
	$.fancybox.close();
});

function add_to_myprofile(){
	var org_id = $('#select_orgid').val();
	controller.postRequest('/organization/', {ajax: 'add_org_to_myprofile', orgid: org_id});
}

$('#org_add_my_btn').click(function (event){
	var $target = $(event.target);
	if ($target.hasClass('disabled')) {
		return;
	}
	var org_name =$('#select_orgname').val();
	var org_id = $('#select_orgid').val();
	controller.showConfirm({
		title: 'Do you want to add '+org_name+' to your profile?',
		message: 'A request to join will be sent to the company or organization administrators, and you will receive an email when your request has been processed.',
		proceedText: 'Add to My Profile',
		cancelText: 'Cancel',
		callback: add_to_myprofile
	});
});

$('#org_details_btn').click(function (event){
	var $target = $(event.target);
	if ($target.hasClass('disabled')) {
		return;
	}
	var org_id = $('#select_orgid').val();
	controller.postRequest('/organization/', {ajax: 'choose_org_details', orgid: org_id});
});

/* testing below */
$('#test_confirm_btn').click(function () {
	controller.showConfirm({
		title: 'This is my Title',
		message: 'This is my message! This is my message! This is my message! This is my message! This is my message! This is my message! This is my message! This is my message! This is my message! This is my message!',
		proceedText: 'Go for It!',
		cancelText: 'Never Mind'
	});
});
$('#test_alert_btn').click(function () {
	controller.showAlert({
		title: 'This is an Alert',
		message: 'Click anywhere on the page to close.'
	});
});

if (typeof placeholder_ie_fix != 'undefined'){
	placeholder_ie_fix('#organization_select_search_form #search_org');
}

