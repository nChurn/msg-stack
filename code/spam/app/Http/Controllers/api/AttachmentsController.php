<?php

namespace App\Http\Controllers\api;

use Illuminate\Http\Request;
use App\Http\Controllers\Controller;

use App\Models\Attachement;
use Carbon\Carbon;

class AttachmentsController extends Controller
{

    public function __construct(Request $request) {
        $this->request = $request;
    }
    /**
     * Display a listing of the resource.
     *
     * @return Response
     */
    public function index()
    {
        // $inputs = $this->request->only(['search_text', 'selected_group', 'used_less', 'used_more', 'order_by', 'order_direction', 'per_page']);

        $groups = Attachement::select('group')->distinct()->get();

        $filters = [];

        $per_page = $this->request->input('atts_per_page')?:50;
        $order_by = $this->request->input('atts_order_by')?:null;
        $order_direction = $this->request->input('atts_order_direction')?:null;

        $selected_group = $this->request->input('att_selected_groups')?:null;
        if ( $selected_group == '' ) $selected_group = null;


        $attachments = Attachement::
                        when((!empty($selected_group)), function($query) use ($selected_group){
                            return $query->whereIn('group', explode(",", $selected_group));
                        })
                        ->when(!empty($order_by), function($query) use ($order_by, $order_direction){
                            return $query->orderBy($order_by, $order_direction);
                        })
                        // ->setPageName('atts_page')
                        ->paginate($per_page, ['*'], 'atts_page')
                        // ->appends($filters)
                        ;

        return response()->json(['success' => true, 'message' => '', 'data' => ['groups' => $groups, 'attachments' => $attachments]]);
    }

    public function groups()
    {
        $groups = Attachement::select('group')->distinct()->get();
        return response()->json(['success' => true, 'message' => '', 'data' => ['groups' => $groups]]);
    }

    public function create()
    {
        $input = $this->request->only(['selected_group', 'group_clear']);

        // process group name
        $group = 'general';
        if(!empty($input['selected_group'])){
            $group = $input['selected_group'];
            \Log::debug("Gt group:" . $group);
        }else{
            \Log::debug("No group:" . json_encode($input));
        }

        // remove all items in group if needed
        if(!empty($input['group_clear']) && $input['group_clear'] !== 'false' && $input['group_clear'] !== false){
            \Log::debug("clear all atts from that group:" . $input['group_clear']);
            Attachement::where('group', $group)->delete();
        }else{
            \Log::debug("Skip clear all atts from that group");
        }

        $attacheTable = (new Attachement())->getTable();
        foreach ($this->request->attachements as $file) {
            // $filename = $file->store('uploads');
            $filename = $file->getClientOriginalName();
            $filepath = $file->path();
            $filesize = filesize($filepath);
            $client_name = $file->getClientOriginalName();
            $client_extension = $file->getClientOriginalExtension();

            $inserted_id = \DB::table($attacheTable)->insertGetId([
                "campaign_id" => 0,
                "group" => $group,
                "data" => file_get_contents($filepath),
                "name" => $client_name,
                "path" => $filename,
                "size" => $filesize,
                "created_at" => \Carbon\Carbon::now(),
                "updated_at" => \Carbon\Carbon::now(),
            ]);

            // \Log::debug("Try to remove file:$filepath");
            // remove attachement after upload
            unlink($filepath);

        }

        return response()->json(['success' => true, 'message' => 'All attachements are added']);
    }

    public function delete()
    {
        $inputs = $this->request->only(['ids', 'groups']);

        if(!empty($inputs['ids']))
            Attachement::whereIn('id', $inputs['ids'])->delete();

        if(!empty($inputs['groups']))
            Attachement::whereIn('group', $inputs['groups'])->delete();

        return response()->json(['success' => true, 'message' => 'Attachement removed']);
    }

    public function update($id)
    {
        $attach = Attachement::find($id);

        if(is_null($attach))
            return response()->json(['success' => false, 'message' => 'Attachement not found']);

        // actually we will have only one file, but it's easier to me
        foreach ($this->request->attachements as $file) {
            $filename = $file->store('uploads');
            $filepath = $file->path();
            $filesize = filesize($filepath);

            $attach->data = file_get_contents($filepath);
            $attach->size = $filesize;

            unlink($filepath);
        }

        $attach->save();

        return response()->json(['success' => true, 'message' => 'Attachement updated']);
    }

}
