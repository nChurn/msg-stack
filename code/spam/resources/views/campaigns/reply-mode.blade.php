<!-- Checkbox -->
<div class="form-group">
  <div class="col-md-12">
    <div class="form-check abc-checkbox abc-checkbox-info abc-checkbox-inline form-check-inline">
        @if(!is_null($campaign) && $campaign->reply_mode == 1 )
        <input class="form-check-input" id="reply_mode" type="checkbox" name="reply_mode" value="1" checked="checked" data-checked="1">
        @else
        <input class="form-check-input" id="reply_mode" type="checkbox" name="reply_mode" value="1" data-checked="0">
        @endif
        <label class="form-check-label" for="reply_mode">Reply mode</label>
    </div>
    <div>
      <span class="help-block text-sm"><small>Reply mode applies only adressbook of mail accounts.</small></span>
    </div>
  </div>
</div>

<div class="form-group reply-days d-none">
  <div class="col-12">
    <label for="reply_days">Maildump search days:</label>
    <input class="form-control" id="reply_days" name="reply_days" type="number" min="0" max="365" step="1" required value="@if(!is_null($campaign)){{$campaign->reply_days}}@else{!!"90"!!}@endif"></input>
  </div>
</div>
