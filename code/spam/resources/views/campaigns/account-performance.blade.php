
<div class="row">
<div class="col-4">
    <label for="max_messages">send max messages</label>
    <input id="max_messages" name="max_messages" class="form-control" required="" type="number" value="@if(!is_null($campaign)){{$campaign->max_messages}}@else{{0}}@endif">
</div>
<div class="col-4">
    <label for="per_time">per time interval (seconds)</label>
    <input id="per_time" name="per_time" class="form-control" required="" type="number" value="@if(!is_null($campaign)){{$campaign->per_time}}@else{{300}}@endif">
</div>
</div>