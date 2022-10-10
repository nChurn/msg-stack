<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Support\Facades\Redis;

class Campaign extends Model
{
    /**
     * The table associated with the model.
     *
     * @var string
     */
    protected $table = 'campaign';

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
    protected $fillable = ['name', 'subject', 'body', 'headers', 'scheduled_to', 'status', 'workers', 'total_emails', 'is_html', 'filters', 'attach_name', 'account_name', 'reply_mode', 'reply_days', 'scheduled'];

    // protected $casts = [
    //     'filters' => 'array',
    // ];

    public function addressBook()
    {
    	return $this->hasMany( 'App\Models\CampaignAddressbook' );
    }

    public function addressBookProcessing()
    {
        return $this->hasMany( 'App\Models\CampaignAddressbook' )->where('record_status', config('campaign.record_status.processing'));
    }

    public function addressBookSuccess()
    {
        return $this->hasMany( 'App\Models\CampaignAddressbook' )->where('record_status', config('campaign.record_status.success'));
    }

    public function addressBookFail()
    {
        return $this->hasMany( 'App\Models\CampaignAddressbook' )->where('record_status', config('campaign.record_status.fail'));
    }

    public function addressBookSkip()
    {
        return $this->hasMany( 'App\Models\CampaignAddressbook' )->where('record_status', config('campaign.record_status.skip'));
    }

    public function addressBookBlacklist()
    {
        return $this->hasMany( 'App\Models\CampaignAddressbook' )->where('record_status', config('campaign.record_status.blacklist'));
    }

    public function addressBookAwait()
    {
        return $this->hasMany( 'App\Models\CampaignAddressbook' )->where('record_status', config('campaign.record_status.await'));
    }

    public function attachements()
    {
        return $this->belongsToMany( 'App\Models\Attachement' );
    }

    public function accounts()
    {
        // return $this->belongsToMany( 'App\Models\MailAccount' );
        return $this->belongsToMany('App\Models\MailAccount', 'campaign_mail_accounts', 'campaign_id', 'mail_account_id');
    }

    // public function accountAddressBook()
    // {
    //     return $this->hasManyThrough(
    //         'App\Models\MailAccount',
    //         'App\Models\CampaignAddressbook',
    //         'acmpaign_id', // Foreign key on accounts table...
    //         'email_account_id' // Foreign key on posts table...
    //         'id', // Local key on countries table...
    //         'id' // Local key on accounts table...
    //     );
    // }

    public function getAllAmountAttribute()
    {
        // count all
        $total = 0;
        $id = $this->attributes['id'];
        foreach (config('campaign.record_status') as $key => $value){
            // $total += Redis::lLen("campaign:{$id}:records:{$value}");
            $total += Redis::scard("campaign:{$id}:records:{$value}");
        }

        return $total;
    }

    public function getAwaitAmountAttribute()
    {
        $id = $this->attributes['id'];
        // return Redis::lLen("campaign:{$id}:records:".config('campaign.record_status.await'));
        return Redis::scard("campaign:{$id}:records:".config('campaign.record_status.await'));
    }

    public function getProcessingAmountAttribute()
    {
        $id = $this->attributes['id'];
        // return Redis::lLen("campaign:{$id}:records:".config('campaign.record_status.processing'));
        return Redis::scard("campaign:{$id}:records:".config('campaign.record_status.processing'));
    }

    public function getSuccessAmountAttribute()
    {
        $id = $this->attributes['id'];
        // return Redis::lLen("campaign:{$id}:records:".config('campaign.record_status.success'));
        return Redis::scard("campaign:{$id}:records:".config('campaign.record_status.success'));
    }

    public function getFailAmountAttribute()
    {
        $id = $this->attributes['id'];
        // return Redis::lLen("campaign:{$id}:records:".config('campaign.record_status.fail'));
        return Redis::scard("campaign:{$id}:records:".config('campaign.record_status.fail'));
    }

    public function getSkipAmountAttribute()
    {
        $id = $this->attributes['id'];
        // return Redis::lLen("campaign:{$id}:records:".config('campaign.record_status.skip'));
        return Redis::scard("campaign:{$id}:records:".config('campaign.record_status.skip'));
    }

    public function getBlacklistAmountAttribute()
    {
        $id = $this->attributes['id'];
        // return Redis::lLen("campaign:{$id}:records:".config('campaign.record_status.blacklist'));
        return Redis::scard("campaign:{$id}:records:".config('campaign.record_status.blacklist'));
    }



    public function getHeadersAttribute()
    {
        $headers = $this->attributes['headers'];
        // return $this->attributes['headers'];
        if( empty($headers) )
            return [];
        else
            return json_decode($headers);
    }

    public function getFiltersAttribute()
    {
        $filters = $this->attributes['filters'];
        if(empty($filters))
            return collect([]);
        else
            return collect(explode(",", $filters));
    }

    // assume we pu array as argument
    public function setFiltersAttribute($new_filters)
    {
        // TODO: can this be collectins and not pure array?
        $this->attributes['filters'] = implode(",", $new_filters);
    }

    public function getEfficiencyAttribute()
    {
        $number = 0;
        if( $this->success_amount > 0 && $this->all_amount > 0 )
            $number = $this->success_amount / $this->all_amount * 100;
        // if( $this->addressBook()->count() > 0 )
        // {
        //     $number = $this->addressBookSuccess()->count() / $this->addressBook()->count() * 100;
        // }
        return number_format((float)$number, 2, '.', '');
    }

    public function getSpamBaseIdsAttribute()
    {
        $id = $this->attributes['id'];
        $spambase_key = "campaign:{$id}:spambases";
        $members = Redis::smembers($spambase_key);
        if( empty($members))
            $members = [];
        return collect($members);
        // return $this->addressBook()->whereNotNull('spam_base_id')->select('spam_base_id')->distinct()->get()->map(function($item){return $item->spam_base_id;});
    }

    public function getMailAccountIdsAttribute()
    {

        return $this->accounts()->select('mail_account_id')->get()->map(function($item){return $item->mail_account_id;});
        // return $this->addressBook()->count();//->whereNotNull('mail_account_id')->select('mail_account_id')->distinct()->get()->map(function($item){return $item->mail_account_id;});
    }
}
