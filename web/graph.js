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


    return [{
        key: "Sentiment",
        values: sentiment,
        color: "#0000ff"
    }]
}

//Used to reconstruct graph every 5 seconds, it'll call the above function (SentimentData) to poll the flask server for new data
//and update the chart accordingly
var interval = setInterval(() => {
    nv.addGraph(function () {
        var chart = nv.models.lineChart();

        chart.xAxis
            .axisLabel("X-axis Label");

        chart.yAxis
            .axisLabel("Y-axis Label")
            .tickFormat(d3.format("d"))
            ;

        d3.select("#series1")
            .datum(myData())
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

        chart.xAxis
            .axisLabel("X-axis Label");

        chart.yAxis
            .axisLabel("Y-axis Label")
            .tickFormat(d3.format("d"))
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
}, 5000);