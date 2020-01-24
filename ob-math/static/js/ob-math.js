var obArray = Vue.component("ob-array", {
    template: `<ul>
    <li is="ob-datum"
        v-for="d in value"
        v-bind:value="d">
    </li>
</ul>`,
    props: {
        value: Number
    }
});

obDatum.prototype.$stone[".vec#vector"] = "ob-array"
