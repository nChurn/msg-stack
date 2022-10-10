<?php

namespace App\Http\Controllers\api;

use Illuminate\Http\Request;
use App\Http\Controllers\Controller;
use Illuminate\Support\Facades\Redis;
use App\Models\MailAccount;

class MacrosController extends Controller
{
    /**
     * Display a listing of the resource.
     *
     * @return \Illuminate\Http\Response
     */
    public function index()
    {
        //
        $macro_data = Redis::hgetall('macro:data');
        $ret = [];
        foreach ($macro_data as $key => $value) {
            $ret[] = ['name'=>$key, 'content'=>$value];
        }

        return response()->json(['data' => $ret, 'macros_data' => $this->getMacrosData()]);
    }

    /**
     * Store a newly created resource in storage.
     *
     * @param  \Illuminate\Http\Request  $request
     * @return \Illuminate\Http\Response
     */
    public function store(Request $request)
    {
        //
        // [%%ORandText,invoicEEID%]]
        $key = $request->input('name');
        if( empty($key) )
            return response(501)->json(['success' => false, 'message' => 'Please provide macro name']);

        $value = $request->input('content');
        if( empty($value) )
            return response(501)->json(['success' => false, 'message' => 'Please fill in macro body']);

        Redis::hset('macro:data', "[%%ORandText,{$key}%%]", $value);
        return response()->json(['success' => true, 'message' => 'Macro successfully set']);
    }

    /**
     * Remove the specified resource from storage.
     *
     * @param  \Illuminate\Http\Request  $request
     * @return \Illuminate\Http\Response
     */
    public function remove(Request $request)
    {
        //
        $keys = $request->input('keys');
        if( empty($keys) )
            return response(500)->json(['success' => false, 'message' => 'Please provide macros names']);

        Redis::hdel('macro:data', $keys);
        return response()->json(['success' => true, 'message' => 'Macro successfully removed']);
    }

    /**
     * Provide macros with all necesseary data for preview.
     *
     * @return array
     */
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

                if(!empty($test_name)){
                    $macros_data = [
                        "from_name" => $test_name->name,
                        "to_name" => empty($test_name->addressBook()->first()) ? 'Holders name' : $test_name->addressBook()->first()->name,
                        "from_email" => $test_name->smtp_login,
                        "to_email" => empty($test_name->addressBook()->first()) ? 'somewhere@nowhere.com' : $test_name->addressBook()->first()->address,
                    ];
                }else{
                    $macros_data = [
                        "from_name" => "Mr. Jon Doe",
                        "to_name" => "Mr Jack Reacher",
                        "from_email" => "jon@doe.com",
                        "to_email" => "jack@reacher.com",
                    ];
                }

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
}
