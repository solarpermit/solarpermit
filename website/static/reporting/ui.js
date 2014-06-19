$(document).ready(function () {
                    add_ui(reports);
                  });
$("#add-filter").on("click", $.fancybox.close);
$("#add-another").on("click", add_ui);
function add_ui(initial_reports) {
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
  if (initial_reports)
    machine.select(initial_reports);
  function build_selection_ui(event, state) {
    var stuff = $("<div>", { 'class': 'whatsit' }).data("reporting-ui-state-machine",
                                                        machine);
    var question_select = $("#hidden_controls > select").clone()
                                                        .on("change", machine.select);
    var filter_link = $("<a>", { text: "Filter this report...",
                                 href: "#filter_selection" });
    filter_link.on("click",
                   function () {
                     controller.showModalDialog("#filter_selection",
                                                { beforeClose: machine.select });
                   });
    machine.selector_ui = $("<div>", { 'class': 'selector' }).append($("<div>", { 'class': 'busy-indicator' }),
                                                                     question_select,
                                                                     filter_link,
                                                                     $("<div><span class='description'></div>"))
                                                             .appendTo(stuff);
    machine.container = $("<div>").appendTo(stuff);
    stuff.appendTo("#all-reports");
    return 'ui-ready';
  }
  function doSelect(event, state) {
    if (machine.req)
      machine.req.abort();
    machine.selector_ui.addClass("loading");
    var question = machine.selector_ui.find("select").find(":checked").attr("value");
    if (!question)
      return 'ui-ready';
    var states = $("#type-state").is(":checked") && $("#id_states").val();
    var jurisdictions = $("#type-jurisdiction").is(":checked") && $("#id_jurisdictions").val();
    machine.req = $.ajax(buildURL("/reporting/"+ question +"/",
                                  { states: states,
                                    jurisdictions: jurisdictions }),
                         { dataType: 'json' })
                   .done(machine.success)
                   .fail(machine.error);
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
    if ('table' in report) {
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
    }
    return ui;
  }
  function draw_graph(report, container) {
    var values = 'table' in report ? report.table.map(select("value")).filter(defined)
                                   : [],
        sum = values.reduce(function (a, b) { return a+b; }, 0),
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
    } else if (report.type == "pie") {
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
    } else {
      $.ajax({ url: "http://permit01.dev.cpf.com:9001/render/",
               dat: { from: "00:00_20120901",
                      lineMode: "connected",
                      target: "integral(solarpermit.dev.counters.question.coverage.1.answered.count)",
                      format: "json" },
               dataType: "json",
               success: function(data) {
                          console.log(data);
                          graph = r.linechart(0, 0, 160, 160, x, ys);
                        }
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
