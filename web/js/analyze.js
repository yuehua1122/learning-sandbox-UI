// 全域變數初始化
let selectedItem = null;
let showCode = false;
let completionChecked = false;
let showWebsite = false;
let timeline = null;
let items = null;
let initialScreenData = null; // 儲存初始的螢幕數據
let examStartTime, examEndTime, studentStartTime, studentEndTime; // 儲存時間
let chartData = []; // 保存圖表數據

// 獲取 Cookie 的值的函數
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
}

// 獲取 examCode 和 studentId 從 Cookie 中
const examCode = getCookie('examCode');
const studentId = getCookie('studentId');

// 當頁面載入完成後執行
window.onload = function () {
    if (examCode && studentId) {
        console.log('考試代碼:', examCode, '學號:', studentId);

        // 調用後端函數，獲取考試時間和螢幕數據
        eel.get_exam_time_and_buttons(examCode, studentId)((response) => {
            if (response.error) {
                console.error(response.error);
                document.getElementById('display-area').textContent += ' 無法獲取考試時間。';
            } else {
                console.log('考試時間和螢幕數據:', response);
                examStartTime = response.exam_start_time;
                examEndTime = response.exam_end_time;
                studentStartTime = response.student_start_time;
                studentEndTime = response.student_end_time;
                initialScreenData = response.screen_data; // 儲存初始螢幕數據
                setupTimeline(); // 設置時間軸
            }
        });

        // 獲取考試數據並處理
        eel.get_exam_data(examCode, studentId)((response) => {
            if (response) {
                console.log('題號和每一題的考試時間:', response);
                processExamData(response);
            } else {
                console.error('無法獲取考試數據');
            }
        });
    } else {
        console.error('未能獲取考試代碼或學號');
        document.getElementById('display-area').textContent = '未能獲取考試代碼或學號！';
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

// 設置時間軸
function setupTimeline() {
    items = new vis.DataSet(); // 初始化時間軸項目

    // 檢查並處理螢幕數據
    console.log("螢幕數據:", initialScreenData);

    initialScreenData.forEach((entry, index) => {
        const endTime = timeStringToSeconds(entry.end_time);
        if (endTime && entry.content) {
            const buttonTime = new Date(new Date(studentStartTime).getTime() + endTime * 1000);
            items.add({
                id: index + 1,
                content: '點擊',
                start: buttonTime
            });
        } else {
            console.log(`跳過無效數據: end_time = ${entry.end_time}, content = ${entry.content}`);
        }
    });

    createTimeline();
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
            if (showCode) {
                // 顯示程式碼內容
                updateDisplayArea(initialScreenData[selectedItem - 1].content);
            } else if (completionChecked) {
                // 不再改變圓餅圖，只顯示完成度訊息
                updateDisplayArea('請選擇功能以顯示內容');
            } else if (showWebsite) {
                // 顯示查詢網站
                displayWebsite();
            } else {
                updateDisplayArea('請選擇功能以顯示內容');
            }
        }
    });
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
}

// 更新顯示區域的內容
function updateDisplayArea(content) {
    const displayArea = document.getElementById('display-area');
    displayArea.textContent = content;
    displayArea.classList.add('show');
}

// 顯示查詢網站
function displayWebsite() {
    const url = "https://www.google.com";
    updateDisplayArea(url);
    window.open(url, '_blank', 'width=800,height=600');
}

// 處理考試數據
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
const ctx = document.getElementById('myPieChart').getContext('2d');
let pieChart = new Chart(ctx, {
    type: 'pie',
    data: {
        labels: [],  // 待更新的標籤
        datasets: [{
            data: [],  // 待更新的數據
            backgroundColor: [],  // 將根據題目數量生成顏色
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
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
    // 生成隨機顏色
    const colors = chartData.map(() => '#' + Math.floor(Math.random() * 16777215).toString(16));

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
    updateDisplayArea('請選擇時間軸以查看程式碼');
};

// 點擊「完成度」按鈕的事件處理
document.getElementById('completion-button').onclick = () => {
    completionChecked = true;
    showCode = false;
    showWebsite = false;
    updateDisplayArea('');

    // 調整界面布局
    document.querySelector('.bottom-section').classList.add('expand-up');
    document.querySelector('.top-section').classList.add('top-section-hidden');
    document.getElementById('exit-button').classList.add('show');
    document.querySelector('.timeline-container').style.bottom = '-600px';

    regenerateTimeline(); // 重新生成時間軸項目
};

// 點擊「退出」按鈕的事件處理，恢復原始界面
document.getElementById('exit-button').onclick = () => {
    document.querySelector('.bottom-section').classList.remove('expand-up');
    document.querySelector('.top-section').classList.remove('top-section-hidden');
    document.querySelector('.timeline-container').style.bottom = '0';
    document.getElementById('exit-button').classList.remove('show');
    document.getElementById('display-area').classList.remove('show');
    
    setupTimeline(); // 恢復初始時間軸
    
    // 不再改變圓餅圖
};

// 點擊「提示」按鈕的事件處理（目前無功能）
document.getElementById('hint-button').onclick = () => {
    // 暫無操作
};

// 點擊「顯示查詢網站」按鈕的事件處理
document.getElementById('show-website-button').onclick = () => {
    showWebsite = true;
    showCode = false;
    completionChecked = false;
    updateDisplayArea('請選擇時間軸以顯示網站');
};

// 點擊「回到首頁」按鈕的事件處理
document.getElementById('home-button').onclick = () => {
    document.body.classList.add('fade-out');
    setTimeout(() => {
        window.location.href = "index.html";
    }, 500);
};
