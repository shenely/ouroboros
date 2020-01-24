var ouroboros = Vue.component("ouroboros", {
    template: `<div>
<h1>ouroboros</h1>
<ob-model v-for="model in models"
          v-bind:key="model.name"
          v-bind:name="model.name"
          v-bind:items="model.items">
</ob-model>
</div>`,
    data: function () {
        return {
            models: Array()
        };
    },
    created: function () {
        this.stream = new WebSocket("ws://localhost:8888/ob-io-stream/");
    },
    mounted: function () {
        var self = this;
        this.stream.onmessage = function (event) {
            console.log(event.data);
            self.models = JSON.parse(event.data);
        };
    },
    destroyed: function () {
        this.stream.close();
    }
});
