@extends('default')
@section('title', 'Accounts')
@section('content')
    <div class="row">
        <div class="col-12">
            <div class="col-12">
                Accounts must be in format: 
                <ul>
                    <li>Each account must be from new line</li>
                    <li>Format: <b>protocol://login:password@host:port</b> separated by <b> | </b> (with spaces) i.e. <i>smtp://mylogin:mypassw0rd@myhost:port | imap://imapl0g1n:imapAssword@imaphost:port</i> </li>
                </ul>
                <!-- <b>login:password@host:port</b> or just <b>host:port</b> if no authorization -->
            </div>
        </div>
    </div>
    <div class="row">
        <div class="col-6">
            <form class="form-horizontal" action="{{action('api\EmailAccountsController@store')}}" id="mailaccsform">
                <fieldset>

                <!-- Form Name -->
                <div class="col-md-12">
                <legend>Add SMTP Accounts</legend>
                </div>
                <!-- Textarea -->
                <div class="form-group">
                  <div class="col-md-12">
                    <textarea class="form-control" id="acc_list" name="acc_list"></textarea>
                  </div>
                </div>

                <!-- Button -->
                <div class="form-group">
                  <div class="col-md-4">
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

    <div class="row">
        <div class="col-12">
            <div class="col-12">
                <legend>Accs status</legend>
            </div>
        </div>
    </div>
    
    <div class="row">
        <div class="col-12">
            <div class="col-12">
            <table class="table table-bordered table-sm table-striped mail_accs-table">
                <thead>
                  <tr>
                    <th>Id</th>
                    <th>Login</th>
                    <th>Host</th>
                    <th>Port</th>
                    <th>Enabled</th>
                    <th>Created</th>
                    <th>Updated</th>
                    <th><div class="cool-checkbox">
                            <div class="form-check abc-checkbox abc-checkbox-info abc-checkbox-inline">
                                <input class="form-check-input" id="selectAllAccounts" type="checkbox" data-checked>
                                <label class="form-check-label" for="selectAllAccounts">&nbsp;</label>
                            </div>
                        </div>
                    </th>
                  </tr>
                </thead>
                <tbody>
                  <tr><td colspan="10" align="center">Loading, please wait...</td></tr>
                </tbody>
              </table>
            </div>
        </div>
        <div class="col-12">
            <form class="form-horizontal" action="{{action('api\EmailAccountsController@massUpdate')}}" id="mailaccsform">
                <!-- Small button groups (default and split) -->
                <div class="col-12 text-right">
                    <div class="btn-group" id="mailAccsMassAction">
                        <button class="btn btn-info dropdown-toggle" type="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false"> <!-- btn-sm -->
                            Chose action
                        </button>
                        <div class="dropdown-menu dropdown-menu-right">
                            <button class="dropdown-item" type="button" data-opntion="delete">Delete</button>
                            <button class="dropdown-item" type="button" data-opntion="enable">Enable</button>
                            <button class="dropdown-item" type="button" data-opntion="disable">Disable</button>
                        </div>
                    </div>
                </div>

                <input type="hidden" name="socks_ids" value="" />
                <input type="hidden" name="action" id="massAction" value="" />
            </form>
        </div>
    </div>

    <script type="text/javascript"> var api_url = "{{action('api\EmailAccountsController@index')}}" </script>
@stop