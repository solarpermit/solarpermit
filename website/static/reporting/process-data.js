// these functions are all about processing the data series for a
// temporal report into the form needed by g.line.js

function processData(alldata, start, end, enabled) {
  var lines = $.map(alldata,
                    function (line) {
                      return [processSeries(line.datapoints, start, end)];
                    });
  var map = {};
  $.each(lines,
         function (i, line) {
           $.each(line,
                  function (j, point) {
                    if (!(point[1] in map)) {
                      map[point[1]] = [];
                    }
                    map[point[1]][i] = point[0];
                  });
         });
  var x = [];
  var ys = [];
  $.each(map,
         function (stamp, counts) {
           x.push(parseInt(stamp, 10));
         });
  x.sort();
  $.each(x,
         function (i, stamp) {
           var column = map[stamp];
           $.each(column,
                  function (j, value) {
                    if (!ys[j]) {
                      ys[j] = [];
                    }
                    if (typeof value === "undefined")
                      if (i-1 in ys[j])
                        value = ys[j][i-1];
                      else
                        value = 0;
                    ys[j][i] = value;
                  });
         });
  var enabled_ys = [];
  $.each(enabled,
         function (i, checkbox) {
           if (checkbox.checked && ys[i])
             enabled_ys.push(ys[i]);
         });
  return [x, enabled_ys];
}
function processSeries(datapoints, start, end) {
  return filterData($.grep(datapoints,
                           function (p) {
                             return !!p[0];
                           }),
                    start,
                    end);
}
function filterData(datapoints, start, end) {
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
  return new Date(stamp * 1000).toLocaleDateString(window.navigator.userLanguage ||
                                                   window.navigator.language,
                                                   { weekday: "long",
                                                     year: "numeric",
                                                     month: "long",
                                                     day: "numeric"
                                                   });
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
