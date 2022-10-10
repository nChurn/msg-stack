<?php

use Illuminate\Support\Facades\Schema;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Database\Migrations\Migration;

class AddEnabledToSpamBaseTable extends Migration
{
    /**
     * Run the migrations.
     *
     * @return void
     */
    public function up()
    {
        Schema::table('spam_base', function (Blueprint $table) {
            //
            $table->boolean('enable_automatics')->default(false);
        });
    }

    /**
     * Reverse the migrations.
     *
     * @return void
     */
    public function down()
    {
        Schema::table('spam_base', function (Blueprint $table) {
            //
            $table->dropColumn(['enable_automatics']);
        });
    }
}
