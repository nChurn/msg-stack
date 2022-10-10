<!-- Checkbox -->
<div class="form-group">
  <div class="col-md-12">
    <div class="form-check abc-checkbox abc-checkbox-info abc-checkbox-inline form-check-inline">
        @if(!is_null($campaign) && $campaign->ignore_selfhost == 1 )
        <input class="form-check-input" id="ignore_selfhost" type="checkbox" name="ignore_selfhost" value="1" checked="checked" data-checked="1">
        @else
        <input class="form-check-input" id="ignore_selfhost" type="checkbox" name="ignore_selfhost" value="1" data-checked="0">
        @endif
        <label class="form-check-label" for="ignore_selfhost">Skip same host emails</label>
    </div>
  </div>
</div>