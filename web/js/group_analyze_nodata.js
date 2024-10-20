// 取得標題元素
const titleElement = document.querySelector('.title-vertical');

// 定義模式類別陣列
const modes = ['score-mode', 'completion-mode', 'design-mode', 'show-website-mode'];

// 顯示標題並更新內容的函式
function showTitle(content) {
    titleElement.style.display = 'block';
    titleElement.textContent = content;
}

// 重置 display-area 的函式，清除內容並設置所需的元素
function setupDisplayArea(innerHTMLContent) {
    const displayArea = document.getElementById('display-area');
    displayArea.innerHTML = innerHTMLContent;
}

// 切換模式的函式
function switchMode(modeClass) {
    const displayArea = document.getElementById('display-area');
    displayArea.classList.remove(...modes); // 移除所有模式類別
    displayArea.classList.add(modeClass);
    displayArea.classList.add('show'); // 顯示 display-area
}

// 返回首頁按鈕事件監聽
document.getElementById('home-button').addEventListener('click', function() {
    document.body.classList.add('fade-out');
    setTimeout(function() {
        window.location.href = "index.html";
    }, 500);
});

// 成績分布圖按鈕事件監聽
document.getElementById('code-button').addEventListener('click', function() {
    showTitle('成績分布圖');
    setupDisplayArea('<canvas id="myChart"></canvas>');
    switchMode('score-mode');
    drawScoreChart();
});

// 各解題規格完成度人數比較圖按鈕事件監聽
document.getElementById('completion-button').addEventListener('click', function() {
    showTitle('各解題規格完成度人數比較圖');
    setupDisplayArea(`
        <canvas id="chart0"></canvas>
        <canvas id="chart10"></canvas>
        <canvas id="chart20"></canvas>
        <canvas id="chart30"></canvas>
    `);
    switchMode('completion-mode');
    drawCompletionCharts();
});

// 解題規格與人數分布圖按鈕事件監聽
document.getElementById('design-specifications').addEventListener('click', function() {
    showTitle('解題規格與人數分布圖');
    setupDisplayArea('<canvas id="designChart"></canvas>');
    switchMode('design-mode');
    drawDesignChart();
});

// 網站查詢次數與人數分布圖按鈕事件監聽
document.getElementById('show-website-button').addEventListener('click', function() {
    showTitle('查詢網站次數圖');
    setupDisplayArea('<canvas id="websiteChart"></canvas>');
    switchMode('show-website-mode');
    drawWebsiteChart();
});

document.getElementById('heatmap-button').addEventListener('click', function() {
    document.body.classList.add('fade-out');
    setTimeout(function() {
        window.location.href = "heatmap.html";
    }, 500);
});

// 繪製成績分布圖的函式
function drawScoreChart() {
    // 假設有一組分數數據
    const scores = [55, 70, 85, 90, 40, 65, 75, 80, 95, 60, 50, 45, 85, 100, 70, 60,
                    62, 78, 88, 53, 73, 84, 92, 57, 66, 76, 83, 94, 68, 71];

    // 計算每個級距的人數
    const bins = new Array(10).fill(0); // 10 個級距，每個代表 10 分

    scores.forEach(score => {
        let index = Math.floor(score / 10);
        if (index >= 10) index = 9; // 分數滿分為 100
        bins[index]++;
    });

    // 準備圖表數據
    const labels = ['0-9', '10-19', '20-29', '30-39', '40-49', '50-59', '60-69', '70-79', '80-89', '90-100'];
    const data = {
        labels: labels,
        datasets: [{
            label: '人數',
            data: bins,
            backgroundColor: '#4caf50',
            borderColor: '#388e3c',
            borderWidth: 1
        }]
    };

    // 計算最大人數，並設置為 Y 軸的最大值
    const maxPeople = Math.max(...bins);

    // 配置圖表選項
    const options = {
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
                suggestedMax: maxPeople // 設定 Y 軸的最大值為 bins 中的最大值
            }
        }
    };

    // 繪製圖表
    const ctx = document.getElementById('myChart').getContext('2d');
    window.myChart = new Chart(ctx, {
        type: 'bar',
        data: data,
        options: options
    });
}

// 繪製完成度圖表的函式
function drawCompletionCharts() {
    // 定義完成度數據，每個時間點的數據包含低、中、高完成度的人數
    const completionData = [
        {   // 0分鐘
            low: [30, 30, 30, 30, 30, 30, 30, 30, 30, 30],
            medium: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            high: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        },
        {   // 10分鐘
            low: [3, 7, 7, 14, 15, 20, 24, 28, 29, 30],
            medium: [5, 9, 11, 8, 10, 7, 5, 2, 1, 0],
            high: [22, 14, 12, 8, 5, 3, 1, 0, 0, 0]
        },
        {   // 20分鐘
            low: [0, 1, 0, 0, 5, 3, 7, 5, 5, 7],
            medium: [1, 3, 2, 10, 8, 14, 15, 19, 18, 16],
            high: [29, 26, 28, 20, 17, 13, 8, 6, 7, 7]
        },
        {   // 30分鐘
            low: [0, 0, 0, 0, 0, 1, 2, 3, 3, 5],
            medium: [0, 0, 1, 4, 3, 4, 4, 3, 2, 2],
            high: [30, 30, 29, 26, 27, 25, 24, 24, 25, 23]
        }
    ];

    // 時間點標題陣列
    const timeTitles = ['第0分鐘', '第10分鐘', '第20分鐘', '第30分鐘'];

    // 迭代每個時間點，繪製對應的圖表
    completionData.forEach((data, index) => {
        drawCompletionChart(data, `chart${index * 10}`, timeTitles[index]);
    });
}

// 繪製單個完成度圖表的函式
function drawCompletionChart(data, chartId, title) {
    const ctx = document.getElementById(chartId).getContext('2d');

    const chartData = {
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
                        text: '解題規格',
                        font: {
                            size: 14,
                            weight: 'bold'
                        },
                        color: '#333'
                    }
                },
                y: {
                    beginAtZero: true,
                    stacked: true,
                    max: 30,
                    title: {
                        display: true,
                        text: '人數',
                        font: {
                            size: 14,
                            weight: 'bold'
                        },
                        color: '#333'
                    }
                }
            }
        }
    });
}

// 繪製解題規格與人數分布圖的函式
function drawDesignChart() {
    // 假設的解題規格時間長度數據
    const labels = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']; // X軸：解題規格
    const lowRange = [0, 0, 0, 0, 2, 1, 1, 5, 2, 7]; // 0-30分區間的人數
    const midRange = [5, 7, 8, 9, 10, 10, 9, 10, 8, 7];  // 30-60分區間的人數
    const highRange = [25, 23, 22, 21, 18, 19, 20, 15, 20, 16]; // 60分以上區間的人數

    const data = {
        labels: labels,
        datasets: [
            {
                label: '60分鐘以上',
                data: lowRange,
                backgroundColor: '#ff4c4c'
            },
            {
                label: '30-60分鐘',
                data: midRange,
                backgroundColor: '#ffd700'
            },
            {
                label: '0-30分鐘',
                data: highRange,
                backgroundColor: '#4caf50'
            }
        ]
    };

    const options = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: true
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
                stacked: true,
                title: {
                    display: true,
                    text: '解題規格',
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
                stacked: true,
                beginAtZero: true,
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
                    color: '#333',
                    font: {
                        size: 14
                    },
                    stepSize: 1,
                    suggestedMax: 30
                },
                grid: {
                    color: '#e0e0e0'
                }
            }
        }
    };

    const ctx = document.getElementById('designChart').getContext('2d');
    window.designChart = new Chart(ctx, {
        type: 'bar',
        data: data,
        options: options
    });
}

// 繪製網站查詢次數與人數分布圖的函式
function drawWebsiteChart() {
    // 假設的查詢網站次數數據
    const labels = ['1次', '2次', '3次', '4次', '5次']; // X軸：查詢次數
    const lowRange = [2, 1, 2, 1, 2];  // 0-59分數區間的人數
    const midRange = [4, 1, 3, 1, 2];  // 60-79分數區間的人數
    const highRange = [3, 2, 2, 3, 1]; // 80-100分數區間的人數

    const data = {
        labels: labels,
        datasets: [
            {
                label: '0-59分數',
                data: lowRange,
                backgroundColor: '#ff4c4c'
            },
            {
                label: '60-79分數',
                data: midRange,
                backgroundColor: '#ffd700'
            },
            {
                label: '80-100分數',
                data: highRange,
                backgroundColor: '#4caf50'
            }
        ]
    };

    const options = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: true
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
                stacked: true,
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
                stacked: true,
                beginAtZero: true,
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
                    color: '#333',
                    font: {
                        size: 14
                    },
                    stepSize: 1,
                    suggestedMax: 30
                },
                grid: {
                    color: '#e0e0e0'
                }
            }
        }
    };

    const ctx = document.getElementById('websiteChart').getContext('2d');
    window.websiteChart = new Chart(ctx, {
        type: 'bar',
        data: data,
        options: options
    });
}
