<template>
    <div class="email-account-list-container">
        <div class="mail-account-filters" v-if="show_filters">
            <div class="row">
                <div class="col-12">
                    <label>Filters:</label>
                </div>
            </div>
            <div class="row mb-3" v-if="show_filters_record_status">
                <div class="col-12">
                    <label for="avlie_state_all">Record status:</label>
                </div>
                <div class="col-12">
                    <div class="abc-radio abc-radio-info form-check form-check-inline">
                        <input id="record_state_all" value="" name="record_status" checked="" type="radio" v-model="paginatorFilters.record_status">
                        <label for="record_state_all">All</label>
                    </div>
                    <div class="abc-radio abc-radio-info form-check form-check-inline">
                        <input id="record_state_wait" value="0" name="record_status" type="radio" v-model="paginatorFilters.record_status">
                        <label for="record_state_wait">Awaiting</label>
                    </div>
                    <div class="abc-radio abc-radio-info form-check form-check-inline">
                        <input id="record_state_valid" value="2" name="record_status" type="radio" v-model="paginatorFilters.record_status">
                        <label for="record_state_valid">Success</label>
                    </div>
                    <div class="abc-radio abc-radio-info form-check form-check-inline">
                        <input id="record_state_errors" value="3" name="record_status" type="radio" v-model="paginatorFilters.record_status">
                        <label for="record_state_errors">Error</label>
                    </div>
                    <div class="abc-radio abc-radio-info form-check form-check-inline">
                        <input id="record_state_skipped" value="4" name="record_status" type="radio" v-model="paginatorFilters.record_status">
                        <label for="record_state_skipped">Skipped</label>
                    </div>
                    <div class="abc-radio abc-radio-info form-check form-check-inline">
                        <input id="record_state_blacklisted" value="5" name="record_status" type="radio" v-model="paginatorFilters.record_status">
                        <label for="record_state_blacklisted">Blacklisted</label>
                    </div>
                    <!-- <div class="abc-radio abc-radio-info form-check form-check-inline">
                        <input id="error_state_errors" value="3" name="record_status" type="radio" v-model="paginatorFilters.record_status">
                        <label for="error_state_errors">Sending</label>
                    </div> -->
                </div>
            </div>
            <div class="row" v-if="show_filters_search_input">
                <div class="col-12"><label for="search_account">Search account by id, host or login:</label></div>
                <div class="col-4">
                    <input type="text" id="search_account" name="search_account" v-model="paginatorFilters.search_account">
                </div>
            </div>
            <div class="row" v-if="show_filters_apply_input">
                <div class="col-12">&nbsp;</div>
                <div class="col-12"><button class="btn btn-info btn-sm" type="button" v-on:click="fetch">Apply filters</button></div>
            </div>
            <hr>
        </div>
        <table class="table table-bordered table-sm table-striped vue_mail_accs-table">
            <thead>
                <tr>
                    <th v-for="item in columns" :class="{'sorted': item.sorted}" v-on:click="setOrderBy(item.column)"><span>{{item.display}}<i v-if="item.icon" class="fa" :class="[item.icon]" v-tooltip.top-end="item.tooltip"></i><i :class="{ 'fa-sort-amount-asc': sortOrders[item.column] == 'asc', 'fa-sort-amount-desc': sortOrders[item.column] == 'desc', 'fa-sort': !sortOrders[item.column], 'd-none': !item.sorted }" class="fa pull-right" aria-hidden="true"></i></span></th>
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
                        <!-- <span>Loading please wait</span> -->
                    </td>
                </tr>
                <tr v-for="list_item in list_items" :class="{'d-none': isFetching}" v-tooltip="{content: list_item.record_status_txt, classes:['error-tooltip', list_item.error_log_class], placement: 'top-end'}" class="small">
                    <td v-for="item in columns" v-on="item.column=='name' || item.column=='from_mail' ? {'click': ()=>{showInput(list_item, item.column)} } : null">
                        <span v-if="item.column=='id'" class="n-w">
                            {{list_item.id}}
                            <span v-if="list_item.intersept" style="color: #4f9fcf"><i class="fa fa-envelope-open" aria-hidden="true" v-tooltip.top="'Intersepting'"></i></span>
                            <span v-if="list_item.record_status==0 || list_item.record_status=='0'" style="color: #777777"><i class="fa fa-clock-o" aria-hidden="true" v-tooltip.top="'Wait for sending'"></i></span>
                            <span v-if="list_item.record_status==1 || list_item.record_status=='1'" style="color: #2F6F9F; font-size: 0.35em;"><i class="fa fa-spinner fa-pulse fa-3x fa-fw" aria-hidden="true" v-tooltip.top="'Sending'"></i></span>
                            <span v-if="list_item.record_status==2 || list_item.record_status=='2'" style="color: #1D9D74"><i class="fa fa-check-square" aria-hidden="true" v-tooltip.top="'Sent ok'"></i></span>
                            <span v-if="list_item.record_status==3 || list_item.record_status=='3'" style="color: #D44950"><i class="fa fa-exclamation-triangle" aria-hidden="true" v-tooltip.top="'Send error'"></i></span>
                            <span v-if="list_item.record_status==4 || list_item.record_status=='4'" style="color: #D44950"><i class="fa fa-recycle" aria-hidden="true" v-tooltip.top="'Skipped'"></i></span>
                            <span v-if="list_item.record_status==5 || list_item.record_status=='5'" style="color: #D44950"><i class="fa fa-shield" aria-hidden="true" v-tooltip.top="'Blacklisted'"></i></span>
                        </span>
                        <span v-else-if="item.column" class="data-truncated" v-html="list_item[item.column]" :contenteditable="item.column=='record_status_txt' ? 'true' : 'false'"></span>
                        <span v-else>{{list_item[item.column]}}</span>
                    </td>

                    <td>
                        <div class="form-check abc-checkbox abc-checkbox-info form-check-inline">
                            <input class="form-check-input" :id="'campaign_record_'+list_item.id" name="campaign_record" type="checkbox" v-model="list_item.is_checked" v-on:change="recordsSelectHandler($event, list_item)">
                            <label class="form-check-label" :for="'campaign_record_'+list_item.id">&nbsp;</label>
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
                <input type="number" min="1" max="99999" step="1" class="form-control form-control-sm" id="per_page" name="per_page" placeholder="Per page (50)" v-model="paginatorFilters.per_page" v-on:change="fetch()" />
            </div>
            <div class="col-3 text-right" :class="{'d-none': !show_mass_assign}">
                <div class="btn-group dropup">
                    <button class="btn btn-info dropdown-toggle" type="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                        Chose action
                    </button>
                    <div class="dropdown-menu dropdown-menu-right" ref="dropdown-menu">
                        <button class="dropdown-item" type="button" v-on:click="dropdownClickHandler($event, 'clear')" data-opntion="enable">Clear error</button>
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
        'mac_id': {
            type: String,
            default: "1"
        },
        'api_url': String,
        'columns': {
            type: Array,
            default: function() {
                return [
                    { column: 'id', display: 'Id', sorted: true, icon: '' ,tooltip:''},
                    { column: 'from_mail', display: 'From Mail', sorted: true, icon: '' ,tooltip:''},
                    { column: 'from_name', display: 'From Name', sorted: true, icon: '' ,tooltip:''},
                    { column: 'address', display: 'To Mail', sorted: true, icon: '' ,tooltip:''},
                    { column: 'name', display: 'To Name', sorted: true, icon: '' ,tooltip:''},
                    { column: 'spam_base_id', display: 'Spam Base', sorted: true, icon: '' ,tooltip:''},
                    { column: 'record_status_txt', display: 'Details', sorted: true, icon: '' ,tooltip:''},
                    { column: 'created_at', display: 'Created', sorted: true, icon: '' ,tooltip:''},
                    { column: 'updated_at', display: 'Updated', sorted: true, icon: '', tooltip:''}
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
        'show_filters_alive': {
            type: Boolean,
            default: true
        },
        'show_filters_record_status': {
            type: Boolean,
            default: true
        },
        'show_filters_search_input': {
            type: Boolean,
            default: true
        },
        'show_filters_apply_input': {
            type: Boolean,
            default: true
        },
        'paginate_amount': {
            type: Number,
            default: 50
        },
        'selection_change_event_name': {
            type: String,
            default: 'campaign-record-selection-{mac_id}'
        },
        'outer_selection_change_event_name': {
            type: String,
            default: 'campaign-record-outer-selection-{mac_id}'
        },
        'selected_records':{
            type: Array,
            default: function() {return []}
        },
        'page_name': {
            type: String,
            default: 'cr_page'
        }
    },
    data: function() {
        return {
            pageCount: 0,
            forcePage: 1,
            list_items: [],
            selectAllRecords: false,
            selectedRecordIds: [],
            paginatorFilters: {
                // 'order_by': '',
                // 'order_direction': '',
                // 'per_page': 50
            },
            sortOrders: {
                "id": null,
                "from_mail": null,
                "from_name": null,
                "to_mail": null,
                "to_name": null,
                "spam_base_id": null,
                "created_at": null,
                "updated_at": null,
            },
            isFetching: false,
            endpoint: window.mail_accounts_api_url, //'api/list_items-api'
            // ab_url: window.ab_url,
            // mb_url: window.md_url,
        };
    },

    created() {
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
        if (this.paginatorFilters.page)
            this.forcePage = Number(this.paginatorFilters.page);

        // append searches
        if (this.paginatorFilters.order_by && this.paginatorFilters.order_by.length) {
            this.sortOrders[this.paginatorFilters.order_by] = this.paginatorFilters.order_direction;
        }

        if (!this.paginatorFilters.per_page && this.paginate_amount != 50) {
            this.paginatorFilters.per_page = this.paginate_amount;
        }

        if(this.selected_records.length){
            var processed = this.selected_records.map((item)=>Number(item));
            this.selectedRecordIds = processed;
            this.dispatchSelectionEvent();
        }

        this.fetch();

        EventBus.$on('append-search', (evt, search) => {
            this.paginatorFilters.filter_name = search;
            this.fetch();
        });

        EventBus.$on('keyup-search', (evt, search) => {
            this.paginatorFilters.filter_name = search;
        });

        // in some cases, make selected items from outside
        // let evt_name = this.outer_selection_change_event_name.replace('{mac_id}', this.mac_id);
        // EventBus.$on(evt_name, (evt, items) => {
        //     // console.log('EmailAccountsComponent hook event:', evt_name, items);
        //     // this.paginatorFilters.filter_name = search;
        //     this.selectedRecordIds = items;
        //     let self = this;
        //     this.list_items.forEach(function(item) {
        //         for(var i = 0 ; i < self.selectedRecordIds.length; i++){
        //             if(item.id == self.selectedRecordIds[i])
        //                 item.is_checked = true;
        //         }

        //         if( item.spam_base_id && item.spam_base_name ){
        //             item.spam_base_id = "[" + item.spam_base_id + "]" + item.spam_base_name;
        //         }


        //     });
        // });
    },

    methods: {
        gottoPage(page = 1) {
            this.paginatorFilters.page = page;
            this.fetch();
            this.forcePage = Number(this.paginatorFilters.page);
            // window.scrollTo(0,0);
            var elm = document.querySelector('.vue_mail_accs-table');
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
                console.log('evt', evt);
                evt.preventDefault();
                evt.stopPropagation();
            }
            // scroll to here
            // document.getElementById("divFirst").scrollIntoView();
            // var table = document.querySelector('.vue_mail_accs-table').scrollIntoView();
            var elm = document.querySelector('.vue_mail_accs-table');
            if(elm)
                elm.scrollIntoView(true);

            this.isFetching = true;
            var filters = [];
            for (var key in this.paginatorFilters) {
                filters.push(key + "=" + encodeURIComponent(this.paginatorFilters[key]));
            }

            var args = filters.join('&');
            window.history.pushState("", document.title, "?" + args);

            var request_url = this.api_url + "?" + args;

            var self = this;
            this.$http.get(request_url)
                .then((response) => {
                    response.data.data.data.forEach(function(item) {
                        item.is_checked = false;
                        for(var i = 0 ; i < self.selectedRecordIds.length; i++){
                            if(item.id == self.selectedRecordIds[i])
                                item.is_checked = true;
                        }

                        if (item.record_status_txt.length) {
                            if (item.record_status_txt.length > 100) {
                                item.error_log_class = 'error-tooltip-truncated';
                            } else {
                                item.error_log_class = '';
                            }
                            item.record_status_txt = item.record_status_txt.replace(/\n/g, '<br/>');
                        }

                        if(item.account){
                            item.from_name = item.account.name;
                            item.from_mail = item.account.from_mail;
                        }
                    });
                    this.list_items = response.data.data.data;
                    this.pageCount = response.data.data.last_page;

                }).catch((error) => {
                    console.log('error', error);
                    this.showRequestError(error);

                })
                .then(() => {
                    this.isFetching = false;
                });
        },

        allRecordsSelectHandler(evt) {
            var selectAllRecords = this.selectAllRecords
            this.list_items.forEach(function(item) {
                item.is_checked = selectAllRecords;
            });

            if (!this.selectAllRecords) {
                // this.selectedRecordIds = [];
                // remove selected on current page
                var page_ids = this.list_items.map(function(item) { return item.id });
                this.selectedRecordIds = this.selectedRecordIds.filter((v)=> page_ids.indexOf(v) === -1 );
            } else {
                // push all items and
                this.selectedRecordIds = this.selectedRecordIds.concat( this.list_items.map(function(item) { return item.id }) )
                // sort for unique
                this.selectedRecordIds = this.selectedRecordIds.filter((v, i, a) => a.indexOf(v) === i);

                // push all items and sort for unique
                // this.selectedRecordIds = this.list_items.map(function(item) { return item.id });
            }
            this.dispatchSelectionEvent();
        },

        recordsSelectHandler(evt, item) {
            if (item.is_checked) {
                this.selectedRecordIds.push(item.id);
            } else {
                this.selectedRecordIds = this.selectedRecordIds.filter(function(account_id) {
                    // console.log('compare', account_id, item.id);
                    return account_id !== item.id;
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
                title: 'Error getting campaign records',
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
            if (this.selectedRecordIds.length && confirm('You are about to ' + option + ' records with id: ' + this.selectedRecordIds.join(','))) {
                // console.log('dropdownClickHandler', evt, option);

                var data = {
                    'option': option,
                    'ids': this.selectedRecordIds
                };

                var url = api_mac_url;
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
                        this.selectedRecordIds = [];
                        this.fetch();
                    });
            }
        },

        dispatchSelectionEvent() {
            let ids = this.selectedRecordIds;
            let evt_name = this.selection_change_event_name.replace('{mac_id}', this.mac_id);
            // console.log('evt_name', evt_name);
            var evt = new CustomEvent(evt_name, {
                detail: { "ids": ids }
            });
            // console.log('EmailAccountsComponent dispatchSelectionEvent', ids);
            window.dispatchEvent(evt);
            EventBus.$emit(evt_name, evt, this.selectedRecordIds);
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
