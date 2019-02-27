/**
 * Created by yuyu on 2018/11/25.
 */

slide_window_data = {};
var selectedBars = [];
var user_approve_groups = [];
var table_labelTrainingPair = $('#table_labelTrainingPair');


function training_question(tableName) {
    $.ajax({
        method: 'GET',    // 如果要使用GET方式，则将此处改为'get'
        url: "/data/req_ques_training",
        data: {
            tableID: 'training_question_from_predict',
        },
        dataType: 'json',
        success: function (data) {
            // success and do something here
            $("#ques_alert").show();
            $("#ques_training").show();
            console.log(data);

        },
        error: function (jqXHR, textStatus, errorThrown) {
            // "use strict";
            alert("something wrong.")
        }
    })
}

$("#ques_training").click(function () {
    $('#trainingModal').modal({backdrop: 'static', keyboard: false}, 'show');
    $("#ques_alert").hide();
    $("#ques_training").hide();
    //读取系统默认数据集
    // $table_labelTrainingPair.show();
});

$(".answer_question").click(function () {
    $("#sent_wait_backend").show();

    //TODO Question selection
    if (Math.random() > 0.6){
        training_question()
    }else {
        slide_window()
    }
});

function resort_by_alph() {
    $.ajax({
        method: 'GET',    // 如果要使用GET方式，则将此处改为'get'
        url: "/data/req_resort",
        data: {
            tableID: 'gold_from_predict',
        },
        dataType: 'json',
        success: function (data) {
            // success and do something here
            let worldMapContainer = document.getElementById('chart4window');

            //用于使chart自适应高度和宽度,通过窗体高宽计算容器高宽
            let resizeWorldMapContainer = function () {
                worldMapContainer.style.width = $("#leftPanel").width()/2.6 + 'px';
                worldMapContainer.style.height = '500px';
                // worldMapContainer.style.display = 'inline';
            };
            //设置容器高宽
            resizeWorldMapContainer();


            let legendData = ['SUM(Citations)', 'Missing', 'outlier'];
            let category_Data = data['x_data'];
            let value_Data = data['y_data'];
            // 基于准备好的dom，初始化echarts实例
            let myChart = echarts.init(document.getElementById('mchart4windowain'));
            // 指定图表的配置项和数据
            let option = {
                title: {
                    text: 'DB Papers'
                },
                grid: {
                    left: '10%',
                    right: '10%',
                    bottom: '30%',
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
                        rotate: 270,
                        interval: 0, //强制显示所有柱子的名字
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
    })
}


// Call this function on $("#ques_slide_window").click ... ...
function ans_slide_window(tableName, answer) {
    $.ajax({
        method: 'GET',    // 如果要使用GET方式，则将此处改为'get'
        url: "/data/ans_slide_window",
        data: {
            tableID: 'gold_from_predict',
            answer: answer
        },
        dataType: 'json',
        success: function (data) {
            // success and do something here
            console.log("Successfully apply the answer on the backend");
            // Update the Visualization Result !!!
            $("#sent_wait_backend").hide();

            console.log('apply the slide window. ==>', data);

            //TODO 更新一下左边的可视化结果
            request_visualization(false)

            //TODO Question selection
            if (Math.random() > 0.6){
                training_question()
            }else {
                slide_window()
            }
        },
        error: function (jqXHR, textStatus, errorThrown) {
            // "use strict";
            alert("something wrong.")
        }
    })
}

// Call this function at the layout.jade
function slide_window(tableName) {
    $.ajax({
        method: 'GET',    // 如果要使用GET方式，则将此处改为'get'
        url: "/data/req_slide_window",
        data: {
            tableID: 'gold_from_predict',
        },
        dataType: 'json',
        success: function (data) {
            // success and do something here
            console.log("get the slide window from back-end and show the data");
            $("#ques_alert").show();
            $("#ques_slide_window").show();
            slide_window_data = data
        },
        error: function (jqXHR, textStatus, errorThrown) {
            // "use strict";
            alert("something wrong.")
        }
    })
}



// Call this function when clicking the button 'Slide Window' under the 'Status'
// this function is for rendering the window-based question (bar chart)
$("#ques_slide_window").click(function () {
    $("#ques_alert").hide();
    $("#ques_slide_window").hide();
    $("#window_table").show();

    var worldMapContainer = document.getElementById('chart4window');

    //用于使chart自适应高度和宽度,通过窗体高宽计算容器高宽
    var resizeWorldMapContainer = function () {
        worldMapContainer.style.width = $("#leftPanel").width()/2.6 + 'px';
        worldMapContainer.style.height = '500px';
        // worldMapContainer.style.display = 'inline';
    };
    //设置容器高宽
    resizeWorldMapContainer();

    let legendData = ['SUM(Citations)'];
    let new_xdata = [];
    let new_ydata = [];
    my_color = ['#2E86C1','#c23531','#2f4554', '#61a0a8', '#d48265', '#91c7ae','#749f83',  '#ca8622', '#bda29a','#6e7074', '#546570', '#c4ccd3']
    // 这里的写法最初是给有多个group的window，现在默认每一个window只有一个group
    for (let i =0; i < slide_window_data["y_data"].length; i++){
        for (let j = 0; j < slide_window_data["y_data"][i].length; j++){
            new_ydata.push({
                "value": slide_window_data["y_data"][i][j],
                "itemStyle": {
                    "color": my_color[i]
                }
            })
        }
    }
    for (let i =0; i < slide_window_data["x_data"].length; i++){
        new_xdata = new_xdata.concat(slide_window_data['x_data'][i])
    }
    let category_Data = new_xdata;
    let value_Data = new_ydata;
    console.log(category_Data);
    console.log(value_Data);

    let selectedBars = [];
    // 基于准备好的dom，初始化echarts实例
    let myChart = echarts.init(document.getElementById('chart4window'));
    // 指定图表的配置项和数据
    let option = {
        title: {
            text: 'DB Papers'
        },
        grid: {
            left: '10%',
            right: '10%',
            bottom: '30%',
        },
        tooltip: {
            axisPointer: {            // 坐标轴指示器，坐标轴触发有效
                type: 'shadow'        // 默认为直线，可选为：'line' | 'shadow'
            }
        },
        toolbox: {
            feature: {
                // the user select some bars to merge.
                // myMergeBar: {
                //     show: true,
                //     title: 'Merge those bars you select',
                //     icon: 'image://./images/merge.png',
                //     onclick: function () {
                //         let nxData = category_Data;
                //         let nyData = value_Data;
                //
                //         // 记录用户merge的group
                //         let selectedBars_name = [];
                //         for (let i = 0; i < selectedBars.length; i++){
                //             selectedBars_name.push(category_Data[selectedBars[i]])
                //         }
                //         user_approve_groups.push(selectedBars_name);
                //
                //         for (let i = 0; i < selectedBars.length; i++) {
                //             nxData.splice(selectedBars[i] - i, 1);
                //             nyData.splice(selectedBars[i] - i, 1);
                //         }
                //
                //         option.xAxis.data = nxData;
                //         option.series[0].data = nyData;
                //         myChart.setOption(option);
                //         //
                //         myChart.dispatchAction({
                //             type: 'restore',
                //             // start: 20,
                //             // end: 30
                //         });
                //
                //         //这里合并了柱子之后，要把结果往后台发送
                //         if (nxData.length == 0){ //TODO 当用户把所有的bar都合并后，就置空
                //             console.log('zero?!!!');
                //             //TODO 清空后，把所有的选择的merge group传给后台
                //             // drop the current window
                //             myChart.dispose();
                //             $("#sent_wait_backend").show();
                //             ans_slide_window('', user_approve_groups)
                //         }
                //
                //     }
                // },
                myReOrderBar: {
                    show: true,
                    title: 'Resort by value',
                    icon: 'image://./images/resort.png',
                    onclick: function () {
                        alert('resort bars')
                    }
                },
                mySortBarByAlpha: {
                    show: true,
                    title: 'Resort by category',
                    icon: 'image://./images/sort-alpha-desc.png',
                    onclick: function () {
                        alert('按字典重排柱子')
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
        // legend: {
        //     data: legendData,
        // },
        xAxis: {
            type: 'category',
            axisLabel: {
                rotate: 270,
                interval: 0, //强制显示所有柱子的名字
                formatter: function (value) {
                    let arr = value.toString().split(' ');
                    let tmp = '';
                    if (arr.length > 3){
                        for (let i = 0; i < arr.length; i++){
                            tmp += arr[i] + ' ';
                            if (i == 3){
                                tmp += '\n';
                            }
                        }
                        return tmp
                    }
                    else {
                        return value
                    }
                }
            },
            data: category_Data
        },
        yAxis: {
            type: 'value',
        },
        series: [{
            name: 'SUM(Citations)',
            type: 'bar',
            data: value_Data,
        }]
    };

    // TODO manually refine. (the user delete a bar from the window)
    // This code block is for refining the Sliding Window,
    // the mouse move over the bar --> show button 'x'
    // then, the user click the button 'x' to remove this bar from the window
    let deleteBarIndex = undefined;
    myChart.on('mouseover', function (params) {
        // mouser move over and show button.
        console.log(params);
        option.series[0]['markPoint'] = {
            symbol: 'circle',
                symbolSize: 20,
                data: [
                {
                    name: 'Delete',
                    value: 'X',
                    xAxis: params.dataIndex,
                    yAxis: params.value
                }
            ]
        };
        myChart.setOption(option);
        // set the deleteBarIndex
        deleteBarIndex = params.dataIndex;
    });
    myChart.on('mouseout', function (params) {
        // mouser move over and show button.
        console.log("delete");
        option.series[0]['markPoint'] = {};
        myChart.setOption(option);
        // set the deleteBarIndex
        deleteBarIndex = undefined;
    });
    // the user click and then remove the bar.
    myChart.on('click', function (params) {
        // console.log(para.name);
        // the user click the bar that he want to remove.
        console.log('mouse click-->para.dataIndex = ', params.dataIndex);
        if (deleteBarIndex != undefined){
            option.xAxis.data.splice(deleteBarIndex ,1);
            option.series[0].data.splice(deleteBarIndex ,1);
            // console.log(option.xAxis.data);
            // console.log(option.series[0].data);
        }

        // 删除markpoint, the button 'x'
        option.series[0]['markPoint'] = {};
        myChart.setOption(option);
    });

    myChart.on('brushSelected', renderBrushed);

    function renderBrushed(params) {
        let brushed = [];
        let brushComponent = params.batch[0];
        for (let sIdx = 0; sIdx < brushComponent.selected.length; sIdx++) {
            let rawIndices = brushComponent.selected[sIdx].dataIndex;

            selectedBars = rawIndices;
            // console.log('dfsdf->selectedBars = ', selectedBars)
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
});

$("#btn_approve_window").click(function () {
    //TODO 清空后，把所有的选择的merge group传给后台
    // drop the current window
    console.log("drop the current window and sent the interaction result to the back-end.");
    let myChart = echarts.getInstanceByDom(document.getElementById('chart4window'));

    $("#sent_wait_backend").show();
    $("#window_table").hide();

    user_approve_groups = myChart.getOption().xAxis[0].data;
    console.log("user_approve_groups = ", user_approve_groups);

    // sent the interaction result to the backend.
    ans_slide_window('', user_approve_groups)

    // 销毁window-based chart对象实例
    myChart.dispose();
});

$("#btn_reject_window").click(function () {
   alert("The user reject the window.")
});