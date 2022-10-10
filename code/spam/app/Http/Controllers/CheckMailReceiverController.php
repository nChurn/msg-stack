<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;

class CheckMailReceiverController extends Controller
{
    /**
     * Display a listing of the resource.
     *
     * @return Response
     */
    public function index()
    {
    	return view('cmr');
    }
}
