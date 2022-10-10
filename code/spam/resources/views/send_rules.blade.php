@extends('default')
@section('title', 'Send rules')
@section('content')
    <div class="row">
        <div class="col-6">
            <form class="form-horizontal" action="{{action('api\SendRulesController@store')}}" id="scanrulesform">
                <fieldset>

                <div class="col-12">
                    
                </div>

                <!-- Form Name -->
                <div class="col-md-12">
                    <legend>Add multiple rules</legend>
                    Each rule starts with new string.
                    <!-- <br>All rules are python regexp with flags multiline and ignorecase set as default. See <a href="https://docs.python.org/3/library/re.html#regular-expression-syntax">here</a> for details. -->
                </div>
                <!-- Textarea -->
                <div class="form-group">
                  <div class="col-md-12">
                    <textarea class="form-control" id="scan_rules" name="scan_rules"></textarea>
                  </div>
                </div>

                <div class="form-group">
                  <div class="col-md-12">
                    <!-- <label for="">Choose group from list</label> -->
                    @include('includes.filter-groups-selector', ['filters' => $filters, 'radio' => true])

                    <label for="rulesGroup">Enter group name manually</label>
                    <input type="text" id="rulesGroup" class="form-control" name="group" value="" placeholder="Groupname">
                  </div>
                </div>

                <!-- Button -->
                <div class="form-group">
                  <div class="col-md-4">
                    <button id="spamsavebutton" name="spamsavebutton" class="btn btn-info">Add rules</button>
                  </div>
                </div>

                </fieldset>
            </form>
        </div>
    </div>

    <!-- <div class="row">
        <div class="col-12">
            <div class="col-12">
                <hr>
            </div>
        </div>
    </div> -->

    <!-- <div class="row">
        <div class="col-12">
            <div class="col-12">
                <legend>Add single rule <button class="btn btn-outline-success btn-sm add-scan-rule"><i class="fa fa-plus"></i></button> </legend>  
                Each rule need no <b>/</b> sumbol, just plain word match.
            </div>
            <div class="col-12 single-rule-container"></div>
            <div class="col-12 d-none save-single-rule-container">
                <button class="btn btn-info save-single-rule" type="button" >Save</button>
            </div>
        </div>
    </div> -->
    
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
                <legend>Existing rules</legend>
            </div>
        </div>
    </div>
    
    <div class="row">
        <div class="col-12">
            <div class="col-12">
            <table class="table table-bordered table-sm table-striped scan_rules-table">
                <thead>
                  <tr>
                    <th>Rule</th>
                    <!-- <th>Excluding</th> -->
                    <th>Group</th>
                    <th>Active</th>
                    <th>
                        <div class="form-check abc-checkbox abc-checkbox-info form-check">
                            <input class="form-check-input check-all" id="selectAllRules" type="checkbox">
                            <label class="form-check-label" for="selectAllRules">All</label>
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
            <form class="form-horizontal" action="{{action('api\SendRulesController@massUpdate')}}" id="actionscan_rulesform">
                <!-- Small button groups (default and split) -->
                <div class="col-12 text-right">
                    <div class="btn-group" id="scan_rulesMassAction">
                        <button class="btn btn-light refresh-list" type="button" > <!-- btn-sm -->
                            Refresh
                        </button>
                        <button class="btn btn-info dropdown-toggle" type="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false"> <!-- btn-sm -->
                            Chose action
                        </button>
                        <div class="dropdown-menu dropdown-menu-right">
                            <button class="dropdown-item" type="button" data-opntion="delete">Delete</button>
                            <button class="dropdown-item" type="button" data-opntion="enable">Enable</button>
                            <button class="dropdown-item" type="button" data-opntion="disable">Disable</button>
                            <!-- <button class="dropdown-item" type="button" data-opntion="set-exclude">Set exlcude</button> -->
                            <!-- <button class="dropdown-item" type="button" data-opntion="set-include">Set include</button> -->
                        </div>
                    </div>
                </div>

                <input type="hidden" name="scan_rules_ids" value="" />
                <input type="hidden" name="action" id="massAction" value="" />
            </form>
        </div>
    </div>

    <div class="d-none add-rule-template">
        <div class="row">
            <div class="form-group">
                <div class="col">
                    <input type="text" class="form-control rule-input" placeholder="match pattern">
                </div>
                <div class="col">
                    <div class="form-check abc-checkbox abc-checkbox-info form-check-inline">
                        <input class="form-check-input exclusive-rule" id="{checkbox_id}" value="option1" type="checkbox" checked>
                        <label class="form-check-label" for="{checkbox_id}">{checkbox_text}</label>
                    </div>
                    <div class="form-check abc-checkbox abc-checkbox-info form-check-inline">
                        <input class="form-check-input enable-rule" id="{checkbox_id}" value="option1" type="checkbox" checked>
                        <label class="form-check-label" for="{checkbox_id}">{checkbox_text}</label>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script type="text/javascript"> var api_url = "{{action('api\SendRulesController@index')}}" </script>
@stop