function select(field) {
  return function (elem) {
           if (elem.key != 'Total')
             return elem[field];
         };
}
function defined(val) {
  return typeof val != "undefined";
}
function draw_graphs(reports) {
  $.each(reports,
         function (idx, report) {
           var values = report.table.map(select("value")).filter(defined),
               sum = values.reduce(function (a, b) { return a+b; });
           if (sum <= 0)
             return;
           var r = Raphael("graph"+ idx), graph, paths = [];
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
           $("#report"+ idx +" .legend-dot").each(function (idx, elem) {
                                                    var head = $(elem).parent();
                                                    if (head.text() != "Total" &&
                                                        !(is_funky && head.next().text() == "0")) {
                                                      $(elem).css("background-color",
                                                                  $(paths[is_funky ? n++ : idx]).css("fill"));
                                                    }
                                                  });
         });
}
$(document).ready(function () { draw_graphs(reports); });
