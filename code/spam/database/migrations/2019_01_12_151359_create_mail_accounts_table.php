<?php

use Illuminate\Support\Facades\Schema;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Database\Migrations\Migration;

class CreateMailAccountsTable extends Migration
{
    /**
     * Run the migrations.
     *
     * @return void
     */
    public function up()
    {
        Schema::create('mail_accounts', function (Blueprint $table) {
            $table->increments('id');

            // SMTP
            $table->string('smtp_host')->default('');
            // SMTP uses port 25, but implicit SSL/TLS encrypted SMTP uses port 465.
            $table->integer('smtp_port')->default(0);
            // default, uses for smtp normally, but also for other methods, if special fields are not filled
            $table->string('smtp_login')->default('');
            $table->string('smtp_password')->default('');
            
            // POP3
            $table->string('pop3_host')->default('');
            // POP uses port 110, but implicit SSL/TLS encrypted POP uses port 995.
            $table->integer('pop3_port')->default(0);
            // in case if default log/pass incorrect
            $table->string('pop3_login')->default('');
            $table->string('pop3_password')->default('');

            // IMAP4
            $table->string('imap_host')->default('');
            // IMAP uses port 143, but implicit SSL/TLS encrypted IMAP uses port 993.
            $table->integer('imap_port')->default(0);
            // in case if default log/pass incorrect
            $table->string('imap_login')->default('');
            $table->string('imap_password')->default('');

            // make this pair unique, ot avoid double addings
            // $table->unique(['smtp_login', 'smtp_host', 'smtp_port']);
            $table->unique(['smtp_login', 'smtp_host', 'test_only']);

            // make this timestamp to retrive duplicates on attempt to insert
            $table->timestamp('duplicate_insert')->nullable();
            // enable disable, just in case
            $table->boolean('enabled', true)->default(false);
            // alive marks as fail when account catn get mails via pop3 or imap4 credentials
            // or when sending smtp is impossible through this account
            $table->boolean('alive', true)->default(true);
            // 
            $table->boolean('test_only')->default(false);

            $table->timestamps();

        });
    }

    /**
     * Reverse the migrations.
     *
     * @return void
     */
    public function down()
    {
        Schema::dropIfExists('mail_accounts');
    }
}
