<?php

use Illuminate\Support\Facades\Schema;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Database\Migrations\Migration;

class AddCheckedFieldToMailAccount extends Migration
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
            $table->dateTime('checked_at')->nullable()->default(null)->after('updated_at');
            $table->boolean('smtp_alive', true)->default(false)->after('smtp_password');
            $table->boolean('pop3_alive', true)->default(false)->after('pop3_password');
            $table->boolean('imap_alive', true)->default(false)->after('imap_password');
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
            $table->dropColumn(['checked_at', 'smtp_alive', 'pop3_alive', 'imap_alive']);
        });
    }
}
