$(document).ready(function (e) {
    $.ajax({
        url: "/forecasts/",
        method: 'GET'
        //async: false

    }).done(function (data) {
        for (var i=0; i<data.length; i++){
            draw_timeseries_chart('#peleus-home-page-chart-'+data[i].id, data[i].votes)
        }
    });
});