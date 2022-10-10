<?php

use Illuminate\Support\Facades\Schema;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Database\Migrations\Migration;

class ChangeSubjectSizeForMailDumpTable extends Migration
{
    /**
     * Run the migrations.
     *
     * @return void
     */
    public function up()
    {
        Schema::table('mail_dump', function (Blueprint $table) {
            // $table->unsignedTinyInteger('need_body')->default(0)->comment('0-no, 1-awaiting, 2-downloaded')->change();
            DB::statement("ALTER TABLE mail_dump CHANGE COLUMN subject subject VARCHAR(1024)");
            // DumbFuck doctrine doesn't know unsigned tiny integer type...
            DB::statement("ALTER TABLE mail_dump CHANGE COLUMN need_body need_body TINYINT UNSIGNED DEFAULT 0 NOT NULL COMMENT '0-no, 1-awaiting, 2-downloaded'");
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
        });
    }
}
