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
    var ui = build_ui(report);
    container.append(ui);
    draw_graph(report, ui);
  }
  function build_ui(report) {
    var even_odd = (function () {
                      var n = 0;
                      return function () {
                               n += 1;
                               return (n % 2 === 0) ? 'even' : 'odd';
                             };
                    })();
    var ui = $("<div>", { id: "report"+ report.idx, 'class': "report" }), table, temporal_table;
    ui.append($("<div>", { id: "graph"+ report.idx, 'class': "graph" }));
    if (report.type == "temporal") {
      if ('name' in report && report.name == "coverage")
        report.table = [{ key: "Answered", value: "" }];
      else
        report.table = report.statsd_metrics.map(function (m) {
                                                   return { key: m, value: "" };
                                                 });
    }
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
               if (v.node)
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
                 if (v.value)
                   path_colors[v.value.order] = $(v.node).css("fill");
               });
    } else if (report.type == "temporal" && report.name) {
      var metric = "integral(solarpermit.dev.counters.question."+ report.name +"."+ report.question_id +".answered.count)";
      $.ajax({ url: "http://permit01.dev.cpf.com:9001/render/",
               data: { from: "00:00_20120901",
                       target: metric,
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
                                                                               change: draw
                                                                             });
                          draw();
                          function draw(event, ui) {
                            var s = ui ? ui.values[0] : start,
                                e = ui ? ui.values[1] : end;
                            var cells = container.find(".temporal_table span");
                            $(cells[0]).text(formatStamp(s));
                            $(cells[1]).text(formatStamp(e));
                            var processed = processSeries(data[0].datapoints, s, e);
                            r.clear();
                            graph = r.linechart(0, 0, 320, 320, processed[0], processed[1]);
                            $.each(graph.lines,
                                   function(i, l) {
                                     path_colors[i] = $(l.node).css("stroke");
                                   });
                            container.find("#report"+ idx +" .legend-dot").each(color);
                          }
                          function processSeries(datapoints, start, end) {
                            var gooddata = $.grep(datapoints,
                                                  function (p) {
                                                    return !!p[0];
                                                  });
                            var x = [],
                                ys = [];
                            $.each(filterdata(gooddata, start, end),
                                   function (i, p) {
                                     x.push(p[1]);
                                     ys.push(p[0]);
                                   });
                            return [x, ys];
                          }
                          function filterdata(datapoints, start, end) {
                            var data = $.grep(datapoints,
                                              function (p) {
                                                return start <= p[1] && p[1] <= end;
                                              });
                            if (data.length == 0 || data[0][1] > start) {
                              var earlier = firstBefore(start, datapoints);
                              data.unshift([earlier ? earlier[0] : 0, start]);
                            }
                            if (data[data.length-1][1] < end) {
                              data.push([data[data.length-1][0], end]);
                            }
                            return data;
                          }
                          function firstBefore(timestamp, datapoints) {
                            for (var i = datapoints.length - 1; i >= 0; i--) {
                              if (datapoints[i][1] < timestamp)
                                return datapoints[i];
                            }
                          }
                          function formatStamp(stamp) {
                            if (typeof stamp === "string")
                              stamp = parseInt(stamp, 10);
                            return new Date(stamp * 1000).toLocaleString();
                          }
                          function tomorrow() {
                            d = new Date();
                            d.setUTCDate(d.getUTCDate()+1);
                            d.setUTCHours(0);
                            d.setUTCMinutes(0);
                            d.setUTCSeconds(0);
                            d.setUTCMilliseconds(0);
                            return d.getTime();
                          }
                          function monthago() {
                            d = new Date();
                            d.setUTCDate(d.getUTCMonth()-1);
                            d.setUTCHours(0);
                            d.setUTCMinutes(0);
                            d.setUTCSeconds(0);
                            d.setUTCMilliseconds(0);
                            return d.getTime();
                          }
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
