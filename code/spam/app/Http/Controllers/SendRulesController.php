<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use \App\Models\ScanRules;

class SendRulesController extends Controller
{
    /**
     * Display a listing of the resource.
     *
     * @return Response
     */
    public function index()
    {
        $filter_group = ScanRules::select('group')->distinct()->get();
    	return view('send_rules', ['filters' => $filter_group]);
    }
}
