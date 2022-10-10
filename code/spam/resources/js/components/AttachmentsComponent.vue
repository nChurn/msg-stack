<template>
    <div class="attachment-list-container">
        <div class="attachement-filters" v-if="show_filters">
            <div class="row">
                <div class="col-12">
                    <label>Filters:</label>
                </div>
            </div>

            <div class="row mb-3">
                <div class="col-12">
                    <label for="selected_group">Select group:</label>
                </div>
                <div class="col-12">
                    <div v-for="item in list_groups" class="abc-checkbox abc-checkbox-info form-check form-check-inline">
                        <input :value="item.group" v-model="selected_groups" name="check_list_group[]" type="checkbox" :id="'check_list_group_'+item.group">
                        <label :for="'check_list_group_'+item.group">{{item.group}}</label>
                    </div>
                </div>
            </div>

            <div class="row" v-if="show_filters_apply_input">
                <div class="col-12"><button class="btn btn-info btn-sm" type="button" v-on:click="fetch">Apply filters</button></div>
            </div>
            <hr>
        </div>
        <table class="table table-bordered table-sm table-striped vue_list_records-table">
            <thead>
                <tr>
                    <th v-for="item in columns" :class="{'sorted': item.sorted}" v-on:click="setOrderBy(item.column)"><span>{{item.display}}<i :class="{ 'fa-sort-amount-asc': sortOrders[item.column] == 'asc', 'fa-sort-amount-desc': sortOrders[item.column] == 'desc', 'fa-sort': !sortOrders[item.column], 'd-none': !item.sorted }" class="fa pull-right" aria-hidden="true"></i></span></th>
                    <th>
                        <div class="form-check abc-checkbox abc-checkbox-info form-check-inline">
                            <input class="form-check-input" id="check_all_mail_account" name="check_all_mail_account" type="checkbox" v-model="selectAllRecords" v-on:change="allRecordsSelectHandler">
                            <label class="form-check-label" for="check_all_mail_account">&nbsp;</label>
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
                    <td>
                        <div class="form-check abc-checkbox abc-checkbox-info form-check-inline">
                            <input class="form-check-input" :id="'check_list_record_'+list_record.id" name="check_mail_account" type="checkbox" v-model="list_record.is_checked" v-on:change="listRecordSelectHandler($event, list_record)">
                            <label class="form-check-label" :for="'check_list_record_'+list_record.id">&nbsp;</label>
                        </div>
                    </td>
                </tr>
            </tbody>
        </table>
        <div class="row">
            <div class="col-7">
                <paginate :page-count="pageCount" :force-page="forcePage" :first-last-button="true" :hide-prev-next="true" :margin-pages="1" :page-range="3" :initial-page="1" :container-class="'pagination'" :click-handler="gottoPage" :first-button-text="'&laquo;'" :last-button-text="'&raquo;'" :page-class="'page-item'" :page-link-class="'page-link'" :prev-link-class="'page-link'" :next-link-class="'page-link'" :class="{'d-none': isFetching}"></paginate>
            </div>
            <div class="col-2">
                <input type="number" min="1" max="99999" step="1" class="form-control form-control-sm" id="per_page" name="per_page" placeholder="Per page (50)" v-model="paginatorFilters.atts_per_page" v-on:change="fetch()" />
            </div>
            <div class="col-3 text-right" :class="{'d-none': !show_mass_assign}">
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
export default {
    props: {
        'att_id': {
            type: String,
            default: "1"
        },
        'api_url': String,
        'create_url': String,
        'update_url': String,
        'delete_url': String,
        'columns': {
            type: Array,
            default: function() {
                return [
                    { column: 'id', display: 'Id', sorted: true },
                    { column: 'name', display: 'Name', sorted: true },
                    { column: 'size', display: 'Size', sorted: true },
                    { column: 'group', display: 'Group', sorted: true },
                    { column: 'used_redis', display: 'Used', sorted: true },
                    { column: 'created_at', display: 'Created', sorted: true },
                    { column: 'updated_at', display: 'Updated', sorted: true },
                ]
            },
        },
        'show_mass_assign': {
            type: Boolean,
            default: true
        },
        'show_filters': {
            type: Boolean,
            default: true
        },
        'paginate_amount': {
            type: Number,
            default: 50
        },
        'selection_change_event_name': {
            type: String,
            default: 'attachement-selection-{att_id}'
        },
        'show_filters_apply_input': {
            type: Boolean,
            default: true
        },
        'page_name': {
            type: String,
            default: 'atts_page'
        },
        'selected_atts':{
            type: String,
            default: ''
        }
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
                // 'atts_order_by': '',
                // 'atts_order_direction': '',
                // 'per_page': 50
            },
            sortOrders: {
                "id": null,
                "name": null,
                "group": null,
                "size": null,
                // "used": null,
                "used_redis": null,
                "created_at": null,
                "updated_at": null,
            },
            isFetching: false,
        };
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
        if (this.paginatorFilters.atts_order_by && this.paginatorFilters.atts_order_by.length) {
            this.sortOrders[this.paginatorFilters.atts_order_by] = this.paginatorFilters.atts_order_direction;
        }

        // appeng paginator
        if (!this.paginatorFilters.atts_per_page && this.paginate_amount != 50) {
            this.paginatorFilters.atts_per_page = this.paginate_amount;
        }

        if(this.paginatorFilters.att_selected_groups ){
            // console.log('this.paginatorFilters.att_selected_groups', this.paginatorFilters.att_selected_groups);
            this.selected_groups = this.paginatorFilters.att_selected_groups.split(',');
        }

        if(this.selected_atts.length){
            var processed = this.selected_atts.split(',').map((item)=>Number(item));
            // console.log('this.selected_atts', this.selected_atts, 'processed', processed);
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

            this.paginatorFilters.atts_order_by = order;
            this.paginatorFilters.atts_order_direction = direction;
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

                    data.attachments.data.forEach(function(item) {
                        // item.active = false;
                        // item.from_active = false;
                        item.is_checked = false;
                        for(var i = 0 ; i < self.selectedIds.length; i++){
                            if(item.id == self.selectedIds[i])
                                item.is_checked = true;
                        }
                    });
                    this.list_records = data.attachments.data;
                    this.list_groups = data.groups;

                    this.pageCount = data.attachments.last_page;
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

                // push all items and sort for unique
                // this.selectedIds = this.list_records.map(function(item) { return item.id });
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
            var message = error.response.statusText;
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

            this.$toast.error({
                title: 'Error getting mail accounts',
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
            if (this.selectedIds.length && confirm('You are about to ' + option + ' records with id(s): ' + this.selectedIds.join(','))) {
                // console.log('dropdownClickHandler', evt, option);

                var data = {
                    'option': option,
                    'ids': this.selectedIds
                };

                var url = this.delete_url;
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

        selectGroupHandler(evt, option){
            console.log('evt', evt, 'option', option);
        },

        dispatchSelectionEvent() {
            let ids = this.selectedIds;
            let evt_name = this.selection_change_event_name.replace('{att_id}', this.att_id);
            // console.log('evt_name', evt_name);
            var evt = new CustomEvent(evt_name, {
                detail: { "ids": ids }
            });
            // console.log('dispatchSelectionEvent', ids);
            window.dispatchEvent(evt);
            EventBus.$emit(evt_name, evt);
        },

        groupItemChangeHandle(evt){
            console.log('evt', evt);
        },
    },

    directives: {
        focus: {
            update: function(el, bind, vnode) {
                if (bind.value && !bind.oldValue) {
                    console.log('we are here');
                    el.focus();
                    el.setSelectionRange(0, 0);
                }
            }
        }
    }
}

</script>
