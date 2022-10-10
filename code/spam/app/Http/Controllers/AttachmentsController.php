<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\Attachement;
use Carbon\Carbon;

class AttachmentsController extends Controller
{
    //
    protected $test_only;

    public function __construct(Request $request) {
        $this->request = $request;
    }
    /**
     * Display a listing of the resource.
     *
     * @return Response
     */
    public function index()
    {
        // $groups = Attachement::select('group')->distinct()->get();
    	return view('attachments');
    }
}
