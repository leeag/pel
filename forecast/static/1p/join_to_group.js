$(document).ready(function (e) {
    $('.join_to_group').click(
        function(e){
            var group_id = $(this).attr('group-id');
            $.ajax(
                {
                    url: "/join_group/",
                    method: 'GET',
                    data:{
                        group: group_id
                    },
                    success: function () {
                        $('#join_'+group_id).hide("slow");
                        $('#joined_group_'+group_id).show("slow");
                    },
                    error: function() {
                        $('#join_error_' + group_id).show("slow");

                    }

                });
        });
});
