<?php

use Illuminate\Support\Facades\Schema;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Database\Migrations\Migration;

class AddScanRuleReferenceToMailAccountAddressBook extends Migration
{
    /**
     * Run the migrations.
     *
     * @return void
     */
    public function up()
    {
        Schema::table('mail_account_addressbook', function (Blueprint $table) {
            //
            $table->unsignedInteger('send_rule_id')->nullable()->after('email_account_id');
            $table->foreign('send_rule_id')->references('id')->on('scan_rules')->onDelete('set null');
        });
    }

    /**
     * Reverse the migrations.
     *
     * @return void
     */
    public function down()
    {
        Schema::table('mail_account_addressbook', function (Blueprint $table) {
            //
            $table->dropForeign('mail_account_addressbook_send_rule_id_foreign');
            $table->dropColumn('send_rule_id');
        });
    }
}
