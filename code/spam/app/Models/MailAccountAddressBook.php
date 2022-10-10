<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class MailAccountAddressBook extends Model
{
    //
    /**
     * The table associated with the model.
     *
     * @var string
     */
    protected $table = 'mail_account_addressbook';

    /**
     * Indicates if the model should be timestamped.
     *
     * @var bool
     */
    public $timestamps = true;

    /**
     * The attributes that are mass assignable.
     *
     * @var array
     */
    protected $fillable = [ 
        'address', 'name', 'email_account_id', 'send_rule_id', 'company', 'rest'
    ];

    public function mailAccount()
    {
    	// return $this->belongsTo( 'App\Models\MailAccount' );
    	return $this->belongsTo('App\Models\MailAccount', 'id', 'email_account_id');

    }
}
