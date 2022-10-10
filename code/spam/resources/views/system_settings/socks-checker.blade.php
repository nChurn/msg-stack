<div class="row">
	<div class="col-12">
		<form action="{{route('api.system_settings.store', 'socks_checker')}}" method="POST" class="update-form">
            <div>
                <h4>Socks checked settings:</h4>
            </div>
			<!-- Input -->
            <div class="form-group row">
                <div class="col-md-2">
                    <label for="number_process">max active processes</label>
                    <input id="number_process" name="number_process" class="form-control" required="" type="number" value="{{$settings['number_process']}}">
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