@extends('default')
@if(is_null($spam_base))
    @section('title', 'New Spam Base')
@else
    @section('title', "Spam base {$spam_base->id} - '{$spam_base->name}' details")
@endif
@section('content')

    <div id="app">
        <ul class="nav nav-tabs mb-3" id="myTab" role="tablist">
            <li class="nav-item">
                <a class="nav-link active" id="campaign_general-tab" data-toggle="tab" href="#campaign_general" role="tab" aria-controls="campaign_general" aria-selected="true">General</a>
            </li>
            <li class="nav-item">
                <a class="nav-link" id="base_account-tab" data-toggle="tab" href="#base_account" role="tab" aria-controls="base_account" aria-selected="false">Accounts</a>
            </li>
        </ul>

        <div class="tab-content" id="myTabContent">
            <div class="tab-pane fade show active" id="campaign_general" role="tabpanel" aria-labelledby="campaign_general-tab">
                <spam-base-details-component
                    @if(is_null($spam_base))
                    api_url="{{route('api.spam_base.get', '-1')}}"
                    edit_url="{{route('api.spam_base.store', '-1')}}"
                    @else
                    api_url="{{route('api.spam_base.get', $spam_base->id)}}"
                    edit_url="{{route('api.spam_base.store', $spam_base->id)}}"
                    @endif
                    mail_acc_select_event_name="selected-spambase-mac-list"
                    outer_mail_acc_select_event_name="outer-selected-spambase-mac-list"
                >
                </spam-base-details-component>
            </div>
            <div class="tab-pane fade" id="base_account" role="tabpanel" aria-labelledby="base_account-tab">
                <mail-acc-list-component
                    api_url="{{action('api\EmailAccountsController@index', 'mail_accs')}}"
                    mb_url="{{action('EmailAccountsController@maildump', 'mail_account_id')}}"
                    ab_url="{{action('EmailAccountsController@addressbook', 'mail_account_id')}}"

                    mac_id="spambase-mac-list"
                    selection_change_event_name="selected-{mac_id}"
                    outer_selection_change_event_name="outer-selected-{mac_id}"

                    v-bind:show_filters="true"
                    v-bind:show_filters_alive="true"
                    v-bind:show_filters_error_status="false"
                    v-bind:show_filters_rest="true"
                    v-bind:show_filters_min_addresses="true"
                    v-bind:show_filters_max_addresses="true"
                    v-bind:show_filters_search_input="false"
                    v-bind:show_filters_apply_input="true"
                    v-bind:show_mass_assign="false"
                    v-bind:paginate_amount="25"

                    v-bind:columns="[
                        { column: 'id', display: 'Id', sorted: true, icon: '' ,tooltip:''},
                        { column: 'name', display: 'Name', sorted: true, icon: '' ,tooltip:''},
                        { column: 'addresses', display: '', sorted: true, icon: 'fa-address-book' ,tooltip:'AddressBook'},
                        { column: 'mail_dumps', display: '', sorted: true, icon: 'fa-envelope' ,tooltip:'Emails'},
                        { column: 'common_login', display: 'Login', sorted: true, icon: '' ,tooltip:''},
                        { column: 'common_host', display: 'Host', sorted: true, icon: '' ,tooltip:''},
                        { column: 'enabled', display: '', sorted: true, icon: 'fa-calendar-check-o' ,tooltip:'Enabled'},
                        { column: 'created_at', display: 'Created', sorted: true, icon: '' ,tooltip:''},
                        { column: 'updated_at', display: 'Updated', sorted: true, icon: '', tooltip:''}
                        ]"
                    ></mail-acc-list-component>
            </div>
        </div>


    </div>

    {{--
    <form action="{{route('api.spam_base.new') }}" method="POST">
    <div class="row">
        <div class="col-3">
            <div class="row">
                <div class="form-group col-12">
                    <label for="spam_base_name">Spam base name:</label>
                    <input id="spam_base_name" name="name" class="form-control" placeholder="New name..." required="" type="text">
                </div>
            </div>
        </div>
    </div>
    <hr>
    <div class="row">
        <div class="col-6">
            <label for="">Add addresses from mail accounts: <a data-toggle="collapse" href="#mail_account_filters" role="button" aria-expanded="false" aria-controls="#mail_account_filters">filters</a></label>
            @include('includes.mail-accounts-list', ['accounts' => $accounts, 'filters' => $filters])
            <!-- paginator -->
            <div class="row">
                <div class="col-12 paginator paginator-offset">
                    {{ $accounts->links() }}
                </div>
            </div>
        </div>
        <div class="col-6">
            <div class="row">
                <div class="form-group col-12">
                    <label for="spam_base_name">Add addresses from cpliboard:</label>
                    <textarea class="form-control" id="mail_list" name="mail_list"></textarea>
                </div>
                <!-- upload file -->
                <div class="form-group col-12">
                    <label for="file_list">Add addresses from txt file:</label>
                    <input class="form-control-file" name="file_list[]" id="file_list" type="file">
                </div>
            </div>
        </div>
    </div>
    <div class="row">
        <div class="col-12"><button type="submit" class="btn btn-info">Create</button></div>
    </div>


    </form>
    --}}

    {{--<script type="text/javascript"> var api_url = "{{action('api\CampaignsController@index')}}" </script>--}}
@stop
