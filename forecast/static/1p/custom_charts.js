function drawChart(selector, data) {
    if(data.forecastType === 'Finite Event') {
        drawFiniteEventChart(selector, data.votes);
    } else {
        drawProbabilityChart(selector, data.votes);
    }
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

