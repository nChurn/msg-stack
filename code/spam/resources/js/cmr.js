var getCMR = function(){
    toggleLoader(true);

    axios.get(api_url)
        .then(function(response) {
            // response is ok
            if (response.data.success) {
            	$('#cmr').val(response.data.data.email);
            }
        })
        .catch(function(error) {
            // console.log('error:', error.response.data);
        })
        .then(function() {
            // always executed
    		toggleLoader(false);
        });
};

var cmrPage = function(argument) {
    $('.form-horizontal').on('submit', formSubmitter);
    getCMR();
};

// init only on /socks path
if (/^\/cmr.*/gmi.test(window.location.pathname)) {
    console.log('we are at cmr');
    $(document).ready(cmrPage);
}
