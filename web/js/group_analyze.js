// 獲取 Cookie 的值的函數
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
}

// 從 Cookie 中獲取 examCode 和 studentId
const examCode = getCookie('examCode');

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
    // 使用 eel 從資料庫取得分數數據
    eel.get_scores(examCode)(function(scores) {
        // 確保取得的 scores 是數字陣列
        scores = scores.map(Number);
        console.log("分數 : " + scores)

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
        const maxPeople = Math.max(...bins) + 1; // 加 1 以避免頂到圖表邊緣

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
                    suggestedMax: maxPeople // 設定 Y 軸的最大值為 bins 中的最大值加 1
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
    });
}

// 繪製完成度圖表的函數
function drawCompletionCharts() {
    eel.get_completion_data(examCode)(function(result) {
        const labels = result.sub_questions;
        const completionData = result.completion_data;

        // 時間點標題陣列
        const timeTitles = ['第0分鐘', '第10分鐘', '第20分鐘', '第30分鐘'];

        // 迭代每個時間點的數據，繪製對應的圖表
        completionData.forEach((data, index) => {
            drawCompletionChart(labels, data, `chart${index * 10}`, timeTitles[index]);
        });
    });
}

// 繪製單個完成度圖表的函數
function drawCompletionChart(labels, data, chartId, title) {
    const ctx = document.getElementById(chartId).getContext('2d');

    const chartData = {
        labels: labels,
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

    // 創建新的圖表實例
    window['completionChart' + chartId] = new Chart(ctx, {
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
    // 使用 eel 從資料庫取得數據
    eel.get_design_chart_data(examCode)(function(result) {
        const labels = result.labels;
        const lowRange = result.lowRange;
        const midRange = result.midRange;
        const highRange = result.highRange;

        console.log("題號 : " + labels)
        console.log("0-30分鐘 : " + lowRange)
        console.log("31-60分鐘 : " + midRange)
        console.log("60分鐘以上 : " + highRange)

        const data = {
            labels: labels,
            datasets: [
                {
                    label: '0-30分鐘',
                    data: lowRange,
                    backgroundColor: '#4caf50'
                },
                {
                    label: '31-60分鐘',
                    data: midRange,
                    backgroundColor: '#ffd700'
                },
                {
                    label: '60分鐘以上',
                    data: highRange,
                    backgroundColor: '#ff4c4c'
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
                        suggestedMax: Math.max(...lowRange, ...midRange, ...highRange) + 5
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
    });
}

// 繪製網站查詢次數與人數分布圖的函式
function drawWebsiteChart() {
    // 使用 eel 從資料庫取得數據
    eel.get_website_chart_data(examCode)(function(result) {
        const labels = result.labels;
        const lowRange = result.lowRange;
        const midRange = result.midRange;
        const highRange = result.highRange;

        console.log("查詢次數 : " + labels)
        console.log("0-59分 : " + lowRange)
        console.log("60-79分 : " + midRange)
        console.log("80-100分數 : " + highRange)

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
                        suggestedMax: Math.max(...lowRange, ...midRange, ...highRange) + 5
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
    });
}
