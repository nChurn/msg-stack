var toggleCheckAllSocks = function(evt){
    var is_checked = $(this).is(':checked');
    // https://stackoverflow.com/questions/24410581/changing-prop-using-jquery-does-not-trigger-change-event
    $('.socks-table tbody .form-check-input').prop('checked', is_checked).change();
};


var getSocksListTimeoutHandler = 0;
var getSocksList = function(){
    // var order_by = "";

    var params = window.location.search.substr(1);
    // var splitted = params.split('&');
    axios.get(api_url + "?" + params)
        .then(function(response) {
            // response is ok
            if (response.data.success) {
                renderSocksList(response.data.data);
            }
        })
        .catch(function(error) {
            // console.log('error:', error.response.data);

        })
        .then(function() {
            // always executed
            getSocksListTimeoutHandler = setTimeout(getSocksList, 5000);
        });
};

var sockListModel = {};

var generateSocksListHtml = function(socks){
    var rows_html = '';
    var checkbox_template = $('.cool-checkbox').html();

    var items_sorted = [];
    for( key in socks)
        items_sorted.push(socks[key]);

    var sort_col = '', sort_dir = '';
    $('.socks-table thead tr th').each(function(){
        if( $(this).data('sort-order') !== 'none' && $(this).data('sort-order') ){
            sort_col = $(this).data('sort');
            sort_dir = $(this).data('sort-order');
        }
    });

    if(sort_col !== '' && sort_dir !== '' && sort_dir !== 'none'){
        // console.log('try to sort...', 'sort_col', sort_col, 'sort_dir', sort_dir);
        items_sorted.sort(function(a, b){
            // console.log('compare', a[sort_col], 'and', b[sort_col]);
            if(sort_dir == 'asc')
                return a[sort_col] > b[sort_col]
            else if (sort_dir == 'desc')
                return a[sort_col] < b[sort_col]
        });
    }

    // Object.keys(socks).map(function(key, index) {
    //     var row = socks[key];
    for(var i = 0; i < items_sorted.length; i++){
        var row = items_sorted[i];

        var checkbox_html = checkbox_template
                            .replace(/\{checkbox_id\}/gmi, 'checkbox_' + row.id)
                            .replace(/\{checkbox_text\}/gmi, '&nbsp;')
                            .replace('data-checked=""', row.checked ? 'checked' : '')
                            .replace('data-checked', row.checked ? 'checked' : '')
                            .replace(/\{checkbox_value\}/gmi, row.id)
                            .replace(/\{checkbox_name\}/gmi, 'selected_socks[]')
                            ;

        var row_classes = ['socks-row-'+row.id];

        // if banlist - override red text
        if(row.banlist){
           row_classes.push("bg-danger text-white");
        }else{
            // create property if not exists
            row.banlist = '';
            // spam must have both fields
            // if( row.type == 'spam' ){
            if( row.checked_at == 'never' )
                row_classes.push('text-muted');
            else if( row.alive == 'no' )
                row_classes.push('text-danger');
            else if ( row.smtp_allow == 'yes' && row.type == 'spam' )
                row_classes.push('text-success');
            // }
            // grabber needs only one
            // if(row.type == 'grabber'){
                // if( row.checked_at == 'never' )
                //     row_classes.push('text-muted');
                // else if( row.alive == 'no' )
                //     row_classes.push('text-danger');
            // }
        }
        row.hostname = row.hostname || '';
        row.outer_ip = row.outer_ip || '';
        var row_html = '<tr data-id='+row.id+' class="'+row_classes.join(' ')+'" data-error="'+row.banlist+'">'
                        + '<td>' + row.host + '</td>'
                        + '<td>' + row.port + '</td>'
                        + '<td>' + row.login + '</td>'
                        + '<td>' + row.password + '</td>'
                        + '<td>' + row.type + '</td>'
                        + '<td>' + row.hostname + '</td>'
                        + '<td>' + row.outer_ip + '</td>'
                        + '<td>' + row.alive + '</td>'
                        + '<td>' + row.enabled + '</td>'
                        + '<td>' + row.smtp_allow + '</td>'
                        + '<td>' + row.checked_at + '</td>'
                        + '<td>' + checkbox_html + '</td>'
                        + '</tr>';
        rows_html += row_html;
    // });
    };

    return rows_html;
};

var renderSocksList = function(data, error){
    // mark all items in model as "deleted"
    for(var idx in sockListModel){
        sockListModel[idx]['remove'] = true;
    }
    // after sync, remove items that remain "deleted" flag
    // fill sockslist model
    for (var i = 0; i < data.length; i++) {
        var row = data[i];
        var id = row.id;
        // check if row exists in list
        if( !sockListModel.hasOwnProperty(id) ){
            sockListModel[id] = {};
        }

        Object.keys(row).map(function(key, index) {
            sockListModel[id][key] = row[key];
            // extra checks
            if(key == 'enabled' || key == 'smtp_allow' || key == 'alive') {
                sockListModel[id][key] = (row[key] == 1 ? 'yes' : 'no');
            }
            // if( key == 'banlist' && row[key].length > 0 )
            //     sockListModel[id]['blacklisted'] = 'yes';
            // else
            //     sockListModel[id]['blacklisted'] = 'no';

            if(key == 'checked_at') sockListModel[id][key] = (row[key] ? row[key] : 'never');
        });
        // fast type conversion for checkbox
        sockListModel[id]['checked'] = sockListModel[id]['checked'] ? true : false;
        sockListModel[id]['remove'] = false;
    }

    // remove all that marked to remove
    for(var idx in sockListModel){
        if( sockListModel[idx]['remove'] )
            delete sockListModel[idx];
    }

    var rows_html = generateSocksListHtml(sockListModel);
    // console.log(rows_html);
    $('.socks-table tbody').html(rows_html);
    // add events
    $('.socks-table tbody .form-check-input').change(function(ev){
        // var id = $(ev.target).closest('tr').data('id');
        var $el = $(ev.target),
            id = $el.closest('tr').data('id');
        // console.log('change:', id);
        // console.log('changed state for:', $el);
        // var id = Number($el.attr('id').replace('checkbox_', ''));

        sockListModel[id]['checked'] = $el.is(":checked");
        // console.log('id:', id);
        // if($(this).is(":checked")) {}
    });

    $('.socks-table tbody').off('mouseover').on('mouseover', function(evt){
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
};

var applySocksMassChange = function(evt){
    var option = $(evt.target).data('opntion');
    $('.actionsocksform input[name="action"]').val( option );
    // get list of selected ids
    var selected = [];
    $('.socks-table tbody .form-check-input:checked').each(function(){
        selected.push( $(this).closest('tr').data('id') );
    });

    var data = {
        'option': option,
        'ids': selected
    };

    var url = $(evt.target).closest('form').attr('action');

    if( option.indexOf('-all-') === -1 ){
        // do nothing if none selected
        var message = "You are about to " + $(evt.target).html().toLowerCase() + " socks with ids: " + selected.join(' , ') + ".\nAre You sure?";
        if( selected.length < 1 || !confirm( message ) ) return;
    }else{
        var message = "You are about to " + $(evt.target).html().toLowerCase() + " socks.\nAre You sure?";
        if( !confirm( message ) ) return;

    }

    toggleLoader(true);
    clearTimeout(getSocksListTimeoutHandler);

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
            getSocksList();
        });
};

var tableHeaderClickHandler = function(evt){
    var td = $(evt.target).closest('th');
    var direction = "none";

    if( td.data('sort-order') == 'none' )
        direction = "desc";
    else if( td.data('sort-order') == 'desc' )
        direction = "asc";
    else if( td.data('sort-order') == 'asc' )
        direction = "desc";

    // mark all as none sort order
    td.parent().find('th').data('sort-order', "none");
    td.parent().find('th i').removeClass('fa-sort-amount-asc fa-sort-amount-desc').addClass('fa-sort');

    td.data('sort-order', direction);
    td.find('i').removeClass('fa-sort').addClass('fa-sort-amount-' + direction);
    var filters = ["order_col=" + td.data('sort'), "order_dir=" + td.data('sort-order')];
    var args = filters.join('&');
    window.history.pushState("", document.title, "?" + args);
    // generateSocksListHtml(sockListModel);
};

var socksPage = function(argument) {
    $('.form-horizontal').on('submit', formSubmitter);
    $('.socksMassAction .dropdown-menu').click(applySocksMassChange);
    $('#checkAllSocks').on('change', toggleCheckAllSocks).prop('checked', false);
    $('.socks-table thead tr').click(tableHeaderClickHandler);

    // mark proper sorting according to url
    var sort_col = '', sort_dir = '';
    var params = window.location.search.substr(1);
    var splitted = params.split('&');
    // console.log(splitted);
    for(var i = 0 ; i < splitted.length; i++){
        if(splitted[i].split('=')[0] == 'order_col'){
            sort_col = splitted[i].split('=')[1];
        }else if(splitted[i].split('=')[0] == 'order_dir'){
            sort_dir = splitted[i].split('=')[1];
        }
    }
    $('.socks-table thead tr th').each(function(){
        if( $(this).data('sort') == sort_col ){
            $(this).data('sort-order', sort_dir);

            $(this).find('i').removeClass('fa-sort').addClass('fa-sort-amount-' + sort_dir);
        }
    });

    getSocksList();
};

// init only on /socks path
if (/^\/socks.*/gmi.test(window.location.pathname)) {
    console.log('we are at socks');
    $(document).ready(socksPage);
}
