let selectedItem = null;
let showCode = false;
let completionChecked = false;
let showWebsite = false;
let timeline = null;
let items = null;
let initialScreenData = null; // 儲存初始的 screenData
let examStartTime, examEndTime, studentStartTime, studentEndTime; // 儲存時間

// 獲取 Cookie 的值
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}

// 獲取 exam_code 和 student_id 從 Cookie 中
const examCode = getCookie('examCode');
const studentId = getCookie('studentId');

// 檢查是否成功獲取值並顯示到頁面上
window.onload = function () {
    if (examCode && studentId) {
        console.log('考試代碼:', examCode, '學號:', studentId);

        // 調用 Python 後端函數，查詢考試時間和按鈕數據
        eel.get_exam_time_and_buttons(examCode, studentId)(function (response) {
            if (response.error) {
                console.error(response.error);
                document.getElementById('display-area').textContent += ' 無法獲取考試時間。';
            } else {
                console.log('考試時間和螢幕數據:', response);
                examStartTime = response.exam_start_time;
                examEndTime = response.exam_end_time;
                studentStartTime = response.student_start_time;
                studentEndTime = response.student_end_time;
                initialScreenData = response.screen_data; // 儲存最初的 screen_data
                setupTimeline(examStartTime, examEndTime, studentStartTime, initialScreenData); // 使用最初的 screen_data
            }
        });
    } else {
        console.error('未能獲取考試代碼或學號');
        document.getElementById('display-area').textContent = '未能獲取考試代碼或學號！';
    }
};

// 設置時間軸
function setupTimeline(examStartTime, examEndTime, studentStartTime, screenData) {
    items = new vis.DataSet(); // 重新定義 items

    // 檢查 screenData 並打印其內容
    console.log("螢幕數據:", screenData);

    screenData.forEach((entry, index) => {
        const endTime = entry.end_time ? timeStringToSeconds(entry.end_time) : null;
        if (endTime && entry.content) {
            const buttonTime = new Date(new Date(studentStartTime).getTime() + endTime * 1000);
            items.add({
                id: index + 1,
                content: `點擊`,
                start: buttonTime
            });
        } else {
            console.log(`跳過無效數據: end_time = ${entry.end_time}, content = ${entry.content}`);
        }
    });

    createTimeline(examStartTime, examEndTime);
}

// 創建時間軸
function createTimeline(startTime, endTime) {
    const container = document.getElementById('timeline-container');
    const options = {
        start: new Date(startTime),
        end: new Date(endTime),
        min: new Date(startTime),
        max: new Date(endTime),
        zoomMin: 1000 * 60,
        zoomMax: 1000 * 60 * 60,
        stack: false
    };

    // 清除現有的 timeline（如果有）
    if (timeline !== null) {
        timeline.destroy();
    }

    timeline = new vis.Timeline(container, items, options);

    timeline.on('select', function (properties) {
        selectedItem = properties.items.length > 0 ? properties.items[0] : null;
        if (selectedItem) {
            if (showCode) {
                updateDisplayArea(initialScreenData[selectedItem - 1].content); // 使用初始數據顯示內容
            } else if (completionChecked) {
                const selectedItemData = items.get(selectedItem);
                const progress = Math.floor(Math.random() * 100);
                updateDisplayArea(`第 ${selectedItemData.id} 分鐘的完成度：${progress}%`);
                pieChart.data.datasets[0].data = [progress, 100 - progress];
                pieChart.update();
            } else if (showWebsite) {
                displayWebsite();
            } else {
                updateDisplayArea('請選擇功能以顯示內容');
            }
        }
    });
}

// 將時間字串轉換為秒數 (格式: HH:MM:SS)
function timeStringToSeconds(timeString) {
    if (!timeString || timeString === 'null') return 0;
    const [hours, minutes, seconds] = timeString.split(':').map(Number);
    return hours * 3600 + minutes * 60 + seconds;
}

// 根據 30 秒間隔重新生成時間軸按鈕，按 `studentStartTime` 到 `studentEndTime` 生成
function regenerateTimeline() {
    items.clear(); // 清除之前的按鈕
    const startTime = new Date(studentStartTime).getTime() + 30 * 1000; // 從 studentStartTime + 30 秒開始
    const endTime = new Date(studentEndTime).getTime();
    
    let buttonId = 1;
    for (let time = startTime; time <= endTime; time += 30 * 1000) {
        items.add({
            id: buttonId++,
            content: `查看`,
            start: new Date(time)
        });
    }
}

// 點擊「程式碼」按鈕
document.getElementById('code-button').onclick = () => {
    showCode = true;
    completionChecked = false;
    showWebsite = false;
    updateDisplayArea('請選擇時間軸以查看程式碼');
};

// 點擊「完成度」按鈕
document.getElementById('completion-button').onclick = () => {
    completionChecked = true;
    showCode = false;
    showWebsite = false;
    updateDisplayArea('');

    document.querySelector('.bottom-section').classList.add('expand-up');
    document.querySelector('.top-section').classList.add('top-section-hidden');
    document.getElementById('exit-button').classList.add('show');
    document.querySelector('.timeline-container').style.bottom = '-600px';

    regenerateTimeline(); // 重新生成時間軸按鈕
};

// 點擊「退出」按鈕，恢復原狀
document.getElementById('exit-button').onclick = () => {
    document.querySelector('.bottom-section').classList.remove('expand-up');
    document.querySelector('.top-section').classList.remove('top-section-hidden');
    document.querySelector('.timeline-container').style.bottom = '0';
    document.getElementById('exit-button').classList.remove('show');

    // 恢復初始按鈕（使用 setupTimeline 和初始 screen_data）
    setupTimeline(examStartTime, examEndTime, studentStartTime, initialScreenData);
    updateDisplayArea('');
};

// 點擊「提示」按鈕（目前無功能）
document.getElementById('hint-button').onclick = () => {
    // 無操作
};

// 點擊「顯示查詢網站」按鈕
document.getElementById('show-website-button').onclick = () => {
    showWebsite = true;
    showCode = false;
    completionChecked = false;
    updateDisplayArea('請選擇時間軸以顯示網站');
};

// 暴露給 Python 使用的 goToHome 函數
eel.expose(goToHome);
function goToHome() {
    document.body.classList.add('fade-out');
    setTimeout(() => {
        window.location.href = "index.html";
    }, 500);
}

// 點擊「回到首頁」按鈕
document.getElementById('home-button').onclick = () => {
    eel.go_to_home();
};

// 更新顯示區域
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

// 初始化圓餅圖
const ctx = document.getElementById('myPieChart').getContext('2d');
const pieChart = new Chart(ctx, {
    type: 'pie',
    data: {
        labels: ['完成', '未完成'],
        datasets: [{
            data: [50, 50],
            backgroundColor: ['#4caf50', '#f44336'],
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false
    }
});
