var filters = require('./filter-groups-selector.js')

var addNewAddresses = function(evt){
    var form = $(evt.target);

    // return false;
    // console.log('form', form);
    // console.log('form.data-id', form.data('id'))
    var url = form.data('action').replace('email_account_id', form.data('id'));
    // TODO: serialize and jsonize form maybe?
    // var data = $(evt.target).serializeObject();
    // data must be via FormData()
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
            if($el.attr('type') == 'checkbox' && !$el.is(':checked')){
                return true;
            }
            formData.append(name, val);
        }
    });
    
    // console.log('send data to url:', url, data);

    toggleLoader(true);
    $('.alert-container').html('');

    toggleModal(false, evt);
    // $('#newAddressModal').modal('hide');

    axios.post(url, formData)
        .then(function(response) {
            var type = response.data.success ? 'success' : 'error';
            showAlert(type, response.data.message);
            // var tarea = $('textarea#acc_list').val(response.data.failed.join("\n"));
            // console.log(tarea);
            // $('textarea#acc_list').html( response.data.failed.join("\n") );
        })
        .catch(function(error) {
            // console.log('error:', error.response.data);
            var exception = error.response.data.exception || '';
            var file = error.response.data.file || '';
            var line = error.response.data.line || '';
            var text = error.response.data.message + '<br>' + (exception ? exception + '<br>' : '' ) + (file ? file + (line?' ('+line+')':'') + '<br/>' : '');
            showAlert('error', text);
        })
        .then(function() {
            // always executed
            toggleLoader(false);
        });

    return false;
};

var toggleModal = function(show, evt){
    $('#newAddressModal form textarea').val('');
    $('#newAddressModal form input[type=file]').val('');
    $('#newAddressModal #parse_rules').val('');
        
    if(show){
        var id = $(evt.target).data('id');
        $('#newAddressModal form').data('id', id);
        $('#newAddressModal').modal();
    }else{
        $('#newAddressModal').modal('hide');
    }


    $('#newAddressModal .select-format input[type=radio]').prop('checked', false).off('change').on('change', function(evt){
        $('#newAddressModal #parse_rules').val( $(this).val() );
    });

    filters.processFilterToggle($('#newAddressModal'), true);
}


var secodFunc = function(val){
    console.log('secodFunc', val);
};

export{ addNewAddresses, secodFunc, toggleModal}
