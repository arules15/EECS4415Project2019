//const axios = require('axios');
//import axios from "https://unpkg.com/axios/dist/axios.min.js";

function myData() {
    var series1 = [];

    for (var i = 1; i < 100; i++) {
        series1.push({
            x: i, y: 100 / i
        });
    }

    return [
        {
            key: "Series #1",
            values: series1,
            color: "#0000ff"
        }
    ];
}

var series2 = []
var sentiment = []
var views = []

//this function is used to pull the sentiment data from the flask server and update the series array
//each analysis will have its own unique function like this
function sentimentData() {
    //series2 = [{ x: 1, y: 460 }, { x: 2, y: 386 }, { x: 3, y: 420 }, { x: 4, y: 410 }, { x: 5, y: 490 }, { x: 6, y: 520 }, { x: 7, y: 479 }];
    axios.get('http://127.0.0.1:5000/GetSentiment', { crossdomain: true })
        .then((response) => {
            console.log(response.data);
            sentiment = response.data;
        })
        .catch((err) => { console.log(err) });

    var series3 = [];
    var objectholder = {};
    var test = [
        {
            "key": "Action",
            "values": [
                { x: new Date(2019, 1), y: 0.12385241598400859 },
                { x: new Date(2019, 1), y: 0.12385241598400859 },
                { x: new Date(2019, 1), y: 0.12385241598400859 },
                { x: new Date(2019, 1), y: 0.12385241598400859 },
                { x: new Date(2019, 2), y: 0.12691673284096508 }]
        },
        {
            "key": "Adventure",
            "values": [
                { x: new Date(2019, 2), y: 0.12691673284096508 },
                { x: new Date(2019, 1), y: 0.12385241598400859 },
                { x: new Date(2019, 2), y: 0.12691673284096508 },
                { x: new Date(2019, 1), y: 0.12385241598400859 }]
        }
    ]

    for (const gen of Object.keys(sentiment)) {
        var arrToPush = {};
        arrToPush.key = gen;
        arrToPush.values = []
        for (const [date, value] of Object.entries(sentiment[gen])) {
            arrToPush.values.push({ x: new Date(parseInt(date.substring(0, 4)), parseInt(date.substring(4)) - 1), y: parseFloat(value) });
        }
        series3.push(arrToPush);
    }
    // console.log([() => {
    //     for (const genre of Object.keys(sentiment)) {
    //         return {
    //             key: genre,
    //             values: [() => {
    //                 for (const [date, value] of Object.entries(sentiment[genre])) {
    //                     return { x: new Date(date.substring(0, 3), date.substring(4)), y: value }
    //                 }
    //             }]
    //         }
    //     }
    // }]);

    // return [() => {
    //     for (const genre of Object.keys(sentiment)) {
    //         return {
    //             key: genre,
    //             values: [() => {
    //                 for (const [date, value] of Object.entries(sentiment[genre])) {
    //                     return { x: new Date(date.substring(0, 3), date.substring(4)), y: value }
    //                 }
    //             }]
    //         }
    //     }
    // }]

    return series3;
}

function viewsData() {
    //have a dictionary as follows [genre: [date:views]]
    //dynamically construct the graph by going through this dictionary and printing values
    //better yet, do this from flask 
    //the data will come in as a dictionary with key genre and value list of date:views
    //each genre will serve as a line, values = 
    //in the return do the following
    //construct a new object as follows
    //object = []
    //for i in input:
    //    for j in i
    //return () => for i in input
    //return[
    //    for i in input
    //return{
    // key: i
    //values: [(i) => for j in i:
    //    return [new(Date(j[0].substring(0,2), j[0].substring(2)), j[1])];
    //        ]
    //color: random colour
    //   }
    //]
    axios.get('http://127.0.0.1:5000/GetViews', { crossdomain: true })
        .then((response) => {
            console.log(response.data);
            views = response.data;
        })
        .catch((err) => { console.log(err) });

    var series3 = [];
    var objectholder = {};
    var test = [
        {
            "key": "Action",
            "values": [
                { x: new Date(2019, 1), y: 0.12385241598400859 },
                { x: new Date(2019, 1), y: 0.12385241598400859 },
                { x: new Date(2019, 1), y: 0.12385241598400859 },
                { x: new Date(2019, 1), y: 0.12385241598400859 },
                { x: new Date(2019, 2), y: 0.12691673284096508 }]
        },
        {
            "key": "Adventure",
            "values": [
                { x: new Date(2019, 2), y: 0.12691673284096508 },
                { x: new Date(2019, 1), y: 0.12385241598400859 },
                { x: new Date(2019, 2), y: 0.12691673284096508 },
                { x: new Date(2019, 1), y: 0.12385241598400859 }]
        }
    ]

    for (const gen of Object.keys(views)) {
        var arrToPush = {};
        arrToPush.key = gen;
        arrToPush.values = []
        for (const [date, value] of Object.entries(views[gen])) {
            arrToPush.values.push({ x: new Date(parseInt(date.substring(0, 4)), parseInt(date.substring(4)) - 1), y: parseInt(value) });
        }
        series3.push(arrToPush);
    }


    return series3;
}

//Used to reconstruct graph every 5 seconds, it'll call the above function (SentimentData) to poll the flask server for new data
//and update the chart accordingly
var interval = setInterval(() => {
    // nv.addGraph(function () {
    //     var chart = nv.models.lineChart();

    //     chart.xAxis
    //         .axisLabel("X-axis Label");

    //     chart.yAxis
    //         .axisLabel("Y-axis Label")
    //         .tickFormat(d3.format("d"))
    //         ;

    //     d3.select("#series1")
    //         .datum(myData())
    //         .transition().duration(500).call(chart);

    //     nv.utils.windowResize(
    //         function () {
    //             chart.update();
    //         }
    //     );

    //     return chart;
    // });

    nv.addGraph(function () {
        var chart = nv.models.lineChart();

        var mindate = new Date(2012, 1, 1);
        var maxdate = new Date(2019, 11, 30);

        var xScale = d3.time.scale();//.domain([mindate, maxdate]);

        chart.xAxis
            .axisLabel("Date")
            .tickFormat(function (d) {
                return d3.time.format('%x')(new Date(d))
            });

        chart.yAxis
            .axisLabel("Sentiment")
            .tickFormat(d3.format(".02f"))
            ;

        d3.select("#sentimentPlot")
            .datum(sentimentData())
            .transition().duration(500).call(chart);

        nv.utils.windowResize(
            function () {
                chart.update();
            }
        );

        return chart;
    });

    nv.addGraph(function () {
        var chart = nv.models.lineChart();

        var mindate = new Date(2012, 1, 1);
        var maxdate = new Date(2019, 11, 30);

        var xScale = d3.time.scale();//.domain([mindate, maxdate]);

        chart.xAxis
            .axisLabel("Date")
            .tickFormat(function (d) {
                return d3.time.format('%x')(new Date(d))
            });

        chart.yAxis
            .axisLabel("Views")
            .tickFormat(d3.format("d"))
            ;

        d3.select("#viewsPlot")
            .datum(viewsData())
            .transition().duration(500).call(chart);

        nv.utils.windowResize(
            function () {
                chart.update();
            }
        );

        return chart;
    });
}, 5000);