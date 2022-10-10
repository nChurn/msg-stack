var preventFillSelectedAtts = false;

var toggleCheckAllAttachements = function(){
    // avoid cascade function call
    preventFillSelectedAtts = true;
    var is_checked = $(this).is(':checked');
    $('.attachements-table tbody .form-check-input').prop('checked', is_checked);
    // enable it back
    preventFillSelectedAtts = false;
    fillSelectedAccs();
};

var fillSelectedAccs = function() {
    // do nothing if flag is set
    if (preventFillSelectedAtts) {
        console.log('preventFillSelectedAtts:', preventFillSelectedAtts);
        return;
    }
};


var campaignSubmitUpdate = function(evt) {
    var url = $(evt.target).attr('action');

    evt.preventDefault();
    var formData = new FormData();

    var validationFailed = false;
    // check if we selected at least one account
    // if( $(evt.target).find('input[name="selected_accs[]"]:checked').length == 0 ){
    //     validationFailed = true;
    //     showAlert('error', "Please select at least one account to send");
    //     return false;
    // }

    // process form
    $(evt.target).find('input, textarea, select').each(function() {
        var $el = $(this);
        if ($el.attr('type') == 'file') {
            var el = $el.get(0),
                ins = el.files.length;
            // if(ins < 1){
            //     validationFailed = true;
            //     showAlert('error', "Please add at least one file to message");
            // }
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
            // if(name == 'selected_accs[]'){
            //     console.log('el is:', $el);
            // }
            formData.append(name, val);
        }
    });
    if( validationFailed ) return false;

    toggleLoader(true);

    axios.post(url, formData)
        .then(function(response) {
            var type = response.data.success ? 'success' : 'error';
            showAlert(type, response.data.message);
        })
        .catch(function(error) {
            var text = error.response.data.message;
            // detrmine type of error: exception or validation
            if(error.response.data.errors){
                var errors = error.response.data.errors;
                for(var error in errors){
                    var err_arr = errors[error];
                    text += '<br>' + error + ": ";
                    for (var i = 0; i < err_arr.length; i++) {
                        text +=  err_arr[i] + " ";
                    }
                }
                // for (var i = 0; i < errors.length; i++) {
                //     var error = errors[i];
                //     for(key in error){
                //         text += '<br>' + key + ": " + error[key];
                //     }
                // }
            }else{
                text += '<br>' + (error.response.data.exception + '<br>' || '') + (error.response.data.file + "(" + error.response.data.line + ")" + '<br>' || '');
            }

            showAlert('error', text);
        })
        .then(function() {
            toggleLoader(false);
        });

    return false;
};


var campaignHeadersChangeHandler = function(evt){
    var data = {};
    $('.custom-headers-container .form-control[name="headers_names[]"]').each(function(){
        var key = $(this).val().trim();
        var value = $(this).closest('.input-group').find('.form-control[name="headers_values[]"]').val().trim();
        data[key] = value;
    });

    $('#sendmailform input[name="headers"]').val(JSON.stringify(data));
};

var campaignAddHeader = function(evt){
    evt.preventDefault();
    var tpl = $('.headers-template').html();
    $('.custom-headers-container').append(tpl);

    $('.custom-headers-container .form-control').off('change').on('change', campaignHeadersChangeHandler);
    return false;
};

var editCampaignPage = function(argument) {
    $('#sendmailform').submit(campaignSubmitUpdate);
    $('#selectAllAttachements').change(toggleCheckAllAttachements);
    $('#selectAllAttachements').prop("checked", false);
    toggleCheckAllAttachements();

    $('.custom-headers-container').click(function(evt){
        evt.preventDefault();
        $elem = $(evt.target);
        if( $elem.hasClass('add-header') )
            campaignAddHeader(evt)
        else if( $elem.hasClass('remove-header-icon') || $elem.closest('.remove-header-icon').length ){
            // console.log('clicked on remove item');
            $elem.closest('.col-12').remove();
            campaignHeadersChangeHandler(evt);
        }
    });
};
// init only on /scan_rules path
if (/^\/campaigns\/show\/\d$/gmi.test(window.location.pathname)) {
    console.log('we are at edit campaign');
    $(document).ready(editCampaignPage);
}
