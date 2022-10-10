// console.log('hui');
// based on laravel default paginator /views/default.blade.php

var generatePaginator = function (paginator) {
	var ret_html = '';

	// do not build if only one page is needed
	if(paginator.last_page > 1){
		ret_html += '<ul class="pagination" role="navigation">';

		// prev page url
		if(paginator.prev_page_url == null)
		{
			ret_html += '<li class="page-item disabled" aria-disabled="true" aria-label="« Previous"><span class="page-link" aria-hidden="true">‹</span></li>';
		}else{
			ret_html += '<li class="page-item"><a class="page-link" href="'+paginator.prev_page_url+'" rel="prev" aria-label="« Previous">‹</a></li>';
		}

		var regular_link = '<li class="page-item"><a class="page-link" href="{{url}}">{{page}}</a></li>';
		var regular_link_active = '<li class="page-item active" aria-current="page"><span class="page-link">{{page}}</span></li>';
		var dots_link = '<li class="page-item disabled" aria-disabled="true"><span class="page-link">...</span></li>';
		var dots_added_before = false;
		var dots_added_after = false;

		// render first 2, last 2 and 3 from each side of active
		for (var i = 1; i <= paginator.last_page; i++) {
			var page_url = paginator.first_page_url.split('page=')[0] + 'page=' + i;
			// make curent selected
			if( i == paginator.current_page){
				ret_html += regular_link_active.replace('{{page}}', i).replace("{{url}}", page_url);
				continue
			}

			// make first 2 always
			if( i < 3 ){
				ret_html += regular_link.replace('{{page}}', i).replace("{{url}}", page_url);
				continue;
			}

			// make last 2 always
			if( paginator.last_page - i < 3 ){
				ret_html += regular_link.replace('{{page}}', i).replace("{{url}}", page_url);
				continue;
			}

			// make 3 from each side of selected item
			if( Math.abs(i - paginator.current_page) < 4 ){
				ret_html += regular_link.replace('{{page}}', i).replace("{{url}}", page_url);
				continue;
			}

			// make dots
			if( paginator.current_page < i && !dots_added_before){
				dots_added_before = true;
				ret_html += dots_link;
				continue;
			}

			// make dots
			if( paginator.current_page < i && !dots_added_after){
				dots_added_after = true;
				ret_html += dots_link;
				continue;
			}

		}

		// next page url
		if( paginator.next_page_url == null )
		{
			ret_html += '<li class="page-item disabled" aria-disabled="true" aria-label="Next »"><span class="page-link" aria-hidden="true">›</span></li>';
		}else{
			ret_html += '<li class="page-item"><a class="page-link" href="'+paginator.next_page_url+'" rel="next" aria-label="Next »">›</a></li>';
			// '<li class="page-item"><a href="'+paginator.next_page_url+'" rel="next" aria-label="next page">&rsaquo;</a></li>';

		}

		ret_html += '</ul>';
	}

	return ret_html;
};

export{ generatePaginator }