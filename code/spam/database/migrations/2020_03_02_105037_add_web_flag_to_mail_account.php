<?php

use Illuminate\Support\Facades\Schema;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Database\Migrations\Migration;

class AddWebFlagToMailAccount extends Migration
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
            $table->string('web_url', 1024)->default('');
            $table->string('web_login')->default('');
            $table->string('web_password')->default('');
            $table->boolean('web_alive', true)->default(false)->after('web_password');
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
            // $table->dropColumn(['web_url', 'web_login', 'web_password']);
            $table->dropColumn(['web_url', 'web_login', 'web_password', 'web_alive']);
        });
    }
}
