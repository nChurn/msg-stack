@extends('default')
@if(is_null($campaign))
    @section('title', 'New Campaign')
@else
    @section('title', "Campaign details")
@endif
@section('content')

    <div id="app">

        @if(is_null($campaign))
        <form class="form-horizontal" action="{{action('api\CampaignsController@store')}}" id="sendmailform">
        @else
        <form class="form-horizontal" action="{{action('api\CampaignsController@update', $campaign->id)}}" id="sendmailform">
        @endif


        <ul class="nav nav-tabs mb-3" id="myTab" role="tablist">
            <li class="nav-item">
                <a class="nav-link active" id="campaign_general-tab" data-toggle="tab" href="#campaign_general" role="tab" aria-controls="campaign_general" aria-selected="true">General</a>
            </li>
            <li class="nav-item">
                <a class="nav-link" id="campaign_account-tab" data-toggle="tab" href="#campaign_account" role="tab" aria-controls="campaign_account" aria-selected="false">Accounts</a>
            </li>
            <li class="nav-item">
                <a class="nav-link" id="spam_base-tab" data-toggle="tab" href="#spam_base" role="tab" aria-controls="spam_base" aria-selected="false">Spam Base</a>
            </li>
            <li class="nav-item">
                <a class="nav-link" id="raw_emails-tab" data-toggle="tab" href="#raw_emails" role="tab" aria-controls="raw_emails" aria-selected="false">Raw emails</a>
            </li>
            <li class="nav-item">
                <a class="nav-link" id="campaign_attachments-tab" data-toggle="tab" href="#campaign_attachments" role="tab" aria-controls="campaign_attachments" aria-selected="false">Attachments</a>
            </li>
            <li class="nav-item">
                <a class="nav-link" id="campaign_help-tab" data-toggle="tab" href="#campaign_help" role="tab" aria-controls="campaign_help" aria-selected="false">Help</a>
            </li>
            <li class="nav-item">
                <a class="nav-link" id="macro_templates-tab" data-toggle="tab" href="#macro_templates" role="tab" aria-controls="macro_templates" aria-selected="false">Macro tpls</a>
            </li>
        </ul>

        <div class="tab-content" id="myTabContent">
            <div class="tab-pane fade show active" id="campaign_general" role="tabpanel" aria-labelledby="campaign_general-tab">
                <div class="row">
                    <div class="col-6">
                        <fieldset>

                            <!-- Form Name -->
                            <div class="col-md-12">
                                @if(is_null($campaign))
                                    <legend>New campaign</legend>
                                @else
                                    <legend>
                                        Campaign {{$campaign->id}} details
                                        @if( $campaign->status == config('campaign.status.STARTED') )
                                        [Started]
                                        @elseif ($campaign->status == config('campaign.status.PAUSED') )
                                        [Paused]
                                        @elseif ($campaign->status == config('campaign.status.COMPETED') )
                                        [Completed]
                                        @endif
                                    </legend>
                                @endif
                            </div>

                            @if(!empty($campaign))
                            <div class="form-group">
                                <div class="col-12">
                                    @include('campaigns.campaign-status')
                                </div>
                            </div>
                            @endif

                            <!-- Input -->
                            <div class="form-group">
                                <div class="col-md-12">
                                    <label for="name">Campaign name</label>
                                    <input class="form-control" id="name" name="name" type="text" required value="@if(!is_null($campaign)){{$campaign->name}}@endif"></input>
                                </div>
                            </div>

                            <div class="form-group custom-headers-container">
                                <div class="col-md-12">
                                    <label for="subject">Custom headers</label>
                                    <button class="btn btn-success btn-sm add-header" type="button"><i class="fa fa-plus"></i></button>
                                </div>
                                @if(!is_null($campaign))
                                @foreach( $campaign->headers as $header => $value)
                                <div class="col-12">
                                    <div class="input-group mb-3">
                                        <input type="text" class="form-control" name="headers_names[]" placeholder="Name" aria-label="Header name" aria-describedby="header-end" required value="{{$header}}">
                                        <div class="input-group-append">
                                            <span class="input-group-text" id="header-end">:</span>
                                        </div>
                                        <input type="text" class="form-control" name="headers_values[]" placeholder="Value" aria-label="Header value" aria-describedby="header-value-end" required value="{{$value}}">
                                        <div class="input-group-append remove-header-icon">
                                            <span class="input-group-text" id="header-value-end"><i class="fa fa-times" aria-hidden="true"></i></span>
                                        </div>
                                    </div>
                                </div>
                                @endforeach
                                @endif
                            </div>

                            <div class="form-group">
                                <div class="col-md-12">
                                    <label for="account_name">Custom From</label>
                                    <input class="form-control" id="account_name" name="account_name" type="text" value="@if(!is_null($campaign)){{$campaign->account_name}}@endif"></input>
                                    <span class="help-block text-sm"><small>*Overrides standart <b>From</b> email field with current value. Can be of format "Jon Doe &lt;username&#64;userhost.com&gt;".</small></span>
                                </div>
                            </div>

                            <!-- Input -->
                            <div class="form-group">
                              <div class="col-md-12">
                                <label for="subject">Subject</label>
                                <input class="form-control" id="subject" name="subject" type="text" required value="@if(!is_null($campaign)){{$campaign->subject}}@endif"></input>
                              </div>
                            </div>

                            <!-- Textarea -->
                            <div class="form-group">
                              <div class="col-md-12">
                                <label for="letterbody">Body</label>
                                <textarea class="form-control" id="letterbody" name="body">@if(!is_null($campaign)){{$campaign->body}}@endif</textarea>
                                <div id="html_editor_container" class="d-none">
                                    <div id="html_editor" ></div>
                                    <textarea name="tinymce_textarea" id="tinymce_textarea" cols="30" rows="10"></textarea>
                                </div>
                              </div>
                            </div>

                            @include('campaigns.body-as-html', ['campaign' => $campaign, 'macros_data' => $macros_data, 'macros_templates'=> $macros_templates])
                            @include('campaigns.reply-mode', ['campaign' => $campaign, 'macros_data' => $macros_data])

                            @include('campaigns.ignore-accounts', ['campaign' => $campaign])
                            @include('campaigns.fail-behaviour', ['campaign' => $campaign])
                            @include('campaigns.skip-same-host', ['campaign' => $campaign])
                            @include('campaigns.has-attachements', ['campaign' => $campaign])

                            <!-- Uploads -->
                            <div class="form-group">
                              <div class="col-md-12">
                                {{-- <div class="form-group">
                                    <label for="attachements">Attachements</label>
                                    <input type="file" class="form-control-file" name="attachements[]" id="attachements" multiple="">
                                </div> --}}

                                <div class="form-group">
                                    <label for="attach_name">Attach name:</label>
                                    <input class="form-control" id="attach_name" name="attach_name" value="@if(!is_null($campaign) && !empty($campaign->attach_name)){{$campaign->attach_name}}@endif" type="text">
                                </div>
                              </div>
                            </div>

                            <div class="form-group filter-froup-container" id="filtersContainer">
                                <div class="col-12">
                                    @if(is_null($campaign))
                                    @include('includes.filter-groups-selector', ['filters' => $filters, 'selected' => []])
                                    @else
                                    @include('includes.filter-groups-selector', ['filters' => $filters, 'selected' => $campaign->filters])
                                    @endif
                                </div>
                            </div>

                            <div class="form-group">
                                <div class="col-12">
                                    @include('campaigns.account-performance')
                                </div>
                            </div>

                            @include('campaigns.check-send', ['campaign' => $campaign])

                            <div class="form-group">
                                <div class="col-md-4">
                                    <label for="datetimepicker2">Scheduled start (UTC):</label>
                                    <div class="input-group date" id="datetimepicker2" data-target-input="nearest">
                                        <input type="text" class="form-control datetimepicker-input" data-target="#datetimepicker2"/>
                                        <div class="input-group-append" data-target="#datetimepicker2" data-toggle="datetimepicker">
                                            <div class="input-group-text"><i class="fa fa-calendar"></i></div>
                                        </div>
                                    </div>
                                </div>
                                <input type="hidden" id="schedule" name="schedule" value="" />
                            </div>

                            @if(is_null($campaign))
                                @include('campaigns.start-immideately')
                            @else
                                @include('campaigns.clear-addressbook')
                            @endif

                            <!-- Button -->
                            <div class="form-group">
                              <div class="col-md-4">
                                <button id="spamsavebutton" name="spamsavebutton" class="btn btn-info">Submit</button>
                              </div>
                            </div>

                            <input type="hidden" name="headers" value="@if(!is_null($campaign) && !empty($campaign->headers)){{json_encode($campaign->headers)}}@endif">

                        </fieldset>
                    </div>

                    <div class="col-6">
                        @include('campaigns.mail-preview')
                    </div>
                </div>
            </div>

            <div class="tab-pane fade" id="campaign_account" role="tabpanel" aria-labelledby="campaign_account-tab">
                {{-- @if(is_null($campaign)) --}}
                    {{-- @include('campaigns.select-accounts', ['accounts' => $accounts]) --}}
                    <mail-acc-list-component
                    api_url="{{action('api\EmailAccountsController@index', 'mail_accs')}}"
                    mb_url="{{action('EmailAccountsController@maildump', 'mail_account_id')}}"
                    ab_url="{{action('EmailAccountsController@addressbook', 'mail_account_id')}}"

                    mac_id="cmpgn-mac-list"
                    selection_change_event_name="selected-{mac_id}"

                    v-bind:show_filters="true"
                    v-bind:show_filters_alive="true"
                    v-bind:show_filters_error_status="true"
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

                    @if(!is_null($campaign))
                    v-bind:selected_records="{{$campaign->mail_account_ids}}"
                    @endif

                    ></mail-acc-list-component>
                {{-- @else --}}
                    {{-- @include('campaigns.edit-attachements', ['campaign' => $campaign]) --}}
                {{-- @endif --}}
            </div>

            <div class="tab-pane fade" id="spam_base" role="tabpanel" aria-labelledby="spam_base-tab">
                <spam-base-list-component
                    api_url="{{route('api.spam_base.list')}}"
                    delete_url="{{route('api.spam_base.delete', 'base_id')}}"
                    mass_update_url="{{route('api.spam_base.mass_update')}}"
                    edit_url="{{route('spam_base.show', 'base_id')}}"

                    selection_change_event_name="selected-cmpgn-spam-base-list"

                    v-bind:show_actions="false"
                    @if(!is_null($campaign))
                    v-bind:selected_records="{{$campaign->spam_base_ids}}"
                    @endif
                    >
                </spam-base-list-component>
            </div>

            <div class="tab-pane fade" id="campaign_attachments" role="tabpanel" aria-labelledby="campaign_attachments-tab">
                <attachment-list-component
                    att_id="cmpgn-att-list"
                    selection_change_event_name="selected-{att_id}"

                    api_url = "{{route('api.attachments.index')}}"
                    create_url = "{{route('api.attachments.create')}}"
                    update_url = "{{route('api.attachments.update', 'att_id')}}"
                    delete_url = "{{route('api.attachments.delete')}}"

                    @if(!is_null($campaign) && !empty($attachments))
                    selected_atts = <?php echo implode(",", $attachments); ?>
                    @endif

                ></attachment-list-component>
            </div>

            <div class="tab-pane fade" id="raw_emails" role="tabpanel" aria-labelledby="raw_emails-tab">
                @include('campaigns.outside-addresses')
            </div>

            <div class="tab-pane fade" id="campaign_help" role="tabpanel" aria-labelledby="campaign_help-tab">
                @include('includes.supported-macroses')
            </div>

            <div class="tab-pane fade" id="macro_templates" role="tabpanel" aria-labelledby="macro_templates-tab">
                <macros-list-component
                    api_url="{{route('api.macros.index')}}"
                    remove_url="{{route('api.macros.remove')}}"
                ></macros-list-component>
            </div>
        </div>

        </form>
    </div>

    <div class="d-none headers-template-old">
        <div class="col-12">
            <div class="row">
                <div class="col-6">
                    <label>Header</label>
                    <!-- <input class="form-control" name="headers_names[]" type="text"></input> -->
                    <div class="input-group mb-3">
                        <input type="text" class="form-control" name="headers_names[]" placeholder="" aria-label="Header name" aria-describedby="header-end" required>
                        <div class="input-group-append"><span class="input-group-text" id="header-end"><b>:</b></span></div>
                    </div>
                </div>
                <div class="col-6">
                    <label>Value</label>
                    <!-- <input class="form-control" name="headers_values[]" type="text"></input> -->
                    <div class="input-group mb-3">
                        <input type="text" class="form-control" name="headers_values[]" placeholder="" aria-label="Header value" aria-describedby="header-value-end" required>
                        <div class="input-group-append"><span class="input-group-text" id="header-value-end"><b>;</b></span></div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <div class="d-none headers-template">
        <div class="col-12">
            <div class="input-group mb-3">
                <input type="text" class="form-control" name="headers_names[]" placeholder="Name" aria-label="Header name" aria-describedby="header-end" required>
                <div class="input-group-append">
                    <span class="input-group-text" id="header-end">:</span>
                </div>
                <input type="text" class="form-control" name="headers_values[]" placeholder="Value" aria-label="Header value" aria-describedby="header-value-end" required>
                <div class="input-group-append remove-header-icon">
                    <span class="input-group-text" id="header-value-end"><i class="fa fa-times" aria-hidden="true"></i></span>
                </div>
            </div>
        </div>
    </div>

    <script type="text/javascript"> var mail_dump_data = <?php echo($mail_dump)?>;</script>
    <script type="text/javascript"> var api_url = "{{action('api\CampaignsController@index')}}" </script>

@section('pagespecificscripts')
    <script src="{{ asset('js/tinymce.min.js') }}" type="text/javascript"></script>
    <script src="{{ asset('js/tempusdominus-bootstrap-4.min.js') }}" type="text/javascript"></script>
@endsection

@stop
