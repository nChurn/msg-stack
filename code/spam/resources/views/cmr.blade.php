@extends('default')
@section('title', 'Check mail receiver')
@section('content')
    <div class="row">
        <div class="col-12">
            <form class="form-horizontal" action="{{action('api\CheckMailReceiverController@store')}}" id="spamsocksform">
                <fieldset>

                <!-- Form Name -->
                <div class="col-md-12">
                <legend>Edit mail receiver for socks check</legend>
                </div>
                <!-- Input -->
                <div class="form-group">
                  <div class="col-md-4">
                    <div class="input-group">
                      <input id="cmr" name="cmr" class="form-control" placeholder="email@example.com" required="" type="email">
                    </div>
                  </div>
                </div>
                <!-- Button (Double) -->
                <div class="form-group">
                    <!-- <label class="col-md-4 control-label" for="savecmrbutton">Double Button</label> -->
                    <div class="col-md-8">
                        <button id="savecmrbutton" name="savecmrbutton" class="btn btn-success">Save</button>
                        <!-- <button id="clearcmrbutton" name="clearcmrbutton" class="btn btn-danger">Delete</button> -->
                    </div>
                </div>

                </fieldset>
            </form>
        </div>
        
    </div>
    
    
    </div>

    <script type="text/javascript"> var api_url = "{{action('api\CheckMailReceiverController@index')}}" </script>
@stop