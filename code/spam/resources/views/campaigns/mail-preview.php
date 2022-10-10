<div class="preview-html">
    <legend>Mail Preview</legend>
    <div class="form-group">
    	<label for="subject_preview">Subject:</label>
    	<input class="form-control" id="subject_preview" name="subject_preview" value="" type="text" disabled="disabled">
    </div>

    <div class="form-group d-none headers-preview">
        <label for="headers_preview">Headers:</label>
        <table class="table table-bordered table-sm table-striped table-headers-preview">
            <thead>
                <tr><th>Name</th><th>Value</th></tr>
            </thead>
            <tbody></tbody>
        </table>
    </div>

    <div class="form-group">
    	<label for="attach_name_preview">Attach:</label>
    	<input class="form-control" id="attach_name_preview" name="attach_name_preview" value="" type="text" disabled="disabled">
    </div>

    <div>
    	<label for="subject_preview">Body:</label>
        <iframe id="mailPreviewContainer" frameborder="1" style="width: 100%;"></iframe>
    </div>
</div>
