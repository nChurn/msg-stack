<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class SpamBaseRecord extends Model
{
    /**
     * The table associated with the model.
     *
     * @var string
     */
    protected $table = 'spam_base_record';

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
    protected $fillable = ['name', 'address', 'spam_base_id', 'email_account_id'];

    // protected $casts = [
    //     'filters' => 'array',
    // ];

    public function base()
    {
    	return $this->belongsTo( 'App\Models\SpamBase' );
    }
}
