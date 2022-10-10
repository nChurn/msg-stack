var toggleCheckAllRecords = function(evt){
    var is_checked = $(this).is(':checked');
    $('.mail_acc_addressbook-table tbody .form-check-input').prop('checked', is_checked);
};

var applyemailAccAddrBookMassChange = function(evt){
    var option = $(evt.target).data('option');
    // $('#actionsocksform input[name="action"]').val( option );
    // get list of selected ids
    var selected = [];
    $('.mail_acc_addressbook-table tbody .form-check-input:checked').each(function(){
        selected.push( $(this).closest('tr').data('id') );
    });

    var data = {
        'option': option,
        'ids': selected
    };

    var url = $(evt.target).closest('form').attr('action');

    // do nothing if none selected
    var message = "You are about to " + $(evt.target).html().toLowerCase() + " records with ids: " + selected.join(' , ') + ".\nAre You sure?";
    if( selected.length < 1 || !confirm( message ) ) return;

    toggleLoader(true);
    
    axios.post(url, data)
        .then(function(response) {
            var type = response.data.success ? 'success' : 'error';
            showAlert(type, response.data.message);
        })
        .catch(function(error) {
            var text = error.response.data.message + '<br>' + (error.response.data.exception + '<br>' || '') + (error.response.data.file + '<br>' || '');
            showAlert('error', text);
        })
        .then(function() {
            // always executed
            toggleLoader(false);
            window.scrollTo(0,0);
            // just reload
            // setTimeout(function(){
            //     window.location.reload();
            // }, 2500);
        });
};

var inputKeyPressHandler = function(evt){
    var item = $(evt.target);

    if(item.hasClass('form-control') && evt.which == 13) {
        // alert('You pressed enter!');
        recordFieldUpdateHandler(evt);
    }
}

var toggleTextInput = function(td, show){
    // hida all at the beginning
    td.closest('tbody').find('.holder-name-text input').addClass('d-none');
    td.closest('tbody').find('span').removeClass('d-none');

    if(show){
        td.find('span').addClass('d-none');
        td.find('input').removeClass('d-none').focus();
    }else{
        td.find('input').addClass('d-none');
        td.find('span').removeClass('d-none');
    }
};

var recordFieldUpdateHandler = function(evt){
    var input = $(evt.target).closest('td').find('input'),
        span = $(evt.target).closest('td').find('span'),
        new_value = input.val() || '',
        id = input.closest('tr').data('id');
    var url = api_url.replace('record_id', id), field = input.data('field');
    var data = {};
    data[field] = new_value;
    // console.log(input, new_value, id, url);

    toggleLoader(true);
    // return false;
    axios.post(url, data)
        .then(function(response) {
            var type = response.data.success ? 'success' : 'error';
            showAlert(type, response.data.message);
            if( response.data.success ){
                span.html(new_value);
                toggleTextInput(input.closest('td'), false);
            }
        })
        .catch(function(error) {
            var text = error.response.data.message + '<br>' + (error.response.data.exception + '<br>' || '') + (error.response.data.file + '<br>' || '');
            showAlert('error', text);
        })
        .then(function() {
            // always executed
            // setTimeout(function(){ 
            toggleLoader(false); 
            // }, 2500);
            
            // window.scrollTo(0,0);
        });

};

var recordFieldClickHandler = function(evt){
    var item = $(evt.target).closest('td');

    // console.log('item:', item)
    if(item.hasClass('holder-editable-field')){
        item.find('input').val( item.find('span').html() );
        toggleTextInput(item, true);
        // console.log('we are here');
        return false;
    }
};

var emailAccAddrBookPage = function(argument) {
    $('#selectAllRecords').on('change', toggleCheckAllRecords).prop('checked', false).change();
    $('#adMassAction .dropdown-menu').click(applyemailAccAddrBookMassChange);
    $('.mail_acc_addressbook-table tbody')
        .click( recordFieldClickHandler)
        // .focusout(recordFieldUpdateHandler)
        .keypress(inputKeyPressHandler);

};

// init only on /socks path
if (/^\/acc_addressbook\/\d+$/gmi.test(window.location.pathname)) {
    console.log('we are at email account addressbook');
    $(document).ready(emailAccAddrBookPage);
}
