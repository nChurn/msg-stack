<?php

use Illuminate\Support\Facades\Schema;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Database\Migrations\Migration;

class CreateEmailsTable extends Migration
{
    /**
     * Run the migrations.
     *
     * @return void
     */
    public function up()
    {
        // actually this IS a spam campaign
        Schema::create('campaign', function (Blueprint $table) {
            $table->increments('id');
            $table->string('name')->default('New campaign');
            $table->string('subject')->default('');
            $table->text('body')->default('');
            // will contain json data
            $table->text('headers')->default('');
            // will containt tmisetamp for scheduled spam letters
            $table->integer('status')->default(0)->comment('0 - created, 1 - started, 2 - paused, 3 - hibernated, 4 - complete');

            //total contacts to send mail, need for statistics, filled automatically when campaign starts/pauses
            $table->integer('total_emails')->default(0); 

            $table->timestamp('scheduled_to')->nullable();
            $table->timestamps();
            $table->timestamp('started_at')->default(DB::raw('CURRENT_TIMESTAMP'));
            $table->timestamp('finnished_at')->nullable();
        });
    }

    /**
     * Reverse the migrations.
     *
     * @return void
     */
    public function down()
    {
        Schema::dropIfExists('campaign');
        Schema::dropIfExists('emails');
    }
}
