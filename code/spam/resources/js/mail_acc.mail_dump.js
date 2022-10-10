var paginator = require('./paginator.js');

var calculateWorkArea = function(evt){
    var bodyHeight = $(document.body).outerHeight(true),
        windowHeight = window.innerHeight,
        footerHeight = $('.page-footer').outerHeight(true),
        navbarHeight = $($('.navbar').get(0)).outerHeight(true),
        contentHeaderHeight = $('.mail-dump-header').outerHeight(true),
        contentFiltersHeight = $('.mail-dump-filters').outerHeight(true)
        separatorHeight = $($('hr').get(0)).outerHeight(true),
        bodyMargins = parseFloat($('.main-content').css('margin-top').replace('px', '')) + parseFloat($('.main-content').css('margin-bottom').replace('px', '')),
        paginatorHeigh = $('.paginator').outerHeight(true)
        selectAllHeight = $('.select-all-letters-container').outerHeight(true);

    var resulting_height = windowHeight 
                            - bodyMargins 
                            - footerHeight 
                            - navbarHeight 
                            - contentHeaderHeight 
                            - contentFiltersHeight 
                            - separatorHeight 
                            - paginatorHeigh 
                            - selectAllHeight 
                            - 2; // 2 px is for calculating mistakes and roundings
    // console.log('resulting_height', resulting_height);
    $('.mail-dump-list-inner-container, .mail-body-details-container').css('max-height', resulting_height + 'px');//.height(resulting_height);

    // and make scrollable mail data container
    var headerHeight = $('.mail-dump-ui-header-container').outerHeight(true),
        somePaddings = 10;

    $('.mail-dump-main-data-container').height( resulting_height - headerHeight -somePaddings );
};

var toggleCheckAllRecords = function(evt){
    var is_checked = $(this).is(':checked');
    $('.mail-dump-list-container .form-check-input').prop('checked', is_checked);
};

var getSelectedRecordsIds = function(){
    return $('.mail-dump-record .form-check-input:checked').map(function(index, item){ return item.value; }).toArray();
};

var multiSelectActionsClickHandler = function(evt){
    var $el = $(evt.target);
    var option = "";
    if($el.hasClass('mail-dump-get-letter')){
        if( !confirm('Download slected letters body?') )
            return false;
        option = "download";
    }else if($el.hasClass('mail-dump-dl-remove-letter')){
        if( !confirm('Remove selected letterr?') )
            return false;
        option = "delete";
    }

    // unrealized options
    if(option == "") return false;

    var data = {
        "option": option,
        "ids": getSelectedRecordsIds()
    };
    toggleLoader(true);
    massUpdateRequest(data)
        .then(function(response){
            var type = response.data.success ? 'success' : 'error';
            showAlert(type, response.data.message);
            appendIframeText( "Body download is in progress" );
        })
        .catch(function(error){
            var text = error.response.data.message + '<br>' + (error.response.data.exception + '<br>' || '') + (error.response.data.file + '<br>' || '');
            showAlert('error', text);
            toggleLoader(false);
        })
        .then(function(){
            // toggleLoader(false);
            $('.mail-dump-details-container').addClass('d-none');
            $('.mail-dump-record').removeClass('active');
            getCurrentPageRecordList(window.location.href);
        });
    
};

var massUpdateRequest = function(data){
    return axios.post(mass_update_api_url, data)
};

var applyEmailAccMailDumpMassChange = function(evt){
    // var option = $(evt.target).data('option');
    // $('#actionsocksform input[name="action"]').val( option );
    // get list of selected ids
    var selected = [];
    $('.mail_acc_maildump-table tbody .form-check-input:checked').each(function(){
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

var toggleMailLoader = function(show){
    if(show)
        $('.loader-bg, .loader-centered').removeClass('d-none');
    else
        $('.loader-bg, .loader-centered').addClass('d-none');
};

var appendIframeText = function(txt){
    var iFrame = $('.mail-dump-body-container .mail-dump-body-iframe');

    var iFrameDoc = iFrame[0].contentDocument || iFrame[0].contentWindow.document;
    iFrameDoc.write( txt.replace(/\r?\n/gmi, "<br/>").replace(/((\\r)?\\n)/gmi, "<br/>") );
    iFrameDoc.close();

    // as usual - some shit browser related, render not so fast
    // and params are not changed too soon
    setTimeout(function(){
        // proper height calculation pretty tricky:
        // https://stackoverflow.com/a/10787807
        var offsetHeight = iFrameDoc.body.offsetHeight;
        var elm = iFrameDoc.body;
        // var elmHeight = document.defaultView.getComputedStyle(elm, '').getPropertyValue('height');
        var elmMargin = parseInt(document.defaultView.getComputedStyle(elm, '').getPropertyValue('margin-top')) + parseInt(document.defaultView.getComputedStyle(elm, '').getPropertyValue('margin-bottom'));

        // console.log('elmHeight', elmHeight);
        // console.log('elmMargin', elmMargin);

        iFrame[0].style.height = (offsetHeight + elmMargin) +'px';
    }, 50);
};

var appendMailDumpData = function(data){
    $('.mail-dump-details-container').data('id', data.id);

    // work with header
    $('.mail-dump-body-from').html( data.from.replace(/\</g, "&lt;").replace(/\>/g, "&gt;") );
    $('.mail-dump-body-date').html( data.mail_date );
    $('.mail-dump-body-to').html( data.to.replace(/\</g, "&lt;").replace(/\>/g, "&gt;") );
    $('.mail-dump-body-subject').html( data.subject.replace(/\</g, "&lt;").replace(/\>/g, "&gt;") );
    
    // work with body
    var body_txt = '';
    body_txt = data.need_body == 1 ? "Body download is in progress" : data.body;
    appendIframeText( body_txt );

    // work with raw headers
    var headers_html = "";
    if (data.headers && data.headers.length){
        var headers_json = JSON.parse(data.headers)
        // console.log('processing headers:', headers_json);
        for(var key in JSON.parse(data.headers)){
            headers_html += key + "&nbsp;:&nbsp;" + headers_json[key] + "<br/>";
        }
    }
    $(".mail-dump-headers-container").html( headers_html.replace(/\</g, "&lt;").replace(/\>/g, "&gt;") );

    $('.mail-dump-details-container').removeClass('d-none');

    // show only icons that are suitable
    if(data.body)
        $('.mail-dump-body-actions .mail-dump-get-letter').addClass('d-none');
    else
        $('.mail-dump-body-actions .mail-dump-get-letter').removeClass('d-none');

    if(data.has_attaches == 2)
        $('.mail-dump-body-actions .mail-dump-dl-attach').removeClass('d-none');
    else
        $('.mail-dump-body-actions .mail-dump-dl-attach').addClass('d-none');
    
    // work with attaches
    var attaches = data.attach_path.split(',');
    var att_tpl = $('.attaches-one-attach-template').html();
    var attaches_html = '';
    for (var i = 0; i < attaches.length; i++) {
        var url = mail_dump_download_attach_url.replace(/mail_dump_id/gmi, data.id) + "/" + i;
        var att_name = attaches[i].split('/').pop();

        var attach_html = att_tpl.replace(/\{attach_url\}/, url)
                                .replace(/\{filename\}/, att_name);

        attaches_html += attach_html;

    }

    if(data.has_attaches == 2)
        $(".mail-dump-attach-list").html(attaches_html);
    else
        $(".mail-dump-attach-list").html('');

    calculateWorkArea();
};

var mailDumpActionsClickHandler = function(evt){
    var $el = $(evt.target);

    // console.log($el);
    var dump_id = $('.mail-dump-details-container').data('id');

    if($el.hasClass('mail-dump-show-headers')){
        // console.log('we have class, ');
        $('.mail-dump-headers-container').toggleClass('d-none');
        calculateWorkArea();
    }else if($el.hasClass('mail-dump-get-letter')){
        if( !confirm('Download letter body?') )
            return false;

        
        var data = {
            "option": "download",
            "ids": [dump_id]
        };
        toggleLoader(true);
        massUpdateRequest(data)
            .then(function(response){
                var type = response.data.success ? 'success' : 'error';
                showAlert(type, response.data.message);
                appendIframeText( "Body download is in progress" );
            })
            .catch(function(error){
                var text = error.response.data.message + '<br>' + (error.response.data.exception + '<br>' || '') + (error.response.data.file + '<br>' || '');
                showAlert('error', text);
            })
            .then(function(){
                toggleLoader(false);
                $('.mail-dump-details-container').removeClass('d-none');
                // getCurrentPageRecordList(window.location.href); 
            });
    }else if($el.hasClass('mail-dump-dl-remove-letter')){
        if( !confirm('Remove letter?') )
            return false;
        
        var dump_id = $('.mail-dump-details-container').data('id');
        var data = {
            "option": "delete",
            "ids": [dump_id]
        };
        toggleLoader(true);
        massUpdateRequest(data)
            .then(function(response){
                var type = response.data.success ? 'success' : 'error';
                showAlert(type, response.data.message);
            })
            .catch(function(error){
                var text = error.response.data.message + '<br>' + (error.response.data.exception + '<br>' || '') + (error.response.data.file + '<br>' || '');
                showAlert('error', text);
            })
            .then(function(){
                $('.mail-dump-details-container').addClass('d-none');
                getCurrentPageRecordList(window.location.href); 
            });
    }else if($el.hasClass('mail-dump-dl-attach')){
        var url = mail_dump_download_attach_url.replace('mail_dump_id', dump_id);
        // window.location.href = url;
        window.open(url,'_blank');
    }
};

var showDumpListClickHandler = function(evt){
    // if clicked on abc-checkbox
    if($(evt.target).hasClass('form-check-input') || $(evt.target).hasClass('form-check-label'))
        return true

    evt.preventDefault();
    evt.stopPropagation();
    var mail_id = $(evt.target).closest('.mail-dump-record').data('id');

    $(evt.target).closest('.mail-dump-record').parent().find('.mail-dump-record').removeClass('active');
    $(evt.target).closest('.mail-dump-record').addClass('active');
    // console.log('retrive data for item:' + mail_id);

    var url = api_url.replace('item_id', mail_id);

    toggleMailLoader(true);

    axios.get(url)
        .then(function(response) {
            // var type = response.data.success ? 'success' : 'error';
            if(response.data.success){
                appendMailDumpData(response.data.data);
            }else{
                showAlert('error', response.data.message);
            }
        })
        .catch(function(error) {
            console.log('error', error);
            // var text = error.response.data.message + '<br>' + (error.response.data.exception + '<br>' || '') + (error.response.data.file + '<br>' || '');
            // showAlert('error', text);
        })
        .then(function() {
            toggleMailLoader(false);
            window.scrollTo(0,0);
        });

    return false;
};

var generateDumpListHtml = function(rows){
    var tpl = $('.mail-dump-record-tpl').html();
    var res_html = '';
    var has_attach_html = '<i class="fa fa-paperclip" aria-hidden="true" title="Mail with attachement(s)"></i>';
    var likely_has_attach = '<i class="fa fa-low-vision" aria-hidden="true" title="Likely mail has attachement"></i>';

    var no_body = '<i class="fa fa-file-o" aria-hidden="true" title="Mail body not downloaded"></i>';
    var body_in_progress = '<i class="fa fa-cloud-download" aria-hidden="true" title="Mail body download in progress"></i>';
    var body_dl_ok = '<i class="fa fa-file-text-o" aria-hidden="true" title="Mail body download complete"></i>';


    for (var i = 0; i < rows.length; i++) {
        var row = rows[i];
        var attach_decision = '&nbsp;';

        if(row.has_attaches == 1)
            attach_decision = likely_has_attach;
        else if(row.has_attaches == 2)
            attach_decision = has_attach_html;

        if(row.need_body == 0)
            attach_decision += no_body;
        else if (row.need_body == 1)
            attach_decision += body_in_progress;
        else if (row.need_body == 2)
            attach_decision += body_dl_ok;

        var row_html = tpl.replace(/\{id\}/gmi, row.id)
                            .replace(/\{from\}/gmi, row.from)
                            .replace(/\{mail_date\}/gmi, row.mail_date || '')
                            .replace(/\{subject\}/gmi, row.subject.replace(/\"/gmi, "\\\"").replace(/\'/, "\\\'"))
                            .replace(/\{attach\}/gmi, attach_decision );

        res_html += row_html;
    }

    return res_html;
};

var generateDumpList = function(all_data){
    console.log('generateDumpList', all_data);
    var data = all_data.data;

    var paginator_html = paginator.generatePaginator(data);
    $('.paginator').html(paginator_html);
    console.log('generateDumpList: paginator generated ok');

    var dump_list_html = generateDumpListHtml(data.data);
    $('.mail-dump-list-inner-container').html(dump_list_html);
    console.log('generateDumpList: dump list generated ok');
};

var getCurrentPageRecordList = function(url){
    var args = url.split('?');
    if( args.length > 1 ){
        // args = args[1];
        url += "&json=true";
    }else{
        url += "?json=true";
    }

    toggleLoader(true);
    axios.get(url)
        .then(function(response) {
            // debugger;
            generateDumpList(response.data);
        })
        .catch(function(error) {
            // debugger;
            var text = error.response.data.message + '<br>' + (error.response.data.exception + '<br>' || '') + (error.response.data.file + '<br>' || '');
            showAlert('error', text);
        })
        .then(function() {
            console.log('all is generated we are here');
            toggleLoader(false);
        });
};

var paginatorClickHandler = function(evt){
    evt.stopPropagation();
    evt.preventDefault();
    var url = $(evt.target).closest('a').attr('href'),
        args = url.split('?')[1];
    // chencge url so that next time we came on same page, it loads ok from controller
    window.history.pushState("", document.title, "?" + args);

    getCurrentPageRecordList(url);

    return false;
};

var emailAccMailDumpPage = function(argument) {
    $('#selectAllRecords').on('change', toggleCheckAllRecords).prop('checked', false).change();
    $('#adMassAction .dropdown-menu').click(applyEmailAccMailDumpMassChange);
    $(window).resize(calculateWorkArea);
    calculateWorkArea();
    $('.paginator').on('click', paginatorClickHandler);
    $('.mail-dump-list-inner-container').on('click', showDumpListClickHandler);

    $('.mail-dump-body-actions').on('click', mailDumpActionsClickHandler);
    $('.selected-mass-actions').on('click', multiSelectActionsClickHandler);

    
};

// init only on /socks path
if (/^\/mail_dump\/\d(\?.+)?/gmi.test(window.location.pathname)) {
    console.log('we are at email account mail dump');
    $(document).ready(emailAccMailDumpPage);
}
