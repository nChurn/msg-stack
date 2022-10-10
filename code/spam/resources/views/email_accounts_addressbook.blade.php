@extends('default')
@section('title', 'Account ' . $account->common_login . ' addressbook')
@section('content')
    <!-- <div class="row">
        <ul>
            @foreach( $filters as $record )
            <li>{{$record}}</li>
            @endforeach
        </ul>
    </div> -->
    <div class="row">
        <div class="col-12">
            <legend>Account {{$account->common_login}} addressbook: has {{$account->address_book_count}} records</legend>
            <table class="table table-bordered table-sm table-striped mail_acc_addressbook-table">
                <thead>
                    <tr>
                        <th>Id</th>
                        <th>Email</th>
                        <th>Holder</th>
                        <th>Company</th>
                        <th>Rest</th>
                        <th>
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
                    @foreach($addressbook as $record)

                    @if(is_null($record->send_rule_id))
                    <tr class="" data-id="{{$record->id}}">
                    @else
                    <tr class="in-send-rules" data-id="{{$record->id}}">
                    @endif
                        <td>{{$record->id}}</td>
                        <td>{{$record->address}}</td>
                        <td class="holder-name-text holder-editable-field">
                            <span>{{--<i class="fa fa-pencil" aria-hidden="true"></i>--}}{{$record->name}}</span>
                            <input type="text" value="{{$record->name}}" class="form-control input-sm d-none" data-field="name" />
                        </td>
                        <td class="holder-company-text holder-editable-field">
                            <span>{{--<i class="fa fa-pencil" aria-hidden="true"></i>--}}{{$record->company}}</span>
                            <input type="text" value="{{$record->company}}" class="form-control input-sm d-none" data-field="company" />
                        </td>
                        <td class="holder-rest-text holder-editable-field">
                            <span>{{--<i class="fa fa-pencil" aria-hidden="true"></i>--}}{{$record->rest}}</span>
                            <input type="text" value="{{$record->rest}}" class="form-control input-sm d-none" data-field="rest" />
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
                {{ $addressbook->links() }}
            </div>
        </div>
        <div class="col-12">
            <form class="form-horizontal" action="{{action('EmailAccountsController@massUpdate')}}" id="actionabform">
                <!-- Small button groups (default and split) -->
                <div class="col-12 text-right">
                    <div class="btn-group" id="adMassAction">
                        <button class="btn btn-info dropdown-toggle" type="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false"> <!-- btn-sm -->
                            Chose action
                        </button>
                        <div class="dropdown-menu dropdown-menu-right">
                            <button class="dropdown-item" type="button" data-option="address_rule">Mark address as rule</button>
                            <button class="dropdown-item" type="button" data-option="host_rule">Mark host as rule</button>
                            <button class="dropdown-item" type="button" data-option="login_rule">Mark login as rule</button>
                            <button class="dropdown-item" type="button" data-option="remove_rule">Unmark as rule</button>
                            <button class="dropdown-item" type="button" data-option="delete">Delete</button>
                        </div>
                    </div>
                </div>

                <input type="hidden" name="socks_ids" value="" />
                <input type="hidden" name="action" id="massAction" value="" />
            </form>
        </div>
    </div>
    
    @php $variable = "pizdec" @endphp    
    @include('includes.acc-new-address', ['filters' => $filters])

    <script type="text/javascript"> var api_url = "{{action('api\EmailAccountsController@updateHolderField', 'record_id')}}" </script>
@stop