var helloRequest = (function($){

  function handleRequest(data) {
    var items = [];
    var id = data[0];

    $.each(JSON.parse(data[1]), function(i, val) {
        
        var req_class = 'old';
        if (parseInt(val.fields.new_request, 10) == 1){
            req_class = 'info';
        }
        items.push('<tr class="' + req_class + '" id="'+ val.pk +'">'
            + '<td class="path">' + val.fields.path + '</td>'
            + '<td>' + val.fields.method + '</td>'
            + '<td>' + val.fields.date + '</td>'
            + '<td class="priority">' + val.fields.priority + '</td>'
            + '<td class="td_click plus" style="cursor: pointer;">\
                    <span class="glyphicon glyphicon-plus" aria-hidden="true">\
                    </span></td>'
            + '<td class="td_click" style="cursor: pointer;">\
                    <span class="glyphicon glyphicon-minus" aria-hidden="true">\
                    </span></td>'
            + '</tr>'
        );
         
   });
   items.sort(function(a, b){
       return parseInt(
           $(a).find('td.priority').text()) > parseInt($(b).find('td.priority').text()) ? -1 : 1;
   });

   var title = $('title').text().split(')')[1] || $('title').text();
   var pre_titile = id ? '(' + id + ')' : '';
   $('#request').find('tbody').html(items);
   $('td').addClass('text-center');
   $('th').addClass('text-center');
   $('title').text(pre_titile + title);
 }

 return {
     loadRequest: function(){
        var viewed = '';
        if ( document.hasFocus() ) {
            viewed = 'yes';
        } 
        $.ajax({
            url: '/requests_ajax/',
            dataType : "json",
            data: {'viewed': viewed},
            success: function(data, textStatus) {
                handleRequest(data);
            },
            error: function(jqXHR) {
                console.log(jqXHR.responseText);
            }
        });
     }
 };
})(jQuery);

$(document).ready(function(){
    helloRequest.loadRequest();
    setInterval(helloRequest.loadRequest, 500);
    
});
