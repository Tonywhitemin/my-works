$(document).ready(function(){
    var element = $('#submit');
    $('button.loading').hide();
    $('#submit').click(function () {
        element.toggleClass('zoomOut animated');
        element.one('webkitAnimationEnd mozAnimationEnd MSAnimationEnd oanimationend animationend', function(e){
        $(e.target).removeClass('zoomOut animated');
        $("button.submit").hide();

        });
    });
})
$(document).ready(function(){
    $('#submit').click(function () {
        document.addEventListener('click',function(){
            $("button.loading").show();
        },true);
        $('#ok').click(function () {
            $("button.loading").show();
        });
    });
})