<?php

use Illuminate\Support\Facades\Schema;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Database\Migrations\Migration;

class AddExtraFieldsToCampaignAddressbook extends Migration
{
    /**
     * Run the migrations.
     *
     * @return void
     */
    public function up()
    {
        Schema::table('campaign_addressbook', function (Blueprint $table) {
            //
            $table->string('rest')->default('')->after('address');
            $table->string('company')->default('')->after('address');
            $table->string('name')->default('')->after('address');
        });
    }

    /**
     * Reverse the migrations.
     *
     * @return void
     */
    public function down()
    {
        Schema::table('campaign_addressbook', function (Blueprint $table) {
            //
            $table->dropColumn(['company', 'rest', 'name']);
        });
    }
}
