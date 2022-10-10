<?php

use Illuminate\Support\Facades\Schema;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Database\Migrations\Migration;

class AddFolderPathToMailDump extends Migration
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
            $table->string('folder_path', 1024)->after('msg_num')->default('');
            // crc32('folder_path');
            $table->string('fp_crc', 32)->default('');
            // can't create unique with folder_path - max key size limit
            // let's just hope that mails from diferent folder will have different timestamps
            // $table->unique(['mail_account_id', 'msg_num', 'fp_crc'], 'fp_unique');
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
            $table->dropColumn(['folder_path', 'fp_crc']);
            // DB::statement("ALTER TABLE `mail_dump` DROP INDEX `fp_unique`");
        });
    }
}
