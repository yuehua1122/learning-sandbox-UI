// 全域變數初始化
let selectedItem = null;
let showCode = false;
let completionChecked = false;
let showWebsite = false;
let timeline = null;
let items = null;
let currentScreenData = null; // 當前使用的螢幕資料
let examStartTime, examEndTime, studentStartTime, studentEndTime; // 儲存時間
let chartData = []; // 保存圓餅圖資料
let attainmentData = []; // 保存 student_program_attainment 資料
let barChart = null; // 水平長條圖

const colorPalette = [
    '#FF6384', // 紅色
    '#36A2EB', // 藍色
    '#FFCE56', // 黃色
    '#4BC0C0', // 青色
    '#9966FF', // 紫色
    '#FF9F40', // 橙色
    '#C9CBCF', // 灰色
    '#FFCD56', // 金色
    '#4D5360', // 深灰
    '#7D4F6D'  // 棕色
];

// 取得 Cookie 的值的函數
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
}

// 從 Cookie 中取得 examCode 和 studentId
const examCode = getCookie('examCode');
const studentId = getCookie('studentId');

// 當頁面載入完成後執行
window.onload = function () {
    if (examCode && studentId) {
        console.log('考試代碼:', examCode, '學號:', studentId);

        // 預設不選擇任何功能
        showCode = false;
        completionChecked = false;
        showWebsite = false;

        // 取得程式碼的螢幕資料，並顯示時間軸
        eel.get_exam_time_and_buttons(examCode, studentId)((response) => {
            if (response.error) {
                console.error(response.error);
                document.getElementById('display-area').textContent += ' 無法取得程式碼資料。';
            } else {
                console.log('螢幕資料:', response);
                examStartTime = response.exam_start_time;
                examEndTime = response.exam_end_time;
                studentStartTime = response.student_start_time;
                studentEndTime = response.student_end_time;
                currentScreenData = response.screen_data; // 保存當前螢幕資料
                setupTimeline(); // 設置時間軸
                updateDisplayArea(''); // 清空顯示區域
            }
        });

        // 取得考試資料並處理（圓餅圖）
        eel.get_exam_data(examCode, studentId)((response) => {
            if (response) {
                console.log('題號和每一題的考試時間:', response);
                processExamData(response);
            } else {
                console.error('無法取得考試資料');
            }
        });

        // 取得 student_program_attainment 資料
        eel.get_attainment_data(examCode, studentId)((response) => {
            if (response) {
                attainmentData = response; // 儲存資料
                console.log('每一題在每個時間點的完成度:', attainmentData);
            } else {
                console.error('無法取得達成度資料');
            }
        });

    } else {
        console.error('未能取得考試代碼或學號');
        document.getElementById('display-area').textContent = '未能取得考試代碼或學號！';
    }
};

// 將時間字串轉換為秒數的函數 (格式: HH:MM:SS)
function timeStringToSeconds(timeString) {
    if (!timeString || timeString === 'null') return 0;
    const parts = timeString.split(':').map(Number);
    if (parts.length !== 3) return 0;
    const [hours, minutes, seconds] = parts;
    return hours * 3600 + minutes * 60 + seconds;
}

// 將秒數轉換為 HH:MM:SS 格式
function secondsToTimeString(seconds) {
    const h = Math.floor(seconds / 3600).toString().padStart(2, '0');
    const m = Math.floor((seconds % 3600) / 60).toString().padStart(2, '0');
    const s = Math.floor(seconds % 60).toString().padStart(2, '0');
    return `${h}:${m}:${s}`;
}

// 設置時間軸
function setupTimeline() {
    items = new vis.DataSet(); // 初始化時間軸項目
    items.clear(); // 清除現有項目

    if (!currentScreenData) {
        console.error('沒有可用的螢幕資料');
        return;
    }

    currentScreenData.forEach((entry, index) => {
        const endTime = timeStringToSeconds(entry.end_time);
        if (endTime) {
            const buttonTime = new Date(new Date(studentStartTime).getTime() + endTime * 1000);
            items.add({
                id: index + 1,
                content: '點擊',
                start: buttonTime,
                dataIndex: index // 保存索引以便後續使用
            });
        } else {
            console.log(`跳過無效資料: end_time = ${entry.end_time}`);
        }
    });

    createTimeline(); // 設置時間軸
}

// 創建時間軸
function createTimeline() {
    const container = document.getElementById('timeline-container');
    const options = {
        start: new Date(examStartTime),
        end: new Date(examEndTime),
        min: new Date(examStartTime),
        max: new Date(examEndTime),
        zoomMin: 60 * 1000, // 最小縮放為1分鐘
        zoomMax: 60 * 60 * 1000, // 最大縮放為1小時
        stack: false
    };

    // 如果已存在時間軸，則銷毀
    if (timeline) {
        timeline.destroy();
    }

    // 初始化時間軸
    timeline = new vis.Timeline(container, items, options);

    // 當選擇時間軸項目時的事件處理
    timeline.on('select', function (properties) {
        selectedItem = properties.items.length > 0 ? properties.items[0] : null;
        if (selectedItem) {
            const selectedItemData = items.get(selectedItem);
            const dataIndex = selectedItemData.dataIndex; // 取得資料索引
            if (completionChecked) {
                // 顯示達成度長條圖
                const selectedTime = getTimeFromItem(selectedItem);
                updateBarChart(selectedTime);
            } else if (showCode) {
                // 顯示程式碼內容
                updateDisplayArea(currentScreenData[dataIndex].content);
            } else if (showWebsite) {
                // 顯示查詢網站
                displayWebsite(currentScreenData[dataIndex].website);
            } else {
                updateDisplayArea('請選擇功能以顯示內容');
            }
        }
    });
}

// 根據按鈕ID取得對應的時間（格式為 HH:MM:SS）
function getTimeFromItem(itemId) {
    // 根據 itemId 計算時間
    const timeInSeconds = 30 * itemId; // 每個按鈕代表 30 秒
    return secondsToTimeString(timeInSeconds);
}

// 更新水平長條圖
function updateBarChart(timeKey) {
    // 從 attainmentData 中取得對應時間點的資料
    const labels = [];
    const dataValues = [];

    attainmentData.forEach(item => {
        labels.push(item.sub_question);
        const value = item[timeKey] !== undefined ? item[timeKey] : 0;
        dataValues.push(value);
    });

    // 如果圖表尚未初始化，則初始化
    if (!barChart) {
        const ctx = document.getElementById('myBarChart').getContext('2d');
        barChart = new Chart(ctx, {
            type: 'bar', // 使用 'bar' 類型
            data: {
                labels: labels,
                datasets: [{
                    label: '達成度 (%)',
                    data: dataValues,
                    backgroundColor: 'rgba(54, 162, 235, 0.7)'
                }]
            },
            options: {
                indexAxis: 'y', // 將 x 和 y 軸互換，顯示水平長條圖
                scales: {
                    x: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });
    } else {
        // 更新圖表資料
        barChart.data.labels = labels;
        barChart.data.datasets[0].data = dataValues;
        barChart.update();
    }

}

// 根據 30 秒間隔重新生成時間軸按鈕
function regenerateTimeline() {
    items.clear(); // 清除現有項目
    const startTime = new Date(studentStartTime).getTime() + 30 * 1000; // 起始時間加30秒
    const endTime = new Date(studentEndTime).getTime();

    let buttonId = 1;
    for (let time = startTime; time <= endTime; time += 30 * 1000) {
        items.add({
            id: buttonId++,
            content: '查看',
            start: new Date(time)
        });
    }

    createTimeline(); // 重新創建時間軸
}

// 更新顯示區域的內容
function updateDisplayArea(content) {
    const displayArea = document.getElementById('display-area');
    displayArea.textContent = content;
    displayArea.classList.add('show');
}

// 顯示查詢網站
function displayWebsite(url) {
    if (url && url !== '') {
        updateDisplayArea(url); // 在 display-area 顯示網址
        window.open(url, '_blank', 'width=800,height=600'); // 開啟新視窗
    } else {
        updateDisplayArea('沒有對應的網站資料');
    }
}

function showDesignSpecifications() {
    eel.get_design_specifications(examCode, studentId)((response) => {
        if (response.error) {
            updateDisplayArea(response.error);
        } else {
            const content = `分數: ${response.score}\n\n違規次數: ${response.violation_count}\n\n思考流程:\n${response.thinking_process}`;
            updateDisplayArea(content);
        }
    });
}

// 初始化長條圖，所有題目的達成度為 0%
function initBarChartWithZero() {
    const labels = attainmentData.map(item => item.sub_question);
    const dataValues = labels.map(() => 0); // 全部設為 0%

    if (!barChart) {
        const ctx = document.getElementById('myBarChart').getContext('2d');
        barChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: '達成度 (%)',
                    data: dataValues,
                    backgroundColor: 'rgba(54, 162, 235, 0.7)'
                }]
            },
            options: {
                indexAxis: 'y',
                scales: {
                    x: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });
    } else {
        // 更新圖表資料
        barChart.data.labels = labels;
        barChart.data.datasets[0].data = dataValues;
        barChart.update();
    }
}

// 處理考試資料（用於圓餅圖）
function processExamData(data) {
    // 將時間轉換為秒並計算總時間
    let totalExamTime = 0;
    let questionTimes = [];

    data.forEach(item => {
        let timeInSeconds = timeStringToSeconds(item.total_time);
        totalExamTime += timeInSeconds;
        questionTimes.push({
            subQuestion: item.sub_question,
            timeInSeconds: timeInSeconds
        });
    });

    // 防止除以零的情況
    if (totalExamTime === 0) {
        console.error('總考試時間為 0，無法計算比例');
        return;
    }

    // 計算每個題目所佔的比例
    chartData = questionTimes.map(item => ({
        label: item.subQuestion,
        value: ((item.timeInSeconds / totalExamTime) * 100).toFixed(2)
    }));

    updatePieChart(); // 更新圓餅圖
}

// 初始化圓餅圖
const pieCtx = document.getElementById('myPieChart').getContext('2d');
let pieChart = new Chart(pieCtx, {
    type: 'pie',
    data: {
        labels: [],  // 待更新的標籤
        datasets: [{
            data: [],  // 待更新的資料
            backgroundColor: [],  // 將根據題目數量生成顏色
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: true,
                position: 'right',  // 將圖例移到右邊
            },
            title: {
                display: true,
                text: '每題考試時間佔比',  // 添加標題
                font: {
                    size: 18
                }
            },
            tooltip: {
                callbacks: {
                    label: function (context) {
                        let label = context.label || '';
                        let value = context.parsed || 0;
                        return `${label}: ${value}%`;
                    }
                }
            }
        }
    }
});

// 更新圓餅圖的函數
function updatePieChart() {
    // 建立主題號與顏色的映射
    const mainQuestionColors = {};
    const mainQuestions = [];

    // 先找出所有的主題號
    chartData.forEach(item => {
        const mainQuestionMatch = item.label.match(/^\d+/);
        const mainQuestion = mainQuestionMatch ? mainQuestionMatch[0] : item.label;
        if (!mainQuestions.includes(mainQuestion)) {
            mainQuestions.push(mainQuestion);
        }
    });

    // 為每個主題號指定顏色
    mainQuestions.forEach((mq, index) => {
        mainQuestionColors[mq] = colorPalette[index % colorPalette.length];
    });

    // 為每個子題指定對應的顏色
    const colors = chartData.map(item => {
        const mainQuestionMatch = item.label.match(/^\d+/);
        const mainQuestion = mainQuestionMatch ? mainQuestionMatch[0] : item.label;
        return mainQuestionColors[mainQuestion];
    });

    pieChart.data.labels = chartData.map(item => item.label);
    pieChart.data.datasets[0].data = chartData.map(item => item.value);
    pieChart.data.datasets[0].backgroundColor = colors;

    pieChart.update();
}

// 事件處理函數

// 點擊「程式碼」按鈕的事件處理
document.getElementById('code-button').onclick = () => {
    showCode = true;
    completionChecked = false;
    showWebsite = false;

    // 再次取得程式碼資料並設置時間軸
    eel.get_exam_time_and_buttons(examCode, studentId)((response) => {
        if (response.error) {
            console.error(response.error);
            document.getElementById('display-area').textContent += ' 無法取得程式碼資料。';
        } else {
            console.log('程式碼螢幕資料:', response);
            examStartTime = response.exam_start_time;
            examEndTime = response.exam_end_time;
            studentStartTime = response.student_start_time;
            studentEndTime = response.student_end_time;
            currentScreenData = response.screen_data; // 保存當前螢幕資料
            setupTimeline(); // 設置時間軸
            updateDisplayArea('請選擇時間軸以查看程式碼');
        }
    });
};

// 點擊「完成度」按鈕的事件處理
document.getElementById('completion-button').onclick = () => {
    completionChecked = true;
    showCode = false;
    showWebsite = false;
    updateDisplayArea('');

    // 顯示長條圖容器
    document.getElementById('bar-chart-container').style.display = 'block';

    // 調整界面佈局
    document.querySelector('.bottom-section').classList.add('expand-up');
    document.querySelector('.top-section').classList.add('top-section-hidden');
    document.getElementById('exit-button').classList.add('show');

    regenerateTimeline(); // 重新生成時間軸項目

    // 初始化長條圖，所有值為 0%
    initBarChartWithZero();
};

// 點擊「退出」按鈕的事件處理，恢復原始界面
document.getElementById('exit-button').onclick = () => {
    // 恢復界面佈局
    document.querySelector('.bottom-section').classList.remove('expand-up');
    document.querySelector('.top-section').classList.remove('top-section-hidden');
    document.querySelector('.timeline-container').style.bottom = '0';
    document.getElementById('exit-button').classList.remove('show');
    document.getElementById('display-area').style.display = "block"; // 確保顯示區域可見

    // 隱藏長條圖容器
    document.getElementById('bar-chart-container').style.display = 'none';

    // 清除長條圖資料
    if (barChart) {
        barChart.destroy();
        barChart = null;
    }

    // 重置狀態變數，不選擇任何功能
    showCode = false;
    completionChecked = false;
    showWebsite = false;

    // 重新取得螢幕資料並設置時間軸
    eel.get_exam_time_and_buttons(examCode, studentId)((response) => {
        if (response.error) {
            console.error(response.error);
            document.getElementById('display-area').textContent += ' 無法取得螢幕資料。';
        } else {
            console.log('螢幕資料:', response);
            examStartTime = response.exam_start_time;
            examEndTime = response.exam_end_time;
            studentStartTime = response.student_start_time;
            studentEndTime = response.student_end_time;
            currentScreenData = response.screen_data; // 保存當前螢幕資料
            setupTimeline(); // 設置時間軸
            updateDisplayArea(''); // 清空顯示區域
        }
    });
};

// 「設計規格花費時長」按鈕的事件處理
document.getElementById('design-specifications').onclick = () => {
    showDesignSpecifications();
};

// 點擊「顯示查詢網站」按鈕的事件處理
document.getElementById('show-website-button').onclick = () => {
    showWebsite = true;
    showCode = false;
    completionChecked = false;

    eel.get_exam_time_and_buttons(examCode, studentId, true)((response) => {
        if (response.error) {
            console.error(response.error);
            document.getElementById('display-area').textContent += ' 無法取得網站資料。';
        } else {
            console.log('網站螢幕資料:', response);
            examStartTime = response.exam_start_time;
            examEndTime = response.exam_end_time;
            studentStartTime = response.student_start_time;
            studentEndTime = response.student_end_time;
            currentScreenData = response.screen_data; // 保存當前螢幕資料
            setupTimeline(); // 設置時間軸
            updateDisplayArea('請選擇時間軸以顯示網站');
        }
    });
};

// 點擊「回到首頁」按鈕的事件處理
document.getElementById('home-button').onclick = () => {
    document.body.classList.add('fade-out');
    setTimeout(() => {
        window.location.href = "index.html";
    }, 500);
};
