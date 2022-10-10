<?php

namespace App\Http\Controllers\api;

use Illuminate\Http\Request;
use App\Http\Controllers\Controller;
use App\Models\CheckMailReceiver;

class CheckMailReceiverController extends Controller
{
    protected $request;

    public function __construct(Request $request) {
        $this->request = $request;
    }

    public function index()
    {
        //
        $data = CheckMailReceiver::first();
        
        if( is_null($data) ){
            $data = CheckMailReceiver::firstOrNew(['email' => '']);
        }

        return response()->json([
            'success' => true, 
            'message' => 'Complete receiver email.',
            'data' => $data
        ]);

    }


    //
    /**
     * Show the form for creating a new resource.
     *
     * @return Response
     */
    public function create()
    {
        //
    }

    /**
     * Store a newly created resource in storage.
     *
     * @return Response
     */
    public function store()
    {
        $mail = $this->request->input('cmr');

        // Create new model if not existed before, without creating database record
        $cmr = CheckMailReceiver::first();
        
        if( is_null($cmr) ){
            $cmr = CheckMailReceiver::firstOrNew(['email' => $mail]);
        }else{
            $cmr->email = $mail;
        }
        // update database
        $cmr->save();

        // sleep(10);
        return response()->json(['success' => true, 'message' => 'Check mail receiver successfully updated.']);
    }

    /**
     * Display the specified resource.
     *
     * @param  int  $id
     * @return Response
     */
    public function show($id)
    {
        //
    }

    /**
     * Show the form for editing the specified resource.
     *
     * @param  int  $id
     * @return Response
     */
    public function edit($id)
    {
        //
    }

    /**
     * Update the specified resource in storage.
     *
     * @param  int  $id
     * @return Response
     */
    public function update($id)
    {
        //
    }

    /**
     * Remove the specified resource from storage.
     *
     * @param  int  $id
     * @return Response
     */
    public function destroy($id)
    {
        //
    }
}
