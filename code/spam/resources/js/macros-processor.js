var addressparser = require('addressparser');

var emptyObject = function(obj) {
	return Object.keys(obj).length === 0 && obj.constructor === Object
}

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

var stringProcessMacro = function(evt, my_string, allow_change_repl=true, _macros_data={}, macros_templates=[]) {
	var macros_data = _macros_data;

	if( emptyObject(_macros_data) ) {
        if(evt){
    		// console.log('we got empty _macros_data', _macros_data);
    	    macros_data = {
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
    	}
    }

    // get all templates avaiable
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

    if( macros_data['acc_name'] && macros_data['acc_name'].length ){
        // split by email and name
        var addresses = addressparser(macros_data['acc_name']);
        // console.log(addresses); // [{name: "andris", address:"andris@tr.ee"}]
        if(addresses.length){
            if( addresses[0]['name'] ) macros_data['from_name'] = addresses[0]['name'];
            if( addresses[0]['address'] ) macros_data['from_email'] = addresses[0]['address'];
        }
    }

    my_string = my_string.replace(/\[\%\%FROMNAME\%\%\]/gmi, macros_data['from_name'])
                            .replace(/\[\%\%TONAME\%\%\]/gmi, macros_data['to_name'])
                            .replace(/\[\%\%FROMEMAIL\%\%\]/gmi, macros_data['from_email'])
                            .replace(/\[\%\%TOEMAIL\%\%\]/gmi, macros_data['to_email'])
                            .replace(/\[\%\%PRICE\%\%\]/gmi, macros_data['price'])
                            .replace(/\[\%\%RANDSTR\%\%\]/gmi, macros_data['rand_str'])
                            ;

    my_string = macrosMultiOptionReplace(my_string, allow_change_repl);
    my_string = megaMacrosReplace(my_string, allow_change_repl);

    return my_string;
};

var macrosMultiOptionReplace = function(my_string, allow_change_repl=true){
    var pattern = /(\[\%\%)(.+?)(\%(const)?\%\])/gmi;
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

        if(item[4] && item[4].toLowerCase() == 'const'){
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
    var pattern = /(\[\%ORandStr\%)(.+?)(\%(Const)?\%\])/gmi;

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
    var choose_str_upper = choose_str.toUpperCase();

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

        // get array of characters
        var chars = choose_str.substring( choose_str.indexOf(alpha_min), choose_str.indexOf(alpha_max)+1 );
        //
        if(letter_case == 'U'){
            chars = chars.toUpperCase();
        }else if(letter_case == 'L'){
            // do nothing we are happy
        }else{
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

export {
	stringProcessMacro
}
