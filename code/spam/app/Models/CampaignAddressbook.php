<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class CampaignAddressbook extends Model
{
    /**
     * The table associated with the model.
     *
     * @var string
     */
    protected $table = 'campaign_addressbook';

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
    protected $fillable = ['campaign_id', 'mail_account_addressbook_id', 'mail_account_id', 'address', 'record_status', 'record_status_txt', 'error_log'];

    public function campaign()
    {
    	return $this->belongsTo( 'App\Models\Campaign' );
    }

    public function account()
    {
        return $this->belongsTo( 'App\Models\MailAccount', 'mail_account_id', 'id' );
    }

    public function getRecordStatusTxtArrayAttribute()
    {
        // return str_replace('\r\n', "<br>", $this->record_status_txt);
        $arr = explode("\n", str_replace('\r\n', "", $this->record_status_txt) );
        return $arr;
        // return "<div>" . join("</div><div>", $arr) . "</div>";
    }
}
