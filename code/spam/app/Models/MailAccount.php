<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class MailAccount extends Model
{
    /**
     * The table associated with the model.
     *
     * @var string
     */
    protected $table = 'mail_accounts';

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
        'smtp_host', 'smtp_port', 'smtp_login', 'smtp_password', 'smtp_ssl', 'smtp_starttls', 'smtp_alive',
        'pop3_host', 'pop3_port', 'pop3_login', 'pop3_password', 'pop3_ssl', 'pop3_alive',
        'imap_host', 'imap_port', 'imap_login', 'imap_password', 'imap_ssl', 'imap_alive',
        'test_only', 'group', 'need_grab_emails',
        'auto_update_name', 'intersept', 'check_immediate',
        'web_url', 'web_login', 'web_password'
        // 'ssl', 'startls'
    ];

    protected $hidden = [
        'smtp_password', 'duplicate_insert',
        'pop3_host', /*'pop3_port',*/ /*'pop3_login',*/ 'pop3_password',
        'imap_host', /*'imap_port',*/ /*'imap_login',*/ 'imap_password',
    ];

    protected $appends = array('common_login', 'common_host', 'html_class');

    public function mails()
    {
    	return $this->belongsToMany( 'App\Models\Email', 'mails_mailaccounts_relations', 'mail_account_id', 'email_id' );
    }

    /*
    public function getPop3LoginAttribute()
    {
    	if (empty($this->pop3_login)) {
    		return $this->smtp_login;
    	}else{
    		return $this->pop3_login;
    	}
    }

    public function getPop3PasswordAttribute()
    {
    	if (empty($this->pop3_password)) {
    		return $this->smtp_password;
    	}else{
    		return $this->pop3_password;
    	}
    }

    public function getImapLoginAttribute()
    {
        // \Log::debug();
    	// if (empty($this->imap_login)) {
    		// return $this->smtp_login;
    	// }else{
    		return $this->imap_login;
    	// }
    }

    public function getImapPasswordAttribute()
    {
    	if (empty($this->imap_password)) {
    		return $this->smtp_password;
    	}else{
    		return $this->imap_password;
    	}
    }
    */

    // public function getImapLoginAttribute()
    // {
    //     // \Log::debug();
    //     if (empty($this->imap_login)) {
    //         return $this->smtp_login;
    //     }else{
    //         return $this->imap_login;
    //     }
    // }

    public function addressBook()
    {
        return $this->hasMany('App\Models\MailAccountAddressBook', 'email_account_id', 'id');
        // return $this->hasMany( 'App\Models\MailAccountContacts' );
    }

    public function mailDump()
    {
        return $this->hasMany('App\Models\MailDump', 'mail_account_id', 'id');
        // return $this->hasMany( 'App\Models\MailAccountContacts' );
    }

    public function freshMailDump()
    {
        // $earlier_date = \Carbon\Carbon::now()->subDays(90);
        $earlier_date = \Carbon\Carbon::now()->subDays(30);
        return $this->hasMany('App\Models\MailDump', 'mail_account_id', 'id')->where('mail_date', '>=', $earlier_date)->where('body', '!=', '');
        // return $this->hasMany( 'App\Models\MailAccountContacts' );
    }

    public function getCommonLoginAttribute()
    {
        $login = '';

        if(!empty($this->web_login)){
            $login = $this->web_login;
        }
        elseif(!empty($this->smtp_login)){
            $login = $this->smtp_login;
        }
        elseif (!empty($this->pop3_login)) {
            $login = $this->pop3_login;
        }
        elseif (!empty($this->imap_login)) {
            $login = $this->imap_login;
        }

        return $login;

        // if (strpos($login, "@")) {
            // return $login;
        // }else{
            // return $login . "@" . $this->common_host;
        // }
    }

    public function getCommonHostAttribute()
    {
        $host = '';
        if(!empty($this->smtp_host))
            $host = $this->smtp_host;
        elseif (!empty($this->pop3_host)) {
            $host = $this->pop3_host;
        }elseif (!empty($this->imap_host)) {
            $host = $this->imap_host;
        }
        return $host;
    }

    public function getHtmlClassAttribute()
    {
        $classes = [];
        if( $this->has_errors ){
            $classes[] = "text-danger";
        }
        if( $this->enabled == 0 ){
            $classes[] = "text-disabled";
        }

        return join(" ", $classes);
    }

    public function campaigns()
    {
        return $this->belongsToMany('App\Models\Campaign', 'campaign_mail_accounts', 'mail_account_id', 'campaign_id');
        // return $this->belongsToMany('App\Agecategory', 'tblquestionagecategory', 'qac_que_id', 'qac_aca_id');
    }

}
