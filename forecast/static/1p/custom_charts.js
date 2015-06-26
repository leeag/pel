function drawChart(selector, data) {
    if(data.votes.length !== 0) {
        if (data.forecastType === 'Finite Event') {
            drawFiniteEventChart(selector, data.votes);
        } else if (data.forecastType === 'Magnitude') {
            drawMagnitudeChart(selector, data.votes);
        } else {
            drawProbabilityChart(selector, data.votes);
        }
    } else {
        $(selector).html('<div class="text-center"><h4>There are no forecasts<h4></div>')
    }
}

function urlDataFromIds() {
    var ids = $('.forecast-chart').map(function() {return $(this).attr('forecast-id') }).get();
    return ids.map(function (el) { return 'id=' + el}).join('&')
}

function transformJsonToColumns(json) {
    var columns = [];

    json.forEach(function(item) {
       var column = [];
        column.push(item.choice);
        column.push(item.votesCount);
        columns.push(column);
    });

    return columns;
}

function drawProbabilityChart(selector, data) {
    var chart = c3.generate({
        bindto: selector,
        data: {
            json: data,
            keys: {
                x: 'date',
                value: ['avgVotes']
            },
            type: 'spline'
        },
        axis: {
            x: {
                type: 'timeseries',
                tick: {
                    format: '%Y-%m-%d',
                    rotate: 80,
                    multiline: false
                }
            },
            y: {
                min: 0,
                max: 100,
                padding: {
                    top: 0,
                    bottom: 0
                }
            }
        }
    });
}

function drawMagnitudeChart(selector, data) {
    var chart = c3.generate({
        bindto: selector,
        data: {
            json: data,
            keys: {
                x: 'date',
                value: ['avgVotes']
            },
            type: 'spline'
        },
        axis: {
            x: {
                type: 'timeseries',
                tick: {
                    format: '%Y-%m-%d',
                    rotate: 80,
                    multiline: false
                }
            },
            y: {
                padding: {
                    top: 10,
                    bottom: 10
                }
            }
        }
    });
}

function drawFiniteEventChart(selector, data) {
    var chart = c3.generate({
        bindto: selector,
        data: {
            columns: transformJsonToColumns(data),
            //keys: {
            //    x: 'choice',
            //    value: ['votesCount']
            //},
            type: 'bar'
        },

        axis: {
            x: {
                show: false
        //        type: 'category'
            }
        }
    });
}

