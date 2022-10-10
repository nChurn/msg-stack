<?php

namespace App\Http\Controllers\api;

use Illuminate\Http\Request;
use App\Http\Controllers\Controller;
use App\Models\ScanRules;

class SendRulesController extends Controller
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
        $data = ScanRules::all();
        return response()->json([
            'success' => true, 
            'message' => 'Complete rules list.',
            'data' => $data
        ]);
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
     * @return \Illuminate\Http\Response
     */
    public function store()
    {
        //
        $data = [];

        $items_list = explode("\n", $this->request->input('scan_rules'));

        $group = $this->request->input('group');

        if(count($items_list) < 1)
            return response()->json(['success' => false, 'message' => 'No rules is sent.']);

        $now = \Carbon\Carbon::now();
        foreach ($items_list as $rule) {
            # code...
            $rule = trim( $rule );
            if(empty($rule)) continue;

            // preg_match_all('/\/(\S+)\/([+-])((dis)|(en))/', $rule, $matches);

            // if(count($matches) < 3) {
            //     \Log::debug("Rule parsing give incorrect result for string:[{$rule}]");
            //     continue 1;
            // }

            $data[] = [
                // "rule" => $matches[1][0],
                "rule" => $rule,
                "group" => $group,
                "exclude" => 1,
                "enabled" => 1,
                "created_at" => $now,
                "updated_at" => $now
            ];

        }


        if( count($data) > 0 )
            ScanRules::insertIgnore($data); // Eloquent approach

        // sleep(10);
        
        return response()->json(['success' => true, 'message' => 'Rules are inserted. New tasks will include those rules in mail grabbing.']);
    }

    public function massUpdate()
    {
        $action = $this->request->input('option');
        $ids = $this->request->input('ids');

        // $socksTable = (new ScanRules())->getTable();
        if( $action == 'enable' ){
            ScanRules::whereIn('id', $ids)->update(array('enabled' => 1));
        }elseif ($action == 'disable') {
            ScanRules::whereIn('id', $ids)->update(array('enabled' => 0));
        }elseif ($action == 'set-exclude') {
            ScanRules::whereIn('id', $ids)->update(array('exclude' => 1));
        }elseif ($action == 'set-include') {
            ScanRules::whereIn('id', $ids)->update(array('exclude' => 0));
        }elseif ($action == 'delete') {
            ScanRules::whereIn('id', $ids)->delete(); 
        }

        return response()->json(['success' => true, 'message' => 'Changes applied.']);

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
        //
        $rule = ScanRules::where('id', $id)->first();
        if( is_null($reult) ){
            return response()->json(['success' => false, 'message' => 'Rule not found.']);
        }

        // maybe there's better way to update, but this one is easiest
        $rule->rule = $this->request->input('rule');
        $rule->exclude = $this->request->input('exclude');
        $rule->is_active = $this->request->input('is_active');
        $rule->save();

        return response()->json(['success' => true, 'message' => 'Rule updated successfully.']);
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
        ScanRules::where('id', $id)->delete(); 
        return response()->json(['success' => true, 'message' => 'Rule deleted successfully.']);

    }

}
