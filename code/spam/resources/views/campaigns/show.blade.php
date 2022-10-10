@extends('default')
@section('title', 'Edit Campaign')
@section('content')
    <form class="form-horizontal" action="{{action('api\CampaignsController@update', $campaign->id)}}" id="sendmailform">
    <div class="row">
        <div class="col-6">
                <fieldset>

                <input type="hidden" name="campaign_id" value="{{$campaign->id}}">

                <!-- Form Name -->
                <div class="col-md-12">
                <legend>Edit campaign data</legend>
                </div>

                <!-- Input -->
                <div class="form-group">
                    <div class="col-md-12">
                        <label for="name">Campaign name</label>
                        <input class="form-control" id="name" name="name" type="text" required value="{{$campaign->name}}"></input>
                    </div>
                </div>
                
                <div class="form-group custom-headers-container">
                    <div class="col-md-12">
                        <label for="subject">Custom headers</label>
                        <button class="btn btn-success btn-sm add-header" type="button"><i class="fa fa-plus"></i></button>
                    </div>
                    @foreach( $campaign->headers as $header => $value)
                    <div class="col-12">
                        <div class="input-group mb-3">
                            <input type="text" class="form-control" name="headers_names[]" placeholder="Name" aria-label="Header name" aria-describedby="header-end" required value="{{$header}}">
                            <div class="input-group-append">
                                <span class="input-group-text" id="header-end">:</span>
                            </div>
                            <input type="text" class="form-control" name="headers_values[]" placeholder="Value" aria-label="Header value" aria-describedby="header-value-end" required value="{{$value}}">
                            <div class="input-group-append remove-header-icon">
                                <span class="input-group-text" id="header-value-end"><i class="fa fa-times" aria-hidden="true"></i></span>
                            </div>
                        </div>
                    </div>
                    @endforeach
                </div>                

                <!-- Input -->
                <div class="form-group">
                  <div class="col-md-12">
                    <label for="subject">Subject</label>
                    <input class="form-control" id="subject" name="subject" type="text" required value="{{$campaign->subject}}"></input>
                  </div>
                </div>

                <!-- Textarea -->
                <div class="form-group">
                  <div class="col-md-12">
                    <label for="letterbody">Body</label>
                    <textarea class="form-control" id="letterbody" name="body">{{$campaign->body}}</textarea>
                  </div>
                </div>

                <!-- Campaign Status -->
                <div class="form-group">
                    <div class="col-12"><label for="">Campaign status</label></div>
                    <div class="col-md-12">
                        <div class="form-group">
                            <div class="form-check abc-radio abc-radio-info form-check-inline">
                                <input class="form-check-input" id="cmpStatus1" value="{{config('campaign.status.STARTED')}}" name="status" type="radio" {{ $campaign->status == config('campaign.status.STARTED') ? 'checked' : '' }}>
                                <label for="cmpStatus1">Started</label>
                            </div>
                            <div class="form-check abc-radio abc-radio-info form-check-inline">
                                <input class="form-check-input" id="cmpStatus2" value="{{config('campaign.status.PAUSED')}}" name="status" type="radio" {{ $campaign->status == config('campaign.status.PAUSED') ? 'checked' : '' }}>
                                <label class="form-check-label" for="cmpStatus2">Paused</label>
                            </div>
                            <div class="form-check abc-radio abc-radio-info form-check-inline">
                                <input class="form-check-input" id="cmpStatus3" value="{{config('campaign.status.HIBERNATED')}}" name="status" type="radio" {{ $campaign->status == config('campaign.status.HIBERNATED') ? 'checked' : '' }}>
                                <label class="form-check-label" for="cmpStatus3">Hibernated</label>
                            </div>
                            <div class="form-check abc-radio abc-radio-info form-check-inline">
                                <input class="form-check-input" id="cmpStatus4" value="{{config('campaign.status.COMPETED')}}" name="status" type="radio" {{ $campaign->status == config('campaign.status.COMPETED') ? 'checked' : '' }}>
                                <label class="form-check-label" for="cmpStatus4">Completed</label>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Uploads -->
                <div class="form-group">
                  <div class="col-md-12">
                    <div class="form-group">
                        <label for="attachements">Add attachements</label>
                        <input type="file" class="form-control-file" name="attachements[]" id="attachements" multiple="">
                    </div>
                  </div>
                </div>

                <!-- Button -->
                <div class="form-group">
                  <div class="col-md-4">
                    <button id="spamsavebutton" name="spamsavebutton" class="btn btn-info">Update</button>
                  </div>
                </div>

                <input type="hidden" name="headers" value="{{json_encode($campaign->headers)}}">

                </fieldset>
        </div>

        <div class="col-6">
            @include('campaigns.editattachements', ['campaign' => $campaign])
        </div>
            
    </div>
    </form>
    <div class="d-none headers-template">
        <div class="col-12">
            <div class="input-group mb-3">
                <input type="text" class="form-control" name="headers_names[]" placeholder="Name" aria-label="Header name" aria-describedby="header-end" required>
                <div class="input-group-append">
                    <span class="input-group-text" id="header-end">:</span>
                </div>
                <input type="text" class="form-control" name="headers_values[]" placeholder="Value" aria-label="Header value" aria-describedby="header-value-end" required>
                <div class="input-group-append remove-header-icon">
                    <span class="input-group-text" id="header-value-end"><i class="fa fa-times" aria-hidden="true"></i></span>
                </div>
            </div>
        </div>
    </div>
    

    <script type="text/javascript"> var api_url = "{{action('api\CampaignsController@index')}}" </script>
@stop