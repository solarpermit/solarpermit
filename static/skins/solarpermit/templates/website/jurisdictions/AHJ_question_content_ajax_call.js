     
        {% for this_question in custom_questions %}
            //alert({{this_question.id}});
            controller.postRequest('{{action}}', {ajax: 'get_question_content', jurisdiction_id: {{jurisdiction.id}}, question_id: {{this_question.id}} });
        {% endfor %}                        
