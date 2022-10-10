<!-- Campaign Status -->
<div class="form-group">
    <label for="">Campaign status</label>
    <div class="form-group">
        <div class="form-check abc-radio abc-radio-info form-check-inline">
            <input class="form-check-input" id="cmpStatus1" value="{{config('campaign.status.STARTED')}}" name="status" type="radio" {{ $campaign->status == config('campaign.status.STARTED') ? 'checked' : '' }}>
            <label class="form-check-label" for="cmpStatus1">Started</label>
        </div>
        <div class="form-check abc-radio abc-radio-info form-check-inline">
            <input class="form-check-input" id="cmpStatus2" value="{{config('campaign.status.PAUSED')}}" name="status" type="radio" {{ $campaign->status == config('campaign.status.PAUSED') ? 'checked' : '' }}>
            <label class="form-check-label" for="cmpStatus2">Paused</label>
        </div>
        <div class="form-check abc-radio abc-radio-info form-check-inline">
            <input class="form-check-input" id="cmpStatus4" value="{{config('campaign.status.COMPETED')}}" name="status" type="radio" {{ $campaign->status == config('campaign.status.COMPETED') ? 'checked' : '' }}>
            <label class="form-check-label" for="cmpStatus4">Completed</label>
        </div>
    </div>
</div>