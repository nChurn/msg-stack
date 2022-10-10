@extends('default')
@section('title', 'Mail list for ' . $account->common_login)
@section('content')
    <!-- header -->
    <div class="row mail-dump-header">
        <div class="col-12">
            <legend class="text-small">
                Mail list for {{$account->common_login}}. Total records: {{$account->maildump_count}}.
                @if( !empty(app('request')->input('search')) )
                Filtered by "{{app('request')->input('search')}}" records: {{$maildump->total()}}.
                @endif
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

    <!-- select all -->
    <div class="row select-all-letters-container">
        <div class="col-12">
            <div class="form-check abc-checkbox abc-checkbox-info form-check-inline">
                <input class="form-check-input" id="selectAllRecords" type="checkbox" name="selected_records_toggler" value="none">
                <label class="form-check-label" for="selectAllRecords">Select all letters</label>
            </div>
            <span class="selected-mass-actions">
                <div style="box-sizing: border-box; padding-bottom: 5px;">
                <i class="fa fa-trash mail-dump-dl-remove-letter" aria-hidden="true" title="Remove letter" data-option="delete"></i>
                <i class="fa fa-download mail-dump-get-letter" aria-hidden="true" title="Get whole letter" data-option="download"></i>
                </div>
            </span>
        </div>
    </div>
    
    <!-- mail content -->
    <div class="row">
        <div class="col-4 mail-dump-list-container">
            <div class="mail-dump-list-inner-container">
            @foreach($maildump as $record)
            <div class="mail-dump-record" data-id="{{$record->id}}">
                <div class="row">
                    <div class="col-1">
                        <div class="form-check abc-checkbox abc-checkbox-info form-check-inline">
                            <input class="form-check-input" id="mail_id_{{$record->id}}" type="checkbox" name="selected_records" value="{{$record->id}}">
                            <label class="form-check-label" for="mail_id_{{$record->id}}"></label>
                        </div>
                    </div>
                    <div class="col-11">
                        <div class="row">
                            <div class="col-8 text-truncate" title="{{$record->from}}">
                                {{$record->from}}
                            </div>
                            <div class="col-4 small text-right">{{$record->mail_date}}</div>
                        </div>
                        <div class="row">
                            <div class="col-10 text-truncate" title="{{$record->subject}}">
                                <h5>{{$record->subject}}</h5>
                            </div>
                            <div class="col-2 text-right">
                                @if($record->has_attaches == 1)
                                <i class="fa fa-low-vision" aria-hidden="true" title="Likely mail has attachement"></i>
                                @elseif($record->has_attaches == 2)
                                <i class="fa fa-paperclip" aria-hidden="true" title="Mail has attachement"></i>
                                @endif

                                @if($record->need_body == 0)
                                <i class="fa fa-file-o" aria-hidden="true" title="Mail body not downloaded"></i>
                                @elseif($record->need_body == 1)
                                <i class="fa fa-cloud-download" aria-hidden="true" title="Mail body download in progress"></i>
                                @elseif($record->need_body == 2)
                                <i class="fa fa-file-text-o" aria-hidden="true" title="Mail body download complete"></i>
                                @endif
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            @endforeach
            </div>
        </div>
        <div class="col-8 mail-body-details-container">
            <div class="loader-bg d-none"></div>
            <div class="loader-centered d-none"></div>
            <div class="mail-dump-details-container d-none" data-id="0">
                <div class="mail-dump-ui-header-container">
                    <div class="row">
                        <div class="col-1">From:</div>
                        <div class="col-5 mail-dump-body-from"></div>
                        <div class="col-6 text-right mail-dump-body-date small">2005-12-18 12:12:45</div>
                    </div>
                    <div class="row">
                        <div class="col-1">To:</div>
                        <div class="col-5 mail-dump-body-to"></div>
                    </div>
                    <div class="row">
                        <div class="col-1">Subject:</div>
                        <div class="col-11 mail-dump-body-subject"></div>
                    </div>
                    <div class="row">
                        <div class="col-1">Actions:</div>
                        <div class="col-6 mail-dump-body-actions">
                            <i class="fa fa-trash mail-dump-dl-remove-letter" aria-hidden="true" title="Remove letter"></i>
                            <i class="fa fa-file-code-o mail-dump-show-headers" aria-hidden="true" title="Show letter headers"></i>
                            <i class="fa fa-download mail-dump-get-letter" aria-hidden="true" title="Get whole letter"></i>
                            <i class="fa fa-paperclip mail-dump-dl-attach" aria-hidden="true" title="Download all mail attachement"></i>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-12 mail-dump-attach-list">
                            <span class="attach-detailed"><a href="{attach_url}"><i class="fa fa-paperclip mail-dump-dl-attach" aria-hidden="true" title="Download mail attachement"></i>{filename}</a></span>
                            <span class="attach-detailed"><a href="{attach_url}"><i class="fa fa-paperclip mail-dump-dl-attach" aria-hidden="true" title="Download mail attachement"></i>{filename}</a></span>
                        </div>
                    </div>
                    <hr>
                </div>

                <div class="row mail-dump-main-data-container">
                    <div class="col-12 mail-dump-headers-container d-none"></div>
                    <div class="col-12">
                        <div class="mail-dump-body-container">
                            <iframe src="" frameborder="0" class="mail-dump-body-iframe"></iframe> 
                        </div>
                    </div>
                </div>

            </div>
        </div>
    </div>

    <!-- paginator -->
    <div class="row">
        <div class="col-12 paginator paginator-offset">
            {{ $maildump->links() }}
        </div>
    </div>

    <!-- template -->
    <div class="d-none templates">
        <div class="mail-dump-record-tpl">
            <div class="mail-dump-record" data-id="{id}">
                <div class="row">
                    <div class="col-1">
                        <div class="form-check abc-checkbox abc-checkbox-info form-check-inline">
                            <input class="form-check-input" id="mail_id_{id}" type="checkbox" name="selected_records" value="{id}">
                            <label class="form-check-label" for="mail_id_{id}"></label>
                        </div>
                    </div>
                    <div class="col-11">
                        <div class="row">
                            <div class="col-8 text-truncate" title="{from}">
                                {from}
                            </div>
                            <div class="col-4 small text-right">{mail_date}</div>
                        </div>
                        <div class="row">
                            <div class="col-10 text-truncate" title="{subject}">
                                <h5>{subject}</h5>
                            </div>
                            <div class="col-2 text-right">
                                {attach}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <div class="attaches-one-attach-template">
            <span class="attach-detailed text-truncate"><a href="{attach_url}" target="_blank"><i class="fa fa-paperclip mail-dump-dl-attach" aria-hidden="true" title="Download mail attachement"></i>{filename}</a></span>
        </div>
    </div>


    {{--
    <div class="row">
        <form action="{{action('EmailAccountsController@maildump', $account->id)}}" method="GET" style="width: 100%; display: block;">
        <div class="col-12">
            <legend>
                Account {{$account->common_login}} maildump. Total records: {{$account->maildump_count}}.
                @if( !empty(app('request')->input('search')) )
                Filtered by "{{app('request')->input('search')}}" records: {{$maildump->total()}}.
                @endif
            </legend>
            <div class="row">
                <input type="hidden" name="page" value="1" />
                <label class="col-12 control-label" for="textinput">Search:</label>  
                <div class="col-4">
                    <input id="textinput" name="search" placeholder="placeholder" class="form-control input-md" type="text" value="{{ app('request')->input('search') }}" >
                </div>
                <div class="col-4">
                    <input class="btn btn-info" type="submit" value="Apply">
                </div>

                <div class="col-12">&nbsp;</div>
            </div>
            <table class="table table-bordered table-sm table-striped mail_acc_maildump-table">
                <thead>
                    <tr>
                        <th>Id</th>
                        <th>From</th>
                        <th>To</th>
                        <th>Subject</th>
                        <th>Body</th>
                        <th style="min-width: 50px;">
                            <div class="cool-checkbox">
                                <div class="form-check abc-checkbox abc-checkbox-info abc-checkbox-inline">
                                    <input class="form-check-input" id="selectAllRecords" type="checkbox" name="selected_records_toggler" value="none">
                                    <label class="form-check-label" for="selectAllRecords"></label>
                                </div>
                            </div>
                        </th>
                    </tr>
                </thead>
                <tbody>
                    @foreach($maildump as $record)

                    @if(is_null($record->send_rule_id))
                    <tr class="" data-id="{{$record->id}}">
                    @else
                    <tr class="in-send-rules" data-id="{{$record->id}}">
                    @endif
                        <td>{{$record->id}}</td>
                        <td>{{$record->from}}</td>
                        <td>{{$record->to}}</td>
                        <td>{{$record->subject}}</td>
                        <td>
                            @if($record->need_body && empty($record->body))
                            Processing...
                            @elseif(!empty($record->body))
                            {{$record->body}}
                            @else
                            None
                            @endif
                        </td>
                        <td>
                            <div class="cool-checkbox">
                                <div class="form-check abc-checkbox abc-checkbox-info abc-checkbox-inline">
                                    <input class="form-check-input" id="selectRecord{{$record->id}}" type="checkbox" name="selected_records" value="{{$record->id}}">
                                    <label class="form-check-label" for="selectRecord{{$record->id}}"></label>
                                </div>
                            </div>
                        </td>
                    </tr>
                    @endforeach
                </tbody>
            </table>
        </div>

        <div class="col-12">
            <div class="paginator">
                {{ $maildump->links() }}
            </div>
        </div>
        </form>

        <div class="col-12">
            <form class="form-horizontal" action="{{action('EmailAccountsController@mailDumpMassUpdate')}}" id="actionabform">
                <!-- Small button groups (default and split) -->
                <div class="col-12 text-right">
                    <div class="btn-group" id="adMassAction">
                        <button class="btn btn-info dropdown-toggle" type="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false"> <!-- btn-sm -->
                            Chose action
                        </button>
                        <div class="dropdown-menu dropdown-menu-right">
                            <button class="dropdown-item" type="button" data-option="download">Download body</button>
                            <button class="dropdown-item" type="button" data-option="undownload">Not-Download body</button>
                            <button class="dropdown-item" type="button" data-option="delete">Delete</button>
                        </div>
                    </div>
                </div>

                <input type="hidden" name="socks_ids" value="" />
                <input type="hidden" name="action" id="massAction" value="" />
            </form>
        </div>
    </div>
    --}}
    <script type="text/javascript">
        var api_url = "{{action('api\EmailAccountsController@mailDumpDetails', 'item_id')}}";
        var mass_update_api_url = "{{action('EmailAccountsController@mailDumpMassUpdate')}}";
        var mail_dump_download_attach_url = "{{action('EmailAccountsController@getMailDumpAttach', 'mail_dump_id')}}";
    </script>
@stop