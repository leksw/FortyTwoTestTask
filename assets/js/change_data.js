var csrftoken = $.cookie('csrftoken');

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}


$(document).ready(function(){
    $('.datepicker').datepicker({dateFormat: 'yy-mm-dd'});
    
    function block_form() {
        $("#loading").show();
        $('textarea').attr('disabled', 'disabled');
        $('input').attr('disabled', 'disabled');
    }

    function unblock_form() {
        $('#loading').hide();
        $('textarea').removeAttr('disabled');
        $('input').removeAttr('disabled');
        $('.errorlist').remove();
    }
    
    function beforeSendHandler(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
        block_form();
    }
    

    
    var validator = $('#person-form').validate({
        rules:{
            focusInvalid: false,
            focusCleanup: true,
            name: {
                required: true,
                minlength: 3,
                maxlength: 16
            },
            surname: {
                required: true,
                minlength: 3,
                maxlength: 16
            },
            date_of_birth: {
                required: true,
                date: true
            },
            email: {
                required: true,
                email: true
            },
            image: {
                required: false,
                accept: 'image/*'
            }
            },
        submitHandler: function(form) {
            var formData = new FormData($(form)[0]);
            $.ajax({
                url: $(form).attr('action'),
                type: $(form).attr('method'),
                data: formData,
                cache: false,
                contentType: false,
                processData: false,
                beforeSend: beforeSendHandler,
                xhr: function () {
                    var xhr = new window.XMLHttpRequest();
                    //Upload Progress
                    xhr.upload.addEventListener("progress", function (evt) {
                        if (evt.lengthComputable) {
                        var percentComplete = (evt.loaded / evt.total) * 100; 
                        $('div.progress > div.progress-bar')
                                .css({ "width": percentComplete + "%" });
                        }
                    }, false);
                 
                    
                    return xhr;
                },
            })
            .done(function(e){
                var new_person = JSON.parse(e);
                var image_link = new_person[0].fields.image;
                $('#personImage').attr('src', '/uploads/'+ image_link);
                unblock_form();
                $("#form_ajax").show();
                
                $('.datepicker').focus();
                setTimeout(function() {
                    $("#form_ajax").hide();
                }, 5000);
                
           })
            .fail(function(data){
                unblock_form();
                $("#form_ajax_error").show();
                var errors = JSON.parse(data.responseText);
                $.each(errors, function(i, val) {
                   var id = '#id_' + i;
                    $(id).parent('div').prepend(val);
                });
                setTimeout(function() {
                    $("#form_ajax_error").hide();
                }, 5000);
            });
            return false;
        }
    });
    $("#cancel").click(function() {
        validator.resetForm();
        $('.errorlist').remove();
        
    });
});