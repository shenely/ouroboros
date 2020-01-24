var obDatum = Vue.component("ob-datum", {
    props: {
        name: [String, Number],
        value: null
    },
    render: function (createElement) {
        if (typeof this.value == "number") {
            var data = {
                props: {
                    value: this.value
                }
            };
            return createElement("ob-number", data, []);
        } else if (typeof this.value == "string") {
            var data = {
                props: {
                    value: this.value
                }
            };
            return createElement("ob-string", data, []);
        } else if (typeof this.value == "object") {
            var key = Object.keys(this.value)[0];
            if (this.$stone.hasOwnProperty(key)) {
                var data = {
                    props: {
                        value: this.value[key]
                    }
                };
                return createElement(this.$stone[key], data, []);
            }
        }
    }
});

obDatum.prototype.$stone = {};

var obNumber = Vue.component("ob-number", {
    template: `<input type="number" step="any" disabled 
       v-bind:value="value" />`,
    props: {
        value: Number
    }
});

var obNumber = Vue.component("ob-string", {
    template: `
<input type="text" disabled
       v-bind:value="value" />`,
    props: {
        value: String
    }
});
