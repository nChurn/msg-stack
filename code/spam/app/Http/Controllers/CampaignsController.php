<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\MailAccount;
use App\Models\Campaign;
use App\Models\ScanRules;
use App\Models\MailAccountAddressBook;
use App\Models\CampaignAddressbook;
use App\Models\MailDump;
use Illuminate\Support\Facades\Redis;

class CampaignsController extends Controller
{
    /**
     * Display a listing of the resource.
     *
     * @return Response
     */
    public function index()
    {
    	// $accounts = MailAccount::withCount(['mailContacts', 'mails'])->get();//(['mailContacts', 'mails'])->get();
        $campaigns = Campaign::withCount([
                'attachements',
                // 'addressBook',
                // 'addressBookSuccess',
                // 'addressBookFail',
                // 'addressBookSkip',
                // 'addressBookBlacklist',
                // 'addressBookAwait',
                // 'addressBookProcessing'
            ])
            ->where('status', '!=', config('campaign.status.REMOVED'))
            ->get();
        // return $campaigns;
        $filter_group = ScanRules::select('group')->distinct()->get();

    	return view('campaigns.all', ['campaigns' => $campaigns]);
    }

    public function new()
    {
        $filter_group = ScanRules::select('group')->distinct()->get();
        $accounts = MailAccount::withCount(['addressBook'])->where('test_only', 0)->get();//(['mailContacts', 'mails'])->get();

        $macros_data = $this->getMacrosData();
        $mail_dump = $this->getMailDump();

        $macro_data = Redis::hgetall('macro:data');
        $ret = [];
        foreach ($macro_data as $key => $value) {
            $ret[] = ['name'=>$key, 'content'=>$value];
        }

        return view('campaigns.new', ['accounts' => $accounts, 'campaign'=>null, 'filters' => $filter_group, "macros_data" => $macros_data, "mail_dump" => $mail_dump, "macros_templates" => $ret]);
        // return $accounts;
    }

    public function show(Request $request, $id)
    {
        // return $id;
        $filter_group = ScanRules::select('group')->distinct()->get();
        // $campaign = Campaign::findOrFail($id)->get();
        $campaign = Campaign::
                    with(['attachements'])
                    ->withCount(['addressBook', 'addressBookProcessing', 'addressBookSuccess', 'addressBookFail', 'addressBookSkip', 'attachements'])
                    ->where('id', $id)
                    // ->get()
                    ->first()
                    ->setAppends(['spam_base_ids', 'mail_account_ids']);

        // \Log::debug("Show campaign:" . json_encode($campaign) );

        $macros_data = $this->getMacrosData();

        // $mail_dump = MailDump::where('body', '!=', '')->orderBy('mail_date', 'desc')->first();
        $mail_dump = $this->getMailDump();


        $selected_atts = $campaign->attachements()->get()->map(function($item){
            return $item->id;
        })->toArray();
        \Log::debug("selected_atts:" .json_encode($selected_atts) );

        $macro_data = Redis::hgetall('macro:data');
        $ret = [];
        foreach ($macro_data as $key => $value) {
            $ret[] = ['name'=>$key, 'content'=>$value];
        }

        return view('campaigns.new', ['accounts' => collect([]), 'campaign' => $campaign, 'filters' => $filter_group, "macros_data" => $macros_data, "mail_dump" => $mail_dump, "attachments" => $selected_atts, "macros_templates" => $ret]);
        // return $campaign;
    }

    public function details(Request $request, $id)
    {
        $filter_group = ScanRules::select('group')->distinct()->get();
        // return $id;
        // $campaign = Campaign::findOrFail($id)->get();
        $campaign = Campaign::
                    // with(['attachements', 'addressBook', 'addressBook.account'])
                    // with(['attachements', 'addressBook.account'])
                    // with(['attachements'])
                    withCount(['addressBook', 'addressBookProcessing', 'addressBookSuccess', 'addressBookFail', 'addressBookSkip', 'attachements'])
                    ->where('id', $id)
                    ->first();

        $macros_data = $this->getMacrosData();

        $ids = $campaign->addressBook()->select('mail_account_id')->distinct()->get()->map(function($item){return $item['mail_account_id'];})->toArray();

        $accounts = MailAccount::whereIn('id', $ids)->get();

        $macro_data = Redis::hgetall('macro:data');
        $ret = [];
        foreach ($macro_data as $key => $value) {
            $ret[] = ['name'=>$key, 'content'=>$value];
        }

        // generate statistics
        $data_stat = [];
        // foreach ($accounts as $acc) {
        //     $data_stat[] = [
        //         "mail_account_id" => $acc->id,
        //         "login" => $acc->common_login,
        //         "total" => CampaignAddressbook::where('mail_account_id', $acc->id)->where('campaign_id', $campaign->id )->count(),
        //         "await" => CampaignAddressbook::where('mail_account_id', $acc->id)->where('campaign_id', $campaign->id )->where('record_status', config('campaign.record_status.await'))->count(),
        //         "processing" => CampaignAddressbook::where('mail_account_id', $acc->id)->where('campaign_id', $campaign->id )->where('record_status', config('campaign.record_status.processing'))->count(),
        //         "success" => CampaignAddressbook::where('mail_account_id', $acc->id)->where('campaign_id', $campaign->id )->where('record_status', config('campaign.record_status.success'))->count(),
        //         "fail" => CampaignAddressbook::where('mail_account_id', $acc->id)->where('campaign_id', $campaign->id )->where('record_status', config('campaign.record_status.fail'))->count(),
        //         "skip" => CampaignAddressbook::where('mail_account_id', $acc->id)->where('campaign_id', $campaign->id )->where('record_status', config('campaign.record_status.skip'))->count(),
        //         "blacklist" => CampaignAddressbook::where('mail_account_id', $acc->id)->where('campaign_id', $campaign->id )->where('record_status', config('campaign.record_status.blacklist'))->count(),
        //     ];
        // }

        // return $data_stat;

        // return $campaign->addressBook()->account()->get();

        return view('campaigns.details', ['accounts' => collect([]), 'campaign' => $campaign, 'filters' => $filter_group, "macros_data" => $macros_data, "data_stat" => $data_stat, "macros_templates" => $ret]);
        // return view('campaigns.new', ['accounts' => collect([]), 'campaign' => $campaign, 'filters' => $filter_group, "macros_data" => $macros_data]);
        // return $campaign;
    }

    public function updateStatus(Request $request, $cid, $sid)
    {
        // Campaign::find($cid)->update(['status' => $sid, 'scheduled' => null]);
        Campaign::find($cid)->update(['status' => $sid, 'scheduled' => null]);
        return redirect()->action('CampaignsController@index');
    }

    public function remove(Request $request, $cid)
    {
        // i have some shit incorrect foreign key relations i guess, kill mails first
        Campaign::find($cid)->addressBook()->delete();
        // kill self campaign
        Campaign::find($cid)->delete();

        // kill every fucking key in redis, related to this campaign
        $all_keys = Redis::command("scan", ["0", "MATCH", "campaign:{$cid}:*", "COUNT", "99999999"]);
        foreach ($all_keys as $key => $value) {
            if( is_array($value) && !empty($value) ){
                Redis::del($value);
            }

        }
        return redirect()->action('CampaignsController@index');
    }

    private function getMacrosData($dummy=false)
    {

        if(!$dummy){
            // try to get from redis
            $macros_data = Redis::hgetall('macros:replace:test:data');
            // put data to redis if not exists
            if(empty($macros_data))
            {
                \Log::debug("No test data for macro replace");
                $test_name = MailAccount::with(['addressBook' => function($query){
                    $query->where('name','!=', '');
                }])->where('test_only', 0)->where('name','!=', '')->first();

                $macros_data = [
                    "from_name" => $test_name->name,
                    "to_name" => empty($test_name->addressBook()->first()) ? 'Holders name' : $test_name->addressBook()->first()->name,
                    "from_email" => $test_name->smtp_login,
                    "to_email" => empty($test_name->addressBook()->first()) ? 'somewhere@nowhere.com' : $test_name->addressBook()->first()->address,
                ];

                Redis::hmset('macros:replace:test:data', $macros_data);
            }
        }else{
            $macros_data = [
                "from_name" => "Mr. Jon Doe",
                "to_name" => "Mr Jack Reacher",
                "from_email" => "jon@doe.com",
                "to_email" => "jack@reacher.com",
            ];
        }


        // $test_name = MailAccount::with(['addressBook' => function($query){
        //     $query->where('name','!=', '');
        // }])->where('test_only', 0)->where('name','!=', '')->first();

        // if(!empty($test_name) && !$dummy)
        //     $macros_data = [
        //         "from_name" => $test_name->name,
        //         "to_name" => empty($test_name->addressBook()->first()) ? 'Holders name' : $test_name->addressBook()->first()->name,
        //         "from_email" => $test_name->smtp_login,
        //         "to_email" => empty($test_name->addressBook()->first()) ? 'somewhere@nowhere.com' : $test_name->addressBook()->first()->address,
        //     ];
        // else
        //     $macros_data = [
        //         "from_name" => "Mr. Jon Doe",
        //         "to_name" => "Mr Jack Reacher",
        //         "from_email" => "jon@doe.com",
        //         "to_email" => "jack@reacher.com",
        //     ];

        return $macros_data;
    }

    private function getMailDump()
    {
        $mail_dump = Redis::hgetall('macro:mail:dump');
        if( empty($mail_dump) ){
            $mail_dump = MailDump::where('body', '!=', '')->orderBy('mail_date', 'desc')->first();

            if(!empty($mail_dump)){
                // convert to json
                $mail_dump_json = json_encode($mail_dump);
                // convert to assoc arrayt
                $redis_data = json_decode($mail_dump_json, true);
                // save to redis
                Redis::hmset('macro:mail:dump', $redis_data);
            }
        }else{
            $mail_dump = new MailDump($mail_dump);
        }

        return $mail_dump;
    }

    public function smtpStop()
    {
        Redis::set('smtp_sender:status', 'stop_all');
        Redis::set('smtp_sender:started', 0);
        Campaign::where( 'name', 'universalio' )->update(['status' => 2, 'scheduled' => null]);
        return redirect()->back();
    }

    public function smtpStart()
    {
        Redis::set('smtp_sender:status', 'start_all');
        Redis::set('smtp_sender:started', 1);
        return redirect()->back();
    }
}
