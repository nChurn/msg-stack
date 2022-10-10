<legend>Select cccounts:</legend>
<table class="table table-bordered table-sm table-striped accounts-table">
    <thead>
        <tr>
            <th>Id</th>
            <th>Login</th>
            <th>Host</th>
            <th>AddressBook</th>
            <th>
                <div class="cool-checkbox">
                    <div class="form-check abc-checkbox abc-checkbox-info abc-checkbox-inline">
                        <input class="form-check-input" id="selectAllAccounts" type="checkbox" name="selected_accs_toggler" value="none">
                        <label class="form-check-label" for="selectAllAccounts"></label>
                    </div>
                </div>
            </th>
        </tr>
    </thead>
    <tbody>
        @if($accounts->count() > 0)
            @foreach ($accounts as $acc)
            <tr class="{{$acc->html_class}}">
                <td>{{$acc->id}}</td>
                <td>{{$acc->common_login}}</td>
                <td>{{$acc->common_host}}</td>
                <td>{{$acc->address_book_count}}</td>
                <td>
                    <div class="cool-checkbox">
                        <div class="form-check abc-checkbox abc-checkbox-info abc-checkbox-inline">
                            <input class="form-check-input" id="check_acc_{{$acc->id}}" type="checkbox" name="selected_accs[]" value="{{$acc->id}}" 
                            @if($acc->enabled == 0)
                            disabled="disabled"
                            @endif
                            >
                            <label class="form-check-label" for="check_acc_{{$acc->id}}"></label>
                        </div>
                    </div>
                </td>
            </tr>
            @endforeach
        @else
            <tr><td colspan="10" align="center">No accounts in system</td></tr>
        @endif
    </tbody>
</table>