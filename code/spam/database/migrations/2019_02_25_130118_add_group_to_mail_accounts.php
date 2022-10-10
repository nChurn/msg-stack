<?php

use Illuminate\Support\Facades\Schema;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Database\Migrations\Migration;

class AddGroupToMailAccounts extends Migration
{
    /**
     * Run the migrations.
     *
     * @return void
     */
    public function up()
    {
        Schema::table('mail_accounts', function (Blueprint $table) {
            //
            $table->string('group')->default('general');
            $table->unsignedTinyInteger('need_grab_emails')->default(0)->comment('1-yes,2-no');
        });
    }

    /**
     * Reverse the migrations.
     *
     * @return void
     */
    public function down()
    {
        Schema::table('mail_accounts', function (Blueprint $table) {
            //
            $table->dropColumn(['group', 'need_grab_emails']);
        });
    }
}
