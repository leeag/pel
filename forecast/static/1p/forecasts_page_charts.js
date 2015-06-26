$(document).ready(function (e) {
    $.ajax({
        url: "/forecasts/",
        method: 'GET',
        data: urlDataFromIds()

    }).done(function (data) {
        for (var i=0; i<data.length; i++) {
            (function (i) {
                $('#collapseOne-' + data[i].id).on('shown.bs.collapse', function () {
                    drawChart('#peleus-forecast-' + data[i].id, data[i]);
                }).on('hidden.bs.collapse', function () {
                    $('#peleus-forecast-' + data[i].id).empty();
                });
            })(i);
        }
    });
});
