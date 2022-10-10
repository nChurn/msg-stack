@extends('default')
@section('title', 'Campaigns')
@section('content')
    <div class="row">
        <div class="col-6">
            <form class="form-horizontal" action="{{action('api\CampaignsController@store')}}" id="sendmailform">
                <fieldset>

                <!-- <input type="hidden" name="selected_accs[]" value=""> -->

                <!-- Form Name -->
                <div class="col-md-12">
                <legend>Write down message</legend>
                </div>
                
                <div class="form-group custom-headers-container">
                    <div class="col-md-12">
                        <label for="subject">Custom headers</label>
                        <button class="btn btn-outline-success btn-sm add-header" type="button"><i class="fa fa-plus"></i></button>
                    </div>
                </div>                

                <!-- Input -->
                <div class="form-group">
                  <div class="col-md-12">
                    <label for="subject">Subject</label>
                    <input class="form-control" id="subject" name="subject" type="text" required></input>
                  </div>
                </div>

                <!-- Textarea -->
                <div class="form-group">
                  <div class="col-md-12">
                    <label for="letterbody">Body</label>
                    <textarea class="form-control" id="letterbody" name="body"></textarea>
                  </div>
                </div>

                <!-- Uploads -->
                <div class="form-group">
                  <div class="col-md-12">
                    <div class="form-group">
                        <label for="attachements">Attachements</label>
                        <input type="file" class="form-control-file" name="attachements[]" id="attachements" multiple="">
                    </div>
                  </div>
                </div>

                <!-- TODO: schedule start -->
                <!-- <div class="form-group">
                    <div class="col-md-12">
                        <label for="attachements">Schedule send (leave empty if ASAP)<br><b>work in progress, feature not implemented yet</b></label>
                        <div class="input-group mb-3">
                            <input type="text" class="form-control" placeholder="datetime" aria-label="Schedule datetime" aria-describedby="calendar">
                            <div class="input-group-append">
                                <span class="input-group-text fa fa-calendar" id="calendar"></span>
                            </div>
                        </div>
                    </div>
                </div> -->

                <!-- Button -->
                <div class="form-group">
                  <div class="col-md-4">
                    <button id="spamsavebutton" name="spamsavebutton" class="btn btn-info">Create</button>
                  </div>
                </div>

                <input type="hidden" name="headers" value="">

                </fieldset>
            </form>
        </div>
    </div>

    <div class="d-none headers-template">
      <div class="col-12">
          <div class="row">
              <div class="col-6">
                <label>Header</label>
                <input class="form-control" name="headers_names[]" type="text"></input>
            </div>
            <div class="col-6">
                <label>Value</label>
                <input class="form-control" name="headers_values[]" type="text"></input>
            </div>
          </div>
      </div>
    </div>
    

    <script type="text/javascript"> var api_url = "{{action('api\CampaignsController@index')}}" </script>
@stop