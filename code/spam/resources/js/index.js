$.fn.serializeObject = function() {
    var o = {};
    var a = this.serializeArray();
    $.each(a, function() {
        if (o[this.name]) {
            if (!o[this.name].push) {
                o[this.name] = [o[this.name]];
            }
            o[this.name].push(this.value || '');
        } else {
            o[this.name] = this.value || '';
        }
    });
    return o;
};
// common functions for all pages
window.toggleLoader = function (turn_on) {
	if(turn_on){
        $('body').addClass('loading');
		$('#loader, #loader-bg').removeClass('d-none');
    }
	else{
        $('body').removeClass('loading');
		$('#loader, #loader-bg').addClass('d-none');
    }
};

window.formSubmitter = function(evt) {
    evt.preventDefault();
    // var data = $(evt.target).serializeObject();

    var formData = new FormData();
    // process form
    $(evt.target).find('input, textarea, select').each(function() {
        var $el = $(this);
        if ($el.attr('type') == 'file') {
            var el = $el.get(0),
                ins = el.files.length;

            for (var x = 0; x < ins; x++) {
                formData.append($el.attr('name'), el.files[x]);
            }
        } else {
            // debugger;
            var name = $el.attr('name'), val = $el.val() || $el.html() || '';
            // skip unchecked
            if( ($el.attr('type') == 'checkbox' || $el.attr('type') == 'radio' ) && !$el.is(':checked')){
                return true;
            }
            formData.append(name, val);
        }
    });

    var data = formData;


    var url = $(evt.target).attr('action');

    toggleLoader(true);
    $('.alert-container').html('');

    axios.post(url, data)
        .then(function(response) {
            var type = response.data.success ? 'success' : 'error';
            showAlert(type, response.data.message);
            $(evt.target).find('textarea').html('');
            // var html = '';
            // if (response.data.success) {
            //     // html = $('.alert-templates .success').html();
            // } else {
            //     // html = $('.alert-templates .error').html();
            // }
            // html = html.replace('{text}', response.data.message);
            // $('.alert-container').html(html);
        })
        .catch(function(error) {
            // console.log('error:', error.response.data);
            var exception = error.response.data.exception || '';
            var file = error.response.data.file || '';
            var text = error.response.data.message + '<br>' + (exception ? exception + '<br>' : '' ) + (file ? file + '<br/>' : '');
            showAlert('error', text);
            // var html = $('.alert-templates .error').html().replace('{text}', text);
            // // console.log(error);
            // $('.alert-container').html(html);
        })
        .then(function() {
            // always executed
            toggleLoader(false);
        });

    // console.log(data);
    return false; //don't submit
};

// success, error
window.showAlert = function(template_class, text, error_text){
    var html = $('.alert-templates .'+template_class).html().replace('{text}', text);
    $('.alert-container').html(html);
};

var socksUpdater = null;
var getSockStats = function(){
    axios.get('/api/socks_stats')
    .then(function(data){
        // console.log('got data for socks stats:', data);
        let my_data = data.data.message;

        $('.navbar .socks-smtp .counter').html(': ' + my_data.smtp);
        $('.navbar .socks-dead .counter').html(': ' + my_data.dead);
        $('.navbar .socks-banned .counter').html(': ' + my_data.banned);
        $('.navbar .socks-unchecked .counter').html(': ' + my_data.unchecked);

        // process shells data
        $('.navbar .nav-item.shells').addClass('d-none');

        if( my_data.shells.clear_all ){
            $('.navbar .nav-item.shells.shells-clearing').removeClass('d-none');
        }else if( my_data.shells.removing && !my_data.shells.clear_all ){
           $('.navbar .nav-item.shells.shells-removing').removeClass('d-none');
        }
        // upload and remove are processed separately
        if( my_data.shells.started && my_data.shells.stopped ){
            $('.navbar .nav-item.shells.shells-stopping').removeClass('d-none');
        }else if( my_data.shells.started && !my_data.shells.stopped ){
            $('.navbar .nav-item.shells.shells-started').removeClass('d-none');
        }else if( !my_data.shells.started && my_data.shells.stopped ){
            $('.navbar .nav-item.shells.shells-stopped').removeClass('d-none');
        }else{
            $('.navbar .nav-item.shells.shells-stopped').removeClass('d-none');
        }

        // process smtp sending data
        $('.navbar .nav-item.smtps').addClass('d-none');
        if( Number(my_data.smtp_send.started) > 1 ){
            $('.navbar .nav-item.smtps.smtp-sending').removeClass('d-none');
        }else if( Number(my_data.smtp_send.started) == 1 ){
            $('.navbar .nav-item.smtps.smtp-preparing').removeClass('d-none');
        }else{
            $('.navbar .nav-item.smtps.smtp-idle').removeClass('d-none');
        }

    })
    .catch(function(error) {
        showAlert('error', 'Socks stat data getting error. Please contact support.');
        if(socksUpdater){
            clearInterval(socksUpdater)
        }
    });
};
getSockStats();
socksUpdater = setInterval(getSockStats, 15000);

window.addEventListener("keydown", function(event) {
    if( event.altKey && event.shiftKey && event.which == 69){
        // toggle socks update on: alt + shift + e

        if( socksUpdater > 0 ){
            console.log('clearInterval socksUpdater');
            clearInterval(socksUpdater);
            socksUpdater = 0;
        } else {
            console.log('setInterval socksUpdater');
            getSockStats();
            socksUpdater = setInterval(getSockStats, 15000);
        }

        // console.log('socksUpdater after operations:', socksUpdater);
    }else if( event.altKey && event.shiftKey && event.which == 70 ){
        // fire one request on: alt + shift + f
        console.log('getSockStats manually fired');
        getSockStats();
    }
}, true);
