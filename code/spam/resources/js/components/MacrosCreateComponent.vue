<template>
    <div class="new-macro-container">
        <div class="row mb-3">
            <div class="col-12">
                <label for="macro_name">Name:</label>
            </div>
            <div class="col-2">
                <input class="form-control form-control-sm" v-model="macro_name" name="macro_name" type="text" :disabled="isUploading" />
            </div>
        </div>
        <div class="row">
            <div class="col-12">
                <label for="macro_name">Content:</label>
            </div>
            <div class="col-4">
                <textarea class="form-control form-control-sm" v-model="macro_content" name="macro_content" :disabled="isUploading"></textarea>
            </div>
        </div>

        <div class="row mt-3">
          <div class="col-4">
            <button id="upload" name="upload" class="btn btn-info" v-on:click="setNewMacro($event)">Create</button>
          </div>
        </div>
    </div>
</template>
<script>
export default {
    props: {
        'api_url': String,
        'mac_id': {
            type: String,
            default: "1"
        },
        'macro_created': {
            type: String,
            default: 'macros-created-{mac_id}'
        },
    },
    data: function() {
        return {
            macro_name: "",
            macro_content: "",
            isUploading: false
        }
    },
    methods: {
        showRequestError(error) {
            var message = error.response.statusText;
            if (error.response.data && typeof error.response.data == 'object') {
                var err_data = error.response.data;
                if (err_data.message) {
                    message = err_data.message;
                }
                if (err_data.file) {
                    message += "\nFile:" + err_data.file;
                }
                if (err_data.line) {
                    message += "\nLine:" + err_data.line;
                }
            }

            this.$toast.error({
                title: 'Error',
                message: message,
                position: 'top right',
                timeOut: 7000,
                progressBar: false,
                hideDuration: 500
            });
        },

        showRequestSuccess(response, title) {
            if (!title) title = "Success";

            this.$toast.success({
                title: title,
                message: response.data.message,
                position: 'top right',
                timeOut: 3500,
                progressBar: false,
                hideDuration: 500
            });
        },

        setNewMacro(evt){
            var formData = new FormData();
            // console.log('setNewMacro fired?');

            // process other vars
            formData.append("name", this.macro_name);
            formData.append("content", this.macro_content);

            if(this.macro_name.length<3){
                this.showRequestError({'response':{'statusText':'Provide name for macro'}});
                return false;
            }

            if(this.macro_content.length<3){
                this.showRequestError({'response':{'statusText':'Provide name for macro'}});
                return false;
            }

            var data = formData;
            var url = this.api_url;

            this.$toast.info({
                title: 'Setting macro',
                message: "Please wait",
                position: 'top right',
                timeOut: 20000,
                progressBar: true,
                hideDuration: 0,
            });

            // var form_headers = {'Content-Type': 'multipart/form-data', ''};

            this.isUploading = true;
            // this.$http.post(url, formData, {headers: form_headers})
            this.$http.post(url, formData)
                .then((response) => {
                    this.$toast.removeAll();
                    this.showRequestSuccess(response);
                }).catch((error) => {
                    this.$toast.removeAll();
                    this.showRequestError(error);
                })
                .then(() => {
                    // this.$toast.removeAll();
                    this.isUploading = false;
                    EventBus.$emit(this.macro_created, evt);
                });
        },

    }
}

</script>
