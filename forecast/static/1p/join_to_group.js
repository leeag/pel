$('.join_to_group').click(
    function(){
        $.ajax(
            {
                url: "/users_groups/",
                method: 'POST',
                data: {
                    group: ''
                }
            }
        );
    }
);
