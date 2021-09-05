var formVue = {
    data() {
        return {
            options: [{}],
            value: '',
            tempOptions: [{}]
        }
    },
    methods: {
        selected(reportId){
            if (sbm){
                window.location.href = '/report/'+reportId+'?sbm='+sbm;
            }else{
                window.location.href = '/report/'+reportId;
            }

        }
    },
    mounted() {
        this.options = []
        for (const option_pair of Object.values(row_options)) {
            // console.log("value: "+value);
            this.options.push({key: Object.keys(option_pair)[0], value: Object.values(option_pair)[0]});
        }
        this.tempOptions = Object.assign({}, this.options);
    }
};

// 这里更改了Vue的分隔符识别，{{ }}和jinja冲突
Vue.options.delimiters = ['{*', '*}'];
var form = Vue.extend(formVue);
//这里是vue加载到html的id位置
new form().$mount('#report')
