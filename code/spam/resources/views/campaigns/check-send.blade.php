<div class="form-group">
	<div class="col-12">
	    <label for="check_send">Send every n-th message to check mail address:</label>
	</div>
	<div class="col-4">
		<input id="check_send" name="check_send" class="form-control" required="" type="number" value="@if(!is_null($campaign)){{$campaign->check_send}}@else{{0}}@endif">
	    <span class="help-block text-sm"><small>Send every n-th letter of campaign to receiver mail address. Kepp 0 for turning feature off.</small></span>
	</div>
</div>
