// 获取标题元素
const titleElement = document.querySelector('.title-vertical');

// 定义一个函数，用于显示标题并更新内容
function showTitle(content) {
    titleElement.style.display = 'block'; // 显示标题
    titleElement.textContent = content;   // 更新标题内容
}

document.getElementById('home-button').onclick = () => {
    document.body.classList.add('fade-out');
    setTimeout(() => {
        window.location.href = "index.html";
    }, 500);
};

document.getElementById('code-button').addEventListener('click', function() {
    // 清空 display-area
    document.getElementById('display-area').innerHTML = '<canvas id="myChart"></canvas>';
    showTitle('評分結果');
    
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
    showTitle('各解題規格完成度人數比較圖');
    // 定义完成度数据，每个时间点的数据包含低、中、高完成度的人数
    let completionData = [
        {   // 0分钟
            low: [30, 30, 30, 30, 30, 30, 30, 30, 30, 30],
            medium: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            high: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        },
        {   // 10分钟
            low: [3, 7, 7, 14, 15, 20, 24, 28, 29, 30],
            medium: [5, 9, 11, 8, 10, 7, 5, 2, 1, 0],
            high: [22, 14, 12, 8, 5, 3, 1, 0, 0, 0]
        },
        {   // 20分钟
            low: [0, 1, 0, 0, 5, 3, 7, 5, 5, 7],
            medium: [1, 3, 2, 10, 8, 14, 15, 19, 18, 16],
            high: [29, 26, 28, 20, 17, 13, 8, 6, 7, 7]
        },
        {   // 30分钟
            low: [0, 0, 0, 0, 0, 1, 2, 3, 3, 5],
            medium: [0, 0, 1, 4, 3, 4, 4, 3, 2, 2],
            high: [30, 30, 29, 26, 27, 25, 24, 24, 25, 23]
        }
    ];

    // 清空 display-area 并添加四个 canvas，形成 2x2 的图表
    document.getElementById('display-area').innerHTML = `
        <canvas id="chart0"></canvas>
        <canvas id="chart10"></canvas>
        <canvas id="chart20"></canvas>
        <canvas id="chart30"></canvas>
    `;

    // 切换到完成度模式，启用 2x2 的布局
    document.getElementById('display-area').classList.remove('score-mode');
    document.getElementById('display-area').classList.remove('show-website-mode');
    document.getElementById('display-area').classList.add('completion-mode');

    // 确保 canvas 元素已经正确加入到 DOM 中
    const chart0 = document.getElementById('chart0');
    const chart10 = document.getElementById('chart10');
    const chart20 = document.getElementById('chart20');
    const chart30 = document.getElementById('chart30');

    // 检查 canvas 是否已经存在，确保可以进行绘制
    if (chart0 && chart10 && chart20 && chart30) {
        drawCompletionChart(completionData[0], 'chart0', '第0分鐘');
        drawCompletionChart(completionData[1], 'chart10', '第10分鐘');
        drawCompletionChart(completionData[2], 'chart20', '第20分鐘');
        drawCompletionChart(completionData[3], 'chart30', '第30分鐘');
    } else {
        console.error('Canvas elements not found in the DOM!');
    }

    // 显示 display-area
    document.getElementById('display-area').classList.add('show');
});

function drawCompletionChart(data, chartId, title) {
    let ctx = document.getElementById(chartId).getContext('2d');

    let chartData = {
        labels: ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10'],
        datasets: [
            {
                label: '低完成度',
                data: data.low,
                backgroundColor: '#ff4c4c'
            },
            {
                label: '中完成度',
                data: data.medium,
                backgroundColor: '#ffd700'
            },
            {
                label: '高完成度',
                data: data.high,
                backgroundColor: '#4caf50'
            }
        ]
    };

    new Chart(ctx, {
        type: 'bar',
        data: chartData,
        options: {
            plugins: {
                title: {
                    display: true,
                    text: title
                }
            },
            scales: {
                x: {
                    stacked: true,
                    title: {
                        display: true,
                        text: '解題規格', // 设置 X 轴标题
                        font: {
                            size: 14,
                            weight: 'bold'
                        },
                        color: '#333' // 可根据需要调整颜色
                    }
                },
                y: {
                    beginAtZero: true,
                    stacked: true,
                    max: 30,
                    title: {
                        display: true,
                        text: '人數', // 设置 Y 轴标题
                        font: {
                            size: 14,
                            weight: 'bold'
                        },
                        color: '#333' // 可根据需要调整颜色
                    }
                }
            }
        }
    });
}

document.getElementById('show-website-button').addEventListener('click', function() {
    showTitle('查詢網站次數分析');
    // 清空 display-area 並添加一個 canvas
    document.getElementById('display-area').innerHTML = '<canvas id="websiteChart"></canvas>';

    // 切換到顯示網站模式
    document.getElementById('display-area').classList.remove('score-mode');
    document.getElementById('display-area').classList.remove('completion-mode');
    document.getElementById('display-area').classList.add('show-website-mode');

    // 假設的查詢網站次數數據
    let searchCounts = ['1次', '2次', '3次', '4次', '5次']; // X軸顯示查詢次數
    let lowRange = [3, 2, 7, 1, 10];  // 每次查詢對應的0-59分數區間的人數
    let midRange = [7, 4, 8, 5, 5];  // 每次查詢對應的60-79分數區間的人數
    let highRange = [10, 8, 15, 9, 3]; // 每次查詢對應的80-100分數區間的人數

    // 準備圖表數據
    let data = {
        labels: searchCounts,  // X軸：查詢次數
        datasets: [
            {
                label: '0-59分數',
                data: lowRange,  // 低分數區間的人數
                backgroundColor: '#ff4c4c',  // 紅色代表低分數
            },
            {
                label: '60-79分數',
                data: midRange,  // 中分數區間的人數
                backgroundColor: '#ffd700',  // 黃色代表高分數
            },
            {
                label: '80-100分數',
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
                    suggestedMax: 30  // 固定人數為 30
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
