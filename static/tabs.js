$(document).ready(function(){
    $("#tabs li").click(function() {
        $("#tabs li").removeClass('active');
        $(this).addClass("active");
        $(".tab_content").hide();
        var selected_tab = $(this).find("a").attr("href");
        $(selected_tab).fadeIn();
        return false;
    });

    $("#split_by_switcher").change(function() {
	    $.post(jQuery.param.querystring(window.location.href,
			    		    'template=tabs.html&splitBy=' + $('#split_by_switcher').val()),
		    function(data) {
			    $('#the_tabs').replaceWith($(data).hide().fadeIn());
		    });
    });
});
