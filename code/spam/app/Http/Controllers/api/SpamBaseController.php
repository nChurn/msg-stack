<?php

namespace App\Http\Controllers\api;

use Illuminate\Http\Request;
use App\Http\Controllers\Controller;

use App\Models\ScanRules;
use App\Models\SpamBase;
use App\Models\SpamBaseRecord;
use App\Models\MailAccount;
use App\Models\MailAccountAddressBook;
use Carbon\Carbon;
use Illuminate\Support\Collection;

class SpamBaseController extends Controller
{
    protected $request;

    public function __construct(Request $request) {
        $this->request = $request;
    }

    public function index(){
        $filters = [];

        $per_page = $this->request->input('blrs_per_page')?:50;
        $order_by = $this->request->input('order_by')?:null;
        $order_direction = $this->request->input('order_direction')?:null;

        $base_list = SpamBase::withCount('records')
                        ->when(!empty($order_by), function($query) use ($order_by, $order_direction){
                            return $query->orderBy($order_by, $order_direction);
                        })
                        ->paginate($per_page, ['*'], 'blr_page')
                        // ->appends($filters)
                        ;

        return response()->json(['success' => true, 'message' => '', 'data' => ['base_list' => $base_list]]);
    }


    public function get($id){
        $base = SpamBase::find($id);
        if(!is_null($base))
            $base->setAppends(['selected_ids']);
        $filter_group = ScanRules::select('group')->distinct()->get(); //->map(function($item){ return $item->group; })->toArray();
        // $selectedIds = $base->selectedIds();
        return response()->json(['success' => true, 'message' => '', 'data' => ['base' => $base, 'filter_group' => $filter_group]]);
    }

    /**
     * Store a newly created resource in storage.
     *
     * @return Response
     */
    public function store()
    {
        $spam_base_id = (int)$this->request->input('id');
        if($spam_base_id < 1){
            $base = new SpamBase();
        }else{
            $base = SpamBase::find($spam_base_id);
        }

        $base->name = $this->request->input('name');

        // use filters to skip unwanted records
        // can be string or array
        $filters = $this->request->input('filters');
        if(is_null($filters))
            $filters = [];

        $base->filters = $filters;

        // \Log::error("SpamBaseController enable_automatics:" . $this->request->input('enable_automatics'));

        if(!empty($this->request->input('enable_automatics')) && $this->request->input('enable_automatics') == 'true' )
            $base->enable_automatics = true;
        else
            $base->enable_automatics = false;

        $base->save();
        $spam_base_id = $base->id;

        // -- kill all previous redords on upload
        $recreate = $this->request->input('recreate');
        if($recreate == 'true' || $recreate == true)
            $recreate = true;
        else
            $recreate = false;
        // -- kill  previous email_account redords on upload
        $remove_account_records = $this->request->input('remove_account_records');
        if($remove_account_records == 'true' || $remove_account_records == true)
            $remove_account_records = true;
        else
            $remove_account_records = false;

        // \Log::debug("recreate:{$recreate} , remove_account_records:{$remove_account_records}");
        if( $remove_account_records )
            $base->records()->whereNotNull('email_account_id')->delete();

        if( $recreate )
            $base->records()->delete();

        if( $base->filters->count() > 0 )
            $rules = ScanRules::whereIn('group', $base->filters)->select('rule')->where('enabled', 1)->distinct()->get()->map(function($item){ return "(".$item['rule'].")"; });
        else
            $rules = collect([]);

        $rules_count = $rules->count();
        // skip regex check by making it never accomplished
        if( $rules->count() == 0 ){
            $rule_regex = "/^\!skip\!/";
        }else{
            $rule_regex = "/". implode("|", $rules->toArray()) ."/i";
        }

        // process email accounts
        $acc_ids = $this->request->input('selected_ids');
        if( is_string($acc_ids) )
            $acc_ids = explode(",", $acc_ids);



        if( is_array($acc_ids) && count($acc_ids) > 0 || $acc_ids instanceof Collection && $acc_ids->count() > 0 || !empty($acc_ids)){
            $accounts = MailAccount::whereIn('id', $acc_ids)->get();
            foreach ($accounts as $account) {
                $this->addMailsFromEmailAccount($spam_base_id, $account->id, $rule_regex, false);
            }
        }

        \Log::debug("SpamBaseController: process other sources");
        // process other sources
        $parse_rules = $this->request->input('parse_rules');//"[email]|[name] , [company]";
        $addrs_raw = $this->request->input('rawEmails');
        // process textarea
        if(!empty($addrs_raw)){
            \Log::debug( "SpamBaseController: processing textarea records:");
            $data = $this->processNewAddressRecords($spam_base_id, $addrs_raw, $parse_rules, $rule_regex);
            // \Log::debug( "textarea records:" . json_encode($data));
        }else{
            \Log::debug( "SpamBaseController: textarea records are empty");
        }

        // file_list
        if(!empty($this->request->attachements)){
            \Log::debug( "SpamBaseController: processing file records:");
            foreach ($this->request->attachements as $file) {
                $filepath = $file->path();
                $addrs_raw = file_get_contents($filepath);
                $items = $this->processNewAddressRecords($spam_base_id, $addrs_raw, $parse_rules, $rule_regex);
                // $data = array_merge($data, $items);
            }
        }else{
            \Log::debug( "SpamBaseController: file records are empty");
        }


        return response()->json(['success' => true, 'message' => 'Check new base created.']);
    }


    private function addMailsFromEmailAccount($spam_base_id=-1, $mail_account_id=-1, $rule_regex="/^\!skip\!/", $save_blacklisted=false)
    {
        $spam_base_record_table = (new SpamBaseRecord())->getTable();
        $mail_account_addressbook_table = (new MailAccountAddressBook())->getTable();
        // might be also few thousands
        $mails = \DB::table('mail_account_addressbook')->select(['name', 'company', 'rest', 'address', 'id'])->where('email_account_id', $mail_account_id)->get()->toArray();

        $mails_filtered = []; //contain whitelisted
        $mails_blacklisted = []; // contain blacklicted

        $mails_filtered = array_filter($mails, function($record) use ($rule_regex){
            return preg_match($rule_regex, $record->address) == 0 && !empty($record->address);
        });

        $mails_good = $mails_filtered;
        // \Log::debug("After mail_dump filter:" . count($mails_filtered) );
        // save successfully fitered
        $now = \Carbon\Carbon::now();
        $chunk_size = 500;
        // now split to chunks ans save
        while (count($mails_good) > 0) {
            $chunk_size = min(count($mails_good), $chunk_size);
            $insert_data = [];
            for ($i=0; $i < $chunk_size; $i++) {
                $item = array_shift($mails_good);

                $insert_data[] = [
                    'spam_base_id' => $spam_base_id,
                    'mail_account_addressbook_id' => $item->id,
                    'email_account_id' => $mail_account_id,
                    'address' => $item->address,
                    'name' => $item->name,
                    'company' => $item->company,
                    'rest' => $item->rest,
                    'created_at' => $now,
                    'updated_at' => $now,
                ];
            }

            // \Log::debug("Insert items:" . json_encode($insert_data));
            $inserted_id = \DB::table($spam_base_record_table)->insertIgnore($insert_data);
        }

        // save blacklisted
        // $save_blacklisted=true;
        if($save_blacklisted){
            $mails_blacklisted = array_filter($mails, function($record) use ($rule_regex){
                return preg_match($rule_regex, $record->address) != 0 || empty($record->address);
            });
            // save blacklisted
            while (count($mails_blacklisted) > 0) {
                $chunk_size = min(count($mails_blacklisted), $chunk_size);
                $insert_data = [];
                for ($i=0; $i < $chunk_size; $i++) {
                    $item = array_shift($mails_blacklisted);

                    $insert_data[] = [
                        'spam_base_id' => $spam_base_id,
                        'mail_account_addressbook_id' => $item->id,
                        'email_account_id' => $mail_account_id,
                        'address' => $item->address,
                        'name' => $item->name,
                        'company' => $item->company,
                        'rest' => $item->rest,
                        'created_at' => $now,
                        'updated_at' => $now,
                    ];
                }

                // \Log::debug("Insert items:" . json_encode($insert_data));
                $inserted_id = \DB::table($spam_base_record_table)->insertIgnore($insert_data);
            }
        }
    }

    private function processNewAddressRecords($id, $addrs_raw, $parse_rules, $scan_regex="")
    {
        $spam_base_record_table = (new SpamBaseRecord())->getTable();

        $mail_preset = "(?P<mail>(?:[a-z0-9!#$%&'*+\/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+\/=?^_`{|}~-]+)*|\"(?:[\\x01-\\x08\\x0b\\x0c\\x0e-\\x1f\\x21\\x23-\\x5b\\x5d-\\x7f]|\\[\\x01-\\x09\\x0b\\x0c\\x0e-\\x7f])*\")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:(?:[\\x01-\\x08\\x0b\\x0c\\x0e-\\x1f\\x21-\\x5a\\x53-\\x7f]|\\[\\x01-\\x09\\x0b\\x0c\\x0e-\\x7f])+)\]))";
        // $name_preset = "(?P<name>[\w\s(\"\')?]+)?";
        $name_preset = "(?P<name>[\s\S]+)?"; //any symbol at all
        // $company_preset = "(?P<company>[\w\s(\"\')?]+)?";
        $company_preset = "(?P<company>[\s\S]+)?";
        // $rest_preset = "(?P<rest>[\w\s(\"\')?]+)?";
        $rest_preset = "(?P<rest>[\s\S]+)?";
        $now = Carbon::now();

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
        \Log::debug("Account add mails, parse regex:$parse_regex");

        $addrs = [];
        foreach ($addr_list as $record) {
            if( empty($record) ) continue;

            preg_match_all($parse_regex, $record, $matches);
            \Log::debug("Processing record:{$record}\n" . json_encode($matches));
            // skip record if no mail found
            $address = array_key_exists("mail", $matches) && !empty($matches['mail']) ? $matches['mail'][0] : "";

            if(empty($address)){
                \Log::debug("Skip. Reason: can't get email from record:{$record}");
                continue;
            }

            // check for scan rules
            if(!empty($scan_regex)){
                if( preg_match($scan_regex, $address) ){
                    \Log::debug("Record:$address\nRule:$scan_regex\nFound forbidden match in adding new email record. Skip.");
                    continue;
                }
            }

            $addrs[] = [
                'mail_account_addressbook_id' => null,
                'email_account_id' => null,
                "address" => $address,
                "name" => array_key_exists("name", $matches) && !empty($matches['name'][0]) ? trim($matches['name'][0]) : "",
                "company" => array_key_exists("company", $matches)  && !empty($matches['company'][0]) ? trim($matches['company'][0]) : "",
                "rest" => array_key_exists("rest", $matches)  && !empty($matches['rest'][0]) ? trim($matches['rest'][0]) : "",
                "spam_base_id" => $id,
                "created_at" => $now,
                "updated_at" => $now
            ];

            // do insertions by chunks, and erase after
            if( count($addrs) >= 50 ){
                $inserted_id = \DB::table($spam_base_record_table)->insertIgnore($addrs);
                $addrs = [];
            }
        }

        // clear rest
        if( !empty($addrs) ){
            $inserted_id = \DB::table($spam_base_record_table)->insertIgnore($addrs);
            $addrs = [];
        }

        return $addrs;
    }

    public function delete($id){
        SpamBaseRecord::where('spam_base_id', $id)->delete();
        SpamBase::where('id', $id)->delete();

        return response()->json(['success' => true, 'message' => 'Spam base deleted.']);
    }

    public function massUpdate()
    {
        $action = $this->request->input('option');
        $ids = $this->request->input('ids');

        // $socksTable = (new MailAccount())->getTable();
        if ($action == 'delete') {
            SpamBaseRecord::whereIn('spam_base_id', $ids)->delete();
            SpamBase::whereIn('id', $ids)->delete();
        }elseif ( $action == 'automatics_enabled' ) {
            SpamBase::whereIn('id', $ids)->update(array('enable_automatics' => true));
        }elseif ( $action == 'automatics_disabled' ) {
            SpamBase::whereIn('id', $ids)->update(array('enable_automatics' => false));
        }

        return response()->json(['success' => true, 'message' => 'Changes applied.']);
    }

    public function export($id)
    {
        set_time_limit(0);

        // get records
        $spam_base_record_table = (new SpamBaseRecord())->getTable();
        $records = \DB::table($spam_base_record_table)
                        ->select(['name', 'company', 'rest', 'address'])
                        ->where('spam_base_id', $id)
                        ->get()
                        ->map(function($item){
                            return $item->address . " | " . $item->name . " | " . $item->company . " | " . $item->rest;
                        })
                        ->toArray();

        $base = SpamBase::find($id);

        $fileName = "{$id}-{$base->name}.txt";
        \Storage::put($fileName, implode("\r\n", $records) );

        //
        $filePath = storage_path("app/{$fileName}");

        $headers = ['Content-Type: test/plain'];

        // TODO: delete file somehow?
        // return \Storage::download($fileName, $fileName); // can't delete after download
        return response()->download($filePath, $fileName, $headers)->deleteFileAfterSend(true);
        // return response()->download($filePath, $fileName)->deleteFileAfterSend(true);

    }
}
