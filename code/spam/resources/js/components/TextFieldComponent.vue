<template>
    <div class="form-group">
        <label for="search_input">{{label_text}}</label>
        <input class="form-control py-2" v-model="text_input" v-bind:id="text_input_id" name="text_input" type="text_input" v-on:keyup.enter="submitInput">
        </div>
    </div>
</template>

<script>
    export default {
        props: ['label_text', 'text_input_id'],
        data:function (){
            return {
                text_input: '',
                // text_input_id: ''
            }
        },
        mounted() {
            console.log('TextField Component mounted.')
        },
        methods: {
            submitInput: function(evt){
                // console.log('searchComponent:', this.search);
                // console.log('searchComponent:', evt);
                this.$root.$emit('append-text-input', evt, this.search);
                EventBus.$emit('append-text-input', evt, this.search);

            }
        }
    }
</script>
