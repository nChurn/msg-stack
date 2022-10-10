<?php

use Illuminate\Support\Facades\Schema;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Database\Migrations\Migration;

class AddCountersForMailAccounts extends Migration
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
            $table->integer('mail_dumps')->default(0)->comment('send test message once in N')->unsigned();
            $table->integer('addresses')->default(0)->comment('send test message once in N')->unsigned();
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
            $table->dropColumn(['mail_dumps', 'addresses']);
        });
    }
}
