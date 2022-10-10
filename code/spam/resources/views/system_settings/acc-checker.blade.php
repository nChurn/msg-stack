<div class="row">
	<div class="col-12">
		<form action="{{route('api.system_settings.store', 'acc_checker')}}" method="POST" class="update-form">
            <div>
                <h4>Email accounts check settings:</h4>
            </div>
			<!-- Input -->
            <div class="form-group row">
                <div class="col-md-2">
                    <label for="number_process">max active processes</label>
                    <input id="number_process" name="number_process" class="form-control" required="" type="number" value="{{$settings['number_process']}}">
                </div>
                <div class="col-md-2">
                    <label for="process_per_proxy">process per proxy</label>
                    <input id="process_per_proxy" name="process_per_proxy" class="form-control" required="" type="number" value="{{$settings['process_per_proxy']}}">
                </div>
                <div class="col-md-2">
                    <label for="threads_per_protocol">threads per protocol</label>
                    <input id="threads_per_protocol" name="threads_per_protocol" class="form-control" required="" type="number" value="{{$settings['threads_per_protocol']}}">
                </div>
                <div class="col-md-2">
                    <label for="min_hours">min hours between check</label>
                    <input id="min_hours" name="min_hours" class="form-control" required="" type="number" value="{{$settings['min_hours']}}">
                </div>
                <div class="col-md-2">
                    <label for="proc_timeout_first">timeout first check</label>
                    <input id="proc_timeout_first" name="proc_timeout_first" class="form-control" required="" type="number" value="{{$settings['proc_timeout_first']}}">
                </div>
                <div class="col-md-2">
                    <label for="proc_timeout_regular">timeout regular check</label>
                    <input id="proc_timeout_regular" name="proc_timeout_regular" class="form-control" required="" type="number" value="{{$settings['proc_timeout_regular']}}">
                </div>
            </div>
            <div class="form-group row">
                <div class="col-12">
                    <b>Attention:</b> max connections to one proxy is: 3 * threads per protocol * process per proxy. Please keep in mind!
                </div>
            </div>
            <!-- Button (Double) -->
            <div class="form-group row">
                <div class="col-md-8">
                    <button id="savecmpgnbutton" name="savecmpgnbutton" class="btn btn-success">Save</button>
                </div>
            </div>
		</form>
	</div>
</div>
