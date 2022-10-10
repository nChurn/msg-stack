<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\MailAccount;
use App\Models\MailAccountAddressBook;
use App\Models\MailDump;
use Carbon\Carbon;
use App\Models\ScanRules;

class EmailAccountsController extends Controller
{
    //
    protected $test_only;

    public function __construct(Request $request) {
        $this->test_only = strpos($request->path(), 'mail_accs') !== false ? 0 : 1;
        $this->request = $request;
    }
    /**
     * Display a listing of the resource.
     *
     * @return Response
     */
    public function index()
    {
        $filter_group = ScanRules::select('group')->distinct()->get();
        $accs_group = MailAccount::select('group')->distinct()->get();
    	return view('email_accounts', ['test_only' => $this->test_only, 'filters' => $filter_group, 'groups' => $accs_group, 'group_radio' => true]);
    }

    public function addressbook($id)
    {
        $account = MailAccount::withCount('addressBook')->where('id', $id)->first();
        $addressbook = MailAccountAddressBook::where('email_account_id', $id)->paginate(50);
        $filter_group = ScanRules::select('group')->distinct()->get();
        // return $account;
        // return $addressbook;
        return view('email_accounts_addressbook', ['account' => $account, 'addressbook' => $addressbook, 'filters' => $filter_group]);
    }

    public function maildump($id)
    {
        $search = $this->request->input('search');

        $filters = [
            'search' => $search,
        ];

        $return_json = !empty($this->request->input('json'));

        $account = MailAccount::withCount('maildump')->where('id', $id)->first();
        $maildump = MailDump::select(['id', 'mail_account_id', 'msg_num', 'subject', 'from', 'to', 'need_body', 'has_attaches', 'mail_date'])
                        ->where('mail_account_id', $id)
                        ->when(!empty($search), function($query) use ($search ){
                            return $query->where(function($query) use ($search){
                                return $query->where('subject', 'like', '%'.$search.'%')
                                            ->orWhere('body', 'like', '%'.$search.'%')
                                            ->orWhere('from', 'like', '%'.$search.'%')
                                            ->orWhere('to', 'like', '%'.$search.'%');
                            });
                        })
                        ->orderBy('mail_date', 'desc')
                        ->paginate(50)
                        ->appends($filters);

        // return $account;
        // return $maildump;
        if($return_json){
            return response()->json([
                'success' => false, 
                'message' => 'Mail dump data',
                'data' => $maildump,
                'filters' => $filters
            ]);
        } else {
            return view('email_accounts_maildump', ['account' => $account, 'maildump' => $maildump]);
        }
    }



    public function massUpdate()
    {
        $action = $this->request->input('option');
        $ids = $this->request->input('ids');

        \Log::debug("EmailAccountsController::massUpdate");

        // $now = Carbon::now();
        // $socksTable = (new MailAccount())->getTable();
        if( $action == 'address_rule' ){
            $accounts = MailAccountAddressBook::whereIn('id', $ids)->get();
            foreach ($accounts as $account) {
                $data = [
                    "rule" => $account->address,
                    "exclude" => 1,
                    "enabled" => 1,
                ];
                $rule = ScanRules::create($data);
                if(!is_null($rule) && !empty($rule->id))
                {
                    $account->send_rule_id = $rule->id;
                    $account->save();
                }
            }

        }elseif( $action == 'host_rule' ){
            $accounts = MailAccountAddressBook::whereIn('id', $ids)->get();
            foreach ($accounts as $account) {
                $data = [
                    "rule" => explode("@", $account->address)[1],
                    "exclude" => 1,
                    "enabled" => 1,
                ];
                $rule = ScanRules::create($data);
                if(!is_null($rule) && !empty($rule->id))
                {
                    $account->send_rule_id = $rule->id;
                    $account->save();
                }
            }
        }elseif( $action == 'login_rule' ){
            $accounts = MailAccountAddressBook::whereIn('id', $ids)->get();
            foreach ($accounts as $account) {
                $data = [
                    "rule" => explode("@", $account->address)[0],
                    "exclude" => 1,
                    "enabled" => 1,
                ];
                $rule = ScanRules::create($data);
                if(!is_null($rule) && !empty($rule->id))
                {
                    $account->send_rule_id = $rule->id;
                    $account->save();
                }
            }
        }elseif( $action == 'remove_rule' ){
            $rules_ids = MailAccountAddressBook::whereIn('id', $ids)->whereNotNull('send_rule_id')->select('send_rule_id')->get()->toArray();
            ScanRules::whereIn('id', $rules_ids )->delete();
        }elseif( $action == 'delete' ) {
            MailAccountAddressBook::whereIn('id', $ids)->delete(); 
        }

        return response()->json(['success' => true, 'message' => 'Changes applied.']);
    }

    public function mailDumpMassUpdate()
    {
        $action = $this->request->input('option');
        $ids = $this->request->input('ids');

        \Log::debug("EmailAccountsController::mailDumpMassUpdate");

        if( $action == 'download' ){
            MailDump::whereIn("id", $ids)->update(['need_body' => 1]);
        }elseif ($action == 'undownload') {
            MailDump::whereIn("id", $ids)->update(['need_body' => 0]);
        }elseif ($action == 'delete') {
            MailDump::whereIn('id', $ids)->delete(); 
        }

        return response()->json(['success' => true, 'message' => 'Changes applied.']);
    }

    public function getMailDumpAttach($id, $att_num = null){
        $item = MailDump::where('id', $id)->first();

        \Log::debug("Download item");

        // $file = File::get("../resources/logs/$id");
        

        $attach_path = "";
        $exploded = explode(',', $item->attach_path);

        if( count($exploded) > 1 && is_null($att_num) ){
            // generate filepaths_array
            // $files = collect($exploded)->map(function($item){
            //     \Log::debug("exploded item:[{$item}]");
            //     return storage_path("app/" . $item);
            // })->toArray();
            
            // outer file
            $attach_path = storage_path('app/uploads/mail_dump_'.$id.'.zip');
            $files = storage_path('app/uploads/mail_dump_'.$id.'/');

            \Log::debug("EmailAccountsController::getMailDumpAttach attach_path:[$attach_path]");
            \Log::debug("EmailAccountsController::getMailDumpAttach files:");
            \Log::debug($files);

            $headers = ["Content-Type"=>"application/zip"];
            \Zipper::make($attach_path)
                ->add($files)
                ->close(); //files tobe zipped

            try{
                return response()->download($attach_path)->deleteFileAfterSend();
            }catch(\Exception $e){
                \Log::error("Download zip archive with attaches for maildump {$id} failed:" . $e->getMessage());
                return response()->view('errors.404', array(), 404);
            }
        }else{
            $headers = array(
                'Content-Type: application/octet-stream',
            );
            // get first element if not noted
            if(is_null($att_num)) $att_num = 0;
            
            $attach_path = storage_path("app/" . $exploded[$att_num]);
            $res = preg_match("/(\w+\.\w+)/i", $attach_path, $matches);

            try{
                return response()->download($attach_path);
            }catch(\Exception $e){
                \Log::error("Download single attach for maildump {$id} failed:" . $e->getMessage());
                return response()->view('errors.404', array(), 404);
            }
        }
    }

    // private function downloadZip($id)
    // {
    //     $headers = ["Content-Type"=>"application/zip"];
    //     $fileName = $id.".zip"; // name of zip
    //     Zipper::make(public_path('/documents/'.$id.'.zip')) //file path for zip file
    //             ->add(public_path()."/documents/".$id.'/')->close(); //files tobe zipped

    //     return response()
    //     ->download(public_path('/documents/'.$fileName),$fileName, $headers);
    // }
}
