$(document).ready(function (e) {
    $.ajax({
        url: "/forecasts/",
        method: 'GET',
        data: urlDataFromIds()

    }).done(function (data) {
        for (var i=0; i<data.length; i++){
            drawChart('#peleus-home-page-chart-'+data[i].id, data[i])
        }
    });
});
