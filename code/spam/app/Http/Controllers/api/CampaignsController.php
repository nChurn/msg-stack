<?php

namespace App\Http\Controllers\api;

use Illuminate\Http\Request;
use App\Http\Controllers\Controller;

use App\Models\Campaign;
use App\Models\Attachement;
use App\Models\CampaignAddressbook;
use App\Models\MailAccount;
use App\Models\ScanRules;
use App\Models\SpamBase;
use App\Models\SpamBaseRecord;
use lastguest\Murmur;
use Illuminate\Support\Facades\Redis;

class CampaignsController extends Controller
{
    protected $request;

    public function __construct(Request $request) {
        $this->request = $request;
    }

    /**
     * Display a listing of the resource.
     *
     * @return \Illuminate\Http\Response
     */
    public function index()
    {
        //
    }

    /**
     * Show the form for creating a new resource.
     *
     * @return \Illuminate\Http\Response
     */
    public function create()
    {
        //
    }

    /**
     * Store a newly created resource in storage.
     *
     * @param  \Illuminate\Http\Request  $request
     * @return \Illuminate\Http\Response
     */
    public function store()
    {
        $request = $this->request;

        /*
        $validatedData = $request->validate([
            // 'subject' => 'max:255',
            // 'body' => 'required',
            // 'attachements' => 'required'
        ]);
        */

        // $total_files = count($request->attachements);

        $mail = new Campaign;
        $mail->name = $request->input('name');
        $mail->subject = $request->input('subject');
        $mail->body = empty($request->input('body')) ? '' : $request->input('body');
        $mail->headers = empty($request->input('headers'))  ? '' : $request->input('headers');
        // mark as paused untill all data is created
        $mail->status = config('campaign.status.PAUSED');
        $mail->is_html = empty($request->input('is_html')) ? 0 : 1;
        $mail->reply_mode = empty($request->input('reply_mode')) ? 0 : 1;
        $mail->reply_days = (int)$request->input('reply_days');
        $mail->ignore_selfhost = empty($request->input('ignore_selfhost')) ? 0 : 1;
        $mail->attach_name = empty($request->input('attach_name')) ? '' : $request->input('attach_name');
        $mail->account_name = empty($request->input('account_name')) ? '' : $request->input('account_name');

        $mail->max_messages = (int)$request->input('max_messages');
        $mail->per_time = (int)$request->input('per_time');

        $mail->fail_behaviour = (int)$request->input('fail_behaviour');
        $mail->ignore_accounts = (int)$request->input('ignore_accounts');
        $mail->check_send = (int)$request->input('check_send');
        $mail->has_attaches = empty($request->input('has_attaches')) ? 0 : 1;


        $filters = $request->input('selected_filters');
        if(is_null($filters))
            $filters = [];
        // \Log::debug("CampaignController: New campaign filters:");
        // \Log::debug($filters);

        $schedule = $request->input('schedule');
        if (!empty($schedule))
        {
            // string of format: yyyy.mm.dd.hh.MM.ss
            $spl = explode(".", $schedule);
            $scdt = \Carbon\Carbon::create((int)$spl[0], (int)$spl[1], (int)$spl[2], (int)$spl[3], (int)$spl[4], (int)$spl[5], 'UTC');
            $now = \Carbon\Carbon::now();
            // if now is more, than ignore schedule
            if( $scdt->greaterThan($now) ){
                $mail->scheduled = $scdt;
                $mail->started_at = $scdt;
            }
        }

        $mail->filters = $filters;
        $mail->save();

        // $campaign_id = $mail->id;

        // process campaign attachments new version
        $attachement_ids = $request->input('selected_atts');
        $mail->attachements()->sync($attachement_ids);

        $acc_ids =  $request->input('selected_accs');
        $mail->accounts()->sync($acc_ids);

        \Log::debug("CampaignController: New campaign created with id:" . $mail->id);

        // TODO: add redis integration
        // process all records
        $this->campaignProcessRecords($mail, $request);

        // now all data is saved, fet proper status flag
        $mail->status = empty($request->input('status')) ? config('campaign.status.PAUSED') : config('campaign.status.STARTED');
        $mail->save();

        return response()->json(['success' => true, 'message' => 'Campaign is created, will be processes ASAP.']);
    }

    private function campaignProcessRecords($mail, $request){
        // if set, only text file will be processed
        // $ignore_account_contacts = empty($request->input('ignore_accounts')) ? 0 : 1;
        $ignore_account_contacts = $mail->ignore_accounts;

        $campaign_id = $mail->id;
        // generate excluding regexp
        \Log::debug("CampaignController: genarate excluding regex");
        // TODO: change generation to append names hash map
        $rules = ScanRules::whereIn('group', $mail->filters)->select(['rule', 'group'])->where('enabled', 1)->distinct()->get()->map(function($item){
            $r_name = sprintf('%u',crc32($item['group'] . $item['rule'] ));
            $r_name = "r_{$r_name}";
            return [
                "regex" => "(?P<{$r_name}>".$item['rule'].")",
                "rule" => $item['rule'],
                "group" => $item['group'],
                "r_name" => $r_name
            ];
        });
        $rules_count = $rules->count();
        // skip regex check by making it never accomplished
        if( $rules->count() == 0 ){
            $rule_regex = "/^\!skip\!/";
        }else{
            $rule_regex = "/". implode("|", $rules->map(function($item){ return $item['regex']; })->toArray()) ."/i";
            // \Log::debug("Generated regex:{$rule_regex}");
        }

        \Log::debug("CampaignController: process campaign mail accounts:");
        // fill table with campaign emails
        // $accounts = $request->input('selected_accs');
        $acc_ids =  $request->input('selected_accs');
        // \Log::debug($acc_ids);
        if(!empty($acc_ids) && $ignore_account_contacts != 1){
            $accounts = MailAccount::whereIn('id', $acc_ids)->get();

            $now = \Carbon\Carbon::now();
            foreach ($accounts as $account) {
                // - for every account get it's maildumps' FROM field distinctly
                // - find proper addressbook record for every mail_dump
                // - perform insertion
                if($mail->reply_mode){
                    $this->campaignAddReplyModeMails($campaign_id, $account->id, $rule_regex, $rules, $mail->reply_days);
                    continue;
                }else{
                    // perform insertion with just filtered
                    $this->campaignAddRegularModeMails($campaign_id, $account->id, $rule_regex, $rules);
                    continue;
                }
            }
        }else{
            \Log::debug("CampaignController: skip campaign mail accounts contacts: ignore_account_contacts -> {$ignore_account_contacts} and !empty(acc_ids) -> " . !empty($acc_ids) );
        }

        \Log::debug("CampaignController: process campaign spambase:");
        // spam base emails
        $acc_ids =  $request->input('selected_bases');
        if(!$mail->reply_mode && !empty($acc_ids)){
            \Log::debug("CampaignController: acc_ids:" . json_encode($acc_ids));
            $spam_bases = SpamBase::whereIn('id', $acc_ids)->get();

            foreach ($spam_bases as $spam_base) {
                $this->campaignAddRegularModeMailsFromBase( $campaign_id, $spam_base->id, $rule_regex, $rules);
            }
        }

        $chunk_size = 100;
        // emails from textarea, will be used in future
        $raw_emails = $request->input('outer_addresses');
        $parse_rules = $this->request->input('parse_rules');//"[email]|[name] , [company]";
        // $parse_rules = "[email]|[name] , [company]";
        if(!empty($raw_emails)){
            \Log::debug("CampaignController: process campaign raw adresses:");
            $insert_data = $this->processNewAddressRecords($campaign_id, $raw_emails, $parse_rules, $rule_regex, $rules);

            $this->putRecordsToRedis($campaign_id, null, $insert_data, config('campaign.record_status.await'));

            // $insert_chunks = array_chunk($insert_data, $chunk_size);

            // foreach ($insert_chunks as $chunk) {
            //     // CampaignAddressbook::insertIgnore($chunk);
            //     $inserted_id = \DB::table("campaign_addressbook")->insertIgnore($chunk);
            // }
        }

        // file_list
        if(!empty($this->request->file_list)){
            \Log::debug("CampaignController: process campaign attached files with raw adresses");
            // \Log::debug( "processing file records:");
            foreach ($this->request->file_list as $file) {
                if( empty($file) )
                    continue;

                $filepath = $file->path();
                $addrs_raw = file_get_contents($filepath);
                $insert_data = $this->processNewAddressRecords($campaign_id, $addrs_raw, $parse_rules, $rule_regex, $rules);
                // $data = array_merge($data, $items);
                $this->putRecordsToRedis($campaign_id, null, $insert_data, config('campaign.record_status.await'));

                // $insert_chunks = array_chunk($insert_data, $chunk_size);

                // foreach ($insert_chunks as $chunk) {
                //     // CampaignAddressbook::insertIgnore($chunk);
                //     $inserted_id = \DB::table("campaign_addressbook")->insertIgnore($chunk);
                // }
            }
        }
    }

    private function campaignAddReplyModeMails($campaign_id=-1, $mail_account_id=-1, $rule_regex="/^\!skip\!/", $rules=[], $reply_days=90, $save_blacklisted=true, $save_skipped=true)
    {
        // might be also few thousands
        $mails = \DB::table('mail_account_addressbook')->select(['name', 'company', 'rest', 'address', 'id'])->where('email_account_id', $mail_account_id)->get()->toArray();

        $mails_filtered = []; //contain whitelisted
        $mails_blacklisted = []; // contain blacklisted
        $mails_skipped = []; // contain no mail_dump found
        $start_date = (\Carbon\Carbon::today())->subDays($reply_days);

        // split mails to 3 arrays:
        // good - items with mail dump an accepted by exclude lists
        // skipped - items without mail dump and accepted by exclude lists
        // bad - not accepted by exclude lists

        $status_skip = config('campaign.record_status.skip');
        $status_await = config('campaign.record_status.await');
        $status_blacklist = config('campaign.record_status.blacklist');

        array_walk($mails, function($record) use (&$mails_filtered, &$mails_blacklisted, &$mails_skipped, $rule_regex, $mail_account_id, $start_date, $status_skip, $status_await, $status_blacklist, $rules){
            $res = preg_match($rule_regex, $record->address, $matches);
            if($res != 0){
                // push blacklisted into proper array
                $bl_str = "Blacklisted on insertion";
                foreach ($matches as $key => $value) {
                    if( is_string($key) && !empty($value) ){
                        $rule = $rules->firstWhere('r_name', $key);
                        $bl_str .= " rule:{$rule['rule']} group:{$rule['group']}";
                    }
                }
                $record->record_status = $status_blacklist;
                $record->record_status_txt = $bl_str;
                // return [$record, $bl_str];
                array_push($mails_blacklisted, $record);
            }else{
                // try to find maildump from counteragent to our account
                $mail_dump = \DB::table('mail_dump')->where('from', 'like', '%'. $record->address .'%')->where('mail_account_id', $mail_account_id)->where('body', '!=', '')->where('mail_date', '>=', $start_date)->distinct()->first();
                if(empty($mail_dump)){
                    $record->record_status = $status_skip;
                    $record->record_status_txt = "No mail dump found. Skip.";
                    array_push($mails_skipped, $record);
                }else{
                    $record->record_status = $status_await;
                    // add few extra fields to record before add it
                    $record->dump_subject = $mail_dump->subject;
                    $record->dump_body = $mail_dump->body;
                    $record->dump_headers = $mail_dump->headers;
                    array_push($mails_filtered, $record);
                }
            }
        }, $mails);


        // put arrays into redis db
        $this->putRecordsToRedis($campaign_id, $mail_account_id, $mails_filtered, $status_await);

        if( $save_blacklisted )
            $this->putRecordsToRedis($campaign_id, $mail_account_id, $mails_blacklisted, $status_blacklist);

        if( $save_skipped )
            $this->putRecordsToRedis($campaign_id, $mail_account_id, $mails_skipped, $status_skip);

        // drop all older logic
        return true;

        // i guess we need firstly remove items from regexp
        // do simple foreach to split results into two arrays, can do with array_walk, but not sure of efficiency
        // foreach ($mails as $item) {
        //     if( preg_match($rule_regex, $item->address) == 0 && !empty($item->address) ){
        //         $mails_filtered[] = $item;
        //     }else{
        //         $mails_blacklisted[] = $item;
        //     }
        // }

        $mails_filtered = array_filter($mails, function($record) use ($rule_regex){
            return preg_match($rule_regex, $record->address) == 0 && !empty($record->address);
        });

        // \Log::debug("CampaignController: Befor filter:" . count($mails) . " after filter:" . count($mails_filtered) );

        // $start_date = (\Carbon\Carbon::today())->subDays($reply_days);
        // might be a few thousands
        $mail_dumps = \DB::table('mail_dump')->select(['from'])->where('mail_account_id', $mail_account_id)->where('body', '!=', '')->where('mail_date', '>=', $start_date)->distinct()->get()->toArray();
        // second filter -> if mail_dump DO have it

        $mails_good = [];
        // foreach ($mails_filtered as $addr_record) {
        //     foreach ($mail_dumps as $md_record) {
        //         if( strpos($md_record->from, $addr_record->address) !== false ){
        //             $mails_good[] = $addr_record;
        //         }else{
        //             $mails_skipped[] = $addr_record;
        //         }
        //     }
        // }
        $mails_good = array_filter($mails_filtered, function($addr_record) use ($mail_dumps){
            // return preg_match($rule_regex, $record->address) == 0;
            foreach ($mail_dumps as $md_record) {
                if( strpos($md_record->from, $addr_record->address) !== false ){
                    // \Log::debug("CampaignController: Found address_record [{$addr_record->address}] related mail_dump: [{$md_record->from}]" );
                    return true;
                }
            }
            return false;
        });

        $this->putRecordsToRedis($campaign_id, $mail_account_id, $mails_good, config('campaign.record_status.await'));


        // \Log::debug("CampaignController: After mail_dump filter:" . count($mails_filtered) );
        // save successfully fitered
        // $now = \Carbon\Carbon::now();
        // $chunk_size = 500;

        // // now split to chunks ans save
        // while (count($mails_good) > 0) {
        //     $chunk_size = min(count($mails_good), $chunk_size);
        //     $insert_data = [];
        //     for ($i=0; $i < $chunk_size; $i++) {
        //         $item = array_shift($mails_good);

        //         $insert_data[] = [
        //             'campaign_id' => $campaign_id,
        //             'mail_account_addressbook_id' => $item->id,
        //             'mail_account_id' => $mail_account_id,
        //             'address' => $item->address,
        //             'name' => $item->name,
        //             'company' => $item->company,
        //             'rest' => $item->rest,
        //             'created_at' => $now,
        //             'updated_at' => $now,
        //         ];
        //     }

        //     // \Log::debug("CampaignController: Insert items:" . json_encode($insert_data));
        //     $inserted_id = \DB::table("campaign_addressbook")->insertIgnore($insert_data);
        // }

        $save_skipped=true;
        // save skipped
        if($save_skipped){
            // $mails_skipped = array_filter($mails_filtered, function($addr_record) use ($mails_good){
            //     // return preg_match($rule_regex, $record->address) == 0;
            //     foreach ($mails_good as $mg_record) {
            //         if( $mg_record->id == $addr_record->id ){
            //             // \Log::debug("CampaignController: Found address_record [{$addr_record->address}] related mail_dump: [{$md_record->from}]" );
            //             return false;
            //         }
            //     }
            //     return true;
            // });
            $skip_status = config('campaign.record_status.skip');
            $this->putRecordsToRedis($campaign_id, $mail_account_id, $mails_blacklisted, $skip_status);
            /*
            while (count($mails_skipped) > 0) {
                $chunk_size = min(count($mails_skipped), $chunk_size);
                $insert_data = [];
                for ($i=0; $i < $chunk_size; $i++) {
                    $item = array_shift($mails_skipped);

                    $insert_data[] = [
                        'campaign_id' => $campaign_id,
                        'mail_account_addressbook_id' => $item->id,
                        'mail_account_id' => $mail_account_id,
                        'address' => $item->address,
                        'name' => $item->name,
                        'company' => $item->company,
                        'rest' => $item->rest,
                        'created_at' => $now,
                        'updated_at' => $now,
                        'record_status' => $skip_status,
                        'record_status_txt' => "Skipped. No mail dump found."
                    ];
                }

                // \Log::debug("CampaignController: Insert items:" . json_encode($insert_data));
                $inserted_id = \DB::table("campaign_addressbook")->insertIgnore($insert_data);
            }
            */

        }

        $save_blacklisted=true;
        // save blacklisted
        if($save_blacklisted){
            // $mails_blacklisted = array_filter($mails, function($record) use ($rule_regex){
            //     return preg_match($rule_regex, $record->address) != 0 || empty($record->address);
            // });

            // TODO: performance check...
            $mails_blacklisted = array_map(function($record) use($rule_regex, $rules){
                $res = preg_match($rule_regex, $record->address, $matches);
                if($res != 0){
                    $bl_str = "Blacklisted on insertion";
                    foreach ($matches as $key => $value) {
                        if( is_string($key) && !empty($value) ){
                            $rule = $rules->firstWhere('r_name', $key);
                            $bl_str .= " rule:{$rule['rule']} group:{$rule['group']}";
                        }
                    }
                    return [$record, $bl_str];
                }else{
                    return false;
                }
            }, $mails);

            // remove falsy
            $mails_blacklisted = array_filter($mails_blacklisted);

            // save blacklisted
            $bl_status = config('campaign.record_status.blacklist');
            $this->putRecordsToRedis($campaign_id, $mail_account_id, $mails_blacklisted, $bl_status);

            /*
            while (count($mails_blacklisted) > 0) {
                $chunk_size = min(count($mails_blacklisted), $chunk_size);
                $insert_data = [];
                for ($i=0; $i < $chunk_size; $i++) {
                    $item_arr = array_shift($mails_blacklisted);
                    $item = $item_arr[0];

                    $insert_data[] = [
                        'campaign_id' => $campaign_id,
                        'mail_account_addressbook_id' => $item->id,
                        'mail_account_id' => $mail_account_id,
                        'address' => $item->address,
                        'name' => $item->name,
                        'company' => $item->company,
                        'rest' => $item->rest,
                        'created_at' => $now,
                        'updated_at' => $now,
                        'record_status' => $bl_status,
                        'record_status_txt' => $item_arr[1]
                    ];
                }

                // \Log::debug("CampaignController: Insert items:" . json_encode($insert_data));
                $inserted_id = \DB::table("campaign_addressbook")->insertIgnore($insert_data);
            }
            */
        }
    }

    private function campaignAddRegularModeMails($campaign_id=-1, $mail_account_id=-1, $rule_regex="/^\!skip\!/", $rules=[], $save_blacklisted=true)
    {
        // might be also few thousands
        $mails = \DB::table('mail_account_addressbook')->select(['name', 'company', 'rest', 'address', 'id'])->where('email_account_id', $mail_account_id)->get()->toArray();

        $mails_filtered = []; //contain whitelisted
        $mails_blacklisted = []; // contain blacklisted

        $mails_filtered = array_filter($mails, function($record) use ($rule_regex){
            return preg_match($rule_regex, $record->address) == 0 && !empty($record->address);
        });

        $mails_good = $mails_filtered;

        $this->putRecordsToRedis($campaign_id, $mail_account_id, $mails_good, config('campaign.record_status.await'));

        // TODO: deprecated, remove when python part is ready
        /*
        // save successfully fitered
        $now = \Carbon\Carbon::now();
        $chunk_size = 500;
        // now split to chunks ans save
        while (count($mails_good) > 0) {
            $chunk_size = min(count($mails_good), $chunk_size);
            $insert_data = [];
            $insert_data_redis = [];
            for ($i=0; $i < $chunk_size; $i++) {
                $item = array_shift($mails_good);

                $insert_data[] = [
                    'campaign_id' => $campaign_id,
                    'mail_account_addressbook_id' => $item->id,
                    'mail_account_id' => $mail_account_id,
                    'address' => $item->address,
                    'name' => $item->name,
                    'company' => $item->company,
                    'rest' => $item->rest,
                    'created_at' => $now,
                    'updated_at' => $now,
                ];
            }

            // \Log::debug("CampaignController: Insert items:" . json_encode($insert_data));
            $inserted_id = \DB::table("campaign_addressbook")->insertIgnore($insert_data);
        }
        */

        // save blacklisted
        $save_blacklisted=true;
        if($save_blacklisted){
            // TODO: performance check...
            $mails_blacklisted = array_map(function($record) use($rule_regex, $rules){
                $res = preg_match($rule_regex, $record->address, $matches);
                if($res != 0){
                    $bl_str = "Blacklisted on insertion";
                    foreach ($matches as $key => $value) {
                        if( is_string($key) && !empty($value) ){
                            $rule = $rules->firstWhere('r_name', $key);
                            $bl_str .= " rule:{$rule['rule']} group:{$rule['group']}";
                        }
                    }
                    return [$record, $bl_str];
                }else{
                    return false;
                }
            }, $mails);

            // remove falsy
            $mails_blacklisted = array_filter($mails_blacklisted);

            // save blacklisted
            $bl_status = config('campaign.record_status.blacklist');

            $this->putRecordsToRedis($campaign_id, $mail_account_id, $mails_blacklisted, $bl_status);

            // TODO: deprecated, remove when python part is ready
            /*
            while (count($mails_blacklisted) > 0) {
                $chunk_size = min(count($mails_blacklisted), $chunk_size);
                $insert_data = [];
                for ($i=0; $i < $chunk_size; $i++) {
                    $item_arr = array_shift($mails_blacklisted);
                    $item = $item_arr[0];

                    $insert_data[] = [
                        'campaign_id' => $campaign_id,
                        'mail_account_addressbook_id' => $item->id,
                        'mail_account_id' => $mail_account_id,
                        'address' => $item->address,
                        'name' => $item->name,
                        'company' => $item->company,
                        'rest' => $item->rest,
                        'created_at' => $now,
                        'updated_at' => $now,
                        'record_status' => $bl_status,
                        'record_status_txt' => $item_arr[1]
                    ];
                }

                // \Log::debug("CampaignController: Insert items:" . json_encode($insert_data));
                $inserted_id = \DB::table("campaign_addressbook")->insertIgnore($insert_data);
            }
            */
        }
    }

    private function campaignAddRegularModeMailsFromBase($campaign_id=-1, $spam_base_id=-1, $rule_regex="/^\!skip\!/", $rules=[], $save_blacklisted=true, $limit=5000)
    {
        $spam_base_tabe = (new SpamBase())->getTable();
        $spam_base_record_tabe = (new SpamBaseRecord())->getTable();
        $campaign_addressbook_table = (new CampaignAddressbook())->getTable();

        $bl_status = config('campaign.record_status.blacklist');
        // first get count
        $total_mails = SpamBaseRecord::where('spam_base_id', $spam_base_id )->count();
        $offset = 0;
        \Log::debug("CampaignController: Spam base has {$total_mails} records");
        while ($total_mails > $offset) {

            $chunk_records = \DB::table($spam_base_record_tabe)
                ->where('spam_base_id', $spam_base_id)
                ->offset($offset)
                ->limit($limit)
                ->get()
                ->toArray();

            // increase counter
            $offset += $limit;


            $now = \Carbon\Carbon::now();
            $mails_filtered = array_filter($chunk_records, function($record) use ($rule_regex){
                return preg_match($rule_regex, $record->address) == 0 && !empty($record->address);
            });

            $insert_data = array_map(function($item) use($campaign_id, $now, $spam_base_id){
                return [
                    'campaign_id' => $campaign_id,
                    'mail_account_addressbook_id' => null,
                    'mail_account_id' => null,
                    'spam_base_id' => $spam_base_id,
                    'spam_base_record_id' => $item->id,
                    'address' => $item->address,
                    'name' => $item->name,
                    'company' => $item->company,
                    'rest' => $item->rest,
                    'created_at' => $now,
                    'updated_at' => $now,
                ];
            }, $mails_filtered);

            // $inserted_id = \DB::table($campaign_addressbook_table)->insertIgnore($insert_data);
            $this->putRecordsToRedis($campaign_id, null, $insert_data, config('campaign.record_status.await'));

            if(!$save_blacklisted)
                continue;

            // TODO: performance check...
            $mails_blacklisted = array_map(function($record) use($rule_regex, $rules){
                $res = preg_match($rule_regex, $record->address, $matches);
                if($res != 0){
                    $bl_str = "Blacklisted on insertion";
                    foreach ($matches as $key => $value) {
                        if( is_string($key) && !empty($value) ){
                            $rule = $rules->firstWhere('r_name', $key);
                            $bl_str .= " rule:{$rule['rule']} group:{$rule['group']}";
                        }
                    }
                    return [$record, $bl_str];
                }else{
                    return false;
                }
            }, $chunk_records);

            // remove falsy
            $mails_blacklisted = array_filter($mails_blacklisted);

            // $mails_blacklisted = array_filter($chunk_records, function($record) use ($rule_regex){
            //     return preg_match($rule_regex, $record->address) != 0 || empty($record->address);
            // });

            $insert_data = array_map(function($item_arr) use($campaign_id, $now, $bl_status, $spam_base_id){
                $item = $item_arr[0];
                return [
                    'campaign_id' => $campaign_id,
                    'mail_account_addressbook_id' => null,
                    'mail_account_id' => null,
                    'spam_base_id' => $spam_base_id,
                    'spam_base_record_id' => $item->id,
                    'address' => $item->address,
                    'name' => $item->name,
                    'company' => $item->company,
                    'rest' => $item->rest,
                    'created_at' => $now,
                    'updated_at' => $now,
                    'record_status' => $bl_status,
                    'record_status_txt' => $item_arr[1]
                ];
            }, $mails_blacklisted);

            \Log::debug("CampaignController: total chunk size:" . count($chunk_records) . " mails_filtered:" . count($mails_filtered) . " blacklisted:" . count($mails_blacklisted));

            // $inserted_id = \DB::table($campaign_addressbook_table)->insertIgnore($insert_data);
            $this->putRecordsToRedis($campaign_id, null, $insert_data, $bl_status);

        }
    }

    // records must be allready filtered
    private function putRecordsToRedis($campaign_id=-1, $mail_account_id=-1, $records=[], $record_status=-1, $record_status_txt='')
    {
        $await_status = config('campaign.record_status.await');
        // SET key
        $list_key = "campaign:{$campaign_id}:records:{$record_status}";
        if ($record_status < $await_status)
            $record_status = $await_status;
        if(!is_null($mail_account_id))
            $acc_set_key = "campaign:{$campaign_id}:account:{$mail_account_id}:records:{$record_status}";
        else
            $acc_set_key = "campaign:{$campaign_id}:account:none:records:{$record_status}";

        $mail_accs_key = "campaign:{$campaign_id}:accounts";

        $account = MailAccount::find($mail_account_id);
        if(empty($account)){
            $from_mail = 'none';
            $from_name = 'none';
        }else{
            $from_name = $account->name;
            $from_mail = $account->common_login;
        }

        // expire after 15 days
        $expire_time = 3600*24*15;
        // $expire_time = 60;
        // bulk insertion
        $spambase_key = "campaign:{$campaign_id}:spambases";
        Redis::pipeline(function ($pipe) use ($campaign_id, $mail_account_id, $records, $list_key, $from_mail, $from_name, $record_status, $record_status_txt, $acc_set_key, $mail_accs_key, $expire_time, $spambase_key) {
            foreach ($records as $item) {
                if( is_array($item) ){
                    // check if it's blacklist item where [item, blacklist]
                    if ( array_key_exists(1, $item) ){
                        $record_status_txt = $item[1];
                        if( is_array($item[0]))
                            $item = (object)$item[0];
                        else
                            $item = $item[0];
                    } elseif ( array_key_exists('1', $item) ){
                        $record_status_txt = $item['1'];
                        if( is_array($item['0']))
                            $item = (object)$item['0'];
                        else
                            $item = $item['0'];
                    } else {
                        $item = (object)$item;
                    }
                }

                if( !property_exists($item, 'address') ){
                    \Log::debug("Item has no address:" . json_encode($item));
                    continue;
                }

                $hash_id = Murmur::hash3("{$campaign_id}{$from_mail}{$from_name}" . $item->address );
                $hash_key = "campaign:{$campaign_id}:record:{$hash_id}";
                $pipe->hMSet( $hash_key, [
                    'campaign_id' => $campaign_id,
                    'mail_account_addressbook_id' => property_exists($item , 'id') ? $item->id : null,
                    'mail_account_id' => $mail_account_id,
                    'spam_base_id' => property_exists($item , 'spam_base_id') ? $item->spam_base_id : null,
                    'spam_base_record_id' => property_exists($item , 'spam_base_record_id') ? $item->spam_base_record_id : null,
                    'address' => $item->address,
                    'name' => $item->name,
                    'company' => $item->company,
                    'rest' => $item->rest,
                    'record_status' => $record_status,
                    'record_status_txt' => empty($item->record_status_txt) ? $record_status_txt : $item->record_status_txt,
                    'dump_subject' => empty($item->dump_subject) ? '' : $item->dump_subject,
                    'dump_body' => empty($item->dump_body) ? '' : $item->dump_body,
                    'dump_headers' => empty($item->dump_headers) ? '' : $item->dump_headers,
                ]);

                // set expire status to clear data
                $pipe->expire($hash_key, $expire_time);
                // per account, so pop it in python
                $pipe->sAdd($acc_set_key, $hash_key);
                // common list
                // $pipe->rPush($list_key, $hash_key);
                $pipe->sAdd($list_key, $hash_key);
                // spam bases set
                if (property_exists($item , 'spam_base_id'))
                    $pipe->sAdd($spambase_key, $item->spam_base_id);
            }

            // if( is_null($mail_account_id) || $mail_account_id < 1 )
            //     $mail_account_id = 'none';
            // store keys for eas of futher usage
            $pipe->sAdd($mail_accs_key, $acc_set_key);
        });
    }

    /**
     * Display the specified resource.
     *
     * @param  int  $id
     * @return \Illuminate\Http\Response
     */
    public function show($id)
    {
        //
    }

    /**
     * Show the form for editing the specified resource.
     *
     * @param  int  $id
     * @return \Illuminate\Http\Response
     */
    public function edit($id)
    {
        //
    }

    /**
     * Update the specified resource in storage.
     *
     * @param  \Illuminate\Http\Request  $request
     * @param  int  $id
     * @return \Illuminate\Http\Response
     */
    public function update($id)
    {
        $request = $this->request;

        // \Log::debug("CampaignController: Updating data for campaign: {$id}");
        // \Log::debug($this->request->all());

        $mail = Campaign::find($id);
        if ($mail == null) {
            return response()->json(['success' => false, 'message' => 'Try to edit non existed campaign.']);
        }
        $mail->name = $request->input('name');
        $mail->subject = $request->input('subject');
        $mail->body = empty($request->input('body')) ? '' : $request->input('body');
        $mail->headers = empty($request->input('headers'))  ? '' : $request->input('headers');
        // $mail->status = (int)$request->input('status') || config('campaign.status.PAUSED');
        $mail->is_html = (int)$request->input('is_html') || 0;
        $mail->ignore_selfhost = (int)$request->input('ignore_selfhost') || 0;
        $mail->attach_name = empty($request->input('attach_name')) ? '' : $request->input('attach_name');
        $mail->account_name = empty($request->input('account_name')) ? '' : $request->input('account_name');

        $mail->status = (int)$request->input('status');

        $mail->max_messages = (int)$request->input('max_messages');
        $mail->per_time = (int)$request->input('per_time');

        $filters = $request->input('selected_filters');
        if(is_null($filters))
            $filters = [];

        $mail->filters = $filters;
        $mail->save();

        $attachement_ids = $request->input('selected_atts');
        if( !empty($attachement_ids) ){
            $mail->attachements()->sync($attachement_ids);
        }

        $acc_ids =  $request->input('selected_accs');
        if( !empty($acc_ids) ){
            $mail->accounts()->sync($acc_ids);
        }

        $recreate = (int)$request->input('recreate_addressbook') ||  0;

        if($recreate){
            // delete all previous records
            // $mail->addressBook()->delete();
            CampaignAddressbook::where('campaign_id', $mail->id)->delete();
            // create new one
            $this->campaignProcessRecords($mail, $request);
        }

        return response()->json(['success' => true, 'message' => 'Campaign is updated.']);

    }

    /**
     * Remove the specified resource from storage.
     *
     * @param  int  $id
     * @return \Illuminate\Http\Response
     */
    public function destroy($id)
    {
        //
    }

    /**
     * Update statuf for campaign.
     *
     * @param  int  $id
     * @return \Illuminate\Http\Response
     */
    public function status($id, $status)
    {
        $res = Campaign::where('id', $id)
                ->update(['status' => $status, 'scheduled' => null]);

        return response()->json([
            'success' => true,
            'message' => 'Campaign status updated.'
        ]);

    }

    public function getAttachements($id)
    {
        $data = Attachement::where('campaign_id', $id)->select(['id', 'name', 'size', 'used'])->get();

        return response()->json([
            'success' => true,
            'message' => 'Campaign attachements list.',
            'data' => $data
        ]);
    }

    public function detailsAddressBook($id){


        // $record_status = $this->request->input('record_status[]');
        $record_status = $this->request->input('record_status');
        $search_account = $this->request->input('search_account');

        // \Log::debug($record_status);
        $filters = [
            'record_status' => $record_status,
            'search_account' => $search_account
        ];

        if(!empty($filters['record_status'])){
            \Log::debug("CampaignController: record_status:" . json_encode($filters['record_status']));
        }

        $order_by = $this->request->input('order_by');
        $order_direction = $this->request->input('order_direction');

        if(!empty($order_by) && empty($order_direction)){
            $order_direction = 'desc';
        }

        $per_page = $this->request->input('per_page');
        if(empty($per_page))
            $per_page = 50;
        else
            $per_page = (int)$per_page;

        return response()->json([
            'success' => true,
            'message' => '',
            'data' => ['data'=>[]],
            'filters' => $filters
        ]);

        $data = CampaignAddressbook::with(['account'])
                ->where('campaign_id', $id)
                ->when(!empty($filters['record_status'] || $filters['record_status'] == 0), function( $query) use ($filters){
                    if(is_string($filters['record_status']) || is_integer($filters['record_status']) )
                        return $query->where('record_status', $filters['record_status']);
                    else
                        return $query->whereIn('record_status', $filters['record_status']);
                })
                ->when(!empty($filters['search_account']), function( $query) use ($filters){
                    $sa = $filters['search_account'];
                    return $query
                                ->whereHas('account', function ($query2) use ($sa) {
                                    return $query2->where('id', $sa)
                                    ->orWhere('name', 'LIKE', "%{$sa}%")
                                    ->orWhere('all_names', 'LIKE', "%{$sa}%")
                                    ->orWhere('smtp_host', 'LIKE', "%{$sa}%")
                                    ->orWhere('smtp_login', 'LIKE', "%{$sa}%")
                                    ;
                                })
                                ->orWhere('address', 'LIKE', "%{$sa}%")
                                ->orWhere('name', 'LIKE', "%{$sa}%")
                                ->orWhere('company', 'LIKE', "%{$sa}%")
                                ->orWhere('rest', 'LIKE', "%{$sa}%")
                                ;
                })
                ->when(!empty($order_by), function($query) use ($order_by, $order_direction){
                    return $query->orderBy($order_by, $order_direction);
                })
                ->paginate($per_page)->appends($filters);
                // ->paginate(50)->appends($filters);

        return response()->json([
            'success' => true,
            'message' => '',
            'data' => $data,
            'filters' => $filters
        ]);
    }

    public function addressBookMassUpdate($id){
        $action = $this->request->input('option');
        $ids = $this->request->input('ids');

        // $socksTable = (new MailAccount())->getTable();
        if( $action == 'mark-await' ){
            CampaignAddressbook::whereIn('id', $ids)->update(array('record_status' => config('campaign.record_status.await') ));
        }elseif( $action == 'mark-processing' ){
            CampaignAddressbook::whereIn('id', $ids)->update(array('record_status' => config('campaign.record_status.processing') ));
        }elseif( $action == 'mark-success' ){
            CampaignAddressbook::whereIn('id', $ids)->update(array(
                'record_status' => config('campaign.record_status.success'),
                'record_status_txt' => 'Marked as success by operator'));
        }elseif( $action == 'mark-fail' ){
            CampaignAddressbook::whereIn('id', $ids)->update(array(
                'record_status' => config('campaign.record_status.fail'),
                'record_status_txt' => 'Marked as failed by operator'));
        }elseif ($action == 'delete') {
            CampaignAddressbook::whereIn('mail_account_id', $ids)->delete();
        }

        return response()->json(['success' => true, 'message' => 'Changes applied.']);
    }

    private function processNewAddressRecords($id, $addrs_raw, $parse_rules, $scan_regex="", $rules=[])
    {
        $mail_preset = "(?P<mail>(?:[a-z0-9!#$%&'*+\/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+\/=?^_`{|}~-]+)*|\"(?:[\\x01-\\x08\\x0b\\x0c\\x0e-\\x1f\\x21\\x23-\\x5b\\x5d-\\x7f]|\\[\\x01-\\x09\\x0b\\x0c\\x0e-\\x7f])*\")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:(?:[\\x01-\\x08\\x0b\\x0c\\x0e-\\x1f\\x21-\\x5a\\x53-\\x7f]|\\[\\x01-\\x09\\x0b\\x0c\\x0e-\\x7f])+)\]))";
        $name_preset = "(?P<name>[\w\s(\"\')?]+)?";
        $company_preset = "(?P<company>[\w\s(\"\')?]+)?";
        $rest_preset = "(?P<rest>[\w\s(\"\')?]+)?";
        $now = \Carbon\Carbon::now();

        // create regexp from parse_rules
        // stop0: remove whitespaces from string
        $parse_rules = preg_replace("/\s/", "", $parse_rules);
        // step1: replace delimiters with (\s?delimiter\s?) four backslashes are needed for escape value of $1
        # $data = preg_replace("/(?:\])(.*?)(?:\[)/", "](\s?\\\\$1\s?)[", $parse_rules);
        $data = preg_replace_callback(
            "/(?:\])\s?(\S*?)\s?(?:\[)/",
            function($matches){
                // check if matches is empty
                if(empty($matches[1]))
                    return '](\s)[';
                else
                    return '](\s?\\'.$matches[1].'\s?)[';
            },
            $parse_rules
        );
        // spet2: replace email with pattern
        $data = preg_replace("/\[e?mail\]/", $mail_preset, $data);
        // step3: replace name with pattern
        $data = preg_replace("/\[name\]/", $name_preset, $data);
        // step4: replace company with pattern
        $data = preg_replace("/\[company\]/", $company_preset, $data);
        // step5: replace rest with pattern
        $data = preg_replace("/\[rest\]/", $rest_preset, $data);

        $parse_regex = "/".$data."/";
        $addr_list = explode("\n", $addrs_raw);
        \Log::debug("CampaignController: Account add mails, parse regex:$parse_regex");

        $bl_status = config('campaign.record_status.blacklist');
        $await_status = config('campaign.record_status.await');
        $save_blacklisted = true;
        $addrs = [];
        foreach ($addr_list as $record) {
            if( empty($record) ) continue;

            preg_match_all($parse_regex, $record, $matches);
            \Log::debug("CampaignController: Processing record:{$record}\n" . json_encode($matches));
            // skip record if no mail found
            $address = array_key_exists("mail", $matches) && !empty($matches['mail']) ? $matches['mail'][0] : "";

            if(empty($address)){
                \Log::debug("CampaignController: Skip. Reason: can't get email from record:{$record}");
                continue;
            }

            $bl_str = '';
            $rs = $await_status;
            // check for scan rules
            if(!empty($scan_regex)){
                $res = preg_match($scan_regex, $address, $matches);
                if($res != 0){
                    $bl_str = "Blacklisted on insertion";
                    foreach ($matches as $key => $value) {
                        if( is_string($key) && !empty($value) ){
                            $rule = $rules->firstWhere('r_name', $key);
                            $bl_str .= " rule:{$rule['rule']} group:{$rule['group']}";
                        }
                    }
                    $rs = $bl_status;
                }

                // if( preg_match($scan_regex, $address) ){
                //     \Log::debug("CampaignController: Record:$address\nRule:$scan_regex\nFound forbidden match in adding new email record. Skip.");
                //     continue;
                // }
            }

            $addrs[] = [
                "address" => $address,
                "name" => array_key_exists("name", $matches) && !empty($matches['name'][0]) ? trim($matches['name'][0]) : "",
                "company" => array_key_exists("company", $matches)  && !empty($matches['company'][0]) ? trim($matches['company'][0]) : "",
                "rest" => array_key_exists("rest", $matches)  && !empty($matches['rest'][0]) ? trim($matches['rest'][0]) : "",
                'campaign_id' => $id,
                "mail_account_id" => null,
                'mail_account_addressbook_id' => null,
                'mail_account_id' => null,
                'created_at' => $now,
                'updated_at' => $now,
                'record_status' => $rs,
                'record_status_txt' => $bl_str
            ];
        }

        return $addrs;
    }
}
