controller.setUpFormSubmit('#form_{{question_id}}', '#save_{{question_id}}');
controller.setUpFormSubmit('#form_edit_{{answer_id}}', '#save_edit_{{answer_id}}');

var fee_flat_rate_html = "<div class='field'>$ <input type='text' name='field_fee_flat_rate_xxx_yyy' id='{{form_id}}_field_fee_flat_rate_xxx_yyy' value='' class='required number' style='width:50px' maxLength='50' ></div><div class='field_help_text' >Enter the flat rate fee.</div>      ";
var fee_percentage_of_total_system_cost_html = "<div class='field'><input type='text' name='field_fee_percentage_of_total_system_cost_xxx_yyy' id='{{form_id}}_field_fee_percentage_of_total_system_cost_xxx_yyy' value='' required number' style='width:50px' maxLength='50' > %</div><div class='field'><input type='checkbox' name='field_fee_percentage_of_total_system_cost_cap_xxx_yyy' id='{{form_id}}_field_fee_percentage_of_total_system_cost_cap_xxx_yyy' value='yes' >This cost is capped at $ <input type='text' name='field_fee_percentage_of_total_system_cost_cap_amt_xxx_yyy' id='{{form_id}}_field_fee_percentage_of_total_system_cost_cap_amt_xxx_yyy' value='' class='number' style='width:50px' maxLength='50' ></div><div class='field_help_text' >Enter the percentage of total system, and the cap amount, if necessary.</div>"; 

var fee_jurisdiction_cost_recovery_notes_html = "<div class='field'><textarea name='field_fee_jurisdiction_cost_recovery_notes_xxx_yyy' id='{{form_id}}_field_fee_jurisdiction_cost_recovery_notes_xxx_yyy' rows='3' cols='25' class='required '></textarea></div><div class='field_help_text' >Enter the jurisdiction cost recovery notes.</div><div class='error_div'></div>     "; 
var fee_per_component_html = "<div class='field'>$ <input type='text' name='field_fee_per_inverter_xxx_yyy' id='{{form_id}}_field_fee_per_inverter_xxx_yyy' value='0' class='required number' style='width:50px' maxLength='50' > per inverter</div><div class='field'>$ <input type='text' name='field_fee_per_module_xxx_yyy' id='{{form_id}}_field_fee_per_module_xxx_yyy' value='0' class='required number' style='width:50px' maxLength='50' > per module</div><div class='field'>$ <input type='text' name='field_fee_per_major_components_xxx_yyy' id='{{form_id}}_field_fee_per_major_components_xxx_yyy' value='0' class='required number' style='width:50px' maxLength='50' > per other major components</div><div class='field'><input type='checkbox' name='field_fee_per_component_cap_xxx_yyy' id='{{form_id}}_field_fee_per_component_cap_xxx_yyy' value='yes'   >This cost is capped at $ <input type='text' name='field_fee_per_component_cap_cap_amt_xxx_yyy' id='{{form_id}}_field_fee_per_component_cap_cap_amt_xxx_yyy' value='' class='number' style='width:50px' maxLength='50' ></div><div class='field_help_text' >Enter the fee per component, and the cap amount, if necessary.</div><div id='fee_per_component_error_xxx_yyy' class='unique_error_div' ></div>";                     
                    
                    
var fee_other_html = "<div class='field'><textarea name='field_fee_other_xxx_yyy' id='{{form_id}}_field_fee_other_xxx_yyy' rows='3' cols='25' class='required' ></textarea></div><div class='field_help_text' >Enter the fee amt, calculation, etc...</div> ";

var fee_type_html = "<div class='form_field' ><div class='label'>Fee type:</div> <div class='field'><input type='text' name='field_fee_type_xxx' id='{{form_id}}_field_fee_type_xxx' value='' class='required' style='width:190px' maxLength='200' ></div><div class='field_help_text' >Enter the name of the fee type</div></div>  ";
//var fee_item_item_html = "<div class='form_field' ><div class='label'>Fee item:</div> <div class='field'><input type='text' name='field_fee_item_xxx_yyy' id='{{form_id}}_field_fee_item_xxx_yyy' value='' class='required' style='width:190px' maxLength='200' ></div><div class='field_help_text' >Enter the name of the fee item</div></div>  ";
// dummy placeholder for fee item
var fee_item_item_html = "<input type='hidden' name='field_fee_item_xxx_yyy' id='{{form_id}}_field_fee_item_xxx_yyy' value='fee item'  > ";

var fee_details_html = "<div class='form_field' id='fee_formulas_xxx_yyy' > <div class='label'>Formula:</div><div class='field'><select name='field_fee_formula_xxx_yyy' id='select_fee_formula_xxx_yyy'  ><option value='flat_rate' selected  >Flat Rate</option><option value='percentage_of_total_system_cost'  >Percentage of total system cost</option><option value='fee_per_component'  >Fee per component</option><option value='jurisdiction_cost_recovery' >Jurisdiction cost recovery</option><option value='other' >Other</option></select></div></div>";
fee_details_html = fee_details_html + "<div id='fee_details_xxx_yyy' ><div class='form_field' > " + fee_flat_rate_html +  "<div class='error_div'></div></div></div>";

var add_fee_item_btn_html = "<input type='button' name='add_another_fee_item_btn_xxx'  id='add_another_fee_item_btn_xxx' class='smallbutton'  title=''  value='+ Add another cost' > ";    
     

var fee_type_count = {{highest_fee_type_id}};
var highest_fee_item_ids = Array();
{% for key in highest_fee_item_ids.keys() %}
highest_fee_item_ids[{{key}}] = {{highest_fee_item_ids.get(key)}};
{% endfor %}

function add_fee_type_row()
{
	fee_type_count = fee_type_count + 1;
	fee_type_str = fee_type_html.replace(/xxx/g, fee_type_count);
	var row = $("<tr>");
	row.append( $("<td width='100%' colspan='2'>").html(fee_type_str));
	$("#fee_{{answer_id}}").append(row);
	highest_fee_item_ids[fee_type_count] = 0;
}

function add_fee_item_row(fee_type_id)
{	//alert('add fee item row');
	highest_fee_item_id = highest_fee_item_ids[fee_type_id] + 1;
	fee_item_item_html_str = fee_item_item_html.replace(/xxx/g, fee_type_id);
	fee_item_item_html_str = fee_item_item_html_str.replace(/yyy/g, highest_fee_item_id);
	
	fee_details_html_str = fee_details_html.replace(/xxx/g, fee_type_id);
	fee_details_html_str = fee_details_html_str.replace(/yyy/g, highest_fee_item_id);	
	var row = $("<tr>");
	//row.append( $("<td width='50%' valign='top'>").html(fee_item_item_html_str));
	row.append( $("<td width='100%' valign='top' colspan='2' >").html(fee_item_item_html_str+fee_details_html_str));	
	
	btn_id = "add_another_fee_item_btn_zzz_tr".replace(/zzz/g, fee_type_id);
	////alert(btn_id);
	$("#"+btn_id).before(row);
	
	////alert(highest_fee_item_id);
	$("#select_fee_formula_"+fee_type_id+'_'+highest_fee_item_id).live("change", function(event) {
		//id = fee_type_id+'_'+highest_fee_item_id;
		//alert('select_fee_formula');
		$target = $(event.target);
	
		id = $target.attr('id');
		//alert(id);
		if (id.indexOf('select_fee_formula_') >= 0)
		{
			array_strs = id.split('select_fee_formula_');
			if (array_strs.length >= 2)
			{			
				fee_item_id = array_strs[1];
				//alert(fee_item_id);
				onchange_select_fee_formula(fee_item_id);
			}
		}
	});		
	
	highest_fee_item_ids[fee_type_id] = highest_fee_item_id
}

function add_add_fee_item_btn_row()
{
	add_fee_item_btn_str = add_fee_item_btn_html.replace(/xxx/g, fee_type_count);
	var row = $("<tr id='add_another_fee_item_btn_"+fee_type_count+"_tr'>");
	row.append( $("<td width='100%' colspan='2'>").html(add_fee_item_btn_str));
	$("#fee_{{answer_id}}").append(row);
	
	$("#add_another_fee_item_btn_"+fee_type_count).live("click", function() {
	    add_fee_item_row(fee_type_count);
	});		
	////alert('xxx');
}

function add_divider_row()
{
	var row = $("<tr>");
	row.append( $("<td width='100%' colspan='2'>").html('<hr>'));
	$("#fee_{{answer_id}}").append(row);
}

$('.smallbutton').click(function(event) {
	////alert('add fee item');
	$target = $(event.target);
	////alert('after target');
	id = $target.attr('id');
	////alert(id);
	if (id.indexOf('add_another_fee_item_btn_') >= 0)
	{
		array_strs = id.split('add_another_fee_item_btn_');
		if (array_strs.length >= 2)
		{
			fee_type_id = array_strs[1];
			////alert(fee_type_id);
			add_fee_item_row(fee_type_id);
		}

	}
});

$('#add_another_fee_type_btn').click(function(event) {
	//////alert('add fee type');
	$target = $(event.target);
	////alert(fee_type_count);
	add_fee_type_row();
	////alert(fee_type_count);
	add_add_fee_item_btn_row();	
	add_fee_item_row(fee_type_count);

	add_divider_row();
});


$('.select_fee_formula').change(function(event) {
	//alert('select_fee_formula');
	$target = $(event.target);

	id = $target.attr('id');
	//alert(id);
	if (id.indexOf('select_fee_formula_') >= 0)
	{
		array_strs = id.split('select_fee_formula_');
		if (array_strs.length >= 2)
		{
			fee_item_id = array_strs[1];
			//alert(fee_item_id);
			onchange_select_fee_formula(fee_item_id);
		}
	}
	
});

function onchange_select_fee_formula(fee_item_id)
{
	//alert(fee_item_id);
	value = $("#select_fee_formula_"+fee_item_id).val();
	array_strs = fee_item_id.split('_');
	if (array_strs.length >= 2)
	{
		fee_type_id = array_strs[0];
		fee_item_id = array_strs[1];
		change_fee_details(fee_type_id, fee_item_id, value);
	}
}

function change_fee_details(fee_type_id, fee_item_id, value)
{
	if (value == 'flat_rate')
	{	
		html_str = fee_flat_rate_html;	
	}
	else if (value == 'percentage_of_total_system_cost')
	{	
		html_str = fee_percentage_of_total_system_cost_html;		
	}
	else if (value == 'fee_per_component')
	{	
		html_str = fee_per_component_html
	}	
	else if (value == 'jurisdiction_cost_recovery')
	{	
		html_str = fee_jurisdiction_cost_recovery_notes_html
	}		
	else if (value == 'other')
	{	
		html_str = fee_other_html	
	}

	html_str = html_str.replace(/xxx/g, fee_type_id);
	html_str = html_str.replace(/yyy/g, fee_item_id);		
	html_str = "<div class='form_field' >" + html_str + "<div class='error_div'></div>   </div>";
	document.getElementById('fee_details_'+fee_type_id+'_'+fee_item_id).innerHTML = html_str;	
}


var submitCount_q_{{question_id}} = 0;
var submitCount_a_{{answer_id}} = 0;

$('#save_{{question_id}}').click(function(event) {
	if (++submitCount_q_{{question_id}} == 1)
	{	
		if (validate_fee_form())
		{
			var success = controller.submitHandler(event, submitCount_q_{{question_id}});	
			if (success == false)
				submitCount_q_{{question_id}} = 0;
		}
	}

	return false;
});

$('#save_edit_{{answer_id}}').click(function(event) {
	if (++submitCount_a_{{answer_id}} == 1)
	{
		if (validate_fee_form())
		{
			var success = controller.submitHandler(event, submitCount_a_{{answer_id}});	
			if (success == false)
				submitCount_a_{{answer_id}} = 0;
		}
	}
	
	return false;
});




function validate_fee_form()
{	
	var validated = true;
	$("input[id^=form_16_field_fee_per_inverter_]").each(function() {

		id  = $(this).attr('id');
		array_strs = id.split('form_16_field_fee_per_inverter_');
		if (array_strs.length >= 2)
		{		
			fee_item_id = array_strs[1];
			if (!validate_fee_per_components(fee_item_id))
			{
				$('#fee_per_component_error_'+fee_item_id).html('At least one fee is required');
				set_fee_per_component_error(fee_item_id);
				validated = false;
			}
			else
			{
				$('#fee_per_component_error_'+fee_item_id).html('');		
				init_fee_per_component_error(fee_item_id);	
			}
		}
	});
	
	return validated;
}

function validate_fee_per_components(fee_item_id)
{
	fee_per_inverter_str = 'form_16_field_fee_per_inverter_'+fee_item_id;
	fee_per_module_str = 'form_16_field_fee_per_module_'+fee_item_id;
	fee_per_major_components_str = 'form_16_field_fee_per_major_components_'+fee_item_id;	

	if (($('#'+fee_per_inverter_str).val() != '' && $('#'+fee_per_inverter_str).val() != '0') 
		|| ($('#'+fee_per_module_str).val() != ''  && $('#'+fee_per_module_str).val() != '0') 
		|| ($('#'+fee_per_major_components_str).val() != ''  && $('#'+fee_per_major_components_str).val() != '0') ) 
	{
		$('#'+fee_per_inverter_str).removeClass('required');
		$('#'+fee_per_module_str).removeClass('required');
		$('#'+fee_per_major_components_str).removeClass('required');				
            
        return true;
	}
	else
	{
		//alert('At least one field is required');
		$('#'+fee_per_inverter_str).removeClass('required');
		$('#'+fee_per_module_str).removeClass('required');
		$('#'+fee_per_major_components_str).removeClass('required');			
		return false;
	}		
	
}

function set_fee_per_component_error(fee_item_id)
{
	fee_per_inverter_str = 'form_16_field_fee_per_inverter_'+fee_item_id;
	fee_per_module_str = 'form_16_field_fee_per_module_'+fee_item_id;
	fee_per_major_components_str = 'form_16_field_fee_per_major_components_'+fee_item_id;	

	document.getElementById(fee_per_inverter_str).style.backgroundColor="#FCC";
	document.getElementById(fee_per_module_str).style.backgroundColor="#FCC"; 
	document.getElementById(fee_per_major_components_str).style.backgroundColor="#FCC"; 	

}

function init_fee_per_component_error(fee_item_id)
{
	fee_per_inverter_str = 'form_16_field_fee_per_inverter_'+fee_item_id;
	fee_per_module_str = 'form_16_field_fee_per_module_'+fee_item_id;
	fee_per_major_components_str = 'form_16_field_fee_per_major_components_'+fee_item_id;	

	document.getElementById(fee_per_inverter_str).style.backgroundColor="";
	document.getElementById(fee_per_module_str).style.backgroundColor=""; 
	document.getElementById(fee_per_major_components_str).style.backgroundColor=""; 	

}


var disable_pre_validation = true;
