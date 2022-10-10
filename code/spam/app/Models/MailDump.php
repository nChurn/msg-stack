<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class MailDump extends Model
{
    //
    /**
     * The table associated with the model.
     *
     * @var string
     */
    protected $table = 'mail_dump';

    /**
     * Indicates if the model should be timestamped.
     *
     * @var bool
     */
    public $timestamps = false;

    /**
     * The attributes that are mass assignable.
     *
     * @var array
     */
    protected $fillable = [
        'subject', 'body', 'mail_account_id', 'msg_num', 'need_body', 'from', 'to', 'headers'
    ];

    public function mailAccount()
    {
    	// return $this->belongsTo( 'App\Models\MailAccount' );
    	return $this->belongsTo('App\Models\MailAccount', 'id', 'mail_account_id');

    }
}
