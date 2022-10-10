@extends('default')
@section('title', 'Campaign details')
@section('content')
    <div class="row">
        <div class="col-12">

            <!-- Form Name -->
            <div class="row">
                <div class="col-12">
                    <div class="col-12">
                        <legend>Campaign detailed report</legend>
                        <label>Total letters - {{$campaign->address_book_count}}, success - {{$campaign->address_book_success_count}}, failed - {{$campaign->address_book_fail_count}}, skipped - {{$campaign->address_book_skip_count}}, efficiency - {{ $campaign->efficiency }}%</label>
                        <hr>
                    </div>
                </div>
            </div>

            <div class="row">
                <!-- Input -->
                <div class="col-6">
                    <div class="col-12">
                    <legend for="">Common info:</legend>
                    <table class="table table-bordered table-sm table-striped common_info-table">
                        <tr>
                            <td>Name:</td>
                            <td>{{$campaign->name}}</td>
                        </tr>
                        <tr>
                            <td>Status:</td>
                            <td>
                                @if( $campaign->status == config('campaign.status.STARTED') )
                                Started
                                @elseif( $campaign->status == config('campaign.status.PAUSED') )
                                Paused
                                @elseif( $campaign->status == config('campaign.status.COMPETED') )
                                Complited
                                @endif
                            </td>
                        </tr>
                    </table>
                    </div>

                    <div class="col-12">
                        <label for="subject">Custom headers</label>
                    </div>
                    @if( empty($campaign->headers) )
                    <div class="col-12">
                        No custom headers
                    </div>
                    @else
                    <div class="col-12">
                    <table class="table table-bordered table-sm table-striped custom_headers-table">
                        <thead>
                            <tr>
                                <th>Header</th>
                                <th>Value</th>
                            </tr>
                        </thead>
                        <tbody>
                            @foreach( $campaign->headers as $header => $value)
                            <tr>
                                <td>{{$header}}</td>
                                <td>{{$value}}</td>
                            </tr>
                            @endforeach
                        </tbody>
                    </table>
                    </div>
                    @endif
                </div>

                <div class="col-6">
                    <div class="col-12">
                    @include('campaigns.mail-preview')
                    </div>

                    <div class="d-none">
                        <input type="hidden" id="subject_raw" value="{{$campaign->subject}}" />
                        <input type="hidden" id="body_raw" value="{{$campaign->body}}" />
                        <input type="hidden" id="attach_name_raw" value="{{$campaign->attach_name}}" />
                        <input type="hidden" id="macros_data" value="{{json_encode($macros_data)}}" />
                        <input type="hidden" id="macro_templates" data-macro-tpls="{{json_encode($macros_templates)}}" />
                    </div>
                </div>
            </div>

            <!-- Attachements -->
            <div class="col-12">
                <label>Attachements:</label>
                <table class="table table-bordered table-sm table-striped attachements-table">
                    <thead>
                        <tr>
                            <th>Id</th>
                            <th>Name</th>
                            <th>Size</th>
                            <th>Used</th>
                        </tr>
                    </thead>
                    <tbody>
                        @if($campaign->attachements_count > 0)
                            @foreach ($campaign->attachements as $att)
                            <tr>
                                <td>{{$att->id}}</td>
                                <td>{{$att->name}}</td>
                                <td>{{$att->size}}</td>
                                <td>{{$att->used_redis}}</td>
                            </tr>
                            @endforeach
                        @else
                            <tr><td colspan="10" align="center">No attachements in campaign</td></tr>
                        @endif
                    </tbody>
                </table>
            </div>

            {{--
            <div class="col-12">
                <label for="">Accounts:</label>
                <table class="table table-bordered table-sm table-striped data-stat-table">
                    <thead>
                        <tr>
                            <th>Id</th>
                            <th>Name</th>
                            <th>Total</th>
                            <th>Waiting</th>
                            <th>Processing</th>
                            <th>Success</th>
                            <th>Failed</th>
                            <th>Skipped</th>
                            <th>Blacklisted</th>
                        </tr>
                    </thead>
                    <tbody>
                        @if(!empty($data_stat))
                            @foreach ($data_stat as $acc)
                            <tr>
                                <td>{{$acc['mail_account_id']}}</td>
                                <td>{{$acc['login']}}</td>
                                <td>{{$acc['total']}}</td>
                                <td>{{$acc['await']}}</td>
                                <td>{{$acc['processing']}}</td>
                                <td>{{$acc['success']}}</td>
                                <td>{{$acc['fail']}}</td>
                                <td>{{$acc['skip']}}</td>
                                <td>{{$acc['blacklist']}}</td>
                            </tr>
                            @endforeach
                        @else
                            <tr><td colspan="10" align="center">No data campaign</td></tr>
                        @endif
                    </tbody>
                </table>
            </div>
            --}}

            <div id="app" class="col-12">
            <!-- Sending details -->
            <campaign-record-details-component
                api_url="{{action('api\CampaignsController@detailsAddressBook', $campaign->id)}}"

                mac_id="cmpgn-records-list"
                selection_change_event_name="selected-campaign-records-{mac_id}"

                v-bind:show_filters="true"
                v-bind:show_filters_record_status="true"
                v-bind:show_filters_search_input="true"
                v-bind:show_filters_apply_input="true"
                v-bind:show_mass_assign="true"
                v-bind:paginate_amount="25"
            ></campaign-record-details-component>
            </div>
            {{--
            <div class="col-12">
                <label>Letter details: <a href="#" class="toggle-filters" data-toggle="collapse" data-target="#filtersCollapse" aria-expanded="false" aria-controls="filtersCollapse" >toggle filters</a></label>
                <div class="filters collapse row" id="filtersCollapse">
                    <form action="#" id="filterform">
                    <div class="col-12">
                        <div class="form-check abc-checkbox abc-checkbox-info form-check-inline">
                            <input class="form-check-input" id="filter_await" type="checkbox" name="record_status[]" value="{{config('campaign.record_status.await')}}">
                            <label class="form-check-label" for="filter_await">Await</label>
                        </div>
                        <div class="form-check abc-checkbox abc-checkbox-info form-check-inline">
                            <input class="form-check-input" id="filter_processing" type="checkbox" name="record_status[]" value="{{config('campaign.record_status.processing')}}">
                            <label class="form-check-label" for="filter_processing">Processing</label>
                        </div>
                        <div class="form-check abc-checkbox abc-checkbox-info form-check-inline">
                            <input class="form-check-input" id="filter_success" type="checkbox" name="record_status[]" value="{{config('campaign.record_status.success')}}">
                            <label class="form-check-label" for="filter_success">Success</label>
                        </div>
                        <div class="form-check abc-checkbox abc-checkbox-info form-check-inline">
                            <input class="form-check-input" id="filter_failed" type="checkbox" name="record_status[]" value="{{config('campaign.record_status.fail')}}">
                            <label class="form-check-label" for="filter_failed">Failed</label>
                        </div>
                    </div>

                    <div class="col-12">
                        <button type="button" class="btn btn-sm btn-small btn-info">Apply</button>
                    </div>
                    </form>
                    <div class="col-12 small">&nbsp;</div>
                </div>
                <table class="table table-bordered table-sm table-striped record_details-table">
                    <thead>
                        <tr>
                            <td>Id</td>
                            <td>AccID</td>
                            <td>Account Login</td>
                            <td>Address</td>
                            <td>Result</td>
                            <td>Details</td>
                            <td>
                                <div class="form-check abc-checkbox abc-checkbox-info form-check-inline">
                                    <input class="form-check-input" id="check_all_detail_records" type="checkbox">
                                    <label class="form-check-label" for="check_all_detail_records">&nbsp;</label>
                                </div>
                            </td>
                        </tr>
                    </thead>
                    <tbody>
                        <tr><td colspan="10" align="center">Loading please wait...</td></tr>
                    </tbody>
                </table>
            </div>

            <div class="row">
                <div class="col-10">
                    <div class="col-12">
                        <div class="paginator"></div>
                    </div>
                </div>
                <div class="col-2 text-right">
                    <div class="col-12">
                    <div class="btn-group" id="detailRecordsMassAction">
                        <button class="btn btn-info dropdown-toggle" type="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false"> <!-- btn-sm -->
                            Chose action
                        </button>
                        <div class="dropdown-menu dropdown-menu-right">
                            <button class="dropdown-item" type="button" data-opntion="mark-await">Mark await</button>
                            <button class="dropdown-item" type="button" data-opntion="mark-success">Mark success</button>
                            <button class="dropdown-item" type="button" data-opntion="mark-processing">Mark processing</button>
                            <button class="dropdown-item" type="button" data-opntion="mark-fail">Mark fail</button>
                            <button class="dropdown-item" type="button" data-opntion="delete">Delete</button>
                        </div>
                    </div>
                    </div>
                </div>
            </div>
            --}}

        </div>
    </div>

    <script type="text/javascript">
        var api_url = "{{action('api\CampaignsController@index')}}";
        var details_url = "{{action('api\CampaignsController@detailsAddressBook', $campaign->id)}}";
        var details_update_url = "{{action('api\CampaignsController@addressBookMassUpdate', $campaign->id)}}";
    </script>

@stop
