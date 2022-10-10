@extends('default')
@if( $test_only )
    @section('title', 'Test Accounts')
@else
    @section('title', 'Accounts')
@endif
@section('content')

    <ul class="nav nav-tabs" id="myTab" role="tablist">
        <li class="nav-item">
            <a class="nav-link" id="old_ver-tab" data-toggle="tab" href="#old_ver" role="tab" aria-controls="old_ver" aria-selected="false">Add new</a>
        </li>
        <li class="nav-item">
            <a class="nav-link active" id="new_ver-tab" data-toggle="tab" href="#new_ver" role="tab" aria-controls="new_ver" aria-selected="true">Manage</a>
        </li>
    </ul>
    <div class="tab-content" id="myTabContent">
        <div class="tab-pane fade" id="old_ver" role="tabpanel" aria-labelledby="old_ver-tab">
            <div class="row">
                <div class="col-12">
                    <div class="col-12">
                        Accounts must be in format:
                        <ul>
                            <li>Each account must be from new line</li>
                            @if( $test_only )
                            <li>Format: <b>smtp://login:password@host:port</b></li>
                            @else
                            <li>Format: <b>protocol://login:password@host:port</b> separated by <b> | </b> (with spaces) i.e. <i>smtp://mylogin:mypassw0rd@myhost:port | imap://imapl0g1n:imapAssword@imaphost:port</i> </li>
                            <li>Format2: <b>smtp_host|x|x|x|x|x|x|x|x|x|smtp_login|smtp_password|x|x|x|x|x|x|x|x|x</b></li>
                            <li>Format3: <b>server,port,login,pass</b></li>
                            <li>Format4 (web accs): <b>URL | login | pass</b></li>
                            <li>If only one protocol is presented in any format, system also will try to find proper missing protocol acount (SMTP/POP3/IMAP) if possible. Web accounts are skipped.</li>
                            @endif
                        </ul>
                        <!-- <b>login:password@host:port</b> or just <b>host:port</b> if no authorization -->
                    </div>
                </div>
            </div>
            <div class="row">
                <div class="col-12">
                    @if( $test_only )
                    <form class="form-horizontal" action="{{action('api\EmailAccountsController@store', 'test_accs')}}" id="mailaccsform">
                    @else
                    <form class="form-horizontal" action="{{action('api\EmailAccountsController@store', 'mail_accs')}}" id="mailaccsform">
                    @endif
                        <fieldset>

                        <!-- Form Name -->
                        <div class="col-12">
                        @if( $test_only )
                        <H6>Add SMTP Test Accounts</H6>
                        @else
                        <H6>Add SMTP with POP3 or IMAP Accounts</H6>
                        @endif
                        </div>
                        <!-- Textarea -->
                        <div class="form-group">
                          <div class="col-12">
                            <textarea class="form-control" id="acc_list" name="acc_list"></textarea>
                          </div>
                        </div>

                        <!-- upload file -->
                        <div class="form-group">
                            <div class="col-12">
                                <label for="file_list">Add from txt file</label>
                                <input class="form-control-file" name="file_list[]" id="file_list" type="file">
                            </div>
                        </div>

                        <!-- selecto group -->
                        <div class="form-group account-groups">
                            <div class="col-12">
                                <label for="">Choose group for new accounts:</label>
                                <div class="row">
                                    @foreach( $groups as $group )
                                    <div class="col-4">
                                    @if(empty($group_radio) || $group_radio == false)
                                        <div class="form-check abc-checkbox abc-checkbox-info form-check">
                                            <input class="form-check-input check-group" name="selected_groups[]" id="select_{{$group->group}}" type="checkbox" value="{{$group->group}}" data-checked="0">
                                            <label class="form-check-label" for="select_{{$group->group}}">{{$group->group}}</label>
                                        </div>
                                        @elseif(!empty($group_radio) && $group_radio == true)
                                        <div class="form-check abc-radio abc-radio-info form-check">
                                            <input class="form-check-input check-group" name="selected_groups[]" id="select_{{$group->group}}" type="radio" value="{{$group->group}}" data-checked="0">
                                            <label class="form-check-label" for="select_{{$group->group}}">{{$group->group}}</label>
                                        </div>
                                    @endif
                                    </div>
                                    @endforeach
                                </div>
                            </div>
                        </div>

                        <!-- write down group name manualy -->
                        <div class="form-group">
                            <div class="col-4">
                                <label for="group_name">... or write down new group:</label>
                                <input type="text" class="form-control" name="group_name" id="group_name" />
                            </div>
                        </div>

                        <!-- grab emails checkbox -->
                        <div class="form-group">
                            <div class="col-12">
                                <div class="form-check abc-checkbox abc-checkbox-info form-check-inline">
                                    <input class="form-check-input check-get-mails" name="need_grab_emails" id="need_grab_emails" type="checkbox" value="1">
                                    <label for="need_grab_emails">Grab email base from new accounts</label>
                                </div>
                            </div>
                        </div>

                        <!-- Button -->
                        <div class="form-group">
                          <div class="col-2">
                            <button id="spamsavebutton" name="spamsavebutton" class="btn btn-info">Add accs</button>
                          </div>
                        </div>

                        </fieldset>
                    </form>
                </div>
            </div>

            <div class="row">
                <div class="col-12">
                    <div class="col-12">
                        <hr>
                    </div>
                </div>
            </div>

            {{--
            <div class="row">
                <div class="col-12">
                    <div class="col-12">
                        <legend>Accs status</legend>
                    </div>
                </div>
            </div>

            <div class="row">
                <form action="#" class="col-12" id="filterform">
                    <div class="col-12">
                        <div class="row">
                            <label class="col-12 control-label" for="textinput">Search:</label>
                            <div class="col-4">
                                <input id="textinput" name="filter_name" placeholder="placeholder" class="form-control input-md" type="text">
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-12">&nbsp;</div>
                            <div class="col-2">
                                <div class="form-check abc-checkbox abc-checkbox-info form-check-inline">
                                    <input class="form-check-input" id="enabled_only" type="checkbox" name="enabled_only" value="1">
                                    <label class="form-check-label" for="enabled_only">Enabled only</label>
                                </div>
                            </div>
                            <div class="col-2">
                                <div class="form-check abc-checkbox abc-checkbox-info form-check-inline">
                                    <input class="form-check-input" id="has_pop" type="checkbox" name="has_pop" value="1">
                                    <label class="form-check-label" for="has_pop">Has pop3</label>
                                </div>
                            </div>
                            <div class="col-2">
                                <div class="form-check abc-checkbox abc-checkbox-info form-check-inline">
                                    <input class="form-check-input" id="has_imap" type="checkbox" name="has_imap" value="1">
                                    <label class="form-check-label" for="has_imap">Has imap</label>
                                </div>
                            </div>
                            <div class="col-2">
                                <div class="form-check abc-checkbox abc-checkbox-info form-check-inline">
                                    <input class="form-check-input" id="has_smtp" type="checkbox" name="has_smtp" value="1">
                                    <label class="form-check-label" for="has_smtp">Has smtp</label>
                                </div>
                            </div>
                            <input type="hidden" value="1" name="page" id="paginate_page" >
                            <!-- <div class="col-12">&nbsp;</div> -->
                        </div>
                        <div class="row">
                            <div class="col-12"><input class="btn btn-sm btn-small btn-info" type="button"value="apply"></div>
                            <div class="col-12">&nbsp;</div>
                        </div>
                    </div>
                </form>
            </div>

            <div class="row">
                <div class="col-12">
                    <div class="col-12">
                    <table class="table table-bordered table-sm table-striped mail_accs-table">
                        <thead>
                          <tr>
                            <th>Id</th>
                            <th>Name</th>
                            <th>Login</th>
                            <th>Host</th>
                            <th>Port</th>
                            <th>Enabled</th>
                            <th>POP3</th>
                            <th>IMAP</th>
                            <th>AddressBook</th>
                            <th>Emails</th>
                            <th>Created</th>
                            <th>Updated</th>
                            <th><div class="cool-checkbox">
                                    <div class="form-check abc-checkbox abc-checkbox-info form-check-inline">
                                        <input class="form-check-input" id="selectAllAccounts" type="checkbox" data-checked>
                                        <label class="form-check-label" for="selectAllAccounts">&nbsp;</label>
                                    </div>
                                </div>
                            </th>
                          </tr>
                        </thead>
                        <tbody>
                          <tr><td colspan="20" align="center">Loading, please wait...</td></tr>
                        </tbody>
                      </table>
                    </div>
                </div>
                <div class="col-12">
                    <div class="col-12">
                        <div class="paginator"></div>
                    </div>
                </div>
                <div class="col-12">
                    @if( $test_only )
                    <form class="form-horizontal" action="{{action('api\EmailAccountsController@massUpdate', 'test_accs')}}" id="mailaccsform">
                    @else
                    <form class="form-horizontal" action="{{action('api\EmailAccountsController@massUpdate', 'mail_accs')}}" id="mailaccsform">
                    @endif
                        <!-- Small button groups (default and split) -->
                        <div class="col-12 text-right">
                            <div class="btn-group" id="mailAccsMassAction">
                                <button class="btn btn-info dropdown-toggle" type="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false"> <!-- btn-sm -->
                                    Chose action
                                </button>
                                <div class="dropdown-menu dropdown-menu-right">
                                    <button class="dropdown-item" type="button" data-opntion="enable">Enable</button>
                                    <button class="dropdown-item" type="button" data-opntion="disable">Disable</button>
                                    <button class="dropdown-item" type="button" data-opntion="clear_addressbook">Clear</button>
                                    <button class="dropdown-item" type="button" data-opntion="intersept">Intersept</button>
                                    <button class="dropdown-item" type="button" data-opntion="delete">Delete</button>
                                </div>
                            </div>
                        </div>

                        <input type="hidden" name="socks_ids" value="" />
                        <input type="hidden" name="action" id="massAction" value="" />
                    </form>
                </div>
            </div>

            <div class="d-none popper-container">
                <div id="popup" class="alert alert-danger">
                    My hint here
                </div>
            </div>
             --}}

            @include('includes.acc-new-address', ['filters' => $filters])
        </div>
        <div class="tab-pane fade show active" id="new_ver" role="tabpanel" aria-labelledby="new_ver-tab">
            <div id="app">
                <mail-acc-list-component
                {{-- @if( $test_only )
                    api_url="{{action('api\EmailAccountsController@index', 'test_accs')}}"
                    api_url_base="{{action('api\EmailAccountsController@index', 'test_accs')}}"
                    api_mac_url="{{action('api\EmailAccountsController@massUpdate', 'test_accs')}}
                @else
                    api_url="{{action('api\EmailAccountsController@index', 'mail_accs')}}"
                    api_url_base="{{action('api\EmailAccountsController@index', 'mail_accs')}}"
                    api_mac_url="{{action('api\EmailAccountsController@massUpdate', 'mail_accs')}}
                @endif --}}
                {{-- ab_url="{{action('EmailAccountsController@addressbook', 'mail_account_id')}}" --}}
                {{-- md_url="{{action('EmailAccountsController@maildump', 'mail_account_id')}}" --}}

                @if( $test_only )
                    api_url="{{action('api\EmailAccountsController@index', 'test_accs')}}"
                @else
                    api_url="{{action('api\EmailAccountsController@index', 'mail_accs')}}"
                @endif

                mb_url="{{action('EmailAccountsController@maildump', 'mail_account_id')}}"
                ab_url="{{action('EmailAccountsController@addressbook', 'mail_account_id')}}"

                ></mail-acc-list-component>
            </div>
        </div>
    </div>




    @if( $test_only )
    <script type="text/javascript"> var api_url = "{{action('api\EmailAccountsController@index', 'test_accs')}}"; </script>
    <script type="text/javascript"> var api_url_base = "{{action('api\EmailAccountsController@index', 'test_accs')}}"; </script>
    <script type="text/javascript"> var api_mac_url = "{{action('api\EmailAccountsController@massUpdate', 'test_accs')}}";</script>
    @else
    <script type="text/javascript"> var api_url = "{{action('api\EmailAccountsController@index', 'mail_accs')}}"; </script>
    <script type="text/javascript"> var api_url_base = "{{action('api\EmailAccountsController@index', 'mail_accs')}}"; </script>
    <script type="text/javascript"> var api_mac_url = "{{action('api\EmailAccountsController@massUpdate', 'mail_accs')}}";</script>
    @endif
    <script type="text/javascript"> var ab_url = "{{action('EmailAccountsController@addressbook', 'mail_account_id')}}"; </script>
    <script type="text/javascript"> var md_url = "{{action('EmailAccountsController@maildump', 'mail_account_id')}}"; </script>
@stop
