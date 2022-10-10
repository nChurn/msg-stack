<?php

use Illuminate\Support\Facades\Schema;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Database\Migrations\Migration;

class AddCompanyAndRestToSpamBaseRecord extends Migration
{
    /**
     * Run the migrations.
     *
     * @return void
     */
    public function up()
    {
        Schema::table('spam_base_record', function (Blueprint $table) {
            //
            $table->string('rest')->default('')->after('name');
            $table->string('company')->default('')->after('name');

            $table->unsignedInteger('mail_account_addressbook_id')->nullable();
            $table->foreign('mail_account_addressbook_id')->references('id')->on('mail_account_addressbook')->onDelete('set null');
        });
    }

    /**
     * Reverse the migrations.
     *
     * @return void
     */
    public function down()
    {
        Schema::table('spam_base_record', function (Blueprint $table) {
            $table->dropForeign(['mail_account_addressbook_id']);
            $table->dropColumn(['company', 'rest', 'mail_account_addressbook_id']);
        });
    }
}
