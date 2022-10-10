@extends('default')
@section('title', 'Socks')
@section('content')
    <div class="row">
        <div class="col-6">
            <form class="form-horizontal" action="{{action('api\SocksController@store')}}" id="spamsocksform">
                <fieldset>

                <!-- Form Name -->
                <div class="col-12">
                    <legend>Add Socks</legend>
                </div>

                <div class="col-12">
                    <p>Socks must be in format: <b>login:password@host:port</b> or just <b>host:port</b> if no authorization</p>
                </div>


                <div class="form-group">
                    <div class="col-4">
                        <label for="socks_type" class="col-form-label">Socks type</label>
                        <select id="socks_type" name="type" class="custom-select">
                            <option value="spam">SMTP Spam</option>
                            <option value="grabber">Mail Grabber</option>
                            <option value="checker">Account Checker</option>
                        </select>
                    </div>
                </div>

                <!-- Textarea -->
                <div class="form-group">
                  <div class="col-12">
                    <label for="spamlist" class="col-form-label">Socks list</label>
                    <textarea class="form-control" id="spamlist" name="ip_list" rows="8"></textarea>
                  </div>
                </div>

                <!-- upload file -->
                <div class="form-group">
                    <div class="col-12">
                        <label for="file_list">Add from txt file</label>
                        <input class="form-control-file" name="file_list[]" id="file_list" type="file">
                    </div>
                </div>

                <!-- Button -->
                <div class="form-group">
                  <div class="col-4">
                    <button id="spamsavebutton" name="spamsavebutton" class="btn btn-info">Add socks</button>
                  </div>
                </div>

                {{-- <input type="hidden" name="type" value="spam" /> --}}

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
        <div class="col-4">
            <div class="col-12">
                <legend>Socks status</legend>
            </div>
        </div>
        <div class="col-8">
            <form class="form-horizontal actionsocksform" action="{{action('api\SocksController@massUpdate')}}">
                <!-- Small button groups (default and split) -->
                <div class="col-12 text-right">
                    <div class="btn-group socksMassAction">
                        <button class="btn btn-info dropdown-toggle" type="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false"> <!-- btn-sm -->
                            Chose action
                        </button>
                        <div class="dropdown-menu dropdown-menu-right">
                            <button class="dropdown-item" type="button" data-opntion="enable">Enable</button>
                            <button class="dropdown-item" type="button" data-opntion="disable">Disable</button>
                            <button class="dropdown-item" type="button" data-opntion="type-spam">Change type to spam</button>
                            <button class="dropdown-item" type="button" data-opntion="type-grabber">Change type to grabber</button>
                            <button class="dropdown-item" type="button" data-opntion="allow-smtp">Allow smtp</button>
                            <button class="dropdown-item" type="button" data-opntion="disallow-smtp">Disallow smtp</button>
                            <button class="dropdown-item" type="button" data-opntion="delete">Delete</button>
                            <button class="dropdown-item" type="button" data-opntion="delete-all-dead">Delete all dead</button>
                            <button class="dropdown-item" type="button" data-opntion="delete-all-banlisted">Delete all banned</button>
                        </div>
                    </div>
                </div>

                <input type="hidden" name="socks_ids" value="" />
                <input type="hidden" name="action" id="massAction" value="" />
            </form>
        </div>
    </div>
    <div class="row">
        <div class="col-12">
            <div class="col-12">
            <table class="table table-bordered table-sm table-striped socks-table">
                <thead>
                  <tr>
                    <th class="sorted" data-sort="host" data-sort-order="none"><span>Host<i aria-hidden="true" class="fa pull-right fa-sort"></i></span></th>
                    <th class="sorted" data-sort="port" data-sort-order="none"><span>Port<i aria-hidden="true" class="fa pull-right fa-sort"></i></span></th>
                    <th class="sorted" data-sort="login" data-sort-order="none"><span>Login<i aria-hidden="true" class="fa pull-right fa-sort"></i></span></th>
                    <th class="sorted" data-sort="password" data-sort-order="none"><span>Password<i aria-hidden="true" class="fa pull-right fa-sort"></i></span></th>
                    <th class="sorted" data-sort="type" data-sort-order="none"><span>Type<i aria-hidden="true" class="fa pull-right fa-sort"></i></span></th>
                    <th class="sorted" data-sort="hostname" data-sort-order="none"><span>HostName<i aria-hidden="true" class="fa pull-right fa-sort"></i></span></th>
                    <th class="sorted" data-sort="outer_ip" data-sort-order="none"><span>OuterIP<i aria-hidden="true" class="fa pull-right fa-sort"></i></span></th>
                    <th class="sorted" data-sort="alive" data-sort-order="none"><span>Alive<i aria-hidden="true" class="fa pull-right fa-sort"></i></span></th>
                    <th class="sorted" data-sort="enabled" data-sort-order="none"><span>Enabled<i aria-hidden="true" class="fa pull-right fa-sort"></i></span></th>
                    <th class="sorted" data-sort="smtp_allow" data-sort-order="none"><span>Smtp<i aria-hidden="true" class="fa pull-right fa-sort"></i></span></th>
                    <th class="sorted" data-sort="checked_at" data-sort-order="none"><span>Checked At<i aria-hidden="true" class="fa pull-right fa-sort"></i></span></th>
                    <th>
                        <div class="form-check abc-checkbox abc-checkbox-info form-check-inline">
                            <input class="form-check-input" id="checkAllSocks" type="checkbox">
                            <label class="form-check-label" for="checkAllSocks">&nbsp;</label>
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
            <form class="form-horizontal actionsocksform" action="{{action('api\SocksController@massUpdate')}}">
                <!-- Small button groups (default and split) -->
                <div class="col-12 text-right">
                    <div class="btn-group socksMassAction">
                        <button class="btn btn-info dropdown-toggle" type="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false"> <!-- btn-sm -->
                            Chose action
                        </button>
                        <div class="dropdown-menu dropdown-menu-right">
                            <button class="dropdown-item" type="button" data-opntion="enable">Enable</button>
                            <button class="dropdown-item" type="button" data-opntion="disable">Disable</button>
                            <button class="dropdown-item" type="button" data-opntion="type-spam">Change type to spam</button>
                            <button class="dropdown-item" type="button" data-opntion="type-grabber">Change type to grabber</button>
                            <button class="dropdown-item" type="button" data-opntion="allow-smtp">Allow smtp</button>
                            <button class="dropdown-item" type="button" data-opntion="disallow-smtp">Disallow smtp</button>
                            <button class="dropdown-item" type="button" data-opntion="delete">Delete</button>
                            <button class="dropdown-item" type="button" data-opntion="delete-all-dead">Delete all dead</button>
                            <button class="dropdown-item" type="button" data-opntion="delete-all-banlisted">Delete all banned</button>
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


    <script type="text/javascript"> var api_url = "{{action('api\SocksController@index')}}" </script>
@stop
