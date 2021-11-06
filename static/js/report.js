var formVue = {
    data() {
        return {
            options: [{}],
            value: '',
            tempOptions: [{}],
            major_structure: [],
            group_structure: {},
            more: false, //是否显示全部单病种
        }
    },
    methods: {
        selected(reportId) {
            if (sbm) {
                window.location.href = '/report/' + reportId + '?sbm=' + sbm;
            } else {
                window.location.href = '/report/' + reportId;
            }

        },
        inReportStructure(item) {
            //检查此小项是否存在
            return this.major_structure.includes(item);
        },
        majorInReport(major) {
            //检查此大项病种是否需要显示
            // console.log(this.major_structure)
            // console.log(this.group_structure)
            return Object.keys(this.group_structure[major]).filter(item => this.major_structure.includes(item)).length > 0

        },
        showMore() {
            this.more = true;
            this.$forceUpdate();
        }
    },
    mounted() {
        this.options = []
        for (let pair of Object.values(groupStructure)) {
            for (let children in pair) {
                this.options.push({key: children, value: pair[children]})
            }
        }
        this.tempOptions = Object.assign({}, this.options);
    },
    created() {
        this.major_structure = Object.assign([], reportStructure);
        this.group_structure = Object.assign({}, groupStructure);

    }
};

// 这里更改了Vue的分隔符识别，{{ }}和jinja冲突
Vue.options.delimiters = ['{*', '*}'];
var form = Vue.extend(formVue);
//这里是vue加载到html的id位置
new form().$mount('#report')
