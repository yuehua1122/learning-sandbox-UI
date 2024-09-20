let selectedItem = null;
let showCode = false;
let completionChecked = false;
let showWebsite = false;

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
window.onload = function() {
    if (examCode && studentId) {
        console.log('Exam Code:', examCode, 'Student ID:', studentId);

        // 調用 Python 後端函數，查詢考試時間和按鈕數據
        eel.get_exam_time_and_buttons(examCode, studentId)(function(response) {
            if (response.error) {
                console.error(response.error);
                document.getElementById('display-area').textContent += ' 無法獲取考試時間。';
            } else {
                console.log('Exam Time and Screen Data:', response);
                setupTimeline(response.exam_start_time, response.exam_end_time, response.student_start_time, response.screen_data);
            }
        });
    } else {
        console.error('未能獲取 exam_code 或 student_id');
        document.getElementById('display-area').textContent = '未能獲取考試代碼或學號！';
    }
};

// 設置時間軸
function setupTimeline(examStartTime, examEndTime, studentStartTime, screenData) {
    const items = new vis.DataSet();

    // 檢查 screenData 並打印其內容
    console.log("Screen Data:", screenData);

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

    const container = document.getElementById('timeline-container');
    const options = {
        start: new Date(examStartTime),  // 確保是日期格式
        end: new Date(examEndTime),
        min: new Date(examStartTime),
        max: new Date(examEndTime),
        zoomMin: 1000 * 60,
        zoomMax: 1000 * 60 * 60,
        stack: false
    };
    const timeline = new vis.Timeline(container, items, options);

    timeline.on('select', function(properties) {
        selectedItem = properties.items.length > 0 ? properties.items[0] : null;
        if (selectedItem) {
            // 根據已選擇的功能顯示對應的內容
            if (showCode) {
                updateDisplayArea(screenData[selectedItem - 1].content); // 顯示程式碼
            } else if (completionChecked) {
                const selectedItemData = items.get(selectedItem);
                const progress = Math.floor(Math.random() * 100);
                updateDisplayArea(`第 ${selectedItemData.id} 分鐘的完成度：${progress}%`);
                pieChart.data.datasets[0].data = [progress, 100 - progress]; // 更新圓餅圖
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

    // 將 bottom-section 的上邊界拉伸至 .top-section 的頂部，並隱藏 top-section
    document.querySelector('.bottom-section').classList.add('expand-up');
    document.querySelector('.top-section').classList.add('top-section-hidden');

    // 將 timeline-container 的 bottom 設置為 -600px，並顯示退出按鈕
    document.querySelector('.timeline-container').style.bottom = '-600px';
    document.getElementById('exit-button').classList.add('show'); // 顯示退出按鈕
};

// 點擊「退出」按鈕，恢復原狀
document.getElementById('exit-button').onclick = () => {
    document.querySelector('.bottom-section').classList.remove('expand-up');
    document.querySelector('.top-section').classList.remove('top-section-hidden');
    document.querySelector('.timeline-container').style.bottom = '0';
    document.getElementById('exit-button').classList.remove('show'); // 隱藏退出按鈕
};

// 點擊「提示」按鈕
document.getElementById('hint-button').onclick = () => {
    completionChecked = true;
    showCode = false;
    showWebsite = false;
    updateDisplayArea('請選擇時間軸以查看提示');
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
    const url = "https://www.google.com"; // 假設的網站網址
    updateDisplayArea(url);
    window.open(url, '_blank', 'width=800,height=600'); // 開啟新視窗
}
