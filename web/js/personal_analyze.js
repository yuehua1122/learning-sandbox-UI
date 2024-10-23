// 全局變量初始化
let selectedItem = null;
let showCode = false;
let completionChecked = false;
let showWebsite = false;
let showHint = false; // 新增，用於追蹤是否顯示提示功能
let timeline = null;
let items = null;
let currentScreenData = null; // 當前使用的螢幕資料
let examStartTime, examEndTime, studentStartTime, studentEndTime; // 儲存時間
let chartData = []; // 保存餅圖資料
let attainmentData = []; // 保存 student_program_attainment 資料
let barChart = null; // 水平柱狀圖
let extraPointsData = null; // 保存 extra_points 資料
let hintData = [];

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

// 獲取 Cookie 的值的函數
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
}

// 從 Cookie 中獲取 examCode 和 studentId
const examCode = getCookie('examCode');
const studentId = getCookie('studentId');

// 當頁面加載完成後執行
window.onload = function () {
    if (examCode && studentId) {
        console.log('考試代碼:', examCode, '學號:', studentId);

        const h2Element = document.getElementById('exam-info');
        h2Element.innerHTML = `學號: ${studentId.toUpperCase()}  考試代碼: ${examCode.toUpperCase()}`;

        // 預設不選擇任何功能
        showCode = false;
        completionChecked = false;
        showWebsite = false;
        showHint = false; // 初始化為 false

        // 獲取程式碼的螢幕資料，並顯示時間軸
        eel.get_exam_time_and_buttons(examCode, studentId)((response) => {
            if (response.error) {
                console.error(response.error);
                document.getElementById('display-area').textContent += ' 無法獲取程式碼資料。';
            } else {
                console.log('螢幕資料:', response);
                examStartTime = response.exam_start_time;
                examEndTime = response.exam_end_time;
                studentStartTime = response.student_start_time;
                studentEndTime = response.student_end_time;
                currentScreenData = response.screen_data; // 保存當前螢幕資料

                // 獲取 extra_points 資料
                eel.get_extra_points(examCode, studentId)((extraPointsResponse) => {
                    if (extraPointsResponse) {
                        console.log('加分:', extraPointsResponse);
                        extraPointsData = extraPointsResponse; // 保存 extra_points 資料
                        setupTimeline(); // 設置時間軸
                        updateDisplayArea('');
                    } else {
                        console.error('無法獲取加分資料');
                    }
                });
            }
        });

        // 獲取考試資料並處理（餅圖）
        eel.get_exam_data(examCode, studentId)((response) => {
            if (response) {
                console.log('題號和每一題的考試時間:', response);
                processExamData(response);
            } else {
                console.error('無法獲取考試資料');
            }
        });

        // 獲取 student_program_attainment 資料
        eel.get_attainment_data(examCode, studentId)((response) => {
            if (response) {
                attainmentData = response; // 存儲資料
                console.log('每一題在每個時間點的完成度:', attainmentData);
            } else {
                console.error('無法獲取達成度資料');
            }
        });

        // 獲取提示資料
        eel.get_student_hints(examCode, studentId)((response) => {
            if (response) {
                hintData = response;
                console.log('提示資料:', hintData);
            } else {
                console.error('無法獲取提示資料');
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

            // 檢查該時間點的 extra_points 狀態
            let extraPoint = 0;
            if (extraPointsData) {
                const matchedData = extraPointsData.find(item => item.end_time === entry.end_time);
                if (matchedData) {
                    extraPoint = matchedData.extra_points;
                }
            }

            items.add({
                id: index + 1,
                content: '點擊',
                start: buttonTime,
                dataIndex: index, // 保存索引以便後續使用
                extraPoint: extraPoint // 保存 extra_points 狀態
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
        stack: false,
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
            const dataIndex = selectedItemData.dataIndex; // 獲取資料索引
            if (completionChecked) {
                // 顯示達成度柱狀圖
                const selectedTime = getTimeFromItem(selectedItem);
                updateBarChart(selectedTime);
            } else if (showCode) {
                // 顯示程式碼內容
                updateDisplayArea(currentScreenData[dataIndex].content);
            } else if (showWebsite) {
                // 顯示查詢網站，並顯示加分按鈕
                displayWebsite(currentScreenData[dataIndex].website, selectedItemData.extraPoint, currentScreenData[dataIndex].end_time);
            } else {
                updateDisplayArea('請選擇功能以顯示內容');
            }
        }
    });
}

// 根據按鈕ID獲取對應的時間（格式為 HH:MM:SS）
function getTimeFromItem(itemId) {
    // 根據 itemId 計算時間
    const timeInSeconds = 30 * itemId; // 每個按鈕代表 30 秒
    return secondsToTimeString(timeInSeconds);
}

// 更新水平柱狀圖
function updateBarChart(timeKey) {
    // 從 attainmentData 中獲取對應時間點的資料
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
                indexAxis: 'y', // 將 x 和 y 軸互換，顯示水平柱狀圖
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

// 顯示查詢網站，並添加加分按鈕
function displayWebsite(url, extraPoint, endTime) {
    const displayArea = document.getElementById('display-area');
    displayArea.innerHTML = ''; // 清空顯示區域

    if (url && url !== '') {
        // 顯示網址
        const urlElement = document.createElement('p');
        urlElement.textContent = url;
        displayArea.appendChild(urlElement);

        // 顯示狀態
        const statusElement = document.createElement('p');
        statusElement.className = 'display-area-status';
        statusElement.textContent = extraPoint === 1 ? '狀態：已加分' : '狀態：未加分';
        displayArea.appendChild(statusElement);

        // 創建按鈕容器
        const buttonContainer = document.createElement('div');
        buttonContainer.className = 'bonus-buttons';
        displayArea.appendChild(buttonContainer);

        // 創建加分按鈕
        const addButton = document.createElement('button');
        addButton.textContent = '加分';
        addButton.disabled = extraPoint === 1; // 已加分時禁用
        buttonContainer.appendChild(addButton);

        // 創建取消加分按鈕
        const cancelButton = document.createElement('button');
        cancelButton.textContent = '取消加分';
        cancelButton.className = 'cancel-button';
        cancelButton.disabled = extraPoint === 0; // 未加分時禁用
        buttonContainer.appendChild(cancelButton);

        // 加分按鈕點擊事件
        addButton.onclick = function () {
            const newExtraPoint = 1;
            // 調用後端函數更新資料庫
            eel.update_extra_points(examCode, studentId, endTime, newExtraPoint)((response) => {
                if (response.success) {
                    extraPoint = newExtraPoint; // 更新 extraPoint 變量

                    // 更新狀態文字
                    statusElement.textContent = '狀態：已加分';

                    // 更新按鈕狀態
                    addButton.disabled = true;
                    cancelButton.disabled = false;

                    // 更新時間軸按鈕（如果需要）
                    const selectedItemData = items.get(selectedItem);
                    selectedItemData.extraPoint = extraPoint;
                    items.update(selectedItemData);
                } else {
                    console.error('更新加分狀態失敗:', response.error);
                }
            });
        };

        // 取消加分按鈕點擊事件
        cancelButton.onclick = function () {
            const newExtraPoint = 0;
            // 調用後端函數更新資料庫
            eel.update_extra_points(examCode, studentId, endTime, newExtraPoint)((response) => {
                if (response.success) {
                    extraPoint = newExtraPoint; // 更新 extraPoint 變量

                    // 更新狀態文字
                    statusElement.textContent = '狀態：未加分';

                    // 更新按鈕狀態
                    addButton.disabled = false;
                    cancelButton.disabled = true;

                    // 更新時間軸按鈕（如果需要）
                    const selectedItemData = items.get(selectedItem);
                    selectedItemData.extraPoint = extraPoint;
                    items.update(selectedItemData);
                } else {
                    console.error('更新加分狀態失敗:', response.error);
                }
            });
        };

        // 創建「開啟網站」按鈕
        const openButton = document.createElement('button');
        openButton.textContent = '開啟網站';
        buttonContainer.appendChild(openButton);

        // 「開啟網站」按鈕點擊事件
        openButton.onclick = function () {
            window.open(url, '_blank', 'width=800,height=600');
        };

    } else {
        updateDisplayArea('沒有對應的查詢網站資料');
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

// 初始化柱狀圖，所有題目的達成度為 0%
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

// 處理考試資料（用於餅圖）
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

    updatePieChart(); // 更新餅圖
}

// 初始化餅圖
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
                text: '依解題規格比較解答所用時間佔比',  // 添加標題
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

// 更新餅圖的函數
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

// 初始化樹狀圖的函數
function initTreeDiagram() {
    // 構建樹狀圖的資料結構
    const treeStructure = {
        text: { name: "提示功能" },
        children: []
    };

    // 根據 hintData 動態生成子節點
    hintData.forEach((item) => {
        const subQuestionNode = {
            text: { name: `題號：${item.sub_question}` },
            children: [
                {
                    text: { name: "當前程式碼" },
                    children: [
                        {
                            text: { name: item.code },
                            children: [
                                {
                                    text: { name: "提示回應" },
                                    children: [
                                        {
                                            text: { name: item.request },
                                            children: [
                                                {
                                                    text: { name: "加分"},
                                                    action: 'add'
                                                },
                                                {
                                                    text: { name: "取消加分"},
                                                    action: 'cancel'
                                                }
                                            ]
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        };
        treeStructure.children.push(subQuestionNode);
    });

    // 使用 Treant.js 繪製樹狀圖
    const config = {
        chart: {
            container: "#tree-container",
            connectors: {
                type: 'bCurve',
                style: {
                    'stroke': '#00838f',
                    'stroke-width': 2,
                    'arrow-end': 'block-wide-long'
                }
            },
            node: {
                collapsable: true,
                HTMLclass: 'node'
            },
            animation: {
                nodeSpeed: 900,
                connectorsSpeed: 900
            }
        },
        nodeStructure: treeStructure
    };

    // 檢查是否已經初始化過
    if (window.myTreeChart) {
        // 如果已經存在，則銷毀並重新創建
        document.getElementById('tree-container').innerHTML = '';
    }

    // 創建樹狀圖
    window.myTreeChart = new Treant(config);
}

// 事件處理函數

// 點擊「程式碼」按鈕的事件處理
document.getElementById('code-button').onclick = () => {
    showCode = true;
    completionChecked = false;
    showWebsite = false;
    showHint = false;

    // 顯示時間軸
    document.getElementById('timeline-container').style.display = 'block';

    // 再次獲取程式碼資料並設置時間軸
    eel.get_exam_time_and_buttons(examCode, studentId)((response) => {
        if (response.error) {
            console.error(response.error);
            document.getElementById('display-area').textContent += ' 無法獲取程式碼資料。';
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
    showHint = false;
    updateDisplayArea('');

    // 顯示柱狀圖容器
    document.getElementById('bar-chart-container').style.display = 'block';

    // 調整界面佈局
    document.querySelector('.bottom-section').classList.add('expand-up');
    document.querySelector('.top-section').classList.add('top-section-hidden');
    document.getElementById('exit-button').classList.add('show');

    // 不隱藏時間軸
    // document.getElementById('timeline-container').style.display = 'none';

    regenerateTimeline(); // 重新生成時間軸項目

    // 初始化柱狀圖，所有值為 0%
    initBarChartWithZero();
};

// 新增：點擊「提示」按鈕的事件處理
document.getElementById('hint-button').onclick = () => {
    showHint = true;
    showCode = false;
    completionChecked = false;
    showWebsite = false;
    updateDisplayArea('');

    // 調整界面佈局（與完成度按鈕相同）
    document.querySelector('.bottom-section').classList.add('expand-up');
    document.querySelector('.top-section').classList.add('top-section-hidden');
    document.getElementById('exit-button').classList.add('show');

    // 隱藏時間軸
    document.getElementById('timeline-container').style.display = 'none';

    // 隱藏其他可能的內容
    document.getElementById('bar-chart-container').style.display = 'none';

    // 顯示樹狀圖容器
    document.getElementById('tree-container').style.display = 'block';

    // 初始化樹狀圖
    initTreeDiagram();
};

// 點擊「退出」按鈕的事件處理，恢復原始界面
document.getElementById('exit-button').onclick = () => {
    // 恢復界面佈局
    document.querySelector('.bottom-section').classList.remove('expand-up');
    document.querySelector('.top-section').classList.remove('top-section-hidden');
    document.querySelector('.timeline-container').style.bottom = '0';
    document.getElementById('exit-button').classList.remove('show');
    document.getElementById('display-area').style.display = "block"; // 確保顯示區域可見

    // 隱藏柱狀圖容器
    document.getElementById('bar-chart-container').style.display = 'none';

    // 隱藏樹狀圖容器
    document.getElementById('tree-container').style.display = 'none';

    // 顯示時間軸
    document.getElementById('timeline-container').style.display = 'block';

    // 清除柱狀圖資料
    if (barChart) {
        barChart.destroy();
        barChart = null;
    }

    // 重置狀態變量，不選擇任何功能
    showCode = false;
    completionChecked = false;
    showWebsite = false;
    showHint = false;

    // 重新獲取螢幕資料並設置時間軸
    eel.get_exam_time_and_buttons(examCode, studentId)((response) => {
        if (response.error) {
            console.error(response.error);
            document.getElementById('display-area').textContent += ' 無法獲取螢幕資料。';
        } else {
            console.log('螢幕資料:', response);
            examStartTime = response.exam_start_time;
            examEndTime = response.exam_end_time;
            studentStartTime = response.student_start_time;
            studentEndTime = response.student_end_time;
            currentScreenData = response.screen_data; // 保存當前螢幕資料

            // 獲取 extra_points 資料
            eel.get_extra_points(examCode, studentId)((extraPointsResponse) => {
                if (extraPointsResponse) {
                    extraPointsData = extraPointsResponse;
                    setupTimeline(); // 設置時間軸
                    updateDisplayArea(''); // 清空顯示區域
                } else {
                    console.error('無法獲取加分資料');
                }
            });
        }
    });
};

// 「解題規格花費時長」按鈕的事件處理
document.getElementById('design-specifications').onclick = () => {
    showDesignSpecifications();
};

// 點擊「顯示查詢網站」按鈕的事件處理
document.getElementById('show-website-button').onclick = () => {
    showWebsite = true;
    showCode = false;
    completionChecked = false;
    showHint = false;

    // 顯示時間軸
    document.getElementById('timeline-container').style.display = 'block';

    eel.get_exam_time_and_buttons(examCode, studentId, true)((response) => {
        if (response.error) {
            console.error(response.error);
            document.getElementById('display-area').textContent += ' 無法獲取網站資料。';
        } else {
            console.log('網站螢幕資料:', response);
            examStartTime = response.exam_start_time;
            examEndTime = response.exam_end_time;
            studentStartTime = response.student_start_time;
            studentEndTime = response.student_end_time;
            currentScreenData = response.screen_data; // 保存當前螢幕資料

            // 獲取 extra_points 資料
            eel.get_extra_points(examCode, studentId)((extraPointsResponse) => {
                if (extraPointsResponse) {
                    extraPointsData = extraPointsResponse; // 保存 extra_points 資料
                    setupTimeline(); // 設置時間軸
                    updateDisplayArea('請選擇時間軸以顯示網站');
                } else {
                    console.error('無法獲取加分資料');
                }
            });
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

