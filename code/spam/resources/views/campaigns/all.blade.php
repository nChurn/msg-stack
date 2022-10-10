@extends('default')
@section('title', 'Campaigns')
@section('content')
    <div class="row">
        <div class="col-12">
            <h2>
                Campaign list
            </h2>
            <a href="{{action('CampaignsController@new')}}">New campaign</a>
        </div>
    </div>

    <div class="row">
    	<div class="col-12">
    		<table class="table table-bordered table-sm table-striped campaigns-table">
    			<thead>
    				<tr>
    					<th>Id</th>
    					<th>Name</th>
                        <th>Status</th>
                        <th>Workers</th>
    					<th>Attachements</th>
    					<th>Total</th>
                        <th>Await</th>
                        <th>Processing</th>
    					<th>Success</th>
                        <th>Failed</th>
                        <th>Skipped</th>
    					<th>Blacklisted</th>
                        <th>Created</th>
    					<th>Scheduled</th>
    					<th>Actions</th>
    				</tr>
    			</thead>
    			<tbody>
    				@foreach($campaigns as $camp)
    				<tr>
    					<td>{{$camp->id}}</td>
    					<td>{{$camp->name}}</td>
                        <td>
                            @if ($camp->status == config('campaign.status.CREATED'))
                                Created
                            @elseif ($camp->status == config('campaign.status.STARTED'))
                                Started
                            @elseif ($camp->status == config('campaign.status.PAUSED'))
                                Paused
                            @elseif ($camp->status == config('campaign.status.HIBERNATED'))
                                Hibernated
                            @elseif ($camp->status == config('campaign.status.COMPETED'))
                                Completed
                            @endif
                        </td>
                        <td>{{$camp->workers}}</td>
    					<td>{{$camp->attachements_count}}</td>
    					<td>{{$camp->all_amount}}</td>
                        <td>{{$camp->await_amount}}</td>
                        <td>{{$camp->processing_amount}}</td>
    					<td>{{$camp->success_amount}}</td>
                        <td>{{$camp->fail_amount}}</td>
                        <td>{{$camp->skip_amount}}</td>
    					<td>{{$camp->blacklist_amount}}</td>
                        <td class="small">{{$camp->created_at}}</td>
    					<td class="small">
                            @if( empty($camp->scheduled) )
                            No
                            @else
                            {{$camp->scheduled}}
                            @endif
                        </td>
    					<td>
                            @if( $camp->status == config('campaign.status.PAUSED') )
                            <button class="btn btn-info btn-sm" title="Start" data-action="{{action('CampaignsController@updateStatus', ['cid' => $camp->id, 'sid' => config('campaign.status.STARTED')])}}"><i class="fa fa-play-circle" aria-hidden="true"></i></button>
							<button class="btn btn-info btn-sm" title="Edit" data-action="{{action('CampaignsController@show', ['cid' => $camp->id])}}"><i class="fa fa-pencil-square-o" aria-hidden="true"></i></button>
                            @elseif( $camp->status != config('campaign.status.COMPETED') )
                            <button class="btn btn-info btn-sm" title="Pause" data-action="{{action('CampaignsController@updateStatus', ['cid' => $camp->id, 'sid' => config('campaign.status.PAUSED')])}}"><i class="fa fa-pause-circle" aria-hidden="true"></i></button>
                            @elseif( $camp->status == config('campaign.status.COMPETED') )
                            <button class="btn btn-info btn-sm" title="Start" data-action="{{action('CampaignsController@updateStatus', ['cid' => $camp->id, 'sid' => config('campaign.status.STARTED')])}}"><i class="fa fa-play-circle" aria-hidden="true"></i></button>
                            @endif
                            <button class="btn btn-info btn-sm" title="Details" data-action="{{action('CampaignsController@details', ['cid' => $camp->id])}}"><i class="fa fa-pie-chart" aria-hidden="true"></i></button>
                            <button class="btn btn-info btn-sm" title="Delete" data-action="{{action('CampaignsController@remove', ['cid' => $camp->id])}}"><i class="fa fa-trash" aria-hidden="true"></i></button>
    					</td>
    				</tr>
    				@endforeach
    			</tbody>
    		</table>
    	</div>
    </div>


    <script type="text/javascript"> var api_url = "{{action('api\CampaignsController@index')}}" </script>
@stop
