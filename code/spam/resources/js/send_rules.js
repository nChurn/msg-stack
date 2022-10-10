var toggleCheckAllRules = function(evt){
    var is_checked = $(this).is(':checked');
    $('.scan_rules-table tbody .form-check-input').prop('checked', is_checked);
};


var getScanRulesListTimeoutHandler = 0;
var getScanRulesList = function(){
    axios.get(api_url)
        .then(function(response) {
            // response is ok
            if (response.data.success) {
                renderScanRulesList(response.data.data);
            }
        })
        .catch(function(error) {
            // console.log('error:', error.response.data);
            
        })
        .then(function() {
            // always executed
            // getScanRulesListTimeoutHandler = setTimeout(getScanRulesList, 5000);
        });
};

var scanRulesListModel = {};

var generateScanRulesListHtml = function(scan_rules){
    var rows_html = '';
    var checkbox_template = $('.cool-checkbox').html();
   
    Object.keys(scan_rules).map(function(key, index) {
        var row = scan_rules[key];
        var checkbox_html = checkbox_template
                                .replace(/\{checkbox_id\}/gmi, 'checkbox_' + row.id)
                                .replace(/\{checkbox_text\}/gmi, '&nbsp;')
                                .replace('data-checked', row.checked ? 'checked' : '')
                                .replace(/\{checkbox_value\}/gmi, row.id)
                                .replace(/\{checkbox_name\}/gmi, 'selected_rules[]');
                                ;
        var row_html = '<tr data-id='+row.id+' class="scan_rules-row-'+row.id+'">'
                        + '<td>' + row.rule + '</td>'
                        // + '<td>' + row.exclude + '</td>'
                        + '<td>' + row.group + '</td>'
                        + '<td>' + row.enabled + '</td>'
                        + '<td>' + checkbox_html + '</td>'
                        + '</tr>';
        rows_html += row_html;
    });

    return rows_html;
};

var renderScanRulesList = function(data, error){
    // fill scan_ruleslist model
    for (var i = 0; i < data.length; i++) {
        var row = data[i];
        var id = row.id;
        // check if row exists in list
        if( !scanRulesListModel.hasOwnProperty(id) ){
            scanRulesListModel[id] = {};
        }

        Object.keys(row).map(function(key, index) {
            scanRulesListModel[id][key] = row[key];
            // extra checks
            if(key == 'enabled' || key == 'exclude') scanRulesListModel[id][key] = row[key] ? 'yes' : 'no';
        });
        // fast type conversion for checkbox
        scanRulesListModel[id]['checked'] = scanRulesListModel[id]['checked'] ? true : false;
    }

    var rows_html = generateScanRulesListHtml(scanRulesListModel);
    // console.log(rows_html);
    $('.scan_rules-table tbody').html(rows_html);
    // add events
    $('.scan_rules-table tbody .form-check-input').change(function(ev){
        var $el = $(ev.target);
        console.log('changed state for:', $el);
        var id = Number($el.attr('id').replace('checkbox_', ''));

        scanRulesListModel[id]['checked'] = $el.is(":checked");
        // console.log('id:', id);
        // if($(this).is(":checked")) {}
    });
};

var applyScanRulesMassChange = function(evt){
    var option = $(evt.target).data('opntion');
    $('#actionscan_rulesform input[name="action"]').val( option );
    // get list of selected ids
    var selected = [];
    $('.scan_rules-table .form-check-input:checked').each(function(){
        selected.push( $(this).closest('tr').data('id') );
    });

    var data = {
        'option': option,
        'ids': selected
    };

    var url = $(evt.target).closest('form').attr('action');

    // do nothing if none selected
    var message = "You are about to " + $(evt.target).html().toLowerCase() + " scan_rules with ids: " + selected.join(' , ') + ".\nAre You sure?";
    if( selected.length < 1 || !confirm( message ) ) return;

    toggleLoader(true);
    clearTimeout(getScanRulesListTimeoutHandler);
    
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
            // restore scan_ruleslist data retrival
            getScanRulesList();
        });
};

var applySelectedGroupName = function(evt)
{
    $('#rulesGroup').val( $(evt.target).val() );
}

var applyInputChange = function(evt){
    // console.log('huihui');
    $('.filter-groups .form-check-input').prop('checked', false);
}

var toggleSingleRuleSave = function(turn_on){
    if(turn_on)
        $('.save-single-rule-container').removeClass('d-none');
    else
        $('.save-single-rule-container').addClass('d-none');
};

var addScanRule = function(evt){
    // var exclude_checkbox_html = check_box_html.replace();
    var row_html = $('.add-rule-template').html();
    var id = (new Date()).getTime();
    // replace first checkbox patterns
    row_html = row_html.replace('{checkbox_id}', 'exclude_' + id).replace('{checkbox_id}', 'exclude_' + id).replace('{checkbox_text}', 'Exclusive rule');
    row_html = row_html.replace('{checkbox_id}', 'enabled_' + id).replace('{checkbox_id}', 'enabled_' + id).replace('{checkbox_text}', 'Enabled');

    $('.single-rule-container').append(row_html);
    toggleSingleRuleSave(true);
};

var saveSingleScanRule = function(evt){
    // commonly function repeats regular formSubmitter, but data is grabbed customly
    var data = {"scan_rules" : ""}, scan_rules = [];

    $(".single-rule-container .form-group").each(function(){
        // generate string formatted just like mass rules add
        var $el = $(this);
        if( $el.find('.rule-input').val().replace(/\//gmi, '').length == 0 ){
            return true;
        }


        var input_rule = "/" + $el.find('.rule-input').val().replace(/\//gmi, '') + "/",
            exclude = $el.find('.exclusive-rule').is(':checked') ? '-' : '+',
            enabled = $el.find('.enable-rule').is(':checked') ? 'en' : 'dis';

        var result_rule = input_rule + exclude + enabled;

        scan_rules.push(result_rule);

        // console.log('result_rule:', result_rule);
    });

    data.scan_rules = scan_rules.join("\n");    

    // console.log('data to send:', data);

    $('.alert-container').html('');

    var url = $('#scanrulesform').attr('action');

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
        });
};


var scanRulesPage = function(argument) {
    $('.form-horizontal').on('submit', formSubmitter);
    $('#actionscan_rulesform .dropdown-menu').click(applyScanRulesMassChange);
    $('.add-scan-rule').click(addScanRule);
    $('.save-single-rule').click(saveSingleScanRule);
    $('.refresh-list').click(getScanRulesList);

    $('.filter-groups .form-check-input').prop('checked', false);
    $('.filter-groups').on('change', applySelectedGroupName);
    $('#selectAllRules').on('change', toggleCheckAllRules);
    $('#rulesGroup').on('keypress', applyInputChange);
    getScanRulesList();
};

// init only on /scan_rules path
if (/^\/send_rules.*/gmi.test(window.location.pathname)) {
    console.log('we are at scan_rules');
    $(document).ready(scanRulesPage);
}
