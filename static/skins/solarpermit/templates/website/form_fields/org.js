	var global_member_id = '';
	var global_org_id = '';
    $('#add_org').click(function(){
        controller.postRequest('/organization/', {ajax: 'open_choose_org'}); 
        return false;
    });  

	$('.org_edit_link').click(function(event){
		$target = $(event.target);
		var orgId = $target.data('orgid');
		controller.postRequest('/organization/', {ajax: 'open_org_details', orgid: orgId });
		return false;
	});                                            
        
	$('.invited_to_join').click(function(event){
		$target = $(event.target);
		var orgId = $target.data('orgid');
		controller.postRequest('/organization/', {ajax: 'open_org_details', orgid: orgId });
		return false;
	});                                            
               
	$('.accept_invite').click(function(event){
		$target = $(event.target);
		var memberId = $target.data('memberid');
		var orgId = $target.data('orgid');
		var orgName = $target.data('orgname');		
		global_member_id = memberId;
		accept_invite (orgName, org_id, memberId);
		
		return false;
	});    
	
	$('.decline_invite').click(function(event){
		$target = $(event.target);
		var memberId = $target.data('memberid');
		var orgId = $target.data('orgid');
		var orgName = $target.data('orgname');	
		global_member_id = memberId;
		decline_invite (orgName, org_id, memberId);
		
		return false;
	});           	                
		
	$('.org_details').click(function(event){
		$target = $(event.target);
		var orgId = $target.data('orgid');
		controller.postRequest('/organization/', {ajax: 'open_org_details', orgid: orgId });
		return false;
	});             
	
	$('.cancel_request').click(function(event){
		$target = $(event.target);
		var orgId = $target.data('orgid');
		var orgName = $target.data('orgname');	
		global_org_id = orgId;
		cancel_my_request(orgName, orgId);
		return false;
	});      
	
	$('.org_remove').click(function(event){
		$target = $(event.target);
		var memberId = $target.data('memberid');
		var orgId = $target.data('orgid');
		var orgName = $target.data('orgname');			
		global_member_id = memberId;
		remove_from_my_profile (orgName, org_id, memberId);
		return false;
	});       	
	

	$('.other_user_profile').click(function(event){
		$target = $(event.target);
	    controller.postRequest('/account/', {ajax: 'other_user_profile'});
		return false;
	});    	              
	
		function remove_request()
		{
			controller.postRequest('/organization/', {ajax: 'remove_from_my_profile', mid: global_member_id, caller:'user_profile'});
		}

		function remove_from_my_profile (org_name, org_id, member_id)
		{
		        controller.showConfirm({
		            title: 'Do you want to remove  '+org_name+' from your profile?',
		            message: '<br>',
		            proceedText: 'Remove from My Profile ',
		            cancelText: 'Cancel',
		            callback: remove_request
		        });
		}	
	  
	          

		function cancel_request()
		{
			controller.postRequest('/organization/', {ajax: 'cancel_org_request', orgid: global_org_id, caller:'user_profile'});
		}
      
		function cancel_my_request (org_name, org_id)
		{
		        controller.showConfirm({
		            title: 'Do you want to cancel your request to join  '+org_name+'?',
		            message: '<br>',
		            proceedText: 'Yes, cancel my request',
		            cancelText: 'No, do not cancel my request',
		            callback: cancel_request
		        });
		}
		
		function accept_invitation(member_id)
		{
			controller.postRequest('/organization/', {ajax: 'accept_invite', mid: global_member_id, caller:'user_profile'});
		}

		function accept_invite (org_name, org_id, member_id)
		{
		        controller.showConfirm({
		            title: 'Do you want to accept the invitation to join  '+org_name+'?',
		            message: '<br>',
		            proceedText: 'I accept ',
		            cancelText: 'Cancel',
		            callback: accept_invitation
		        });
		}			

		function decline_invitation()
		{
			controller.postRequest('/organization/', {ajax: 'decline_invite', mid: global_member_id, caller:'user_profile'});
		}

		
		function decline_invite (org_name, org_id, member_id)
		{
		        controller.showConfirm({
		            title: 'Do you want to decline the invitation to join  '+org_name+'?',
		            message: '<br>',
		            proceedText: 'I decline ',
		            cancelText: 'Cancel',
		            callback: decline_invitation
		        });
		}			