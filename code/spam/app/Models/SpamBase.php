<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class SpamBase extends Model
{
    /**
     * The table associated with the model.
     *
     * @var string
     */
    protected $table = 'spam_base';

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
    protected $fillable = ['name', 'filters', 'enable_automatics'];

    // protected $appends = ['selected_ids'];

    public function records()
    {
    	return $this->hasMany( 'App\Models\SpamBaseRecord', 'spam_base_id', 'id' );
    }

    //
    public function getFiltersAttribute()
    {
        $filters = $this->attributes['filters'];
        if(empty($filters))
            return collect([]);
        else
            return collect(explode(",", $filters));
    }

    // assume we put array as argument
    public function setFiltersAttribute($new_filters)
    {
        // TODO: can this be collectins and not pure array?
        if(is_string($new_filters))
            $this->attributes['filters'] = $new_filters;
        elseif (is_array($new_filters)) {
            $this->attributes['filters'] = implode(",", $new_filters);
            # code...
        }
    }

    public function getSelectedIdsAttribute()
    {
        return  $this->records()->select('email_account_id')->distinct()->get()->map(function($item){ return $item->email_account_id;});
    }
}
