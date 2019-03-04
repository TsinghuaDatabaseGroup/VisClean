/**
 * Created by yuyu on 2018/11/20.
 */
var express = require('express');
var router = express.Router();
const spawn = require('child_process').spawn;


router.get('/req_TableDataServerSidePaging', async function (req,res,next) {
    console.log('req_TableDataServerSidePaging receive the request');

    let tableID = req.query.tableID;
    let limit = req.query.limit;
    let offset = req.query.offset;
    console.log("tableID = ",tableID, ", limit = ",limit, ", offset = ", offset);

    let result = await req_TableDataServerSidePaging(tableID, limit, offset);
    res.send(result)
});

router.get('/req_VisQueryRes', async function (req, res, next) {
    console.log('req_VisQueryRes receive the request');
    // GroupByCol, AggCol, AggFunc
    let tableID = req.query.tableID;
    let GroupByCol = req.query.GroupByCol;
    let AggCol = req.query.AggCol;
    let AggFunc = req.query.AggFunc;
    console.log("tableID = ",tableID, ", GroupByCol = ",GroupByCol, ", AggCol = ", AggCol, ", AggFunc = ",AggFunc);

    let result = await req_VisQueryRes(tableID, GroupByCol, AggCol, AggFunc);
    res.send(result)
});

router.get('/req_slide_window', async function (req, res, next) {
    console.log('req_slide_window receive the request');
    let tableID = req.query.tableID;
    // Call the function here
    let result = await req_slide_window(tableID);
    res.send(result)
});

router.get('/ans_slide_window', async function (req, res, next) {
    console.log('ans_slide_window receive the answer');
    let tableID = req.query.tableID;
    let answer = req.query.answer;
    console.log('ans_slide_window ==> tableID = ', tableID);
    console.log('ans_slide_window ==> answer = ', answer);
    // Call the function here
    let result = await ans_slide_window(tableID, answer);
    res.send(result)
});

router.get('/req_ques_training', async function (req, res, next) {
    console.log('req_ques_training receive the request');
    let tableID = req.query.tableID;
    let result = await req_ques_training(tableID);
    res.send(result)
});

router.get('/req_resort', async function (req, res, next) {
    console.log('req_resort receive the request');
    let tableID = req.query.tableID;
    let result = await req_resort(tableID);
    res.send(result)
});

async function req_resort(tableID) {
    // call python algorithm here.
    let data = await new Promise((resolve, reject) => {
        const cPath = process.cwd() + '/src/question_selector.py' ;
        console.log(cPath);
        let argv = [];
        argv.push(cPath);
        argv.push('req_resort'); // for tag
        argv.push(process.cwd() + '/dataset/DBConf/' + tableID + '.csv');
        console.log(argv);
        const ls = spawn('python', argv);
        let result = '';
        ls.stdout.on('data', (data) => {
            result += data;
        });

        ls.stderr.on('data', (data) => {
            console.log(`stderr: ${data}`);
        });

        ls.on('close', (code) => {
            console.log(`child process exited with code ${code}`);
            resolve(result);
        });
    });
    console.log(data);
    return data;
}

async function req_ques_training(tableId){
    // call python algorithm here.
    let data = await new Promise((resolve, reject) => {
        const cPath = process.cwd() + '/src/question_selector.py' ;
        console.log(cPath);
        let argv = [];
        argv.push(cPath);
        argv.push('ques_training'); // for tag
        argv.push(process.cwd() + '/dataset/DBConf/expr_tmp/training_question_from_predict.csv');
        console.log(argv);
        const ls = spawn('python', argv);
        let result = '';
        ls.stdout.on('data', (data) => {
            result += data;
        });

        ls.stderr.on('data', (data) => {
            console.log(`stderr: ${data}`);
        });

        ls.on('close', (code) => {
            console.log(`child process exited with code ${code}`);
            resolve(result);
        });
    });
    console.log(data);
    return data;
}

async function req_slide_window(tableID) {
    // call python algorithm here.
    let data = await new Promise((resolve, reject) => {
        const cPath = process.cwd() + '/src/question_selector.py' ;
        console.log(cPath);
        let argv = [];
        argv.push(cPath);
        argv.push('slide_window'); // for tag
        argv.push(process.cwd() + '/dataset/DBConf/' + 'expr_tmp');
        argv.push('/gold_from_predict.csv');
        console.log(argv);
        const ls = spawn('python', argv);
        let result = '';
        ls.stdout.on('data', (data) => {
            result += data;
        });

        ls.stderr.on('data', (data) => {
            console.log(`stderr: ${data}`);
        });

        ls.on('close', (code) => {
            console.log(`child process exited with code ${code}`);
            resolve(result);
        });
    });
    console.log(data);
    return data;
}

async function ans_slide_window(tableID, answer) {
    // call python algorithm here.
    let data = await new Promise((resolve, reject) => {
        const cPath = process.cwd() + '/src/question_selector.py' ;
        console.log(cPath);
        let argv = [];
        argv.push(cPath);
        argv.push('ans_slide_window'); // for tag
        argv.push(process.cwd() + '/dataset/DBConf/'+ 'expr_tmp/' + 'gold_from_predict' + '.csv');

        let answer_argv = "";
        // [begin] code block for dealing with several groups in the window
        // for (let i = 0; i < answer.length; i++){
        //     for (let j = 0; j < answer[i].length; j++){
        //         answer_argv += answer[i][j];
        //         if (j != answer[i].length-1){
        //             answer_argv +='+'
        //         }
        //     }
        //     if (i != answer.length -1){
        //         answer_argv += ','
        //     }
        // }
        // [end] code block for dealing with several groups in the window

        // [begin] code block for dealing with one group in the window
        for (let i = 0; i < answer.length; i++){
           answer_argv += answer[i];
           if (i != answer.length-1)
               answer_argv += "+";
        }
        // [end] code block for dealing with one group in the window

        console.log(answer_argv);
        argv.push(answer_argv);
        console.log("ans_slide_window, sent to back-end: ", argv);
        const ls = spawn('python', argv);
        let result = '';
        ls.stdout.on('data', (data) => {
            result += data;
        });

        ls.stderr.on('data', (data) => {
            console.log(`stderr: ${data}`);
        });

        ls.on('close', (code) => {
            console.log(`child process exited with code ${code}`);
            resolve(result);
        });
    });
    console.log(data);
    return data;
}

async function req_VisQueryRes(tableID, GroupByCol, AggCol, AggFunc){
    // call python algorithm here.
    let data = await new Promise((resolve, reject) => {
        const cPath = process.cwd() + '/src/query.py' ;
        console.log(cPath);
        let argv = [];
        argv.push(cPath);
        argv.push(process.cwd() + '/dataset/DBConf/' + 'expr_tmp/' + 'gold_from_predict' + '.csv');
        argv.push(GroupByCol);
        argv.push(AggCol);
        argv.push(AggFunc);
        console.log(argv);
        const ls = spawn('python', argv);
        let result = '';
        ls.stdout.on('data', (data) => {
            result += data;
        });

        ls.stderr.on('data', (data) => {
            console.log(`stderr: ${data}`);
        });

        ls.on('close', (code) => {
            console.log(`child process exited with code ${code}`);
            resolve(result);
        });
    });
    console.log(data);
    return data;

}

async function req_TableDataServerSidePaging(tableID, limit, offset){
    // call python algorithm here.
    let data = await new Promise((resolve, reject) => {
        const cPath = process.cwd() + '/web/webPython/data.py' ;
        console.log(cPath);
        let argv = [];
        argv.push(cPath);
        argv.push(process.cwd() + '/dataset/DBConf/' + tableID + '.csv');
        argv.push(limit);
        argv.push(offset);
        console.log(argv);
        const ls = spawn('python', argv);
        let result = '';
        ls.stdout.on('data', (data) => {
            result += data;
        });

        ls.stderr.on('data', (data) => {
            console.log(`stderr: ${data}`);
        });

        ls.on('close', (code) => {
            console.log(`child process exited with code ${code}`);
            resolve(result);
        });
    });
    // console.log(data)
    return data;
}


module.exports = router;