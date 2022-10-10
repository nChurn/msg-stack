var abm = require('./addressbook_module.js');

var paginator = require("./paginator.js");

var toggleCheckAllMailAccs = function(evt){
    var is_checked = $(this).is(':checked');
    // https://stackoverflow.com/questions/24410581/changing-prop-using-jquery-does-not-trigger-change-event
    $('.mail_accs-table tbody .form-check-input').prop('checked', is_checked).change();
};

var accFormSubmitter = function(evt) {
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
    

    var url = $(evt.target).attr('action');

    toggleLoader(true);
    $('.alert-container').html('');

    axios.post(url, formData)
        .then(function(response) {
            var type = response.data.success ? 'success' : 'error';
            showAlert(type, response.data.message);
            var tarea = $('textarea#acc_list').val(response.data.failed.join("\n"));
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

    // console.log(data);
    return false; //don't submit
};


var getMailAccsListTimeoutHandler = 0;
var allowRender = true;
var getMailAccsList = function(){
    return axios.get(api_url)
        .then(function(response) {
            // response is ok
            if (response.data.success && allowRender) {
                renderMailAccsList(response.data.data);
            }
        })
        .catch(function(error) {
            // console.log('error:', error.response.data);
            
        })
        .then(function() {
            // always executed
            if(allowRender)
                getMailAccsListTimeoutHandler = setTimeout(getMailAccsList, 5000);
            else
                clearTimeout(getMailAccsListTimeoutHandler);
        });
};

var mailAccsListModel = {};

var generateMailAccsListHtml = function(mail_accs){
    var rows_html = '';
    var checkbox_template = $('.alert-templates .cool-checkbox').html();
   
    Object.keys(mail_accs).map(function(key, index) {
        var row = mail_accs[key];
        var checkbox_html = checkbox_template
                                .replace(/\{checkbox_id\}/gmi, 'checkbox_' + row.id)
                                .replace(/\{checkbox_text\}/gmi, '&nbsp;')
                                .replace('data-checked=""', row.checked ? 'checked' : '')
                                .replace('data-checked', row.checked ? 'checked' : '')
                                .replace(/\{checkbox_value\}/gmi, row.id)
                                .replace(/\{checkbox_name\}/gmi, 'selected_accs[]');
        // add error checking here
        var danger_class = ( row.has_errors == 1 ? ' text-danger' : "" );
        var disabled_class = ( row.enabled == 'no' ? ' text-disabled' : "" );
        var html_class = ' ' + row.html_class;
        var row_html = '<tr data-id='+row.id+' class="mail_accs-row-'+row.id+ html_class +'" data-error="'+row.error_log+'">'
                        + '<td>' + row.id + '</td>'
                        + '<td class="acc-name"><span>' + row.name + '</span><input type="text" class="form-control d-none" value="'+row.name+'" /></td>'
                        + '<td>' + row.common_login + '</td>'
                        + '<td>' + row.common_host + '</td>'
                        + '<td>' + row.smtp_port + '</td>'
                        + '<td>' + row.enabled + '</td>'
                        + '<td>' + row.pop3_port + '</td>'
                        + '<td>' + row.imap_port + '</td>'
                        + '<td><a href="' + window.ab_url.replace('mail_account_id',row.id) + '" title="show" class="'+danger_class+'">' + row.addressbook_count + ' (show)</a><br/><a class="add-email-to-account" href="#" onclick="javascript:return false;" data-id="'+row.id+'">[add]</a></td>'
                        + '<td><a href="' + window.md_url.replace('mail_account_id',row.id) + '" title="show" class="'+danger_class+'">' + row.maildump_count + ' (show)</a></td>'
                        + '<td>' + row.created_at + '</td>'
                        + '<td>' + row.updated_at + '</td>'
                        + '<td>' + checkbox_html + '</td>'
                        + '</tr>';
        rows_html += row_html;
    });

    if( rows_html.length == 0){
        rows_html += '<tr><td colspan="20" align="center">No records found...</td></tr>';
    }

    return rows_html;
};

var renderMailAccsList = function(all_data, error){
    // console.log('data:', data)
    // mark all items in model as "deleted"

    var data = all_data.data;
    for(var idx in mailAccsListModel){
        mailAccsListModel[idx]['remove'] = true;
    }
    // fill sockslist model
    for (var i = 0; i < data.length; i++) {
        var row = data[i];
        var id = row.id;
        // check if row exists in list
        if( !mailAccsListModel.hasOwnProperty(id) ){
            mailAccsListModel[id] = {};
        }

        Object.keys(row).map(function(key, index) {
            mailAccsListModel[id][key] = row[key];
            // extra checks
            if(key == 'enabled' || key == 'smtp_allow' || key == 'pop3_port' || key == 'imap_port') mailAccsListModel[id][key] = row[key] ? 'yes' : 'no';
            if(key == 'checked_at') mailAccsListModel[id][key] = row[key] ? row[key] : 'never';
        });
        // fast type conversion for checkbox
        mailAccsListModel[id]['checked'] = mailAccsListModel[id]['checked'] ? true : false;
        mailAccsListModel[id]['remove'] = false;
    }

    // remove all that marked to remove
    for(var idx in mailAccsListModel){
        if( mailAccsListModel[idx]['remove'] )
            delete mailAccsListModel[idx];
    }

    var rows_html = generateMailAccsListHtml(mailAccsListModel);
    // console.log(rows_html);
    // console.log('all_data.current_page:', all_data.current_page);
    // $('.mail_accs-table').data('page', all_data.current_page);
    $('#paginate_page').val(all_data.current_page);
    $('.mail_accs-table tbody').html(rows_html);
    // add events
    $('.mail_accs-table tbody .form-check-input').change(function(ev){
        var $el = $(ev.target);
        // console.log('changed state for:', $el);
        var id = Number($el.attr('id').replace('checkbox_', ''));

        mailAccsListModel[id]['checked'] = $el.is(":checked");
    });

    var item = $('.mail_accs-table');
    $('.mail_accs-table tbody').off('mouseover').on('mouseover', function(evt){
        var $tr = $(evt.target).closest('tr');
        // show errros also for everyone
        var err_text = $tr.data('error') || "";
        if( err_text.length ){
            $popup = $('#popup');
            $popup.html( err_text.replace(/\n/gmi, "<br/>") ).parent().removeClass('d-none');
            var popper = new Popper($tr, $('#popup'), {placement: 'top-end'} );

        } else{
            $('.popper-container').addClass('d-none');
        }
    }).on('mouseleave', function(){
        $('.popper-container').addClass('d-none');
    });

    var paginator_html = paginator.generatePaginator(all_data);
    $('.paginator').html(paginator_html);

    $('.paginator ul a').on('click', function(evt){
        // actually urls are now generated properly so no reason in this shit, but anyway, i feel more comfortable
        var $link = $(this);
        var page = $link.attr('href').split('page=')[1];
        $('#filterform #paginate_page').val(page);
        applyFilters(evt);
        return false;
    });
};

var refreshTableData = function(){
    toggleLoader(true);
    clearTimeout(getMailAccsListTimeoutHandler);
    getMailAccsList().then(function(){
        toggleLoader(false);
    });
};

var applyMailMassChange = function(evt){
    var option = $(evt.target).data('opntion');
    $('#mailaccsform input[name="action"]').val( option );
    // get list of selected ids
    var selected = [];
    $('.mail_accs-table tbody .form-check-input:checked').each(function(){
        selected.push( $(this).closest('tr').data('id') );
    });

    var data = {
        'option': option,
        'ids': selected
    };

    var url = $(evt.target).closest('form').attr('action');

    // do nothing if none selected
    var message = "You are about to " + $(evt.target).html().toLowerCase() + " accs with ids: " + selected.join(' , ') + ".\nAre You sure?";
    if( selected.length < 1 || !confirm( message ) ) return;

    toggleLoader(true);
    allowRender = false;
    clearTimeout(getMailAccsListTimeoutHandler);
    
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
            // restore sockslist data retrival
            allowRender = true;
            getMailAccsList();
        });
};

var getPaginatorParams = function()
{
    var filters = $('#filterform').serialize();
    var url = api_url_base + "?" + filters;
    return url;
};

var applyFilters = function(evt){
    var url = getPaginatorParams();
    api_url = url;
    refreshTableData();
    return false;
};

var accountListClickHandler = function(evt){
    // check if we clicked on Name
    var $nameTd = $(evt.target).closest('td.acc-name');
    var addEmail = $(evt.target).hasClass('add-email-to-account');
    if($nameTd.length == 0 && !addEmail){
        return true;
    }

    if($nameTd.length){
        // stop rendering
        allowRender = false;
        clearTimeout(getMailAccsListTimeoutHandler);

        var input = $nameTd.find('input');
        if(input.hasClass('d-none')){
            toggleAccountNameInputVisibility($nameTd, true);
        }
    }else if(addEmail){
        abm.toggleModal(true, evt);
    }

    return false;
};

var toggleAccountNameInputVisibility = function(td, show){
    // hide all
    td.closest('tbody').find('.acc-name span').removeClass('d-none');
    td.closest('tbody').find('.acc-name input').addClass('d-none');

    if(show){
        td.find('span').addClass('d-none');
        td.find('input').removeClass('d-none')
            .off('keypress')
            .on('keypress', inputKeyPressHandler)
            .off('focusout')
            .on('focusout', updateMailAccountName)
            .focus();
    }
};

var inputKeyPressHandler = function(evt){
    // if pressed enter
    if( evt.which == 13) {
        updateMailAccountName(evt);
    }
};

var updateMailAccountName = function(evt){
    var input = $(evt.target), 
        new_name = input.val(),
        id = input.closest('tr').data('id');

    var url = api_url_base+"/name/" + id;

    console.log('updateMailAccountName', url, new_name);
    // allowRender = true;
    // getMailAccsList();

    toggleLoader(true);
    clearTimeout(getMailAccsListTimeoutHandler);

    var data = {"new_name": new_name};
    
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
            input.addClass('d-none').closest('td').find('span').html(new_name).removeClass('d-none');

            allowRender = true;
            // always executed
            toggleLoader(false);
            // restore sockslist data retrival
            getMailAccsList();
        });
};

var updateInputGroupOnRadioChange = function(evt){
    var elem = $(evt.target);
    $('#group_name').val($(evt.target).val());
};


var mailAccsPage = function(argument) {
    $('.form-horizontal').on('submit', accFormSubmitter);
    // $('#mailAccsMassAction .dropdown-menu').click(applyMailMassChange);
    // $('#selectAllAccounts').on('change', toggleCheckAllMailAccs).prop('checked', false);
    // $('#filterform .btn').click(applyFilters);
    // $('#filterform').submit(applyFilters);

    // $('.mail_accs-table tbody').on('click', accountListClickHandler);

    // $('#add_addresses_form').on('submit', abm.addNewAddresses);

    $('.account-groups').on('change', updateInputGroupOnRadioChange);
    // getMailAccsList();

    $('.account-groups .form-check-input').prop('checked', false);
};


if (/^\/(mail|test)_accs.*/gmi.test(window.location.pathname)) {
    console.log('we are at ' + window.location.pathname);
    $(document).ready(mailAccsPage);
}
