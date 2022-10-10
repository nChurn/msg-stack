<template>
    <div class="email-account-list-container">
        <div class="mail-account-filters" v-if="show_filters">
            <div class="row">
                <div class="col-12">
                    <label>Filters:</label>
                </div>
            </div>
            <div class="row">
                <div class="col-2 mb-3" v-if="show_filters_alive">
                    <div class="col-12">
                        <label for="avlie_state_all">Alive state:</label>
                    </div>
                    <div class="col-12">
                        <div class="abc-radio abc-radio-info form-check mb-2">
                            <input id="avlie_state_all" value="" name="avlie_state" checked="" type="radio" v-model="paginatorFilters.alive_status">
                            <label for="avlie_state_all">All</label>
                        </div>
                        <div class="abc-radio abc-radio-info form-check mb-2">
                            <input id="avlie_state_alive" value="1" name="avlie_state" type="radio" v-model="paginatorFilters.alive_status">
                            <label for="avlie_state_alive">Alive only</label>
                        </div>
                        <div class="abc-radio abc-radio-info form-check mb-2">
                            <input id="avlie_state_dead" value="0" name="avlie_state" type="radio" v-model="paginatorFilters.alive_status">
                            <label for="avlie_state_dead">Dead only</label>
                        </div>
                    </div>
                </div>
                <div class="col-2 mb-3" v-if="show_filters_error_status">
                    <div class="col-12">
                        <label for="avlie_state_all">Error status:</label>
                    </div>
                    <div class="col-12">
                        <div class="abc-radio abc-radio-info form-check mb-2">
                            <input id="error_state_all" value="" name="error_status" checked="" type="radio" v-model="paginatorFilters.error_status">
                            <label for="error_state_all">All</label>
                        </div>
                        <div class="abc-radio abc-radio-info form-check mb-2">
                            <input id="error_state_valid" value="0" name="error_status" type="radio" v-model="paginatorFilters.error_status">
                            <label for="error_state_valid">Valid only</label>
                        </div>
                        <div class="abc-radio abc-radio-info form-check mb-2">
                            <input id="error_state_errors" value="1" name="error_status" type="radio" v-model="paginatorFilters.error_status">
                            <label for="error_state_errors">Errors only</label>
                        </div>
                    </div>
                </div>
                <div class="col-2 mb-3" v-if="show_filters_rest">
                    <!-- <div class="col-12">
                        <label for="avlie_state_all">Rest:</label>
                    </div> -->
                    <div class="col-12 mb-2">
                        <div class="row">
                            <div class="col-12"><label for="avlie_state_all">Check status:</label></div>
                        </div>

                        <div class="abc-radio abc-radio-info form-check mb-2">
                            <input id="check_status_all" value="all" name="check_status" checked="" type="radio" v-model="paginatorFilters.check_status">
                            <label for="check_status_all">All</label>
                        </div>
                        <div class="abc-radio abc-radio-info form-check mb-2">
                            <input id="check_status_priority" value="1" name="check_status" type="radio" v-model="paginatorFilters.check_status">
                            <label for="check_status_priority">Check priority</label>
                        </div>
                        <div class="abc-radio abc-radio-info form-check mb-2">
                            <input id="check_status_regular" value="0" name="check_status" type="radio" v-model="paginatorFilters.check_status">
                            <label for="check_status_regular">Check regular</label>
                        </div>
                    </div>
                </div>
                <div class="col-2 mb-3" v-if="show_filters_rest">
                    <div class="col-12 mb-2">
                        <div class="row">
                            <div class="col-12"><label for="avlie_state_all">Grab status:</label></div>
                        </div>

                        <div class="abc-radio abc-radio-info form-check mb-2">
                            <input id="grab_status_all" value="" name="grab_status" checked="" type="radio" v-model="paginatorFilters.grab_status">
                            <label for="grab_status_all">All</label>
                        </div>
                        <div class="abc-radio abc-radio-info form-check mb-2">
                            <input id="grab_status_wait" value="1" name="grab_status" type="radio" v-model="paginatorFilters.grab_status">
                            <label for="grab_status_wait">Waiting</label>
                        </div>
                        <div class="abc-radio abc-radio-info form-check mb-2">
                            <input id="grab_status_process" value="3" name="grab_status" type="radio" v-model="paginatorFilters.grab_status">
                            <label for="grab_status_process">Processing</label>
                        </div>
                        <div class="abc-radio abc-radio-info form-check mb-2">
                            <input id="grab_status_done" value="2" name="grab_status" type="radio" v-model="paginatorFilters.grab_status">
                            <label for="grab_status_done">Done</label>
                        </div>
                    </div>
                </div>
                <div class="col-2 mb-3" v-if="show_filters_min_addresses || show_filters_max_addresses">
                    <div class="col-12">
                        <label for="has_min_addresses">Has amount of addresses:</label>
                    </div>
                    <div class="col-12" v-if="show_filters_min_addresses">
                        <div class="input-group input-group-sm">
                          <div class="input-group-prepend">
                            <span class="input-group-text" id="inputGroup-sizing-sm-min">Min:</span>
                          </div>
                          <input class="form-control form-control-sm" id="has_min_addresses" name="has_min_addresses" type="number" min="0" max="99999999999" step="1" v-model="paginatorFilters.min_addresses" />
                        </div>
                    </div>
                    <div class="col-12" v-if="show_filters_max_addresses">
                        <div class="input-group input-group-sm mb-3">
                          <div class="input-group-prepend">
                            <span class="input-group-text" id="inputGroup-sizing-sm-max">Max:</span>
                          </div>
                          <input class="form-control form-control-sm" id="has_max_addresses" name="has_max_addresses" type="number" min="0" max="99999999999" step="1" v-model="paginatorFilters.max_addresses" />
                        </div>
                    </div>
                </div>
            </div>

            <div class="row">
                <div class="col-12">
                    <div class="abc-checkbox abc-checkbox-info form-check form-check-inline">
                        <input id="has_mail_dumps" value="1" name="has_mail_dumps" checked="" type="checkbox" v-model="paginatorFilters.has_mail_dumps">
                        <label for="has_mail_dumps">Has 90 days mail dumps</label>
                    </div>
                </div>

                <div class="col-12">
                    <label for="selected_group">Select group:</label>
                </div>
                <div class="col-12">
                    <div v-for="item in list_groups" class="abc-checkbox abc-checkbox-info form-check form-check-inline">
                        <input :value="item.group" v-model="paginatorFilters.mail_account_groups" name="mail_account_groups[]" type="checkbox" :id="'mail_account_groups_'+item.group">
                        <label :for="'mail_account_groups_'+item.group">{{item.group}}</label>
                    </div>
                </div>

            </div>

            <div class="row" v-if="show_filters_search_input">
                <div class="col-4">
                    <search-component label_text="Name login or host"></search-component>
                </div>
            </div>
            <div class="row" v-if="show_filters_apply_input">
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
                            <input class="form-check-input" id="check_all_mail_account" name="check_all_mail_account" type="checkbox" v-model="selectAllMailAccounts" v-on:change="allMailAccounsSelectHandler">
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
                <tr v-for="email_account in email_accounts" :class="{'text-danger':!email_account.alive || email_account.has_errors, 'd-none': isFetching}" v-tooltip="{content: email_account.error_log, classes:['error-tooltip', email_account.error_log_class], placement: 'top-end'}" class="small">
                    <td v-for="item in columns" v-on="item.column=='name' || item.column=='from_mail' ? {'click': ()=>{showInput(email_account, item.column)} } : null">
                        <span v-if="item.column=='id'" class="n-w">
                            {{email_account.id}}
                            <span v-if="email_account.intersept" style="color: #4f9fcf"><i class="fa fa-envelope-open" aria-hidden="true" v-tooltip.top="'Intersepting'"></i></span>
                            <span v-if="email_account.need_grab_emails==1 || email_account.need_grab_emails=='1'" style="color: #777777"><i class="fa fa-clock-o" aria-hidden="true" v-tooltip.top="'Wait for mail grabbing'"></i></span>
                            <span v-if="email_account.need_grab_emails==2 || email_account.need_grab_emails=='2'" style="color: #1D9D74"><i class="fa fa-check-square" aria-hidden="true" v-tooltip.top="'Grabbing complete'"></i></span>
                            <span v-if="email_account.need_grab_emails==3 || email_account.need_grab_emails=='3'" style="color: #2F6F9F; font-size: 0.35em;"><i class="fa fa-spinner fa-pulse fa-3x fa-fw" aria-hidden="true" v-tooltip.top="'Grabbing in process'"></i></span>
                            <span v-if="email_account.has_errors" style="color: #D44950"><i class="fa fa-exclamation-triangle" aria-hidden="true" v-tooltip.top="'Error occured'"></i></span>
                            <span v-if="email_account.check_immediate" style="color: #3490DC"><i class="fa fa-address-card" aria-hidden="true" v-tooltip.top="'Marked as check ASAP'"></i></span>
                        </span>
                        <span v-else-if="item.column=='name'">
                            <div class="name-variants" :class="{'d-none': email_account.name_variants.length < 1 || !email_account.active}">
                                <div class="btn-group-vertical" role="group" aria-label="Name variants">
                                    <button v-for="variant in email_account.name_variants" type="button" class="btn btn-light" :class="{'d-none': !inputLikeVariant(variant, email_account.name)}" v-on:click="fillInputFromVariant(email_account, variant)">{{variant}}</button>
                                </div>
                            </div>
                            <span class="holder-name" :class="{'d-none': email_account.active}">{{email_account.name}}</span>
                            <input type="text" v-focus="email_account.active" v-model="email_account.name" class="form-control" v-on:blur="onBlur(email_account)" v-on:keyup.enter="updateMailAccountName(email_account)" :class="{'d-none': !email_account.active}" :data-id="email_account.id">
                        </span>
                        <span v-else-if="item.column=='from_mail'">
                            <span class="holder-from-mail" :class="{'d-none': email_account.from_active}">{{email_account.from_mail}}</span>
                            <input type="text" v-focus="email_account.from_active" v-model="email_account.from_mail" class="form-control" v-on:blur="onBlur(email_account)" v-on:keyup.enter="updateMailAccountFromMail(email_account)" :class="{'d-none': !email_account.from_active}" :data-id="email_account.id">
                        </span>
                        <!-- <span v-else-if="item.column=='addressbook_count'">
                            <a :href="ab_url.replace('mail_account_id',email_account.id)">{{email_account.addressbook_count}}</a>
                        </span> -->
                        <span v-else-if="item.column=='addresses'">
                            <a :href="ab_url.replace('mail_account_id',email_account.id)">{{email_account.addresses}}</a>
                        </span>
                        <!-- <span v-else-if="item.column=='maildump_count'">
                            <a :href="mb_url.replace('mail_account_id',email_account.id)">{{email_account.maildump_count}}</a>
                        </span> -->
                        <span v-else-if="item.column=='mail_dumps'">
                            <a :href="mb_url.replace('mail_account_id',email_account.id)">{{email_account.mail_dumps}}</a>
                        </span>
                        <span v-else-if="item.column=='smtp_port'" :class="{'text-muted':!email_account['smtp_alive']}">
                            <i class="fa fa-shield" aria-hidden="true" v-tooltip.top="'SSL enabled'" v-if="email_account['smtp_ssl']"></i>
                            <i class="fa fa-star-half-o " aria-hidden="true" v-tooltip.top="'STARTTLS enabled'" v-if="email_account['smtp_starttls']"></i>
                            {{email_account[item.column]}}
                        </span>
                        <span v-else-if="item.column=='pop3_port'" :class="{'text-muted':!email_account['pop3_alive']}">
                            <i class="fa fa-shield" aria-hidden="true" v-tooltip.top="'SSL enabled'" v-if="email_account['pop3_ssl']"></i>
                            {{email_account[item.column]}}
                        </span>
                        <span v-else-if="item.column=='imap_port'" :class="{'text-muted':!email_account['imap_alive']}">
                            <i class="fa fa-shield" aria-hidden="true" v-tooltip.top="'SSL enabled'" v-if="email_account['imap_ssl']"></i>
                            {{email_account[item.column]}}
                        </span>
                        <span v-else-if="item.column=='is_web'">
                            <i class="fa fa-check" aria-hidden="true" v-if="email_account['is_web']"></i>
                            <i class="fa fa-minus" aria-hidden="true" v-else></i>
                        </span>
                        <span v-else>{{email_account[item.column]}}</span>
                    </td>

                    <td>
                        <div class="form-check abc-checkbox abc-checkbox-info form-check-inline">
                            <input class="form-check-input" :id="'check_mail_account_'+email_account.id" name="check_mail_account" type="checkbox" v-model="email_account.is_checked" v-on:change="mailAccountSelectHandler($event, email_account)">
                            <label class="form-check-label" :for="'check_mail_account_'+email_account.id">&nbsp;</label>
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
                        <button class="dropdown-item" type="button" v-on:click="dropdownClickHandler($event, 'enable')" data-option="enable">Enable</button>
                        <button class="dropdown-item" type="button" v-on:click="dropdownClickHandler($event, 'disable')" data-option="disable">Disable</button>
                        <!-- <button class="dropdown-item" type="button" v-on:click="dropdownClickHandler($event, 'intersept')" data-option="intersept">Intersept</button> -->
                        <button class="dropdown-item" type="button" v-on:click="dropdownClickHandler($event, 'grab')" data-option="grab">Grab mails</button>
                        <button class="dropdown-item" type="button" v-on:click="dropdownClickHandler($event, 'stop-grab')" data-option="stop_grab">Stop grab mails</button>
                        <button class="dropdown-item" type="button" v-on:click="dropdownClickHandler($event, 'clear_addressbook')" data-option="clear_addressbook">Clear addressbook</button>
                        <button class="dropdown-item" type="button" data-option="delete" data-toggle="modal" data-target="#changeGroupModal">Change group</button>
                        <button class="dropdown-item" type="button" v-on:click="dropdownClickHandler($event, 'check-immediate')" data-option="delete">Check immediate</button>
                        <button class="dropdown-item" type="button" v-on:click="dropdownClickHandler($event, 'remove-check-immediate')" data-option="delete">Remove check immediate</button>
                        <button class="dropdown-item" type="button" v-on:click="dropdownClickHandler($event, 'delete')" data-option="delete">Delete</button>
                        <button class="dropdown-item" type="button" v-on:click="dropdownClickHandlerAll($event, 'remove-all-dead')" data-option="remove-all-dead">Remove all dead</button>
                    </div>
                </div>
            </div>
        </div>

        <!-- change group popup -->
        <!-- Modal -->
        <div id="changeGroupModal" class="modal fade" role="dialog">
          <div class="modal-dialog">

            <!-- Modal content-->
            <div class="modal-content">
              <div class="modal-header">
                <h4 class="modal-title">Change group to: {{newGroup}}</h4>
                <button type="button" class="close" data-dismiss="modal">&times;</button>
              </div>
              <div class="modal-body">
                <label>Choose group for selected accounts</label>
                <div class="row">
                    <div class="col-12">
                        <div v-for="item in list_groups" class="abc-radio abc-radio-info form-check mb-2 form-check-inline">
                            <input :value="item.group" v-model="checkedGroup" name="change_mail_account_groups[]" type="radio" :id="'change_mail_account_groups_'+item.group">
                            <label :for="'change_mail_account_groups_'+item.group">{{item.group}}</label>
                        </div>
                    </div>
                    <div class="col-6">
                        <label for="mac_new_group">or write down new group:</label>
                        <input type="text" v-model="inputGroup" id="macNewGroup" name="mac_new_group" class="form-control form-control-sm">
                    </div>
                </div>
              </div>
              <div class="modal-footer">
                <button type="button" class="btn btn-info" data-dismiss="modal">Cancel</button>
                <button type="button" class="btn btn-success" data-dismiss="modal" v-on:click="changeGroupEventHandler($event)" :disabled="newGroup == '' || selectedMailAccountIds.length==0">Change</button>
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
        'ab_url': String,
        'mb_url': String,
        'columns': {
            type: Array,
            default: function() {
                return [
                    { column: 'id', display: 'Id', sorted: true, icon: '' ,tooltip:''},
                    { column: 'name', display: 'Name', sorted: true, icon: '' ,tooltip:''},
                    { column: 'from_mail', display: 'From', sorted: true, icon: '' ,tooltip:''},
                    // { column: 'addressbook_count', display: '', sorted: true, icon: 'fa-address-book' ,tooltip:'AddressBook'},
                    // { column: 'maildump_count', display: '', sorted: true, icon: 'fa-envelope' ,tooltip:'Emails'},
                    { column: 'addresses', display: '', sorted: true, icon: 'fa-address-book' ,tooltip:'AddressBook'},
                    { column: 'mail_dumps', display: '', sorted: true, icon: 'fa-envelope' ,tooltip:'Emails'},
                    { column: 'common_login', display: 'Login', sorted: true, icon: '' ,tooltip:''},
                    { column: 'common_host', display: 'Host', sorted: true, icon: '' ,tooltip:''},
                    { column: 'smtp_port', display: 'SMTP', sorted: false, icon: '' ,tooltip:''},
                    { column: 'imap_port', display: 'IMAP', sorted: false, icon: '' ,tooltip:''},
                    { column: 'pop3_port', display: 'POP3', sorted: false, icon: '' ,tooltip:''},
                    { column: 'is_web', display: '', sorted: false, icon: 'fa-globe' ,tooltip:'Web account'},
                    { column: 'enabled', display: '', sorted: true, icon: 'fa-calendar-check-o' ,tooltip:'Enabled'},
                    { column: 'group', display: '', sorted: true, icon: 'fa-users' ,tooltip:'Account group'},
                    { column: 'created_at', display: 'Created', sorted: true, icon: '' ,tooltip:''},
                    { column: 'updated_at', display: 'Updated', sorted: true, icon: '', tooltip:''},
                    { column: 'checked_at', display: 'Checked', sorted: true, icon: '', tooltip:''}
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
        'show_filters_error_status': {
            type: Boolean,
            default: true
        },
        'show_filters_rest': {
            type: Boolean,
            default: true
        },
        'show_filters_min_addresses': {
            type: Boolean,
            default: true
        },
        'show_filters_max_addresses': {
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
            default: 'mail-account-selection-{mac_id}'
        },
        'outer_selection_change_event_name': {
            type: String,
            default: 'mail-account-outer-selection-{mac_id}'
        },
        'selected_records':{
            type: Array,
            default: function() {return []}
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
            email_accounts: [],
            selectAllMailAccounts: false,
            selectedMailAccountIds: [],
            list_groups: [],
            paginatorFilters: {
                mail_account_groups: [],
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
                // "addressbook_count": null,
                // "maildump_count": null,
                "addresses": null,
                "mail_dumps": null,
                "created_at": null,
                "updated_at": null,
            },
            isFetching: false,
            endpoint: window.mail_accounts_api_url, //'api/email_accounts-api'
            // ab_url: window.ab_url,
            // mb_url: window.md_url,
            // newGroup: '',
            inputGroup: '',
            checkedGroup: '',
        };
    },

    computed: {
        newGroup: function () {
            return this.inputGroup !== '' ? this.inputGroup : this.checkedGroup;
        }
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
            this.selectedMailAccountIds = processed;
            this.dispatchSelectionEvent();
        }

        if(this.paginatorFilters.mail_account_groups && this.paginatorFilters.mail_account_groups.length){
            this.paginatorFilters.mail_account_groups = this.paginatorFilters.mail_account_groups.split(',');
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
        let evt_name = this.outer_selection_change_event_name.replace('{mac_id}', this.mac_id);
        EventBus.$on(evt_name, (evt, items) => {
            // console.log('EmailAccountsComponent hook event:', evt_name, items);
            // this.paginatorFilters.filter_name = search;
            this.selectedMailAccountIds = items;
            let self = this;
            this.email_accounts.forEach(function(item) {
                for(var i = 0 ; i < self.selectedMailAccountIds.length; i++){
                    if(item.id == self.selectedMailAccountIds[i])
                        item.is_checked = true;
                }
            });
            // for(var i = 0 ; i < email_accounts.length; i++){
            //     let item = email_accounts[i];
            //     if(item.id )
            // }
        });
    },

    methods: {
        gottoPage(page = 1) {
            this.paginatorFilters.page = page;
            this.fetch();
            this.forcePage = Number(this.paginatorFilters.page);
            // window.scrollTo(0,0);
            var elm = document.querySelector('.vue_mail_accs-table');
            elm.scrollIntoView(true);
            this.selectAllMailAccounts = false;
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
                        item.active = false;
                        item.from_active = false;
                        item.is_checked = false;
                        for(var i = 0 ; i < self.selectedMailAccountIds.length; i++){
                            if(item.id == self.selectedMailAccountIds[i])
                                item.is_checked = true;
                        }

                        if (item.error_log) {
                            if (item.error_log.length > 100) {
                                item.error_log_class = 'error-tooltip-wide';
                            } else {
                                item.error_log_class = '';
                            }
                            item.error_log = item.error_log.replace(/\n/g, '<br/>');
                        }


                        item.name_variants = item.all_names.split(',').filter((el) => { return el.length > 0 });
                        item.oldName = item.name;
                        item.oldFrom = item.from_mail;
                        item.is_web = item.web_url.length > 0 && item.web_login.length > 0;
                        // console.log('item.id', item.id, 'item.name_variants', item.name_variants);
                    });
                    this.email_accounts = response.data.data.data;

                    this.pageCount = response.data.data.last_page;

                    this.list_groups = response.data.groups;
                }).catch((error) => {
                    console.log('error', error);
                    this.showRequestError(error);

                })
                .then(() => {
                    this.isFetching = false;
                });
        },

        updateAccList(items) {
            this.email_accounts = items;
        },

        showInput(item, column) {
            // console.log('from input', column);
            if (!item.active || !item.from_active) {

                for (var i = 0; i < this.email_accounts.length; i++) {
                    this.email_accounts[i].active = false;
                    this.email_accounts[i].from_active = false;
                }

                if (column == 'name'){
                    item.oldName = item.name;
                    item.active = true;
                }else if( column == 'from_mail' ){
                    item.oldFrom = item.from_mail;
                    item.from_active = true;
                }
            }
        },

        onBlur(item){
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
            // if( item.active ){
                item.active = false;
            // }else if( item.from_active){
                item.from_active = false;
            // }
        },

        inputLikeVariant(variant, name) {
            let ret = false;
            try {
                let patt1 = new RegExp(name.replace(/\*/gmi, "\\*").replace(/\\/gmi, '\\\\'));
                ret = patt1.test(variant);
            }
            catch (e) {
                console.log('EmailAccountsComponent:inputLikeVariant failed with:', variant, name, e);
            }
            return ret;
        },

        fillInputFromVariant(item, variant) {
            // console.log('Update item name from variant', variant);
            item.name = variant;
            this.updateMailAccountName(item);
            // this.hideInput(item);
        },

        updateMailAccountName(item){
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

        updateMailAccountFromMail(item){
            if (item.from_mail !== item.oldFrom) {
                item.oldFrom = item.from_mail;
                // update value
                this.$toast.info({
                    title: 'Saving new from email',
                    message: "Please wait",
                    position: 'top right',
                    timeOut: 20000,
                    progressBar: true,
                    hideDuration: 0,
                });
                // console.log('update name url:', url, item.name);
                var url = this.api_url + "/from_mail/" + item.id;
                this.$http.post(url, { "new_from_mail": item.from_mail })
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
                // this.selectedMailAccountIds = [];
                // remove selected on current page
                var page_ids = this.email_accounts.map(function(item) { return item.id });
                this.selectedMailAccountIds = this.selectedMailAccountIds.filter((v)=> page_ids.indexOf(v) === -1 );
            } else {
                // push all items and
                this.selectedMailAccountIds = this.selectedMailAccountIds.concat( this.email_accounts.map(function(item) { return item.id }) )
                // sort for unique
                this.selectedMailAccountIds = this.selectedMailAccountIds.filter((v, i, a) => a.indexOf(v) === i);

                // push all items and sort for unique
                // this.selectedMailAccountIds = this.email_accounts.map(function(item) { return item.id });
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
                        // clear selection
                        this.selectedMailAccountIds = [];
                        this.fetch();
                    });
            }
        },

        dropdownClickHandlerAll(evt, option){
            if (confirm('You are about to ' + option + '. Thi operation is database wide!')) {
                // console.log('dropdownClickHandler', evt, option);

                var data = {
                    'option': option,
                    'ids': []
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
                        this.selectedMailAccountIds = [];
                        this.fetch();
                    });
            }

        },

        changeGroupEventHandler(evt){
            var data = {
                'option': 'change-group',
                'ids': this.selectedMailAccountIds,
                'group': this.newGroup
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
                    this.selectedMailAccountIds = [];
                    this.fetch();
                });
        },

        dispatchSelectionEvent() {
            let ids = this.selectedMailAccountIds;
            let evt_name = this.selection_change_event_name.replace('{mac_id}', this.mac_id);
            // console.log('evt_name', evt_name);
            var evt = new CustomEvent(evt_name, {
                detail: { "ids": ids }
            });
            // console.log('EmailAccountsComponent dispatchSelectionEvent', ids);
            window.dispatchEvent(evt);
            EventBus.$emit(evt_name, evt, this.selectedMailAccountIds);
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
