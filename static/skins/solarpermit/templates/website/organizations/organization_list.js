//call this script only for the 1st page of list
var selectOrgClick = function (event) {
	var $target = $(event.target);
	$('#org_add_my_btn').removeClass('disabled');
	$('#org_details_btn').removeClass('disabled');
	$('#org_add_my_btn').removeAttr('disabled');
	$('#org_details_btn').removeAttr('disabled');
	$('#select_orgid').val($target.val());
	$('#select_orgname').val($target.data('orgName'));
};
$('#org_list').jscroll({
	callback: function () {
		//since the list changed, bind events only to items with unbind class (new)
		$('.organization_radio.unbind').click(function (event) {
			selectOrgClick(event);
		});
		$('.organization_radio.unbind').removeClass('unbind'); //remove unbind class
	}
});
//initial bind event for list items
$('.organization_radio.unbind').click(function (event) {
	selectOrgClick(event);
});
$('.organization_radio.unbind').removeClass('unbind'); //remove unbind class


	$('.org').click(function() {
		$target = $(event.target);
		var orgId = $target.data('orgid');
		controller.postRequest('/organization/', {ajax: 'choose_org_details', orgid: orgId});
		return false;
					
	});	