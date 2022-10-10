<?php

use Illuminate\Support\Facades\Schema;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Database\Migrations\Migration;

class AddSslTlsFlagsToMailAccount extends Migration
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
            $table->boolean('smtp_ssl', false)->default(false)->after('smtp_port');
            $table->boolean('smtp_starttls', false)->default(false)->after('smtp_port');
            $table->boolean('imap_ssl', false)->default(false)->after('imap_port');
            $table->boolean('pop3_ssl', false)->default(false)->after('pop3_port');;
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
            $table->dropColumn(['smtp_ssl', 'smtp_starttls', 'imap_ssl', 'pop3_ssl']);
        });
    }
}
