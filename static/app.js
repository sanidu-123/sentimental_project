

// Initialize charts
let pieChart, barChart, timeChart, heatmap;
const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
const hours = Array.from({ length: 24 }, (_, i) => `${i}:00`);

document.addEventListener('DOMContentLoaded', function () {
    loadDashboardData();
    loadWordClouds();
});

async function analyzeText() {
    const text = document.getElementById('textInput').value.trim();
    if (!text) {
        showError('Please enter some text');
        return;
    }

    const resultDiv = document.getElementById('result');
    resultDiv.innerHTML = '<div class="loading">Analyzing...</div>';
    resultDiv.className = 'result';

    try {
        const response = await fetch('/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ text })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.message || 'Analysis failed');
        }

        // Fix: Pass the input text and result data correctly
        // Log the response to see its structure
        console.log("API Response:", data);

        // Based on your backend code, the correct structure should be:
        // data = { status: 'success', data: { result: { label: '...', score: ... }, processed_text: '...' } }
        console.log("Full response structure:", JSON.stringify(data, null, 2));

        // Pass the original input text and the result object to displayResult
        if (data && data.status === 'success') {
            // The expected structure based on your Flask backend
            displayResult(text, data.data.result);
        } else {
            throw new Error('Unexpected response format from server');
        }

        loadDashboardData();
        loadWordClouds();
    } catch (error) {
        showError(error.message);
    }
}

// Fixed function to properly handle result data with more robust error handling
function displayResult(inputText, result) {
    const resultDiv = document.getElementById('result');

    console.log("Result object received:", result);

    // Handle potential undefined or unexpected result structure
    if (!result) {
        showError("Received empty result from server");
        return;
    }

    // Check if we have the necessary properties
    if (!result.label || typeof result.score === 'undefined') {
        // Try to handle different potential response structures
        if (result.result && result.result.label) {
            // If result is nested one level deeper
            result = result.result;
        } else {
            showError("Invalid result format received from server");
            console.error("Invalid result format:", result);
            return;
        }
    }

    resultDiv.className = `result ${result.label.toLowerCase()}`;

    // Display the original input text and the sentiment analysis result
    resultDiv.innerHTML = `
         <h3>Analysis Result</h3>
         <p><strong>Text:</strong> "${inputText.length > 100 ? inputText.substring(0, 100) + '...' : inputText}"</p>
         <p><strong>Sentiment:</strong> <span style="font-weight: bold; color: ${result.label === 'POSITIVE' ? '#2ecc71' : '#e74c3c'}">
             ${result.label} (${(result.score * 100).toFixed(1)}%)
         </span></p>
     `;
}

function showError(message) {
    const resultDiv = document.getElementById('result');
    resultDiv.innerHTML = `<div class="error-message">Error: ${message}</div>`;
    resultDiv.className = 'result';
}

async function loadDashboardData() {
    try {
        const response = await fetch('/stats');
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.message || 'Failed to load dashboard data');
        }

        updatePieChart(data.data.sentiment_counts);
        updateBarChart(data.data.score_distribution);
        updateTimeChart(data.data.time_trends);
        updateHeatmap(data.data.heatmap);
    } catch (error) {
        console.error('Failed to load dashboard data:', error);
    }
}

async function loadWordClouds() {
    try {
        // Positive word cloud
        const positiveLoading = document.getElementById('positiveWordcloudLoading');
        const positiveImg = document.getElementById('positiveWordcloud');

        positiveLoading.style.display = 'block';
        positiveImg.style.display = 'none';

        const positiveResponse = await fetch('/wordcloud/positive');
        const positiveData = await positiveResponse.json();

        if (positiveData.data.image) {
            positiveImg.src = positiveData.data.image;
            positiveImg.style.display = 'block';
            positiveLoading.style.display = 'none';
        } else {
            positiveLoading.textContent = positiveData.data.message || 'No positive word cloud available';
        }

        // Negative word cloud
        const negativeLoading = document.getElementById('negativeWordcloudLoading');
        const negativeImg = document.getElementById('negativeWordcloud');

        negativeLoading.style.display = 'block';
        negativeImg.style.display = 'none';

        const negativeResponse = await fetch('/wordcloud/negative');
        const negativeData = await negativeResponse.json();

        if (negativeData.data.image) {
            negativeImg.src = negativeData.data.image;
            negativeImg.style.display = 'block';
            negativeLoading.style.display = 'none';
        } else {
            negativeLoading.textContent = negativeData.data.message || 'No negative word cloud available';
        }
    } catch (error) {
        console.error('Failed to load word clouds:', error);
        document.getElementById('positiveWordcloudLoading').textContent = 'Failed to load word cloud';
        document.getElementById('negativeWordcloudLoading').textContent = 'Failed to load word cloud';
    }
}

function updatePieChart(sentimentData) {
    const ctx = document.getElementById('pieChart').getContext('2d');

    if (pieChart) {
        pieChart.destroy();
    }

    // Ensure we always have both positive and negative keys
    const data = {
        POSITIVE: sentimentData.POSITIVE || 0,
        NEGATIVE: sentimentData.NEGATIVE || 0
    };

    pieChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: Object.keys(data),
            datasets: [{
                data: Object.values(data),
                backgroundColor: [
                    '#2ecc71', // green
                    '#e74c3c'  // red
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom',
                },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            const label = context.label || '';
                            const value = context.raw || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = total > 0 ? Math.round((value / total) * 100) : 0;
                            return `${label}: ${value} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

function updateBarChart(scoreData) {
    const ctx = document.getElementById('barChart').getContext('2d');

    if (barChart) {
        barChart.destroy();
    }

    // Ensure we have data for all bins
    const positiveData = scoreData.positive || [0, 0, 0, 0, 0];
    const negativeData = scoreData.negative || [0, 0, 0, 0, 0];
    const labels = scoreData.bins || ['0.5-0.6', '0.6-0.7', '0.7-0.8', '0.8-0.9', '0.9-1.0'];

    barChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Positive',
                    data: positiveData,
                    backgroundColor: 'rgba(46, 204, 113, 0.7)',
                    borderColor: 'rgba(46, 204, 113, 1)',
                    borderWidth: 1
                },
                {
                    label: 'Negative',
                    data: negativeData,
                    backgroundColor: 'rgba(231, 76, 60, 0.7)',
                    borderColor: 'rgba(231, 76, 60, 1)',
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Number of Analyses'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Score Range'
                    }
                }
            }
        }
    });
}

function updateTimeChart(timeData) {
    const chartDom = document.getElementById('timeChart');

    if (timeChart) {
        timeChart.dispose();
    }

    timeChart = echarts.init(chartDom);

    // Ensure we have data
    const hours = timeData.hours || [];
    const positiveData = timeData.positive || [];
    const negativeData = timeData.negative || [];

    const option = {
        tooltip: {
            trigger: 'axis',
            axisPointer: {
                type: 'shadow'
            }
        },
        legend: {
            data: ['Positive', 'Negative']
        },
        grid: {
            left: '3%',
            right: '4%',
            bottom: '3%',
            containLabel: true
        },
        xAxis: {
            type: 'category',
            data: hours,
            axisLabel: {
                rotate: 45
            }
        },
        yAxis: {
            type: 'value',
            name: 'Number of Analyses'
        },
        series: [
            {
                name: 'Positive',
                type: 'line',
                stack: 'total',
                smooth: true,
                lineStyle: {
                    width: 0
                },
                showSymbol: false,
                areaStyle: {
                    opacity: 0.8,
                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                        {
                            offset: 0,
                            color: 'rgba(46, 204, 113, 0.8)'
                        },
                        {
                            offset: 1,
                            color: 'rgba(46, 204, 113, 0.1)'
                        }
                    ])
                },
                emphasis: {
                    focus: 'series'
                },
                data: positiveData
            },
            {
                name: 'Negative',
                type: 'line',
                stack: 'total',
                smooth: true,
                lineStyle: {
                    width: 0
                },
                showSymbol: false,
                areaStyle: {
                    opacity: 0.8,
                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                        {
                            offset: 0,
                            color: 'rgba(231, 76, 60, 0.8)'
                        },
                        {
                            offset: 1,
                            color: 'rgba(231, 76, 60, 0.1)'
                        }
                    ])
                },
                emphasis: {
                    focus: 'series'
                },
                data: negativeData
            }
        ]
    };

    timeChart.setOption(option);

    window.addEventListener('resize', function () {
        timeChart.resize();
    });
}

function updateHeatmap(heatmapData) {
    const chartDom = document.getElementById('heatmap');

    if (heatmap) {
        heatmap.dispose();
    }

    heatmap = echarts.init(chartDom);

    // Process heatmap data with fallbacks
    const days = heatmapData.days || ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    const hours = heatmapData.hours || Array.from({ length: 24 }, (_, i) => `${i}:00`);
    const positiveData = heatmapData.positive || Array(7).fill().map(() => Array(24).fill(0));
    const negativeData = heatmapData.negative || Array(7).fill().map(() => Array(24).fill(0));

    // Find max value for visual map scaling
    const maxValue = Math.max(
        ...positiveData.flat(),
        ...negativeData.flat(),
        1
    );

    const option = {
        tooltip: {
            position: 'top',
            formatter: function (params) {
                return `${days[params.value[1]]} at ${params.value[0]}:00<br>
                         Positive: ${positiveData[params.value[1]][params.value[0]] || 0}<br>
                         Negative: ${negativeData[params.value[1]][params.value[0]] || 0}`;
            }
        },
        grid: {
            top: '15%',
            left: '3%',
            right: '4%',
            bottom: '10%',
            containLabel: true
        },
        xAxis: {
            type: 'category',
            data: hours,
            splitArea: {
                show: true
            },
            axisLabel: {
                interval: 3
            }
        },
        yAxis: {
            type: 'category',
            data: days,
            splitArea: {
                show: true
            }
        },
        visualMap: {
            min: 0,
            max: maxValue,
            calculable: true,
            orient: 'horizontal',
            left: 'center',
            bottom: '0%',
            inRange: {
                color: ['#e0f3f8', '#abd9e9', '#74add1', '#4575b4', '#313695']
            }
        },
        series: [
            {
                name: 'Positive',
                type: 'heatmap',
                data: positiveData.flatMap((dayData, dayIndex) =>
                    dayData.map((count, hourIndex) =>
                        count > 0 ? [hourIndex, dayIndex, count] : null
                    ).filter(Boolean)
                ),
                label: {
                    show: false
                },
                emphasis: {
                    itemStyle: {
                        shadowBlur: 10,
                        shadowColor: 'rgba(0, 0, 0, 0.5)'
                    }
                }
            },
            {
                name: 'Negative',
                type: 'heatmap',
                data: negativeData.flatMap((dayData, dayIndex) =>
                    dayData.map((count, hourIndex) =>
                        count > 0 ? [hourIndex, dayIndex, count] : null
                    ).filter(Boolean)
                ),
                label: {
                    show: false
                },
                emphasis: {
                    itemStyle: {
                        shadowBlur: 10,
                        shadowColor: 'rgba(0, 0, 0, 0.5)'
                    }
                }
            }
        ]
    };

    heatmap.setOption(option);

    window.addEventListener('resize', function () {
        heatmap.resize();
    });
}

// Example fetch request
fetch('/analyze', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text: 'I love this app!' })
})
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success' && data.data && data.data.result) {
            console.log('Sentiment:', data.data.result.label);
            console.log('Score:', data.data.result.score);
        } else {
            console.error('Unexpected response structure:', data);
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
