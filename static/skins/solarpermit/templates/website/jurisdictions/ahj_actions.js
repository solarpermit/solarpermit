
        $('.add_to_favorites_'+{{current_question_id}}).click(function(event) 
        {   
            var $target = $(event.target);
            var questionId = $target.data('id');
            var jid = $target.data('jid');    
            $('#add_to_favorites_'+questionId).unbind('click');
            $('#add_to_favorites_'+questionId).attr('disabled', 'disabled');            
            controller.postRequest('.', {ajax: 'add_to_views', jurisdiction_id: jid, question_id: questionId, entity_name: 'favorites', destination: '' });
        });
        
        $('.add_to_quirks_'+{{current_question_id}}).click(function(event) 
        {

            var $target = $(event.target);
            var questionId = $target.data('id');
            var jid = $target.data('jid');   
            $('#add_to_quirks_'+questionId).unbind('click');
            $('#add_to_quirks_'+questionId).attr('disabled', 'disabled');            
            controller.postRequest('.', {ajax: 'add_to_views', jurisdiction_id: jid, question_id: questionId, entity_name: 'quirks', destination: '' });
        });
        
        $('.remove_from_favorites_'+{{current_question_id}}).click(function(event) 
        {   
            var $target = $(event.target);
            var questionId = $target.data('id');
            var jid = $target.data('jid');    
            controller.postRequest('.', {ajax: 'remove_from_views', jurisdiction_id: jid, question_id: questionId, entity_name: 'favorites', destination: '' });
        });
        
        $('.remove_from_quirks_'+{{current_question_id}}).click(function(event) 
        {
            var $target = $(event.target);
            var questionId = $target.data('id');
            var jid = $target.data('jid');    
            controller.postRequest('.', {ajax: 'remove_from_views', jurisdiction_id: jid, question_id: questionId, entity_name: 'quirks', destination: '' });
        });        
        