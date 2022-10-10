<template>
    <div class="bases-lists-container">
        <table class="table table-bordered table-sm table-striped vue_list_records-table">
            <thead>
                <tr>
                    <th v-for="item in columns" :class="{'sorted': item.sorted}" v-on:click="setOrderBy(item.column)"><span>{{item.display}}<i :class="{ 'fa-sort-amount-asc': sortOrders[item.column] == 'asc', 'fa-sort-amount-desc': sortOrders[item.column] == 'desc', 'fa-sort': !sortOrders[item.column], 'd-none': !item.sorted }" class="fa pull-right" aria-hidden="true"></i></span></th>
                    <th v-if="show_actions">Actions</th>
                    <th>
                        <div class="form-check abc-checkbox abc-checkbox-info form-check-inline">
                            <input class="form-check-input" id="check_all_base_records" name="check_all_base_records" type="checkbox" v-model="selectAllRecords" v-on:change="allRecordsSelectHandler">
                            <label class="form-check-label" for="check_all_base_records">&nbsp;</label>
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
                <tr v-for="list_record in list_records" :class="{'d-none': isFetching}">
                    <td v-for="item in columns">
                        <span>{{list_record[item.column]}}</span>
                    </td>
                    <td v-if="show_actions">
                        <a :href="edit_url.replace('base_id', list_record.id)" title="edit"><i class="fa fa-pencil-square-o" aria-hidden="true"></i></a>
                        <a :href="export_url.replace('base_id', list_record.id)" title="export"><i class="fa fa-download" aria-hidden="true"></i></a>
                    </td>
                    <td>
                        <div class="form-check abc-checkbox abc-checkbox-info form-check-inline">
                            <input class="form-check-input" :id="'check_list_record_'+list_record.id" name="check_mail_account" type="checkbox" v-model="list_record.is_checked" v-on:change="listRecordSelectHandler($event, list_record)">
                            <label class="form-check-label" :for="'check_list_record_'+list_record.id">&nbsp;</label>
                        </div>
                    </td>
                </tr>
                <tr v-if="!list_records.length && !isFetching">
                    <td colspan="20" class="text-center">No records found</td>
                </tr>
            </tbody>
        </table>

        <div class="row" :class="{'d-none': !show_mass_assign}">
            <div class="col-3 text-right offset-md-9" :class="{'d-none': !show_mass_assign}">
                <div class="btn-group dropup">
                    <button class="btn btn-info dropdown-toggle" type="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                        Chose action
                    </button>
                    <div class="dropdown-menu dropdown-menu-right" ref="dropdown-menu">
                        <button class="dropdown-item" type="button" v-on:click="dropdownClickHandler($event, 'delete')" data-opntion="delete">Delete</button>
                        <button class="dropdown-item" type="button" v-on:click="dropdownClickHandler($event, 'automatics_enabled')" data-opntion="automatics_enabled">Enable automatics</button>
                        <button class="dropdown-item" type="button" v-on:click="dropdownClickHandler($event, 'automatics_disabled')" data-opntion="automatics_enabled">Disable automatics</button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
<script>
export default {
    props:{
        'api_url': String,
        'edit_url': String,
        'mass_update_url': String,
        'export_url': String,
        'show_mass_assign': {
            type: Boolean,
            default: true
        },
        'show_filters': {
            type: Boolean,
            default: true
        },
        'show_actions':{
            type: Boolean,
            default: true
        },
        'paginate_amount': {
            type: Number,
            default: 50
        },
        'component_id': {
            type: String,
            default: "1"
        },
        'selection_change_event_name': {
            type: String,
            default: 'base-list-record-selection-{component_id}'
        },
        'show_filters_apply_input': {
            type: Boolean,
            default: true
        },
        'page_name': {
            type: String,
            default: 'bl_page'
        },
        // 'selected_records':{
        //     type: String,
        //     default: ''
        // },
        'selected_records':{
            type: Array,
            default: function() {return [];}
        },
        'columns': {
            type: Array,
            default: function() {
                return [
                    { column: 'id', display: 'Id', sorted: true },
                    { column: 'name', display: 'Name', sorted: true },
                    { column: 'records_count', display: 'Records', sorted: true },
                    { column: 'filters', display: 'Filters', sorted: true },
                    { column: 'enable_automatics', display: 'Automatics', sorted: true },
                    { column: 'created_at', display: 'Created', sorted: true },
                    { column: 'updated_at', display: 'Updated', sorted: true },
                ]
            },
        },
    },
    data: function() {
        return {
            pageCount: 0,
            forcePage: 1,
            list_records: [],
            list_groups: [],
            selectAllRecords: false,
            selectedIds: [],
            selected_groups: [],
            paginatorFilters: {
                // 'selected_groups': []
                // 'selected_group' : 'any',
                // 'order_by': '',
                // 'order_direction': '',
                // 'per_page': 50
            },
            sortOrders: {
                "id": null,
                "name": null,
                "group": null,
                "size": null,
                "used": null,
                "created_at": null,
                "updated_at": null,
            },
            isFetching: false,
        }
    },
    created() {
        // console.log('event for selection:', this.selection_change_event_name, this.att_id);
        // TODO: custom page name handling here and in gotoPage and fetch functions
        var params = window.location.search.substr(1);
        var splitted = params.split('&');
        for (var i = 0; i < splitted.length; i++) {
            var key_val = splitted[i].split('=');
            // if we have anything
            if (key_val[0])
                this.paginatorFilters[key_val[0]] = decodeURIComponent(key_val[1]);
        }

        // append page
        if (this.paginatorFilters[this.page_name])
            this.forcePage = Number(this.paginatorFilters[this.page_name]);

        // append searches
        if (this.paginatorFilters.order_by && this.paginatorFilters.order_by.length) {
            this.sortOrders[this.paginatorFilters.order_by] = this.paginatorFilters.order_direction;
        }

        // appeng paginator
        if (!this.paginatorFilters.records_per_page && this.paginate_amount != 50) {
            this.paginatorFilters.records_per_page = this.paginate_amount;
        }

        if(this.selected_records.length){
            var processed = this.selected_records.map((item)=>Number(item));
            // console.log('this.selected_records', this.selected_records, 'processed', processed);
            this.selectedIds = processed;
            this.dispatchSelectionEvent();
        }

        this.fetch();
    },
    methods: {
        gottoPage(page = 1) {
            this.paginatorFilters[this.page_name] = page;
            this.fetch();
            this.forcePage = Number(this.paginatorFilters[this.page_name]);
            // window.scrollTo(0,0);
            var elm = document.querySelector('.vue_list_records-table');
            elm.scrollIntoView(true);
            this.selectAllRecords = false;
        },

        setOrderBy(order) {
            // set filter data
            let direction = this.sortOrders[order] == 'asc' ? 'desc' : 'asc';
            // reset all filters
            for (var key in this.sortOrders)
                this.sortOrders[key] = null;
            // sert the only one filter
            this.sortOrders[order] = direction;

            this.paginatorFilters.order_by = order;
            this.paginatorFilters.order_direction = direction;
            // sort moves page to 1 always
            this.gottoPage(1);
        },

        fetch(evt) {
            if(evt){
                // console.log('evt', evt);
                evt.preventDefault();
                evt.stopPropagation();
            }
            // scroll to here
            // document.getElementById("divFirst").scrollIntoView();
            // var table = document.querySelector('.vue_list_records-table').scrollIntoView();
            var elm = document.querySelector('.vue_list_records-table');
            if(elm)
                elm.scrollIntoView(true);

            this.isFetching = true;
            var filters = [];
            if( this.selected_groups.length > 0)
                this.paginatorFilters.att_selected_groups = this.selected_groups;
            else
                delete this.paginatorFilters.selected_groups;

            for (var key in this.paginatorFilters) {
                filters.push(key + "=" + encodeURIComponent(this.paginatorFilters[key]));
            }

            var args = filters.join('&');
            window.history.pushState("", document.title, "?" + args);

            var request_url = this.api_url + (args.length ? "?" + args : "");

            var self = this;
            this.$http.get(request_url)
                .then((response) => {
                    var data = response.data.data;
                    // console.log('response', response);

                    data.base_list.data.forEach(function(item) {
                        // item.active = false;
                        // item.from_active = false;
                        item.is_checked = false;
                        for(var i = 0 ; i < self.selectedIds.length; i++){
                            if(item.id == self.selectedIds[i])
                                item.is_checked = true;
                        }
                    });
                    this.list_records = data.base_list.data;
                    this.list_groups = data.groups;

                    this.pageCount = data.base_list.last_page;
                }).catch((error) => {
                    console.log('error', error);
                    this.showRequestError(error);

                })
                .then(() => {
                    this.isFetching = false;
                });
        },

        allRecordsSelectHandler(evt){
            var selectAllRecords = this.selectAllRecords;
            this.list_records.forEach(function(item) {
                item.is_checked = selectAllRecords;
            });

            if (!this.selectAllRecords) {
                // this.selectedIds = [];
                // remove selected on current page
                var page_ids = this.list_records.map(function(item) { return item.id });
                this.selectedIds = this.selectedIds.filter((v)=> page_ids.indexOf(v) === -1 );
            } else {
                // push all items and
                this.selectedIds = this.selectedIds.concat( this.list_records.map(function(item) { return item.id }) )
                // sort for unique
                this.selectedIds = this.selectedIds.filter((v, i, a) => a.indexOf(v) === i);
            }
            this.dispatchSelectionEvent()
        },

        listRecordSelectHandler(evt, item) {
            if (item.is_checked) {
                this.selectedIds.push(item.id);
            } else {
                this.selectedIds = this.selectedIds.filter(function(record_id) {
                    // console.log('compare', record_id, item.id);
                    return record_id !== item.id;
                })
            }

            this.dispatchSelectionEvent();
        },

        showRequestError(error) {
            var message = '';
            if (error.response && error.response.data && typeof error.response.data == 'object') {
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
            }else if(typeof error == 'string'){
                message = error;
            }

            this.$toast.error({
                title: 'Error getting base list',
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

        dropdownClickHandler(evt, option) {
            if (this.selectedIds.length && confirm('You are about to ' + option + ' record(s) with id: ' + this.selectedIds.join(','))) {
                // console.log('dropdownClickHandler', evt, option);

                var data = {
                    'option': option,
                    'ids': this.selectedIds
                };

                var url = this.mass_update_url;
                this.isFetching = true;
                this.$http.post(url, data)
                    .then((response) => {
                        this.$toast.removeAll();
                        this.showRequestSuccess(response);
                    })
                    .catch((err) => {
                        this.showRequestError(err);
                    })
                    .then(() => {
                        // clear selection
                        this.selectedIds = [];
                        this.fetch();
                    });
            }
        },

        dispatchSelectionEvent(){
            let ids = this.selectedIds;
            let evt_name = this.selection_change_event_name.replace('{component_id}', this.component_id);
            // console.log('evt_name', evt_name);
            var evt = new CustomEvent(evt_name, {
                detail: { "ids": ids }
            });
            // console.log('dispatchSelectionEvent', ids);
            window.dispatchEvent(evt);
            EventBus.$emit(evt_name, evt);
        },
    }
}
</script>
