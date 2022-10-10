@extends('default')
@section('title', 'System settings')
@section('content')
    <div class="row">
        <div class="col-12">
            <ul class="nav nav-tabs mb-3" id="myTab" role="tablist">
                <li class="nav-item">
                    <a class="nav-link active" id="campaign-tab" data-toggle="tab" href="#campaign" role="tab" aria-controls="campaign" aria-selected="true">campaign</a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" id="socks-tab" data-toggle="tab" href="#socks" role="tab" aria-controls="socks" aria-selected="false">socks</a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" id="grabber-tab" data-toggle="tab" href="#grabber" role="tab" aria-controls="grabber" aria-selected="false">grabber</a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" id="acc_checker-tab" data-toggle="tab" href="#acc_checker" role="tab" aria-controls="acc_checker" aria-selected="false">accounts</a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" id="shells-tab" data-toggle="tab" href="#shells" role="tab" aria-controls="shells" aria-selected="false">shells</a>
                </li>
            </ul>
            <div class="tab-content" id="myTabContent">
                <div class="tab-pane fade show active" id="campaign" role="tabpanel" aria-labelledby="campaign-tab">
                    @include('system_settings.campaign', ['settings' => $settings['campaign']])
                </div>
                <div class="tab-pane fade" id="socks" role="tabpanel" aria-labelledby="socks-tab">
                    @include('system_settings.socks-checker', ['settings' => $settings['socks_checker']])

                </div>
                <div class="tab-pane fade" id="grabber" role="tabpanel" aria-labelledby="grabber-tab">
                    @include('system_settings.mail-grabber', ['settings' => $settings['mail_grabber']])
                </div>
                <div class="tab-pane fade" id="acc_checker" role="tabpanel" aria-labelledby="acc_checker-tab">
                    @include('system_settings.acc-checker', ['settings' => $settings['acc_checker']])
                </div>
            </div>
        </div>
    </div>

    <script type="text/javascript"> var api_url = "{{action('api\CheckMailReceiverController@index')}}" </script>
@stop
