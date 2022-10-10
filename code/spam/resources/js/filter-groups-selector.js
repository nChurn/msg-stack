var processFilterToggle = function($container, force_uncheck){
	// $container.find('.filter-groups')
	$('.filter-groups .check-all', $container).off('change').on('change', function(){
		var is_checked = $(this).is(':checked');
		$('.filter-groups .check-group', $container).prop('checked', is_checked).data('checked', is_checked ? 1 : 0);
	}).prop('checked', false);

	// in case of filters passed selected value
	$('.filter-groups .check-group', $container).each(function(){
		var self_checked = $(this).data('checked') == 1;
		$(this).prop('checked', self_checked);
	});

	if(force_uncheck)
		$('.filter-groups .check-all', $container).change();
};

export {
	processFilterToggle
}