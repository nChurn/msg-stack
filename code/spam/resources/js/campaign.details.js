var paginator = require("./paginator.js");
var macrosProcessor = require("./macros-processor.js");

var toggleCheckAllDetailRecords = function(evt){
    var is_checked = $(this).is(':checked');
    // https://stackoverflow.com/questions/24410581/changing-prop-using-jquery-does-not-trigger-change-event
    $('.record_details-table tbody .form-check-input').prop('checked', is_checked).change();
};


var getRecordDetailsListTimeoutHandler = 0;
var allowRender = true;
var getRecordDetailsList = function(_url){
    return axios.get(_url)
        .then(function(response) {
            // response is ok
            if (response.data.success && allowRender) {
                renderRecordDetailsList(response.data.data);
            }
        })
        .catch(function(error) {
            // console.log('error:', error.response.data);

        })
        .then(function() {
    		toggleLoader(false);

            // always executed
            if(allowRender)
                getRecordDetailsListTimeoutHandler = setTimeout(getRecordDetailsList, 5000);
            else
                clearTimeout(getRecordDetailsListTimeoutHandler);
        });
};

var recordDetailsListModel = {};
var renderRecordDetailsList = function(all_data, error){

	var data = all_data.data;
    for(var idx in recordDetailsListModel){
        recordDetailsListModel[idx]['remove'] = true;
    }

    for (var i = 0; i < data.length; i++) {
        var row = data[i];
        var id = row.id;
        // check if row exists in list
        if( !recordDetailsListModel.hasOwnProperty(id) ){
            recordDetailsListModel[id] = {};
        }

         Object.keys(row).map(function(key, index) {
            recordDetailsListModel[id][key] = row[key];
        });

        // fast type conversion for checkbox
        recordDetailsListModel[id]['checked'] = recordDetailsListModel[id]['checked'] ? true : false;
        recordDetailsListModel[id]['remove'] = false;
    }

    // remove all that marked to remove
    for(var idx in recordDetailsListModel){
        if( recordDetailsListModel[idx]['remove'] )
            delete recordDetailsListModel[idx];
    }

    var rows_html = generateRecordDetailsHtml(recordDetailsListModel);
    // $('#paginate_page').val(all_data.current_page);
    $('.record_details-table tbody').html(rows_html);
    // toggle dateils show
    $('.record_details-table tbody .details-toggler').on('click', function(evt){
    	evt.preventDefault();
    	evt.stopPropagation();
    	var id = $(this).closest('tr').data('id');

    	$(this).next().toggleClass('d-none');
    	recordDetailsListModel[id]['show_details'] = !$(this).next().hasClass("d-none");
    	if($(this).next().hasClass("d-none")){
    		$(this).html('Show');
    	}else{
    		$(this).html('Hide');
    	}

    	return false;
    });




    // append checked property
    $('.record_details-table tbody .form-check-input').change(function(ev){
        var $el = $(ev.target);
        // console.log('changed state for:', $el);
        var id = Number($el.attr('id').replace('checkbox_', ''));

        recordDetailsListModel[id]['checked'] = $el.is(":checked");
    });


	var paginator_html = paginator.generatePaginator(all_data);
    $('.paginator').html(paginator_html);

    $('.paginator a').on('click', function(evt){
    	evt.preventDefault();
    	evt.stopPropagation();
    	var url = $(evt.target).attr('href');
		toggleLoader(true);
    	getRecordDetailsList(url);
    	return false;
    });
};

var generateRecordDetailsHtml = function(record_details){
    var rows_html = '';
    var checkbox_template = $('.alert-templates .cool-checkbox').html();

    var status = {
    	'await': 0,
        'processing': 1,
        'success': 2,
        'fail': 3
    };


    Object.keys(record_details).map(function(key, index) {
        var row = record_details[key];
        var checkbox_html = checkbox_template
                                .replace(/\{checkbox_id\}/gmi, 'checkbox_' + row.id)
                                .replace(/\{checkbox_text\}/gmi, '&nbsp;')
                                .replace('data-checked=""', row.checked ? 'checked' : '')
                                .replace('data-checked', row.checked ? 'checked' : '')
                                .replace(/\{checkbox_value\}/gmi, row.id)
                                .replace(/\{checkbox_name\}/gmi, 'selected_records[]');
        // add error checking here
        var record_classes = [];
        if( row.record_status == status.fail ){
        	record_classes.push('text-danger');
        	row.status_txt = 'Failed';
        }else if(row.record_status == status.await){
			row.status_txt = 'Waiting';
        }else if(row.record_status == status.processing){
			row.status_txt = 'Processing';
        }else if(row.record_status == status.success){
			row.status_txt = 'Success';
        }

        var html_class = record_classes.join(' ');
        var row_html = '<tr data-id='+row.id+' class="record_details-row-'+row.id+ html_class +'">'
                        + '<td>' + row.id + '</td>'
                        + '<td>' + row.mail_account_id + '</td>'
                        + '<td>' + row.account.common_login + '</td>'
                        + '<td>' + row.address + '</td>'
                        + '<td>' + row.status_txt + '</td>'
                        + '<td>' + '<a href="#" class="details-toggler">'+(row.show_details ? 'Hide' : 'Show')+'</a><div class="' + (row.show_details ? '' : 'd-none') +  ' small">' + row.record_status_txt.replace(/\n/g, '<br/>') + '</div>' +  '</td>'
                        + '<td>' + checkbox_html + '</td>'
                        + '</tr>';
        rows_html += row_html;
    });

    if( rows_html.length == 0){
        rows_html += '<tr><td colspan="20" align="center">No records found...</td></tr>';
    }

    return rows_html;
};

var processMacroses = function(){
	var macros_list = JSON.parse($('#macros_data').val());
    var macro_templates = $('#macro_templates').data('macro-tpls');
    // console.log('macro_templates', macro_templates);

    var subjString = $('#subject_raw').val();
    subjString = macrosProcessor.stringProcessMacro(null, subjString, true, macros_list, macro_templates);
    $('#subject_preview').val(subjString);

    var attachString = $('#attach_name_raw').val();
    attachString = macrosProcessor.stringProcessMacro(null, attachString, false, macros_list, macro_templates);
    $('#attach_name_preview').val(attachString);

    var htmlString = $('#body_raw').val();
    htmlString = macrosProcessor.stringProcessMacro(null, htmlString, false, macros_list, macro_templates);

    // if not html - replace \r\n with <br/>
    if( !$('#is_html').is(':checked') ){
        htmlString = "<div style=\"font-family: monospace\">" + htmlString.replace(/(\r)?\n/gmi, '<br/>') + "</div>";
    }

    // console.log('htmlString', htmlString);
    var iFrame = $('#mailPreviewContainer');

    var iFrameDoc = iFrame[0].contentDocument || iFrame[0].contentWindow.document;
    iFrameDoc.write(htmlString);
    iFrameDoc.close();

	// console.log('macros_list', macros_list);

	// $('#letterbody, #campaign_subject').each(function(){
	// 	var str = $(this).html();
	// 	str = str.replace(/\%FROMNAME\%/gmi, macros_list['from_name'])
	// 		.replace(/\%TONAME\%/gmi, macros_list['to_name'])
	// 		.replace(/\%FROMEMAIL\%/gmi, macros_list['from_email'])
	// 		.replace(/\%TOEMAIL\%/gmi, macros_list['to_email']);
	// 	$(this).html(str);
	// });

};

var applyMassChange = function(evt){
    var option = $(evt.target).data('opntion');
    // get list of selected ids
    var selected = [];
    $('.record_details-table tbody .form-check-input:checked').each(function(){
        selected.push( $(this).closest('tr').data('id') );
    });

    var data = {
        'option': option,
        'ids': selected
    };

    var url = details_update_url;

    // do nothing if none selected
    var message = "You are about to " + $(evt.target).html().toLowerCase() + " accs with ids: " + selected.join(' , ') + ".\nAre You sure?";
    if( selected.length < 1 || !confirm( message ) ) return;

    toggleLoader(true);
    allowRender = false;
    clearTimeout(getRecordDetailsListTimeoutHandler);

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
            // TODO: save filter data somehow...
            var url = getPaginatorParams()
            getRecordDetailsList(url);
        });
};

var getPaginatorParams = function()
{
    var filters = $('#filterform').serialize();
    var url = details_url + "?" + filters;
    return url;
};

var applyFilters = function(evt){
    var url = getPaginatorParams();
    // api_url = url;
    getRecordDetailsList(url);
    return false;
};

var campaignDetailsPage = function(argument) {
	$('#check_all_detail_records').on('change', toggleCheckAllDetailRecords);
    $('#detailRecordsMassAction .dropdown-menu').click(applyMassChange);

    $('#filterform .btn').click(applyFilters);
    $('#filterform').submit(applyFilters);

	getRecordDetailsList(details_url);
	processMacroses();
};

// init only on /socks path
if (/^\/campaign\/details\/\d+$/gmi.test(window.location.pathname)) {
    console.log('we are at campaign details');
    $(document).ready(campaignDetailsPage);
}
