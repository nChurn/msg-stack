<div class="row">
	<div class="col-12">
		<form action="{{route('api.system_settings.store', 'mail_grabber')}}" method="POST" class="update-form">
            <div>
                <h4>Mail grabber settings:</h4>
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
                    <label for="partial">save every xx grabbed mails</label>
                    <input id="partial" name="partial" class="form-control" required="" type="number" value="{{$settings['partial']}}">
                </div>
                <div class="col-md-2">
                    <label for="max_mail_days_old">get whole body for letters younger than days</label>
                    <input id="max_mail_days_old" name="max_mail_days_old" class="form-control" required="" type="number" value="{{$settings['max_mail_days_old']}}">
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