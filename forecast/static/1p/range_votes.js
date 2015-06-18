$(function () {
    var opts = {
        range: true,
        values: [10, 100],
        slide: function (event, ui) {
            $("#id_vote_0").val(ui.values[0] + " - " + ui.values[1]);
        }
    };

    var vote0 = $('#id_vote_0');
    var vote1 = $('#id_vote_1');
    opts.min = +$(vote0).attr('min');
    opts.max = +$(vote0).attr('max');

    $("#range_vote").slider(opts);
    $("#id_vote_1").val($("#range_vote").slider("values", 0) +
    " - " + $("#range_vote").slider("values", 1));
});
