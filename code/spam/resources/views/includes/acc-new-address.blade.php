<!-- Modal -->
<div class="modal fade" id="newAddressModal" tabindex="-1" role="dialog" aria-labelledby="newAddressModalTitle" aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered" role="document">
        <div class="modal-content">
            <form action="#" data-action="{{action('api\EmailAccountsController@addAddresses', 'email_account_id')}}" name="add_addresses" id="add_addresses_form" data-id="0">
            <div class="modal-header">
                <h5 class="modal-title" id="newAddressModalTitle">Add new address</h5>
                <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                    <span aria-hidden="true">&times;</span>
                </button>
            </div>
            <div class="modal-body">
                <!--  -->
                <div class="form-group">
                    <div class="col-12">
                        <textarea class="form-control" name="new_addresses" id="new_addresses" rows="5"></textarea>
                    </div>
                </div>
                <!-- upload file -->
                <div class="form-group">
                    <label for="file_list">Add from txt file</label>
                    <input class="form-control-file" name="file_list[]" id="file_list" type="file">
                </div>
                <div class="form-group presets">
                    <label for="">Parse presets:</label>
                    <div class="form-check abc-radio abc-radio-info select-format">
                        <input class="form-check-input" id="pr0" value="[email]|[name]" name="status" type="radio">
                        <label for="pr0">[email]|[name]</label>
                    </div>
                    <div class="form-check abc-radio abc-radio-info select-format">
                        <input class="form-check-input" id="pr2" value="[email] [name]" name="status" type="radio">
                        <label for="pr2">[email]&nbsp;[name]</label>
                    </div>
                    <div class="form-check abc-radio abc-radio-info select-format">
                        <input class="form-check-input" id="pr1" value="[email]|[name]" name="status" type="radio">
                        <label for="pr1">[email]&nbsp;|&nbsp;[name]</label>
                    </div>
                    <div class="form-check abc-radio abc-radio-info select-format">
                        <input class="form-check-input" id="pr3" value="[email],[name],[company],[rest]" name="status" type="radio">
                        <label for="pr3">[email],[name],[company],[rest]</label>
                    </div>
                </div>
                <div class="form-group">
                    <label for="">Emails parser rules</label>
                    <input class="form-control" name="parse_rules" id="parse_rules" type="text" required="required">
                </div>

                <div class="form-group">
                    <a href="#" data-toggle="collapse" data-target="#parse_rules_info">Read info</a>
                </div>

                <div class="form-group collapse" id="parse_rules_info">
                    <label for="">
                        Common format: [module]delimiter[module], e.g: [name],[email]
                        <br>Currenctly supported following modules:
                        <ul>
                            <li>[mail] - email</li>
                            <li>[name] - holder's name and surname</li>
                            <li>[company] - company</li>
                            <li>[rest] - all the rest</li>
                        </ul>
                    </label>
                </div>

                @include('includes.filter-groups-selector', ['filters' => $filters])
                
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button>
                <button type="submit" class="btn btn-primary">Save</button>
            </div>
            </form>
        </div>
    </div>
</div>