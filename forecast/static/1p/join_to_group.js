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
                    success: function (data) {
                        //console.log("DATA", data);
                        if(data == 'request'){
                            $('#join_'+group_id).hide("slow");
                            $('#request_to_group_'+group_id).show("slow");
                        }else if(data == 'followed'){
                            $('#join_'+group_id).hide("slow");
                            $('#joined_group_'+group_id).show("slow");
                        }
                    },
                    error: function() {
                        $('#join_error_' + group_id).show("slow");

                    }

                });
        });
});
