$(document).ready(function () {
                    show_reports(reports);
                  });
function get_reports(question, filter) {
  $.ajax("/reporting/"+ question +"/",
         { dataType: 'json',
           success: function (data) {
                      show_reports(data);
                    }
         });
}
function show_reports(reports) {
  var container = $("<div>", { 'class': 'whatsit' }).appendTo(".contentOnlyPage");
  $.each(reports,
         function (idx, report) {
           show_report(report, container);
         });
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
  ui.append($("<div>", { id: "graph"+ report.idx }),
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
