$("#id_states").on("change",
		   function (event) {
		       $("#type-state").prop('checked', true);
		   });
$("#id_jurisdictions-deck").on("DOMSubtreeModified",
			       function (event) {
				   $("#type-jurisdiction").prop('checked', true);
			       });
