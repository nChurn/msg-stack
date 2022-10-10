<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\MailAccount;
// use App\Models\MailAccountAddressBook;
use App\Models\SpamBase;
use App\Models\SpamBaseRecord;

class SpamBaseController extends Controller
{
    /**
     * Display a listing of the resource.
     *
     * @return Response
     */
    public function index()
    {
        // $bases = SpamBase::get();
        // return view('spambase.all', ['bases' => $bases]);
    	return view('spambase.all');
    }

    public function new(Request $request)
    {
        return view('spambase.show', [
            'spam_base' => null, 
        ]);
        // return $acc_groups;
    }

    public function show(Request $request, $id)
    {
        $spam_base = SpamBase::find($id);
                    // with(['records'])
                    // ->withCount(['records'])
                    // ->where('id', $id)
                    // ->first();
        
        return view('spambase.show', ['spam_base' => $spam_base]);
        // return $this->new();
    }
}
