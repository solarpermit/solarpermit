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
      }
      var states = filter && filter.type == 'states' && filter.values;
      var jurisdictions = filter && filter.type == 'jurisdictions' && filter.values;

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
      var graph = build_ui(report);
      container.append(graph);
      draw_graph(report, graph);
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
      ui.append($("<div>", { id: "graph"+ report.idx, 'class': "graph" }));
      if (report.type == "temporal") {
        ui.append(table = $("<table>", { 'class': "data_table" }));
        table.append($("<tr class='even'><th class='header_row'>Value</th><th class='header_row_right'>Jurisdictions</th></tr>"));
        $.each(report.table,
               function (i, row) {
                 var tr = $("<tr>", { 'class': even_odd() }),
                     name = "series-"+ i +"-enabled";
                 tr.append($("<th>").append($("<label>", { for: name }).append($("<span>", { 'class': "legend-dot" }),
                                                                               $("<span>", { text: row.key }))),
                           $("<td>").append($("<input>", { type: "checkbox",
                                                           checked: true,
                                                           name: name,
                                                           'class': name })));
                 table.append(tr);
               });
      } else {
        if ('table' in report) {
          ui.append(table = $("<table>", { 'class': "data_table" }));
          table.append($("<tr class='even'><th class='header_row'>Value</th><th class='header_row_right'>Jurisdictions</th></tr>"));
          report.table.forEach(function (row) {
                                 var tr = $("<tr>", { 'class': even_odd() });
                                 tr.append($("<th>").append($("<span>", { 'class': "legend-dot" }),
                                                            $("<span>", { text: row.key })),
                                           $("<td>").append($("<span>", { text: row.value })));
                                 table.append(tr);
                               });
        }
      }
      if (report.type == "temporal") {
        ui.append(temporal_table = $("<table>", { 'class': "data_table temporal_table" }),
                  $("<div>", { 'class': 'date-slider' }));
        temporal_table.append($("<tr class='even'><th class='header_row'>From</th><th class='header_row_right'>To</th></tr>"),
                              $("<tr>", { 'class': "odd" }).append($("<td>").append($("<span>", { html: "&nbsp;" })),
                                                                   $("<td>").append($("<span>", { html: "&nbsp;" }))));
      }
      return ui;
    }
    function draw_graph(report, container) {
      var values = 'table' in report ? report.table.map(select("value")).filter(defined)
                                     : [],
          sum = values.reduce(function (a, b) { return a+b; }, 0),
          idx = report.idx;
      var r = Raphael(container.find("#graph"+ idx).get(0)), graph, path_colors = [];
      if (report.type == "histogram") {
        if (sum <= 0)
          return;
        graph = r.barchart(0, 0, 320, 320, values);
        $.each(graph.bars,
               function(k, v) {
                 if (v.node && report.table[k].key != "Total")
                   path_colors[k] = $(v.node).css("fill");
               });
      } else if (report.type == "pie") {
        if (sum <= 0)
          return;
        graph = r.piechart(160, 160, 150, values);
        var is_funky = graph.series.length == 1;
        if (is_funky)
          path_colors = [$(graph.series[0].node).css("fill")];
        else
          $.each(graph.series,
                 function(k, v) {
                   if (v.value && report.table[k].key != "Total")
                     path_colors[v.value.order] = $(v.node).css("fill");
                 });
      } else if (report.type == "temporal" && report.name) {
        var metrics = $.map(report.statsd_metrics,
                            function (metric) {
                              return "integral(solarpermit.counters.question."+ report.name +"."+ report.question_id +"."+ metric.toLowerCase() +".count)";
                            });
        $.ajax({ url: "http://permit01.dev.cpf.com:8080/render/",
                 data: { from: "00:00_20120601",
                         target: metrics,
                         format: "json" },
                 dataType: "json",
                 success: function(data) {
                            var max = tomorrow() / 1000,
                                min = Date.UTC(2013,6,13) / 1000;
                            var end = max,
                                start = min; //Math.max(monthago() / 1000, min);
                            var slider = container.find(".date-slider").slider({ range: true,
                                                                                 min: min,
                                                                                 max: max,
                                                                                 values: [ start, end ],
                                                                                 step: 86400,
                                                                                 slide: draw,
                                                                                 change: draw
                                                                               });
                            var checkboxes = container.find("input[type=checkbox]");
                            checkboxes.on("change", draw);
                            draw();
                            function draw(event, ui) {
                              var s = ui ? ui.values[0] : start,
                                  e = ui ? ui.values[1] : end;
                              var cells = container.find(".temporal_table span");
                              $(cells[0]).text(formatStamp(s));
                              $(cells[1]).text(formatStamp(e));
                              var processed = processData(data, s, e, checkboxes);
                              r.clear();
                              if (!(processed[0].length && processed[1].length))
                                return;
                              graph = r.linechart(0, 0, 320, 320, processed[0], processed[1], { snapEnds: false });
                              $.each(graph.lines,
                                     function(i, l) {
                                       if (l.node)
                                         path_colors[i] = $(l.node).css("stroke");
                                     });
                              var color_idx = 0;
                              container.find(".legend-dot")
                                       .each(function (idx, elem) {
                                               if (checkboxes[idx].checked)
                                                 color(color_idx++, elem);
                                               else
                                                 $(elem).css("background-color", "transparent");
                                             });
                            }
                          }
               });
      }
      var n = 0;
      container.find(".legend-dot").each(color);
      function color(idx, elem) {
        var head = $(elem).parent();
        if (!(is_funky && head.next().text() == "0")) {
          $(elem).css("background-color",
                      path_colors[is_funky ? n++ : idx]);
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
          fillBox.empty();
          $.ajax('/autocomplete/JurisdictionGetNames/?q=' + filter.values.join('&q='),
                 { success: function(selectedItems) {
                              var choices = JSON.parse(selectedItems);
                              $.each(choices,
                                     function(index, jurisdiction) {
                                       var newOption = $("<option></option>",
                                                         { 'data-value': jurisdiction.id }).text(jurisdiction.display);
                                       var selectedOption = $("<option></option>",
                                                              { value: jurisdiction.id, selected: 'selected' });
                                       fillBox.append(newOption);
                                       $("#id_jurisdictions").append(selectedOption);
                                     });
                            }
                 });
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
