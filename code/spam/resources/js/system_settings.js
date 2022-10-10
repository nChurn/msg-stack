    
var systemSettingsPage = function (argument) {
	$('.update-form').on('submit', formSubmitter);
};


// init only on /scan_rules path
if (/^\/settings$/gmi.test(window.location.pathname)) {
    console.log('we are at system settings');
    $(document).ready(systemSettingsPage);
}