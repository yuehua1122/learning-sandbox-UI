document.getElementById('home-button').onclick = () => {
    document.body.classList.add('fade-out');
    setTimeout(() => {
        window.location.href = "index.html";
    }, 500);
};

document.getElementById('code-button').addEventListener('click', function() {
    // 清空 display-area
    document.getElementById('display-area').innerHTML = '<canvas id="myChart"></canvas>';
    
    // 切換到評分模式
    document.getElementById('display-area').classList.remove('completion-mode');
    document.getElementById('display-area').classList.remove('show-website');
    document.getElementById('display-area').classList.add('score-mode');
    
    // 假設有一組分數數據
    let scores = [55, 70, 85, 90, 40, 65, 75, 80, 95, 60, 50, 45, 85, 100, 70, 60];

    // 計算每個級距的人數
    let bins = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]; // 10 個級距，每個代表 10 分

    scores.forEach(score => {
        let index = Math.floor(score / 10);
        if (index >= 10) index = 9; // 分數滿分為 100
        bins[index]++;
    });

    // 計算總人數
    let totalPeople = bins.reduce((a, b) => a + b, 0);

    // 準備圖表數據
    let labels = ['0-9', '10-19', '20-29', '30-39', '40-49', '50-59', '60-69', '70-79', '80-89', '90-100'];
    let data = {
        labels: labels,
        datasets: [{
            label: '人數',
            data: bins,
            backgroundColor: '#4caf50',
            borderColor: '#388e3c',
            borderWidth: 1
        }]
    };

    // 配置圖表選項
    let options = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: false
            },
            tooltip: {
                backgroundColor: '#f5f5f5',
                titleColor: '#333',
                bodyColor: '#666',
                borderColor: '#ddd',
                borderWidth: 1
            }
        },
        scales: {
            x: {
                title: {
                    display: true,
                    text: '分數',
                    color: '#333',
                    font: {
                        size: 16,
                        weight: 'bold'
                    }
                },
                ticks: {
                    color: '#333',
                    font: {
                        size: 14
                    }
                },
                grid: {
                    display: false
                }
            },
            y: {
                title: {
                    display: true,
                    text: '人數',
                    color: '#333',
                    font: {
                        size: 16,
                        weight: 'bold'
                    }
                },
                ticks: {
                    beginAtZero: true,
                    color: '#333',
                    font: {
                        size: 14
                    },
                    stepSize: 1
                },
                grid: {
                    color: '#e0e0e0'
                },
                max: totalPeople // 設定 Y 軸的最大值為總人數
            }
        }
    };

    // 在 display-area 中繪製圖表
    let ctx = document.getElementById('myChart').getContext('2d');
    window.myChart = new Chart(ctx, {
        type: 'bar',
        data: data,
        options: options
    });

    // 顯示 display-area
    document.getElementById('display-area').classList.add('show');
});

document.getElementById('completion-button').addEventListener('click', function() {
    // 定義完成度數據
    let completionData = [
        [5, 10, 5, 7, 6, 5, 8, 4, 3, 2],  // 0分鐘
        [8, 12, 10, 12, 11, 10, 9, 7, 6, 5],  // 10分鐘
        [12, 14, 13, 15, 12, 13, 11, 8, 7, 6],  // 20分鐘
        [15, 16, 18, 20, 16, 15, 13, 12, 10, 8]  // 30分鐘
    ];

    // 清空 display-area 並添加四個 canvas，形成 2x2 的圖表
    document.getElementById('display-area').innerHTML = `
        <canvas id="chart0"></canvas>
        <canvas id="chart10"></canvas>
        <canvas id="chart20"></canvas>
        <canvas id="chart30"></canvas>
    `;

    // 切換到完成度模式，啟用 2x2 的佈局
    document.getElementById('display-area').classList.remove('score-mode');
    document.getElementById('display-area').classList.remove('show-website-mode');
    document.getElementById('display-area').classList.add('completion-mode');

    // 確保 canvas 元素已經正確加入到 DOM 中
    const chart0 = document.getElementById('chart0');
    const chart10 = document.getElementById('chart10');
    const chart20 = document.getElementById('chart20');
    const chart30 = document.getElementById('chart30');

    // 檢查 canvas 是否已經存在，確保可以進行繪製
    if (chart0 && chart10 && chart20 && chart30) {
        drawCompletionChart(completionData[0], 'chart0');
        drawCompletionChart(completionData[1], 'chart10');
        drawCompletionChart(completionData[2], 'chart20');
        drawCompletionChart(completionData[3], 'chart30');
    } else {
        console.error('Canvas elements not found in the DOM!');
    }

    // 顯示 display-area
    document.getElementById('display-area').classList.add('show');
});

function drawCompletionChart(data, chartId) {
    let ctx = document.getElementById(chartId).getContext('2d');

    // 設置每個題目固定人數，例如總人數為30
    let totalPeople = 30;

    // 假設數據分為低、中、高完成度
    let lowCompletion = [5, 10, 5, 7, 6, 5, 8, 4, 3, 2];
    let mediumCompletion = [10, 10, 10, 10, 12, 10, 12, 14, 10, 8];
    let highCompletion = [15, 10, 15, 13, 12, 15, 10, 12, 17, 20];

    let chartData = {
        labels: ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10'],
        datasets: [
            {
                label: '低完成度',
                data: lowCompletion,
                backgroundColor: '#ff4c4c'
            },
            {
                label: '中完成度',
                data: mediumCompletion,
                backgroundColor: '#ffd700'
            },
            {
                label: '高完成度',
                data: highCompletion,
                backgroundColor: '#4caf50'
            }
        ]
    };

    new Chart(ctx, {
        type: 'bar',
        data: chartData,
        options: {
            scales: {
                x: { stacked: true },
                y: { beginAtZero: true, stacked: true, max: totalPeople }
            }
        }
    });
}

document.getElementById('show-website-button').addEventListener('click', function() {
    // 清空 display-area 並添加一個 canvas
    document.getElementById('display-area').innerHTML = '<canvas id="websiteChart"></canvas>';

    // 切換到顯示網站模式
    document.getElementById('display-area').classList.remove('score-mode');
    document.getElementById('display-area').classList.remove('completion-mode');
    document.getElementById('display-area').classList.add('show-website-mode');

    // 假設的查詢網站次數數據
    let searchCounts = ['1次', '2次', '3次', '4次', '5次']; // X軸顯示查詢次數
    let lowRange = [5, 6, 7, 8, 10];  // 每次查詢對應的0-40分數區間的人數
    let highRange = [25, 24, 23, 22, 20]; // 每次查詢對應的40-100分數區間的人數

    // 準備圖表數據
    let data = {
        labels: searchCounts,  // X軸：查詢次數
        datasets: [
            {
                label: '0-40分數',
                data: lowRange,  // 低分數區間的人數
                backgroundColor: '#ff4c4c',  // 紅色代表低分數
            },
            {
                label: '40-100分數',
                data: highRange,  // 高分數區間的人數
                backgroundColor: '#4caf50',  // 綠色代表高分數
            }
        ]
    };

    // 配置圖表選項
    let options = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: true  // 顯示圖例
            },
            tooltip: {
                backgroundColor: '#f5f5f5',
                titleColor: '#333',
                bodyColor: '#666',
                borderColor: '#ddd',
                borderWidth: 1
            }
        },
        scales: {
            x: {
                title: {
                    display: true,
                    text: '查詢網站次數',
                    color: '#333',
                    font: {
                        size: 16,
                        weight: 'bold'
                    }
                },
                ticks: {
                    color: '#333',
                    font: {
                        size: 14
                    }
                },
                grid: {
                    display: false
                }
            },
            y: {
                title: {
                    display: true,
                    text: '人數',
                    color: '#333',
                    font: {
                        size: 16,
                        weight: 'bold'
                    }
                },
                ticks: {
                    beginAtZero: true,
                    color: '#333',
                    font: {
                        size: 14
                    },
                    stepSize: 1,
                    max: 30  // 固定人數為 30
                },
                grid: {
                    color: '#e0e0e0'
                }
            }
        }
    };

    // 在 display-area 中繪製堆疊圖表
    let ctx = document.getElementById('websiteChart').getContext('2d');
    window.websiteChart = new Chart(ctx, {
        type: 'bar',
        data: data,
        options: {
            ...options,
            scales: {
                ...options.scales,
                x: {
                    ...options.scales.x,
                    stacked: true  // 啟用 X 軸的堆疊
                },
                y: {
                    ...options.scales.y,
                    stacked: true  // 啟用 Y 軸的堆疊
                }
            }
        }
    });

    // 顯示 display-area
    document.getElementById('display-area').classList.add('show');
});
