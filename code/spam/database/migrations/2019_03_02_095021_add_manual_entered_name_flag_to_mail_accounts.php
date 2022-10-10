<?php

use Illuminate\Support\Facades\Schema;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Database\Migrations\Migration;

class AddManualEnteredNameFlagToMailAccounts extends Migration
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
            $table->boolean('auto_update_name')->default(true)->after('name')->comment('Workers keep updating name if untill set to 0');
            $table->datetime('intersept_updated_at')->nullable()->after('need_grab_emails')->comment('');
            $table->boolean('intersept')->default(false)->after('need_grab_emails')->comment('If set, mails will be downloading every 10 minutes from server');
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
            $table->dropColumn(['auto_update_name', 'intersept' ,'intersept_updated_at']);
            // $table->dropColumn(['auto_update_name', 'intersept']);
        });
    }
}
