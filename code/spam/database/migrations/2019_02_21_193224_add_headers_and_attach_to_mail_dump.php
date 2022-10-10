<?php

use Illuminate\Support\Facades\Schema;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Database\Migrations\Migration;

class AddHeadersAndAttachToMailDump extends Migration
{
    /**
     * Run the migrations.
     *
     * @return void
     */
    public function up()
    {
        Schema::table('mail_dump', function (Blueprint $table) {
            // 
            $table->text('headers')->default('')->after('mail_account_id');
            $table->unsignedTinyInteger('has_attaches')->default(0)->comment('0-definetly no, 1-possible has, 2-definetly yes');
            $table->text('attach_path')->default('');
            $table->dateTime('mail_date')->nullable();
        });
    }

    /**
     * Reverse the migrations.
     *
     * @return void
     */
    public function down()
    {
        Schema::table('mail_dump', function (Blueprint $table) {
            // 
            $table->dropColumn(['headers', 'has_attaches', 'attach_path', 'mail_date']);
        });
    }
}
