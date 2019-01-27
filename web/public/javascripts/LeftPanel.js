/**
 * Created by yuyu on 2018/11/20.
 */
// TODO  set table name
var tableName = 'DBPublications-input_id';
var $table_showDataDetails = $('#table_showDataDetails'); //用于展示当前选中数据表的 每一行详细数据
//2. 通过Bootstrap - table 接口来查询数据库并且返回
//TODO 加载服务器数据库中已经存在的数据表/files
$("#uploadBtn").click(function () {
    alert('Limit this function right now.')
});

//点击数据表标签，通过模态框返回给用户数据表的首页数据
$("#dataBtn").click(function () {

    // //show 方法调用之后立即触发该函数
    // //判断之前是否加载过这个表格的数据
    // if ($("#tableName_showDataDetails").text() != tableName){
    //     reqTableDataServerSidePagination(tableName);
    //     // console.log("selectedTableID: ",tableName);
    // }
    // //Add Table Name
    // //TODO 更新模态框里面的表名
    // $("#tableName_showDataDetails").text(tableName);

    //Todo 新 after 11/20

    $.ajax({
        method: 'GET',    // 如果要使用GET方式，则将此处改为'get'
        url: "/data/req_TableDataServerSidePaging",
        data: {
            tableID: tableName,
            limit : 3, // 每页显示数量
            offset : 0, // SQL语句偏移量
        },
        dataType: 'json',
        success: function (data) {
            data = data['rows'];
            console.log(data);
            // varColName = Object.keys(data[0]);
            //如果请求成功，则对进行相应的数据处理
            let colName = Object.keys(data[0]);
            console.log(colName)
            // let colType = Object.values(data[5]);
            // console.log(colType)
            let columns = [];
            for (let i = 0; i < colName.length; i++) {
                columns.push({
                    field: colName[i],
                    title: colName[i],
                    // sortable: true
                })
            }
            console.log(columns);
            $table_showDataDetails.bootstrapTable('destroy').bootstrapTable({
                method: 'get',
                url: '/data/req_TableDataServerSidePaging',
                pagination: true,
                sidePagination: 'server',//分页方式：client客户端分页，server服务端分页（*）
                pageNumber:1,      //初始化加载第一页，默认第一页
                pageSize: 15, //每页的记录行数（*）
                queryParams: queryParams,	// 请求参数，这个关系到后续用到的异步刷新
                pageList:[10,25],
                search: false, //是否启用搜索框
                strictSearch:true,//设置为 true启用 全匹配搜索，否则为模糊搜索
                searchOnEnterKey: true, //设置为 true时，按回车触发搜索方法，否则自动触发搜索方法
                showHeader: true,
                columns: columns
            });

            //TODO 更新[selected table下的]tableName
            // tableName = tableID;

            // TODO Ask Slide Window Question
            // slide_window(tableName)
        },
        error: function (jqXHR, textStatus, errorThrown) {
            // "use strict";
            alert("something wrong.")
        }
    })
});

function queryParams(params) {
    return{
        limit : params.limit, // 每页显示数量
        offset : params.offset, // SQL语句偏移量
        tableID : tableName,
    }
}


function request_visualization(isInit) {
    console.log("Update Visualization!!!");
    $.ajax({
        method: 'GET',    // 如果要使用GET方式，则将此处改为'get'
        url: "/data/req_VisQueryRes",
        data: {
            tableID: tableName,
            GroupByCol: 'Venue', // 每页显示数量
            AggCol: 'Citations', // SQL语句偏移量
            AggFunc: 'sum'
        },
        dataType: 'json',
        success: function (data) {
            //TODO 如果是首次调用
            if (isInit == true){
                setTimeout(function () {
                    slide_window(tableName)
                },500);
            }

            //data = data['Citations'];
            //console.log(data);
            let worldMapContainer = document.getElementById('main');

            //用于使chart自适应高度和宽度,通过窗体高宽计算容器高宽
            let resizeWorldMapContainer = function () {
                worldMapContainer.style.width = $("#leftPanel").width()/1.9 + 'px';
                worldMapContainer.style.height = '550px';
            };
            //设置容器高宽
            resizeWorldMapContainer();


            let legendData = ['SUM(Citations)', 'Missing', 'outlier'];
            let category_Data = data['x_data'];
            // TODO 只是为了demo
            // for (let i = 0; i < category_Data.length; i++){
            //     let str = category_Data[i].split(' ');
            //     console.log(str)
            //     let str_len = str.length;
            //     if (str_len >= 5){
            //         console.log(">4")
            //         let new_x = "";
            //         for (let j = 0; j < str_len; j++){
            //             if (j >= 5){
            //                 new_x += '.'
            //             }else {
            //                 new_x += str[j] + ' ';
            //             }
            //         }
            //         category_Data[i] = new_x;
            //     }
            //
            // }

            console.log("Distinct value of X-axis = ", category_Data.length);
            let value_Data = data['y_data'];
            // 基于准备好的dom，初始化echarts实例
            let myChart = echarts.init(document.getElementById('main'));
            // 指定图表的配置项和数据
            let option = {
                title: {
                    text: 'DB Papers'
                },
                grid: {
                    left: '10%',
                    right: '10%',
                    bottom: '35%',
                    //containLabel: true //防止标签溢出
                },
                tooltip: {
                    // trigger: 'axis',
                    axisPointer: {            // 坐标轴指示器，坐标轴触发有效
                        type: 'shadow'        // 默认为直线，可选为：'line' | 'shadow'
                    }
                },
                toolbox: {
                    feature: {
                        myMergeBar: {
                            show: true,
                            title: '合并所选区域的柱子',
                            icon: 'image://./images/merge.png',
                            onclick: function () {
                                /**
                                 * For Training Question
                                 */
                                setTimeout(function () {
                                    training_question(tableName)
                                }, 1500);

                                let nxData = category_Data;
                                let nyData = value_Data;
                                for (let i = 0; i < selectedBars.length; i++) {
                                    nxData.splice(selectedBars[i] - i, 1);
                                    nyData.splice(selectedBars[i] - i, 1);
                                }
                                option.xAxis.data = nxData;
                                option.series[0].data = nyData;
                                myChart.setOption(option);
                            }
                        },
                        myReOrderBar: {
                            show: true,
                            title: '对所选区域的柱子重排序',
                            icon: 'image://./images/resort.png',
                            onclick: function () {
                                alert('resort bars')
                            }
                        },
                        mySortBarByAlpha: {
                            show: true,
                            title: '按字典重排柱子',
                            icon: 'image://./images/sort-alpha-desc.png',
                            onclick: function () {
                                //alert('按字典重排柱子')
                                resort_by_alph()
                            }
                        }
                    }
                },
                brush: {
                    toolbox: ['rect', 'lineX', 'lineY', 'keep', 'clear'],
                    xAxisIndex: 0
                },
                dataZoom: [

                    {
                        type: 'slider',
                        top: '6%',
                        show: true,
                        xAxisIndex: [0],
                        start: 0,
                        end: 100
                    },
                    {
                        type: 'slider',
                        show: true,
                        yAxisIndex: [0],
                        left: '93%',
                        start: 0,
                        end: 100
                    },


                ],
                legend: {
                    data: legendData
                },
                xAxis: {
                    type: 'category',
                    axisLabel: {
                        rotate: 270
                    },
                    data: category_Data
                    //data: yData
                },
                yAxis: {
                    type: 'value',

                },
                series: [{
                    name: 'SUM(Citations)',
                    type: 'bar',
                    data: value_Data
                }]
            };

            myChart.on('brushSelected', renderBrushed);

            function renderBrushed(params) {
                let brushed = [];
                let brushComponent = params.batch[0];
                for (let sIdx = 0; sIdx < brushComponent.selected.length; sIdx++) {
                    let rawIndices = brushComponent.selected[sIdx].dataIndex;

                    selectedBars = rawIndices;

                    for (let rId = 0; rId < rawIndices.length; rId++) {
                        brushed.push('(' + category_Data[rawIndices[rId]] + ' , ' + value_Data[rawIndices[rId]] + ')')
                    }
                }

                myChart.setOption({
                    title: {
                        backgroundColor: '#333',
                        text: 'SELECTED DATA INDICES: \n' + brushed.join('\n'),
                        bottom: -5,
                        right: 0,
                        width: 100,
                        textStyle: {
                            fontSize: 12,
                            color: '#fff'
                        }
                    }
                });
            }
            // 使用刚指定的配置项和数据显示图表。
            myChart.setOption(option);

            //用于使chart自适应高度和宽度
            window.onresize = function () {
                //重置容器高宽
                resizeWorldMapContainer();
                myChart.resize();
            };
        },
        error: function (jqXHR, textStatus, errorThrown) {
            // "use strict";
            alert("something wrong.")
        }
    });

}