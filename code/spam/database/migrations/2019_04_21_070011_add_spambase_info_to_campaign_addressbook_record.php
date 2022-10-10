<?php

use Illuminate\Support\Facades\Schema;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Database\Migrations\Migration;

class AddSpambaseInfoToCampaignAddressbookRecord extends Migration
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
            $table->unsignedInteger('spam_base_record_id')->nullable()->after('mail_account_id');
            $table->foreign('spam_base_record_id')->references('id')->on('spam_base_record')->onDelete('set null');
            // 
            $table->unsignedInteger('spam_base_id')->nullable()->after('mail_account_id');
            $table->foreign('spam_base_id')->references('id')->on('spam_base')->onDelete('set null');
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
            $table->dropForeign(['spam_base_id']);
            $table->dropForeign(['spam_base_record_id']);
            $table->dropColumn(['spam_base_id', 'spam_base_record_id']);
            //
        });
    }
}
