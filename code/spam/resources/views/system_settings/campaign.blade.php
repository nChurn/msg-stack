<div class="row">
	<div class="col-12">
		<form action="{{route('api.system_settings.store', 'campaign')}}" method="POST" class="update-form">
            <div>
                <h4>Campaign settings:</h4>
            </div>
			<!-- Input -->
            <div class="form-group row">
             	<div class="col-md-2">
                    <label for="max_active_campaigns">max active campaigns</label>
                    <input id="max_active_campaigns" name="max_active_campaigns" class="form-control" required="" type="number" value="{{$settings['max_active_campaigns']}}">
                </div>
                <div class="col-md-2">
                    <label for="workers_per_campaign">process per campaign</label>
                    <input id="workers_per_campaign" name="workers_per_campaign" class="form-control" required="" type="number" value="{{$settings['workers_per_campaign']}}">
                </div>
                <div class="col-md-2">
                    <label for="connection_per_proxy">connection per proxy</label>
                    <input id="connection_per_proxy" name="connection_per_proxy" class="form-control" required="" type="number" value="{{$settings['connection_per_proxy']}}">
                </div>
                <div class="col-md-2">
                    <label for="cmp_check_interval">settings check interval (seconds)</label>
                    <input id="cmp_check_interval" name="cmp_check_interval" class="form-control" required="" type="number" value="{{$settings['cmp_check_interval']}}">
                </div>
            </div>

            <div>
                <h5>Automatics behaviour:</h5>
            </div>
            <div class="form-group row">
                <div class="col-md-2">
                    <label for="use_spambases">Spambases</label>
                    <select id="use_spambases" name="use_spambases" class="custom-select">
                        <option value="0">Ignore</option>
                        <option value="1">Use bases instead of addressbook</option>
                        <option value="2">Combine addressbook and bases</option>
                    </select>
                </div>

                <div class="col-md-2">
                    <label for="reply_empty_status">No conversation found</label>
                    <select id="reply_empty_status" name="reply_empty_status" class="custom-select">
                        <option value="0">Autogenerate message</option>
                        <option value="4">Mark as skipped</option>
                        <option value="5">Mark as blacklisted</option>
                    </select>
                </div>

                <div class="col-md-2">
                    <label for="start_from">Start sending at:</label>
                    <input id="start_from" name="start_from" class="form-control" min="0" max="24" step="1" required="" type="number" value="{{$settings['start_from']}}">
                </div>

                <div class="col-md-2">
                    <label for="end_to">Stop sending at:</label>
                    <input id="end_to" name="end_to" class="form-control" min="0" max="24" step="1" required="" type="number" value="{{$settings['end_to']}}">
                </div>
            </div>
            <div class="form-group row">
                <div class="col-12">
                    <b>Attention:</b> 'No conversation found' behaviour applies on spambases as well! Keep that in mind!
                </div>
            </div>

            {{-- <div class="form-group row">
                <div class="col-md-2">
                    <label for="max_messages">send max messages</label>
                    <input id="max_messages" name="max_messages" class="form-control" required="" type="number" value="@if(!empty($settings['max_messages'])){{$settings['max_messages']}}@else{{10000}}@endif">
                </div>
                <div class="col-md-2">
                    <label for="per_time">per time interval (seconds)</label>
                    <input id="per_time" name="per_time" class="form-control" required="" type="number" value="@if(!empty($settings['per_time'])){{$settings['per_time']}}@else{{300}}@endif">
                </div>
            </div> --}}
            <!-- Button (Double) -->
            <div class="form-group row">
                <div class="col-md-8">
                    <button id="savecmpgnbutton" name="savecmpgnbutton" class="btn btn-success">Save</button>
                </div>
            </div>
		</form>
	</div>
</div>
