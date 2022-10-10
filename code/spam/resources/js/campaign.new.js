var filters = require('./filter-groups-selector.js');
var addressparser = require('addressparser');

var reply_tpl = '<html><head><meta http-equiv="Content-Type" content="text/html; "></meta><title>Re: {subject}</title></head><body text="#000000" bgcolor="#FFFFFF">{new_text}<div class="moz-cite-prefix">On {date}, {from} wrote:<br/></div><blockquote type="cite" cite="mid:{msg_id}"><pre class="moz-quote-pre" wrap="">{orig_body}</pre></blockquote></body></html>';
                // '<html><head><title>Re: {subject}</title><link rel="important stylesheet" href="chrome://messagebody/skin/messageBody.css"></link></head><body><table border="0" cellspacing="0" cellpadding="0" width="100%" class="header-part1"><tr><td><b>Subject: </b>Re: {subject}</td></tr><tr><td><b>From: </b>{from}</td></tr><tr><td><b>Date: </b>{date}</td></tr></table><table border="0" cellspacing="0" cellpadding="0" width="100%" class="header-part2"><tr><td><b>To: </b>{to}</td></tr></table><br><html><head><meta http-equiv="Content-Type" content="text/html; "></meta></head><body text="#000000" bgcolor="#FFFFFF">{new_text}<p><br/></p><div class="moz-cite-prefix">On {date}, {from_name} wrote:<br/></div><blockquote type="cite" cite="mid:{msg_id}"><pre class="moz-quote-pre" wrap="">{orig_body}</pre></blockquote></body></html></body></html>';

// var preventFillSelectedAccs = false;

// var toggleCheckAllAccounts = function(){
//     // avoid cascade function call
//     preventFillSelectedAccs = true;
//     var is_checked = $(this).is(':checked');
//     $('.accounts-table tbody .form-check-input:not([disabled])').prop('checked', is_checked);
//     // enable it back
//     preventFillSelectedAccs = false;
//     fillSelectedAccs();
// };

// var fillSelectedAccs = function() {
//     // do nothing if flag is set
//     if (preventFillSelectedAccs) {
//         console.log('preventFillSelectedAccs:', preventFillSelectedAccs);
//         return;
//     }
// };

// var preventFillSelectedAtts = false;

var toggleCheckAllAttachements = function(){
    // avoid cascade function call
    preventFillSelectedAtts = true;
    var is_checked = $(this).is(':checked');
    $('.attachements-table tbody .form-check-input').prop('checked', is_checked);
    // enable it back
    preventFillSelectedAtts = false;
    fillSelectedAtts();
};

var updateAttachements = function(){
    if( $('.attachements-table').length == 0 )
        return;

    var table = $('.attachements-table'),
        url =  table.data('url'),
        checkbox_template = $('.alert-templates .cool-checkbox').html();

    axios.get(url)
        .then(function(response) {
            var type = response.data.success ? 'success' : 'error';
            // showAlert(type, response.data.message);
            var data = response.data.data;
            var new_body = '';

            for (var i = 0; i < data.length; i++) {
                var row = data[i];

                var checkbox_html = checkbox_template
                                    .replace(/\{checkbox_id\}/gmi, 'checkbox_' + row.id)
                                    .replace(/\{checkbox_text\}/gmi, '&nbsp;')
                                    .replace(/\{checkbox_value\}/gmi, row.id)
                                    .replace(/\{checkbox_name\}/gmi, 'selected_atts[]');

                new_body += "<tr>"
                            + "<td>" +row.id+ "</td>"
                            + "<td>" +row.name+ "</td>"
                            + "<td>" +row.size+ "</td>"
                            + "<td>" +row.used+ "</td>"
                            + "<td>" +checkbox_html+ "</td>"
                            +"</tr>";

                table.find('tbody').html(new_body);
            }
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
            }else{
                text += '<br>' + (error.response.data.exception + '<br>' || '') + (error.response.data.file + "(" + error.response.data.line + ")" + '<br>' || '');
            }

            showAlert('error', text);
        })
        .then(function() {
            // toggleLoader(false);
        });
};

var fillSelectedAtts = function() {
    // do nothing if flag is set
    if (preventFillSelectedAtts) {
        console.log('preventFillSelectedAtts:', preventFillSelectedAtts);
        return;
    }
};

var selected_mail_accounts = [];
var selected_attachments = [];
var selected_spam_bases = [];
var campaignSubmitMessage = function(evt) {
    var form = $(evt.target) ,
        url = form.attr('action');

    evt.preventDefault();
    var formData = new FormData();

    var validationFailed = false;

    // check if we selected at least one account, and we are on new campaign page
    // if( form.find('table.accounts-table').length )
    //     if( form.find('input[name="selected_accs[]"]:checked').length == 0 ){
    //         validationFailed = true;
    //         showAlert('error', "Please select at least one account to send");
    //         return false;
    //     }

    // check for not selected accounts only if they are shown
    if(selected_mail_accounts.length == 0 && $('.vue_mail_accs-table').length && selected_spam_bases.length == 0){
        validationFailed = true;
        showAlert('error', "Please select at least one email account or spam base");
        // return false;
    }

    for (var i = 0; i < selected_mail_accounts.length; i++) {
        formData.append('selected_accs[]', selected_mail_accounts[i]);
    }

    if ($('#has_attaches').is(':checked') && selected_attachments.length == 0 && $('.vue_list_records-table').length ){
        validationFailed = true;
        showAlert('error', "Please select at least one attachement to send");
        // return false;
    }

    for (var i = 0; i < selected_attachments.length; i++) {
        formData.append('selected_atts[]', selected_attachments[i]);
    }

    for (var i = 0; i < selected_spam_bases.length; i++){
        formData.append('selected_bases[]', selected_spam_bases[i]);
    }

    // process form
    form.find('input, textarea, select').each(function() {
        var $el = $(this);
        // debugger;
        var name = $el.attr('name'), val = $el.val() || $el.html() || '';

        // skip unchecked radios and checkboxes
        if( ($el.attr('type') == 'checkbox' || $el.attr('type') == 'radio' ) && !$el.is(':checked')){
            return true;
        }

        // skip disabled textarea
        var tag_name = $el.prop("tagName").toLowerCase();
        if( $el.is(':disabled') && tag_name == 'textarea' ){
            return true;
        }


        // process files differently, only if they are enabled
        // https://stackoverflow.com/a/9062788
        if ($el.attr('type') == 'file' && $el.is(':enabled')) {
            var el = $el.get(0),
                ins = el.files.length;

            for (var x = 0; x < ins; x++) {
                formData.append(name, el.files[x]);
            }
        }else{
            formData.append(name, val);
        }

        /*if ($el.attr('type') == 'file') {
            var el = $el.get(0),
                ins = el.files.length;

            // check for new attachements only if we are on new campaign page
            if(ins < 1 && form.find('table.accounts-table').length ){
                validationFailed = true;
                showAlert('error', "Please add at least one file to message");
            }
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
        }*/
    });
    if( validationFailed ){
        // $('.alert-container').focus();
        $([document.documentElement, document.body]).animate({
            scrollTop: $(".alert-container").offset().top - 20
        }, 150);
        return false;
    }

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
            updateAttachements();
            $([document.documentElement, document.body]).animate({
                scrollTop: $(".alert-container").offset().top - 20
            }, 150);
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

    console.log('headers data:', data);
    $('#sendmailform input[name="headers"]').val(JSON.stringify(data));
};

var campaignAddHeader = function(evt){
    evt.preventDefault();
    var tpl = $('.headers-template').html();
    $('.custom-headers-container').append(tpl);

    $('.custom-headers-container .form-control').off('change').on('change', campaignHeadersChangeHandler);
    return false;
};

var toggleIsHTMLCheckBox = function(evt){
    var is_checked = $(this).is(':checked');
    if( is_checked ){
        $('#html_editor_container').removeClass('d-none');
        $('#letterbody').addClass('d-none');
    }else{
        $('#html_editor_container').addClass('d-none');
        $('#letterbody').removeClass('d-none');
    }
};

var randStr = function(size_min, size_max=0, possible="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789") {
    var text = "";
    // var possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";

    var size = size_min;
    if( size_max != 0)
        size = Math.floor(Math.random()*(size_max-size_min+1)+size_min);

    for (var i = 0; i < size; i++)
        text += possible.charAt(Math.floor(Math.random() * possible.length));

  return text;
};

var generateReplyModeString = function(htmlString){
    var mail_dump = window['mail_dump'];
    var new_string = reply_tpl.replace(/\{subject\}/g, mail_dump_data.headers.Subject)
                            .replace(/\{from\}/g, mail_dump_data.headers.From)
                            .replace(/\{to\}/g, mail_dump_data.headers.To)
                            .replace(/\{orig_body\}/g, mail_dump_data.body)
                            .replace(/\{new_text\}/g, htmlString)
                            .replace(/\{date\}/g, mail_dump_data.headers.Date.split('-')[0].split("+")[0])
                            .replace(/\{from_name\}/g, mail_dump_data.headers.From.split(/\s/)[0])
                            ;

    return new_string;

    // return htmlString;
}

var previewHtmlHandler = function(evt){

    // debugger;
    evt.preventDefault();
    evt.stopPropagation();

    var attachString = $('#attach_name').val();
    attachString = stringProcessMacro(evt, attachString, false);
    $('#attach_name_preview').val(attachString);


    var subjString = $('#subject').val();

    var htmlString = $('#letterbody').val();
    htmlString = stringProcessMacro(evt, htmlString, false);

    if( $('#reply_mode').is(':checked') ){
        htmlString = generateReplyModeString(htmlString);
        subjString = "Re: " + mail_dump_data.headers.Subject;
    }else{
        subjString = stringProcessMacro(evt, subjString, true);
    }
    // apply subject only after all processings
    $('#subject_preview').val(subjString);

    // process headers
    var custom_headers_data = $('#sendmailform input[name="headers"]').val()+'',
        custom_headers = custom_headers_data.length ? JSON.parse(custom_headers_data) : {};
    var headers_html = '';
    for (var key in custom_headers) {
        headers_html += '<tr><td>'+key+'</td><td>' + stringProcessMacro(evt, custom_headers[key], false) + '</td></tr>';
    }
    $('.table-headers-preview tbody').html( headers_html );
    if( headers_html.length ){
        $('.headers-preview').removeClass('d-none');
    } else {
        $('.headers-preview').addClass('d-none');
    }



    // if not html - replace \r\n with <br/>
    if( !$('#is_html').is(':checked') ){
        htmlString = "<div style=\"font-family: monospace\">" + htmlString.replace(/(\r)?\n/gmi, '<br/>') + "</div>";
    }

    // console.log('htmlString', htmlString);
    var iFrame = $('#mailPreviewContainer');

    var iFrameDoc = iFrame[0].contentDocument || iFrame[0].contentWindow.document;
    iFrameDoc.write(htmlString);
    iFrameDoc.close();

    $('.preview-html').removeClass('d-none');

    return false;
};

var stringProcessMacro = function(evt, my_string, allow_change_repl=true) {
    var macros_data = {
        "from_name_orig" : $(evt.target).data('macro-from-name'),
        "from_name" : $(evt.target).data('macro-from-name'),
        "to_name" : $(evt.target).data('macro-to-name'),
        "from_email" : $(evt.target).data('macro-from-email'),
        "from_email_orig" : $(evt.target).data('macro-from-email'),
        "to_email" : $(evt.target).data('macro-to-email'),
        "price": (91 + Math.random()*(950-91) ).toFixed(2),
        "rand_str": randStr(24),
        "acc_name": $('#account_name').val() ? $('#account_name').val() : $(evt.target).data('macro-from-name')
    };

    // get all templates avaiable
    // var macros_templates = JSON.parse($(evt.target).data('macro-tpls'));
    var macros_templates = $(evt.target).data('macro-tpls');
    // console.log('macros_templates', macros_templates);
    // process templates before any system macros
    // [%%ORandText,macro_name%%]
    for (var i = 0; i < macros_templates.length; i++) {
        var name = macros_templates[i].name,
            content = macros_templates[i].content,
            content_items = content.split('\n'),
            rnd_content_string = content_items[Math.floor(Math.random()*content_items.length)];


        // avoid any possible escapings in creating regexps
        while(my_string.indexOf(name) > -1){
            my_string = my_string.replace(name, rnd_content_string);
        }
    }

    if( macros_data['acc_name'].length ){
        // split by email and name
        var addresses = addressparser(macros_data['acc_name']);
        // console.log(addresses); // [{name: "andris", address:"andris@tr.ee"}]
        if(addresses.length){
            if( addresses[0]['name'] ) macros_data['from_name'] = addresses[0]['name'];
            if( addresses[0]['address'] ) macros_data['from_email'] = addresses[0]['address'];
        }
    }

    // console.log('macros_data', macros_data)

    my_string = my_string
                            .replace(/\[\%\%ACCORIGNAME\%\%\]/gmi, macros_data['from_name_orig'])
                            .replace(/\[\%\%ACCORIGMAIL\%\%\]/gmi, macros_data['from_email_orig'])
                            .replace(/\[\%\%FROMNAME\%\%\]/gmi, macros_data['from_name'])
                            .replace(/\[\%\%TONAME\%\%\]/gmi, macros_data['to_name'])
                            .replace(/\[\%\%FROMEMAIL\%\%\]/gmi, macros_data['from_email'])
                            .replace(/\[\%\%TOEMAIL\%\%\]/gmi, macros_data['to_email'])
                            .replace(/\[\%\%PRICE\%\%\]/gmi, macros_data['price'])
                            .replace(/\[\%\%RANDSTR\%\%\]/gmi, macros_data['rand_str'])
                            .replace(/\[\%\%ACCOUNTNAME\%\%\]/gmi, macros_data['acc_name'])
                            .replace(/\[\%\%FROMEMAILDOMAIN\%\%\]/gmi, macros_data['from_email'].split('@').pop())
                            ;

    my_string = macrosMultiOptionReplace(my_string, allow_change_repl);
    my_string = megaMacrosReplace(my_string, allow_change_repl);

    return my_string;
};

var macrosMultiOptionReplace = function(my_string, allow_change_repl=true){
    var pattern = /(\[\%\%)(.+?)(\%(\(?const\)?)?\%\])/gmi;
    var search_res = [];
    var match = pattern.exec(my_string);
    while (match != null) {
        search_res.push(match);
        match = pattern.exec(my_string);
    }

    var search_res_unique = search_res.filter(function(item, current_index){
        var first_index = -1;
        for (var i = 0; i < search_res.length; i++)
            if( search_res[i][0] == item[0] )
                first_index = i;

        return first_index == current_index;
    });

    for (var i = 0; i < search_res_unique.length; i++) {
        var item = search_res_unique[i],
            repl_pattern = item[0];

        if(item.length > 3 && item[4] && item[4].toLowerCase() == 'const'){
            var repl = ''
            if (!change_sequence_items[repl_pattern] || allow_change_repl){
                var strings = item[2].split("|");
                repl = strings[Math.floor(Math.random()*strings.length)];
                change_sequence_items[repl_pattern] = repl;
            }else{
                repl = change_sequence_items[repl_pattern];
            }
            while( my_string.indexOf(repl_pattern) !== -1 )
                my_string = my_string.replace(repl_pattern, repl);
        }else{
            while( my_string.indexOf(repl_pattern) !== -1 ){
                var strings = item[2].split("|");
                var repl = strings[Math.floor(Math.random()*strings.length)];
                my_string = my_string.replace(repl_pattern, repl);
            }
        }
    }

    return my_string;
};

var change_sequence_items = {};
var megaMacrosReplace = function(my_string, allow_change_repl=true){
    var pattern = /(\[\%ORandStr\%)(.+?)(\%(\(?const\)?)?\%\])/gmi;

    var search_res = [];
    var match = pattern.exec(my_string);
    while (match != null) {
        search_res.push(match);
        match = pattern.exec(my_string);
    }

    var search_res_unique = search_res.filter(function(item, current_index){
        var first_index = -1;
        for (var i = 0; i < search_res.length; i++)
            if( search_res[i][0] == item[0] )
                first_index = i;

        return first_index == current_index;
    });

    var choose_str = 'abcdefghijklmnopqrstuvwxyz0123456789';
    var choose_str_rev = 'abcdefghijklmnopqrstuvwxyz0123456789';
    // var choose_str_upper = choose_str.toUpperCase();

    for (var i = 0; i < search_res_unique.length; i++) {
        var item = search_res_unique[i],
            repl_pattern = item[0];

        // console.log('Processing pattern:', repl_pattern);

        // nerate all variables

        var splitted = item[2].split(',');
        var size, size, alphabet, letter_case, change_sequence;

        if( splitted.length > 0 ) size = splitted[0];
        if( splitted.length > 1 ) alphabet = splitted[1];
        if( splitted.length > 2 ) letter_case = splitted[2];
        if( splitted.length > 3 ) change_sequence = splitted[3];

        var size_min = parseInt( size.split('-')[0]),
            size_max = parseInt( size.split('-')[1]),
            alpha_min = alphabet.split('-')[0],
            alpha_max = alphabet.split('-')[1];

        // console.log('size_min', size_min, 'size_max', size_max, 'alpha_min', alpha_min, 'alpha_max', alpha_max);

        // get array of characters for f-0
        var chars = choose_str.substring( choose_str.indexOf(alpha_min), choose_str.indexOf(alpha_max)+1 );
        // case if 0-f
        if( !isNaN(alpha_min) && isNaN(alpha_max) )
            chars = choose_str_rev.substring( choose_str_rev.indexOf(alpha_min), choose_str_rev.indexOf(alpha_max)+1 );

        //
        if(letter_case == 'U'){
            chars = chars.toUpperCase();
        }else if(letter_case == 'L'){
            // do nothing we are happy
        }else if(letter_case == 'UL' || letter_case == 'LU'){
            // randomly choose:
            if (Math.random() > 0.5)
                chars = chars.toUpperCase();
        }else if(letter_case == 'R'){
            // both
            chars = chars + chars.toUpperCase();
            chars = chars.split('')
                .filter(function(item, pos, self) {
                  return self.indexOf(item) == pos;
                })
                .join('');
        }

        // console.log("chars:", chars);

        if(item[4] && item[4].toLowerCase() == 'const'){
            var repl = '';
            if( !change_sequence_items[repl_pattern] || allow_change_repl ){
                repl = randStr(size_min, size_max, chars);
                change_sequence_items[repl_pattern] = repl
            }else{
                repl = change_sequence_items[repl_pattern];
            }

            while( my_string.indexOf(repl_pattern) !== -1){
                my_string = my_string.replace(repl_pattern, repl);
            }
        }else{
            while( my_string.indexOf(repl_pattern) !== -1){
                repl = randStr(size_min, size_max, chars);
                my_string = my_string.replace(repl_pattern, repl);
            }
        }
    }

    return my_string
};

var getHtmlEditorContent = function(){
    return $('#html_editor').trumbowyg('html');
};

var setHtmlEditorContent = function(data){
    return $('#html_editor').trumbowyg('html', data);
};

var updateLetterBodyFromHemlEditor = function(evt){
    var data = getHtmlEditorContent();
    // console.log('updateLetterBodyFromHemlEditor data');
    // console.log(data);
    $('#letterbody').val( data );
};

var tinyMceChange = function(ed)
{
    var data = ed.getContent();
    // console.debug('Editor contents was modified. Contents: ' + ed.getContent());
    $('#letterbody').val( data );
};

var newCampaignPage = function(argument) {
    // $('.accounts-table tbody .form-check-input').change(fillSelectedAccs);
    $('#sendmailform').submit(campaignSubmitMessage);

    // $('#selectAllAccounts').change(toggleCheckAllAccounts);
    // $('#selectAllAccounts').prop("checked", false);
    // toggleCheckAllAccounts();

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

    filters.processFilterToggle($('#filtersContainer'));

    $('#is_html').change(toggleIsHTMLCheckBox);
    // somewhi this shit need to be activated like this as blade checked property refuses to work normally
    if( $('#is_html').data('checked') == 1 )
        $('#is_html').prop('checked', true).change();

    if( $('#ignore_selfhost').data('checked') == 1 )
        $('#ignore_selfhost').prop('checked', true);
    else
        $('#ignore_selfhost').prop('checked', false);
    // thou this is not happens to "ignore self host"

    // determine some shit errors
    // $.trumbowyg.svgPath = '/svg/icons.svg';
    // $('#html_editor')
    // .trumbowyg()
    // .on('tbwchange', updateLetterBodyFromHemlEditor)
    // .on('tbwpaste', updateLetterBodyFromHemlEditor)
    // .trumbowyg('html', $('#letterbody').text() )
    // ;
    // setHtmlEditorContent( $('#letterbody').val() );

    // tinymce init
    tinymce.init({
        selector: "#tinymce_textarea",
        plugins: "code fullpage",
        // toolbar: "code fullpage",
        setup: function (ed) {
            ed.on('keyup', function (e) {
                tinyMceChange(ed);
            });
            ed.on('change', function(e) {
                tinyMceChange(ed);
            });
        }
    });

    // fill editor with data
    // if($('#letterbody').val())
    //     editor.setContent($('#letterbody').val());
    tinymce.activeEditor.setContent($('#letterbody').val());

    $('#is_html').change();


    $('#previeButton button').on('click', previewHtmlHandler);

    $('#selectAllAttachements').change(toggleCheckAllAttachements);
    toggleCheckAllAttachements();

    if(typeof mail_dump_data !== "undefined"){
        mail_dump_data.headers = JSON.parse(mail_dump_data.headers.replace(/\\\\/gmi, '\\'));
        // console.log('mail_dump:', mail_dump_data);
    }


    $('#reply_mode').change(function(evt){
        var is_checked = $(this).is(':checked');
        // console.log('change fired', is_checked);
        if(is_checked){
            $('.reply-days').removeClass('d-none');
            // disable file input
            $('#file_list, #outer_addresses').prop('disabled', true);
        }else{
            $('.reply-days').addClass('d-none');
            $('#file_list, #outer_addresses').prop('disabled', false);
        }
    });

    $('#reply_mode').change();

    $('#datetimepicker2').datetimepicker({timeZone: 'UTC'});
    $('#datetimepicker2').on('change.datetimepicker', function(evt){
        // console.log('checked:', dt)
        var date = evt.date.format('YYYY.MM.DD.HH.mm') + '.00';
        // console.log('date:', date);
        $('#schedule').val(date);
        $('#startCampaign').attr('checked', false);
    });

    // clear schedule
    $('#startCampaign').change(function(){
        $('#datetimepicker2 input, #schedule').val('');
    });
};

// init only on /scan_rules path
if (/^\/campaigns\/((new)|(show\/\d+))$/gmi.test(window.location.pathname)) {
    // start listening above all
    addEventListener('selected-cmpgn-att-list', (evt)=>{ selected_attachments = evt.detail.ids;});
    addEventListener('selected-cmpgn-mac-list', (evt)=>{ selected_mail_accounts = evt.detail.ids; $('#reCreateAddressBook').prop('checked', true).change(); });
    addEventListener('selected-cmpgn-spam-base-list', (evt)=>{ selected_spam_bases = evt.detail.ids; $('#reCreateAddressBook').prop('checked', true).change(); });

    // console.log('we are at campaign.new.js');
    // console.log('reply mode tpl:' ,reply_tpl);
    $(document).ready(newCampaignPage);
}
