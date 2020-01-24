var obModel = Vue.component("ob-model", {
    template: `<div>
<h2>{{ name }}</h2>
<ob-item v-for="item in items"
         v-bind:key="item.key"
         v-bind:name="item.key"
         v-bind:data="item.data"
         v-bind:ctrl="item.ctrl">
</ob-item>
</div>`,
    props: {
        name: [String, Number],
        items: Array
    }
});
