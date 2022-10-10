<template>
    <div class="email-messages-list-container">
        <!-- header -->
        <div class="row mail-dump-header">
            <div class="col-12">
                <legend class="text-small">
                    Mail list for {{email_account.common_login}}. Total records: {{email_account.maildump_count}}.
                    <!-- @if( !empty(app('request')->input('search')) ) -->
                    <!-- Filtered by "{{app('request')->input('search')}}" records: {{$maildump->total()}}. -->
                    <!-- @endif -->
                </legend>
            </div>
        </div>
        <!-- filters -->
        <div class="row mail-dump-filters">
            <div class="col-12">
                <form action="{{action('EmailAccountsController@maildump', $account->id)}}" method="GET" style="width: 100%; display: block;">
                    <div class="row">
                        <div class="input-group col-md-4 input-group-sm">
                            <input class="form-control py-2" type="search" value="{{ app('request')->input('search') }}" id="textinput" name="search">
                            <span class="input-group-append">
                                <button class="btn btn-secondary" type="submit">
                                    <i class="fa fa-search"></i>
                                </button>
                            </span>
                        </div>
                    </div>
                    <input type="hidden" name="page" value="1" />
                </form>
            </div>
        </div>
        <hr />
    </div>
</template>
<script>
export default {
    props: {
        'api_url': String,
        'ab_url': String,
        'mb_url': String,
        'columns': {
            type: Array,
            default: function() {
                return [
                    { column: 'id', display: 'Id', sorted: true },
                    { column: 'name', display: 'Name', sorted: true },
                    { column: 'common_login', display: 'Login', sorted: true },
                    { column: 'common_host', display: 'Host', sorted: true },
                    { column: 'smtp_port', display: 'Port', sorted: true },
                    { column: 'enabled', display: 'Enabled', sorted: true },
                    { column: 'pop3_port', display: 'POP3', sorted: false },
                    { column: 'imap_port', display: 'IMAP', sorted: false },
                    { column: 'addressbook_count', display: 'AddressBook', sorted: true },
                    { column: 'maildump_count', display: 'Emails', sorted: true },
                    { column: 'created_at', display: 'Created', sorted: true },
                    { column: 'updated_at', display: 'Updated', sorted: true }
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
            default: 'mail-account-selection-{mac_id}'
        },
        'page_name': {
            type: String,
            default: 'page'
        }
    },
    data: function() {
        return {
            pageCount: 0,
            forcePage: 1,
            email_account: {},
            paginatorFilters: {
                // 'order_by': '',
                // 'order_direction': '',
                // 'per_page': 50
            },
            sortOrders: {
                "id": null,
                "name": null,
                "smtp_login": null,
                "smtp_host": null,
                "smtp_port": null,
                "enabled": null,
                // "POP3": null,
                // "IMAP": null,
                "addressbook_count": null,
                "maildump_count": null,
                "created_at": null,
                "updated_at": null,
            },
            isFetching: false,
            endpoint: window.mail_accounts_api_url, //'api/email_accounts-api'
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

        this.fetch();

        // EventBus.$on('append-search', (evt, search) => {
        //     this.paginatorFilters.filter_name = search;
        //     this.fetch();
        // });

        // EventBus.$on('keyup-search', (evt, search) => {
        //     this.paginatorFilters.filter_name = search;
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

        fetch() {
            this.isFetching = true;
            var filters = [];
            for (var key in this.paginatorFilters) {
                filters.push(key + "=" + encodeURIComponent(this.paginatorFilters[key]));
            }

            var args = filters.join('&');
            window.history.pushState("", document.title, "?" + args);

            var request_url = this.api_url + "?" + args;

            this.$http.get(request_url)
                .then((response) => {
                    response.data.data.data.forEach(function(item) {
                        item.active = false;
                        item.is_checked = false;
                        item.name_variants = item.all_names.split(',').filter((el) => { return el.length > 0 });
                        item.oldName = item.name;
                        // console.log('item.id', item.id, 'item.name_variants', item.name_variants);
                    });
                    this.email_accounts = response.data.data.data;

                    this.pageCount = response.data.data.last_page;
                }).catch((error) => {
                    // console.log('error', error);
                    this.showRequestError(error);

                })
                .then(() => {
                    this.isFetching = false;
                });
        },

        updateAccList(items) {
            this.email_accounts = items;
        },

        showInput(item) {
            if (!item.active) {
                // hide all others
                for (var i = 0; i < this.email_accounts.length; i++) {
                    this.email_accounts[i].active = false;
                }

                item.oldName = item.name;
                item.active = true;
            }
        },

        onBlur(item) {
            // console.log('onBlur fire');
            // if( item.oldName !== item.name){
            //     console.log('old name and new name mismatched');
            //     this.updateMailAccountName(item);
            // }else{
            //     var self = this;
            //     setTimeout(function() {
            //         self.hideInput(item);
            //     }, 250);
            // }
        },

        hideInput(item) {
            // item.active == true ?? item.active = false;
            if (item.active) {
                //     console.log('hideInput', item);
                item.active = false;
            }
        },

        inputLikeVariant(variant, name) {
            let ret = false;
            try {
                let patt1 = new RegExp(name);
                ret = patt1.test(variant);
            }
            catch (e) {
                console.log('inputLikeVariant failed with:', variant, name, e);
            }
            return ret;
        },

        fillInputFromVariant(item, variant) {
            // console.log('Update item name from variant', variant);
            item.name = variant;
            this.updateMailAccountName(item);
            // this.hideInput(item);
        },

        updateMailAccountName(item) {
            // console.log('updateMailAccountName', item);
            // if (item.active) {
            // item.active = false;
            if (item.name !== item.oldName) {
                item.oldName = item.name;
                // update value
                this.$toast.info({
                    title: 'Saving new name',
                    message: "Please wait",
                    position: 'top right',
                    timeOut: 20000,
                    progressBar: true,
                    hideDuration: 0,
                });
                // console.log('update name url:', url, item.name);
                var url = this.api_url + "/name/" + item.id;
                this.$http.post(url, { "new_name": item.name })
                    .then((response) => {
                        this.$toast.removeAll();
                        this.showRequestSuccess(response);
                    })
                    .catch((err) => {
                        this.showRequestError(err);
                    });
                // return true;
            }

            this.hideInput(item);

        },

        allMailAccounsSelectHandler(evt) {
            var selectAllMailAccounts = this.selectAllMailAccounts
            this.email_accounts.forEach(function(item) {
                item.is_checked = selectAllMailAccounts;
            });

            if (!this.selectAllMailAccounts) {
                this.selectedMailAccountIds = [];
            } else {
                this.selectedMailAccountIds = this.email_accounts.map(function(item) { return item.id });
            }
            this.dispatchSelectionEvent();
        },

        mailAccountSelectHandler(evt, item) {
            if (item.is_checked) {
                this.selectedMailAccountIds.push(item.id);
            } else {
                this.selectedMailAccountIds = this.selectedMailAccountIds.filter(function(account_id) {
                    // console.log('compare', account_id, item.id);
                    return account_id !== item.id;
                })
            }

            this.dispatchSelectionEvent();
        },

        searchUpdateHandler(search) {
            console.log('search', search);
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
            if (this.selectedMailAccountIds.length && confirm('You are about to ' + option + ' accounts with id: ' + this.selectedMailAccountIds.join(','))) {
                // console.log('dropdownClickHandler', evt, option);

                var data = {
                    'option': option,
                    'ids': this.selectedMailAccountIds
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
                        this.fetch();
                    });
            }
        },

        dispatchSelectionEvent() {
            let ids = this.selectedMailAccountIds;
            let evt_name = this.selection_change_event_name.replace('{mac_id}', this.mac_id);
            // console.log('evt_name', evt_name);
            var evt = new CustomEvent(evt_name, {
                detail: { "ids": ids }
            });
            window.dispatchEvent(evt);
            EventBus.$emit(evt_name, evt, this.search);
        },
    },

}

</script>
