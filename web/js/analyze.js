let selectedItem = null;
let showCode = false;
let completionChecked = false;
let showWebsite = false;

// 設定時間軸的資料
const items = new vis.DataSet([
    {id: 1, content: '第10分鐘', start: '2024-09-16 00:10:00'},
    {id: 2, content: '第20分鐘', start: '2024-09-16 00:20:00'},
    {id: 3, content: '第30分鐘', start: '2024-09-16 00:30:00'},
    {id: 4, content: '第40分鐘', start: '2024-09-16 00:40:00'},
    {id: 5, content: '第50分鐘', start: '2024-09-16 00:50:00'},
]);

// 初始化時間軸
const container = document.getElementById('timeline-container');
const options = {
    start: '2024-09-16 00:00:00',
    end: '2024-09-16 01:00:00',
    min: '2024-09-16 00:00:00',
    max: '2024-09-16 01:00:00',
    zoomMin: 1000 * 60,
    zoomMax: 1000 * 60 * 60,
};
const timeline = new vis.Timeline(container, items, options);

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
    completionChecked = false; // 重置完成度狀態
    showWebsite = false; // 重置顯示網站狀態
    if (!selectedItem) {
        updateDisplayArea('請選擇時間軸以查看程式碼');
    } else {
        displayCode();
    }
};

// 點擊「完成度」按鈕
document.getElementById('completion-button').onclick = () => {
    completionChecked = true;
    showCode = false; // 重置程式碼狀態
    showWebsite = false; // 重置顯示網站狀態
    updateDisplayArea('請選擇時間軸以查看完成度');
};

// 點擊「提示」按鈕
document.getElementById('hint-button').onclick = () => {
    completionChecked = true;
    showCode = false; // 重置程式碼狀態
    showWebsite = false; // 重置顯示網站狀態
    updateDisplayArea('請選擇時間軸以查看提示');
};

// 點擊「顯示查詢網站」按鈕
document.getElementById('show-website-button').onclick = () => {
    showWebsite = true;
    showCode = false; // 重置程式碼狀態
    completionChecked = false; // 重置完成度狀態
    updateDisplayArea('請選擇時間軸以顯示網站');
};

// 點擊「回到首頁」按鈕
document.getElementById('home-button').onclick = () => {
    window.location.href = "index.html";
};

// 點擊時間軸上的按鈕
timeline.on('select', function (properties) {
    selectedItem = properties.items.length > 0 ? properties.items[0] : null;

    // 顯示程式碼
    if (showCode && selectedItem) {
        displayCode();
    }

    // 顯示完成度
    if (completionChecked && selectedItem) {
        const progress = Math.floor(Math.random() * 100); // 模擬完成度數據
        updateDisplayArea(`第 ${selectedItem} 分鐘的完成度：${progress}%`);
        pieChart.data.datasets[0].data = [progress, 100 - progress]; // 更新圓餅圖
        pieChart.update();
    }

    // 顯示查詢網站
    if (showWebsite && selectedItem) {
        displayWebsite();
    }
});

// 更新顯示區域
function updateDisplayArea(content) {
    const displayArea = document.getElementById('display-area');
    displayArea.textContent = content;
    displayArea.classList.add('show');
}

// 顯示程式碼
function displayCode() {
    const codeContent = `function example() {\n    console.log('Hello, world!');\n    let x = Math.random();\n    if (x > 0.5) {\n        return 'High';\n    } else {\n        return 'Low';\n    }\n}`;
    updateDisplayArea(codeContent);
}

// 顯示查詢網站
function displayWebsite() {
    const url = "https://www.google.com"; // 假設的網站網址
    updateDisplayArea(url);
    window.open(url, '_blank', 'width=800,height=600'); // 開啟新視窗
}
