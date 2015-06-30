$('#active_forecasts').on('shown.bs.modal', function () {
    $.ajax({
        url: "/profile_forecasts/{{ profile.id }}/",
        method: 'GET',
        data: {
            filter: 'active'
        }
    }).done(function (data) {
        $('#active-set-modal').html(data);
        $.ajax({
            url: "/forecasts/",
            method: 'GET',
            data: urlDataFromIds()

        }).done(function (data) {
            for (var i = 0; i < data.length; i++) {
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
}).on('hidden.bs.modal', function () {
    $('#active-set-modal').empty()
});

$('#archived_forecasts').on('shown.bs.modal', function () {

    $.ajax({
        url: "/profile_forecasts/{{ profile.id }}/",
        method: 'GET',
        data: {
            filter: 'archived'
        }
    }).done(function (data) {
        $('#archived-set-modal').html(data);

        $.ajax({
            url: "/forecasts/",
            method: 'GET',
            data: urlDataFromIds()

        }).done(function (data) {
            for (var i = 0; i < data.length; i++) {
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

}).on('hidden.bs.modal', function () {
    $('#archived-set-modal').empty()
});


$('#active_forecasts').on('shown.bs.modal', function () {
    $.ajax({
        url: "/profile_forecasts/{{ profile.id }}/",
        method: 'GET',
        data: {
            filter: 'active'
        }
    }).done(function (data) {
        $('#active-set-modal').html(data);
        $.ajax({
            url: "/forecasts/",
            method: 'GET',
            data: urlDataFromIds()

        }).done(function (data) {
            for (var i = 0; i < data.length; i++) {
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
}).on('hidden.bs.modal', function () {
    $('#active-set-modal').empty()
});

$('#archived_forecasts').on('shown.bs.modal', function () {

    $.ajax({
        url: "/profile_forecasts/{{ profile.id }}/",
        method: 'GET',
        data: {
            filter: 'archived'
        }
    }).done(function (data) {
        $('#archived-set-modal').html(data);

        $.ajax({
            url: "/forecasts/",
            method: 'GET',
            data: urlDataFromIds()

        }).done(function (data) {
            for (var i = 0; i < data.length; i++) {
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

}).on('hidden.bs.modal', function () {
    $('#archived-set-modal').empty()
});