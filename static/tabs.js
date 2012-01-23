active_tab = function() {
        $("#tabs li").removeClass('active');
        $(this).addClass("active");
        $(".tab_content").hide();
        var selected_tab = $(this).find("a").attr("href");
        $(selected_tab).fadeIn();
        return false;
};

$(document).ready(function(){
    $("#tabs li").click(active_tab);

    $("#split_by_switcher").change(function() {
	    $.post(jQuery.param.querystring(window.location.href,
			    		    'whole=No&splitBy=' + $('#split_by_switcher').val()),
		    function(data) {
			    $('#the_tabs').replaceWith($(data).hide().fadeIn());
			    $("#tabs li").click(active_tab);
		    });
    });
});
