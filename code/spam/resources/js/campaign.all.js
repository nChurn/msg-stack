
var allCampaignPage = function(argument) {
    $('.campaigns-table').on('click', function(evt){
        // console.log(evt.target);
        var btn  = $(evt.target).closest('button.btn');
        // console.log(evt.target, btn);
        if(btn.length){
            var url = btn.data('action');
            // get nor returns pure DOMElement not wrapped in jQ object
            var message = btn.attr('title') + ' campaign "' + $(btn.closest('tr').find('td').get(1)).html() + '"?';
            console.log('url:', url);
            if(url && confirm(message + "\nAre you sure?"))
                window.location.href = url;
        }
    })
};

// init only on /scan_rules path
if (/^\/campaigns$/gmi.test(window.location.pathname) || /^\/$/gmi.test(window.location.pathname)) {
    console.log('we are at all campaign');
    $(document).ready(allCampaignPage);
}
