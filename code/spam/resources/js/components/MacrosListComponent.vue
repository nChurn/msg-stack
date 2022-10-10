<template>
    <div class="emacros-list-container">
        <h4>Macros templates list:</h4>
        <table class="table table-bordered table-sm table-striped vue_mail_accs-table">
            <thead>
                <tr>
                    <th>Name</th>
                    <th width="50%">Content</th>
                    <th width="50%">Preview</th>
                    <th>
                        <div class="form-check abc-checkbox abc-checkbox-info form-check-inline">
                            <input class="form-check-input" id="check_all_records" name="check_all_records" type="checkbox" v-model="selectAllRecords" v-on:change="allRecordsSelectHandler">
                            <label class="form-check-label" for="check_all_records">&nbsp;</label>
                        </div>
                    </th>
                </tr>
            </thead>
            <tbody>
                <tr :class="{'d-none': !isFetching}">
                    <td colspan="20" align="center">
                        <div class="progress">
                            <div class="progress-bar progress-bar-striped progress-bar-animated" role="progressbar" aria-valuenow="100" aria-valuemin="0" aria-valuemax="100" style="width: 100%"></div>
                        </div>
                    </td>
                </tr>
                <tr v-for="item in records" :class="{'d-none': isFetching}">
                    <td>{{item.name}}</td>
                    <td v-html="item.content"></td>
                    <td v-html="item.preview"></td>
                    <td>
                        <div class="form-check abc-checkbox abc-checkbox-info form-check-inline">
                            <input class="form-check-input" :id="'check_item'+item.name" name="check_mail_account" type="checkbox" v-model="item.is_checked" v-on:change="recordSelectHandler($event, item)">
                            <label class="form-check-label" :for="'check_item'+item.name">&nbsp;</label>
                        </div>
                    </td>
                </tr>
            </tbody>
        </table>
        <div class="row">
            <div class="col-12 text-right" :class="{'d-none': !show_mass_assign}">
                <div class="btn-group dropup">
                    <button class="btn btn-info dropdown-toggle" type="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                        Chose action
                    </button>
                    <div class="dropdown-menu dropdown-menu-right" ref="dropdown-menu">
                        <button class="dropdown-item" type="button" v-on:click="dropdownClickHandler($event, 'delete')" data-opntion="delete">Delete</button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
<script>
var addressparser = require('addressparser');
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
var stringProcessMacro = function(server_macro_data, my_string, allow_change_repl=true) {
    var macros_data = {
        "from_name_orig" : server_macro_data['from_name'],
        "from_name" : server_macro_data['from_name'],
        "to_name" : server_macro_data['to_name'],
        "from_email" : server_macro_data['from_email'],
        "from_email_orig" : server_macro_data['from_email'],
        "to_email" : server_macro_data['to_email'],
        "price": (91 + Math.random()*(950-91) ).toFixed(2),
        "rand_str": randStr(24),
        "acc_name": $('#account_name').val() ? $('#account_name').val() : server_macro_data['from_name']
    };

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
    var choose_str_rev = '0123456789abcdefghijklmnopqrstuvwxyz';
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


export default {
    props: {
        'mac_id': {
            type: String,
            default: "1"
        },
        'api_url': String,
        'remove_url': String,
        'selection_change_event_name': {
            type: String,
            default: 'macros-selection-{mac_id}'
        },
        'outer_selection_change_event_name': {
            type: String,
            default: 'macros-outer-selection-{mac_id}'
        },
        'macros_created_event_name': {
            type: String,
            default: 'macros-created-{mac_id}'
        },
        'selected_records':{
            type: Array,
            default: function() {return []}
        },
        'show_mass_assign':{
            type: Boolean,
            default: true
        }
    },
    data: function() {
        return {
            records: [],
            selectAllRecords: false,
            selectedRecords: [],
            isFetching: false,
            // macros_data: {}
        };
    },

    created() {
        // listen on event
        EventBus.$on(this.macros_created_event_name, (evt, data) => {
            this.fetch();
        });

        this.fetch();
    },

    methods: {
        fetch(evt) {
            this.isFetching = true;
            var request_url = this.api_url;
            var self = this;
            this.$http.get(request_url)
                .then((response) => {
                    var macros_data = response.data.macros_data;
                    this.records = response.data.data.map( (item) =>{
                        // item.content = item.content.replace(/\r?\n/gmi, '<br/>');
                        // get random string from content
                        let content_items = item.content.split('\n'),
                            rnd_content_string = content_items[Math.floor(Math.random()*content_items.length)];

                        item.preview = stringProcessMacro(macros_data, rnd_content_string, false);
                        return item;
                    });
                    // this.macros_data = response.data.macros_data;
                }).catch((error) => {
                    console.log('error', error);
                    this.showRequestError(error);
                })
                .then(() => {
                    this.isFetching = false;
                });
        },

        updateRecordsList(items) {
            this.records = items;
        },

        allRecordsSelectHandler(evt) {
            var selectAllRecords = this.selectAllRecords
            this.records.forEach(function(item) {
                item.is_checked = selectAllRecords;
            });

            if (!this.selectAllRecords) {
                // this.selectedRecords = [];
                // remove selected on current page
                var page_ids = this.records.map(function(item) { return item.name });
                this.selectedRecords = this.selectedRecords.filter((v)=> page_ids.indexOf(v) === -1 );
            } else {
                // push all items and
                this.selectedRecords = this.selectedRecords.concat( this.records.map(function(item) { return item.name }) )
                // sort for unique
                this.selectedRecords = this.selectedRecords.filter((v, i, a) => a.indexOf(v) === i);

                // push all items and sort for unique
                // this.selectedRecords = this.records.map(function(item) { return item.name });
            }
            this.dispatchSelectionEvent();
        },

        recordSelectHandler(evt, item) {
            if (item.is_checked) {
                this.selectedRecords.push(item.name);
            } else {
                this.selectedRecords = this.selectedRecords.filter(function(account_id) {
                    // console.log('compare', account_id, item.name);
                    return account_id !== item.name;
                })
            }

            this.dispatchSelectionEvent();
        },

        showRequestError(error) {
            var message = new String(error);
            if (typeof error == 'object' && error.response){
                message = error.response.statusText;
                if (error.response.data && typeof error.response.data == 'object') {
                    var err_data = error.response.data;
                    if (err_data.message) {
                        message = err_data.message;
                    }
                    if (err_data.file) {
                        message += "\nFile:" + err_data.file;
                    }
                    if (err_data.line) {
                        message += "\nLine:" + err_data.line;
                    }
                }
            }

            this.$toast.error({
                title: 'Error getting data',
                message: message,
                position: 'top right',
                timeOut: 7000,
                progressBar: false,
                hideDuration: 500
            });
        },

        showRequestSuccess(response, title) {
            if (!title) title = "Success";

            this.$toast.success({
                title: title,
                message: response.data.message,
                position: 'top right',
                timeOut: 3500,
                progressBar: false,
                hideDuration: 500
            });
        },

        dispatchSelectionEvent() {
            let ids = this.selectedRecords;
            let evt_name = this.selection_change_event_name.replace('{mac_id}', this.mac_id);
            var evt = new CustomEvent(evt_name, {
                detail: { "ids": ids }
            });
            window.dispatchEvent(evt);
            EventBus.$emit(evt_name, evt, this.selectedRecords);
        },

        dropdownClickHandler(evt, option) {
            if (this.selectedRecords.length && confirm('You are about to ' + option + ' records with id(s): ' + this.selectedRecords.join(','))) {
                this.$toast.info({
                    title: 'Removing selected macros',
                    message: "Please wait",
                    position: 'top right',
                    timeOut: 10000,
                    progressBar: true,
                    hideDuration: 0,
                });
                this.removeRecords();
            }
        },

        removeRecords(){
            this.isFetching = true;
            var request_url = this.remove_url;
            var self = this;
            var formData = {
                "keys": this.selectedRecords
            };
            this.$http.post(request_url, formData)
                .then((response) => {
                    // this.records = response.data.data.data;
                    this.showRequestSuccess(response, 'Macros removed');
                }).catch((error) => {
                    this.showRequestError(error);
                })
                .then(() => {
                    this.fetch();
                });
        },
    }
}

</script>
