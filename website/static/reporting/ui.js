(function () {
  var historyState = new stateHistory(deserializeReports,
				      serializeReports,
				      resetUIs);
  
  $(document).ready(function () {
    var reports = historyState.getState();
    
    if (reports) {
      $.each(reports,
	     function (index, report) {
	       add_ui(report);
	     });
    } else {
      add_ui();
    }
  });
  $("#add-filter").on("click", $.fancybox.close);
  $("#add-another").on("click", add_ui);
  function add_ui(initial_report) {
    var machine = new StateMachine('reporting-ui',
				   'uninitialized',
				   { 'uninitialized': { 'init': build_selection_ui },
				     'ui-ready': { 'select': doSelect },
				     'loading': { 'success': show_reports,
						  'error': show_error,
						  'select': doSelect },
				     'reports-ready': { 'select': doSelect }
				   });
    machine.init();
    if (initial_report) {
      machine.select(initial_report);
    }
    function build_selection_ui(event, state) {
      var container = $("<div>", { 'class': 'whatsit' });
      var stuff = container.data("reporting-ui-state-machine",
					 machine);
      var question_select = $("#hidden_controls > select").clone()
	  .on("change", machine.select);
      var filter_link = $("<a>", { text: "Filter this report...",
				   href: "javascript:void(0);" });
      filter_link.on("click",
		     function () {
		       controller.showModalDialog("#filter_selection",
						  { beforeShow:
			    function() {
			      setupFilterDialog(container);
			    },
						    beforeClose:
			    function() {
			      saveFilter(container);
			      machine.select(); } });
		     });

      if (initial_report && initial_report.filter) {
	$(container).data("filter", initial_report.filter);
      }

      machine.selector_ui = $("<div>", { 'class': 'selector' }).append($("<div>", { 'class': 'busy-indicator' }),
								       question_select,
								       filter_link,
								       $("<div><span class='description'></div>"))
	.appendTo(stuff);
      machine.container = $("<div>").appendTo(stuff);
      stuff.appendTo("#all-reports");
      return 'ui-ready';
    }
    function doSelect(event, state, rest) {
      
      var filter = {};
      
      if (machine.req)
	machine.req.abort();
      machine.selector_ui.addClass("loading");
      if (rest && rest.question) {
	var question = rest.question;
	machine.selector_ui.find("select").find('[value='+question+']').attr('selected', true);
	filter = rest.filter || {};
      } else {
	var question = machine.selector_ui.find("select").find(":checked").attr("value");
	filter = machine.selector_ui.closest('.whatsit').data('filter');
/*	var states = $("#type-state").is(":checked") && $("#id_states").val();
	var jurisdictions = $("#type-jurisdiction").is(":checked") && $("#id_jurisdictions").val();
	if (states) {
	  filter = { type: 'states', values: states };
	} else if (jurisdictions) {
	  filter = { type: 'jurisdictions', values: jurisdictions };
	}*/
      }
      var states = filter.type == 'states' && filter.values;
      var jurisdictions = filter.type == 'jurisdictions' && filter.values;
      
      if (!question)
	return 'ui-ready';
      
      machine.req = $.ajax(buildURL("/reporting/"+ question +"/",
				    { states: states,
				      jurisdictions: jurisdictions }),
			   { dataType: 'json' })
	.done(machine.success)
	.fail(machine.error);
      
      if (!rest || !rest.question) {
	updateStateHistory();
      }
      
      return 'loading';
    }
    function show_error(event, state) {
      machine.container.empty();
      var again = $("<a>", { text: "Try again" }).on("click", machine.select);
      $("<span>", { text: "Oops, there was an error." }).append(again)
	.appendTo(machine.container);
      machine.selector_ui.removeClass("loading");
      return 'ui-ready';
    }
    function show_reports(event, state, data) {
      machine.container.empty();
      if (data.description)
	machine.selector_ui.find(".description").html(data.description);
      else
	machine.selector_ui.find(".description").empty();
      $.each(data.reports,
	     function (idx, report) {
	       show_report(report, machine.container);
	     });
      machine.selector_ui.removeClass("loading");
      return 'reports-ready';
    }
    function show_report(report, container) {
      container.append(build_ui(report));
      draw_graph(report, container);
    }
    function build_ui(report) {
      var even_odd = (function () {
	var n = 0;
	return function () {
	  n += 1;
	  return (n % 2 === 0) ? 'even' : 'odd';
	};
      })();
      var ui = $("<div>", { id: "report"+ report.idx, 'class': "report" }), table;
      ui.append($("<div>", { id: "graph"+ report.idx, 'class': "graph" }),
		table = $("<table>", { 'class': "data_table" }));
      table.append($("<tr class='even'><th class='header_row'>Value</th><th class='header_row_right'>Jurisdictions</th></tr>"));
      report.table.forEach(function (row) {
	var tr = $("<tr>", { 'class': even_odd() });
	tr.append($("<th>").append($("<span>", { 'class': "legend-dot" }),
				   $("<span>", { text: row.key })),
		  $("<td>").append($("<span>", { text: row.value })));
	table.append(tr);
      });
      return ui;
    }
    function draw_graph(report, container) {
      var values = report.table.map(select("value")).filter(defined),
	  sum = values.reduce(function (a, b) { return a+b; }),
	  idx = report.idx;
      if (sum <= 0)
	return;
      var r = Raphael(container.find("#graph"+ idx).get(0)), graph, paths = [];
      if (report.type == "histogram") {
	graph = r.barchart(0, 0, 320, 320, values);
	$.each(graph.bars,
	       function(k, v) {
		 if (v.node)
		   paths[k] = v.node;
	       });
      } else {
	graph = r.piechart(160, 160, 150, values);
	var is_funky = graph.series.length == 1;
	if (is_funky)
	  paths = [graph.series[0].node];
	else
	  $.each(graph.series,
		 function(k, v) {
		   if (v.value)
		     paths[v.value.order] = v.node;
		 });
      }
      var n = 0;
      container.find("#report"+ idx +" .legend-dot").each(color);
      function color(idx, elem) {
	var head = $(elem).parent();
	if (head.text() != "Total" &&
	    !(is_funky && head.next().text() == "0")) {
	  $(elem).css("background-color",
		      $(paths[is_funky ? n++ : idx]).css("fill"));
	}
      }
    }
    function select(field) {
      return function (elem) {
	if (elem.key != 'Total')
	  return elem[field];
      };
    }
    function defined(val) {
      return typeof val != "undefined";
    }
  }

  function buildURL(base, params) {
    var kv = [];
    $.each(params,
	   function (key, values) {
	     if ($.isArray(values)) {
	       $.each(values,
		      function (i, value) {
			if (value)
			  kv.push([key, encodeURIComponent(value)]);
		      });
	     } else {
	       if (values)
		 kv.push([key, encodeURIComponent(values)]);
	     }
	   });
    kv = kv.map(function (param) { return param[0] +'='+ param[1]; });
    if (kv)
      base += '?' + kv.join('&');

    return base;
  }

  function resetUIs() {
    var currentUIs = document.querySelectorAll(".whatsit");
    var reports = historyState.getState();

    $.each(currentUIs,
	   function (index, item) {
	     item.parentNode.removeChild(item);
	   });

    $.each(reports,
	   function (index, report) {
	     add_ui(report);
	   });
  }

  function updateStateHistory() {
    var reportContainers = document.querySelectorAll('.whatsit');
    var newState = [];

    $.each(reportContainers,
	   function(index, container) {
	     var $container = $(container);
	     var question = $container.find("select").find(":checked").attr("value");
	     var filter = $container.data("filter");

	     newState.push({ question: question, filter: filter });
	   });
    
    historyState.pushState(newState);
  }
  
  function serializeReports(params) {
    var reports = [];
    
    $.each(params,
	   function (index, item) {
	     var question = item.question;
	     var result = question;
	     
	     if (item.filter && item.filter.type && item.filter.values) {
	       var filterType = item.filter.type;
	       var filterValues = item.filter.values;
	       
	       result += ":" + filterType + "=" + filterValues.join(',');
	     }
	     
	     reports.push(result);
	   });
    
    return reports.join(';');
  }
  
  function deserializeReports(paramstring) {
    var reports = paramstring.split(';');
    var newState = [];
    
    $.each(reports,
	   function(index, report) {
	     var result = {};
	     var parts = report.split(':');
	     
	     result['question'] = parts[0];
	     
	     if (parts[1]) {
	       var filter = parts[1].split('=');
	       if (filter[1]) {
		 var filterValues = filter[1].split(',');
		 result['filter'] = { type: filter[0], values: filterValues };
	       }
	     }
	     
	     newState.push(result);
	   });
    
    return newState;
  }

  function setupFilterDialog(container) {
    var filter = container.data("filter");

    if (filter) {
      if (filter.type == 'states') {
	$("#type-state").prop('checked', true);
	$("#id_states").val(filter.values);
	$("#type-jurisdiction").prop('checked', false);
	$("#id_jurisdictions").val('');
      } else if (filter.type == 'jurisdictions') {
	var fillBox = $("#id_jurisdictions-deck");
	$("#type-state").prop('checked', false);
	$("#id_states").val('');
	$("#type-jurisdiction").prop('checked', true);
	if (!$("#id_jurisdictions").val() && filter.values) {
	  $.ajax('/jurisdiction/?id=' + filter.values.join(','),
		 { success:
		   function(selectedItems)
		   {
		     $.each(selectedItems,
			    function(index, jurisdiction) {
			      var newOption = $("<option></option>", { 'data-value': jurisdiction.id }).text(jurisdiction.display);
			      var selectedOption = $("<option></option>", { value: jurisdiction.id, selected: 'selected' })
			      
			      fillBox.append(newOption);
			      $("#id_jurisdictions").append(selectedOption);
			    });
		   } });
	}
      }
    }
  }

  function saveFilter(container) {
    var filter = {};
    var states = $("#type-state").is(":checked") && $("#id_states").val();
    var jurisdictions = $("#type-jurisdiction").is(":checked") && $("#id_jurisdictions").val();
    
    if (states) {
      filter = { type: 'states', values: states };
    } else if (jurisdictions) {
      filter = { type: 'jurisdictions', values: jurisdictions };
    }

    container.data("filter", filter);
  }
  
})();
