var obItem = Vue.component("ob-item", {
    template: `<div>
<h3>{{ name }}</h3>
<ob-datum v-for="d in data"
          v-bind:key="d.key"
          v-bind:name="d.key"
          v-bind:value="d.value">
</ob-datum>
<ul>
    <li v-for="c in ctrl">{{ c.key }}: {{ c.value }}</li>
</ul>
</div>`,
    props: {
        name: [String, Number],
        data: Array,
        ctrl: Array
    }
});
