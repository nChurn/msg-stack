{{-- View accepts params:
	$fields => array if field names 
	$accounts => array of accounts to show
--}}
<div id="mail_account_filters" class="collapse">
    <form action="#" id="mail_account_filters_form">
    <div class="row">
        <div class="form-group col-6">
            <label for="mail_account_name">Account name or host:</label>
            <input id="mail_account_name" name="mail_account_name" class="form-control" placeholder="abc@def.xyz" required="" type="text">
        </div>
    </div>

    <div class="row">
        <div class="col-12">
            <span>Choose email account groups:</span>
        </div>
        @foreach($acc_groups as $key => $value)
        <div class="col-2">
            <div class="form-check abc-checkbox abc-checkbox-info form-check-inline">
                <input class="form-check-input" name="selected_mail_account_groups[]" id="mail_account_group{{$value}}" type="checkbox" data-checked value="{{$value}}">
                <label class="form-check-label" for="mail_account_group{{$value}}">{{$value}}</label>
            </div>
        </div>
        @endforeach
    </div>

    <div class="row">
        <div class="col-12">
            <button type="submit" class="btn btn-primary btn-sm">Apply</button>
        </div>
    </div>
    <hr>
    </form>
</div>

<table class="table-bordered table-sm table-striped mail_accs-table">
	<thead>
		<tr>
			@if(empty($fields))
			<th>Id</th>
			<th>Login</th>
            <th>Host</th>
            <th>Mails</th>
            <th>Group</th>
            @else
            @foreach($fields as $key => $value)
            <th>{{$value}}</th>
            @endforeach
            @endif
            <th>
            	<div class="cool-checkbox">
                    <div class="form-check abc-checkbox abc-checkbox-info form-check-inline">
                        <input class="form-check-input" id="selectAllAccounts" type="checkbox" data-checked>
                        <label class="form-check-label" for="selectAllAccounts">&nbsp;</label>
                    </div>
                </div>
            </th>
		</tr>
	</thead>
    <tbody>
        @if( empty($accounts) )
        <tr>
            <td colspan="20" align="center">Loading, please wait...</td>
        </tr>
        @else
        @foreach( $accounts as $record )
        <tr>
            <td>{{$record->id}}</td>
            <td>{{$record->common_login}}</td>
            <td>{{$record->smtp_host}}</td>
            <td>{{$record->address_book_count}}</td>
            <td>{{$record->group}}</td>
            <td>
                <div class="cool-checkbox">
                    <div class="form-check abc-checkbox abc-checkbox-info form-check-inline">
                        <input class="form-check-input" name="selected_accs[]" id="mail_account_{{$record->id}}" type="checkbox" data-checked value="{{$record->id}}">
                        <label class="form-check-label" for="mail_account_{{$record->id}}">&nbsp;</label>
                    </div>
                </div>
            </td>
        </tr>
        @endforeach
        @endif
    </tbody>
</table>