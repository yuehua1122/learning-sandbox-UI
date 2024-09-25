// 設定視窗大小
window.resizeTo(1500, 900);

// 從 Cookie 中取得值的函數
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
}

// 通用的顯示與隱藏切換函數
function toggleVisibility(hideId, showId) {
    document.getElementById(hideId).classList.remove('show');
    document.getElementById(hideId).classList.add('hidden');

    const showElement = document.getElementById(showId);
    showElement.classList.remove('hidden');

    // 使用 setTimeout 以觸發過渡效果
    setTimeout(() => {
        showElement.classList.add('show');
    }, 100);
}

// 導覽功能函數
function goToStep2() {
    const examCode = document.getElementById('examCode').value.trim();
    const errorElement = document.getElementById('examCodeError');

    if (examCode === "") {
        errorElement.style.display = 'block';
        errorElement.textContent = '請輸入考試代碼！';
        return;
    }

    // 呼叫 Python 函數檢查考試代碼
    eel.check_exam_code(examCode)((response) => {
        if (response === 'valid') {
            // 隱藏錯誤訊息
            errorElement.style.display = 'none';
            // 儲存考試代碼到 Cookie
            document.cookie = `examCode=${examCode}; path=/`;
            // 切換到下一步
            toggleVisibility('step1', 'step2');
        } else {
            // 顯示錯誤訊息
            errorElement.style.display = 'block';
            errorElement.textContent = '無效的考試代碼！';
        }
    });
}

function goToIndividual() {
    toggleVisibility('step2', 'step3-individual');
}

function goToGroup() {
    // 添加動畫效果
    document.getElementById('step2').classList.add('fade-out');

    // 延遲跳轉以顯示動畫
    setTimeout(() => {
        window.location.href = 'group_analyze.html';
    }, 500); // 0.5秒後跳轉
}

function goToIndividualAnalysis() {
    const studentId = document.getElementById('studentId').value.trim();
    const examCode = getCookie('examCode'); // 從 Cookie 中取得考試代碼
    const errorElement = document.getElementById('studentIdError');

    if (studentId === "") {
        errorElement.style.display = 'block';
        errorElement.textContent = '請輸入學號！';
        return;
    }

    // 呼叫 Python 函數檢查學生是否參加該考試
    eel.check_student_exam(studentId, examCode)((response) => {
        if (response === 'valid') {
            // 隱藏錯誤訊息
            errorElement.style.display = 'none';
            // 儲存學號到 Cookie
            document.cookie = `studentId=${studentId}; path=/`;

            // 添加動畫效果
            document.getElementById('step3-individual').classList.add('fade-out');

            // 延遲跳轉以顯示動畫
            setTimeout(() => {
                window.location.href = 'personal_analyze.html';
            }, 500); // 0.5秒後跳轉
        } else {
            // 顯示錯誤訊息
            errorElement.style.display = 'block';
            errorElement.textContent = '該學生未參加此考試！';
        }
    });
}

function goBack(previousStep) {
    const currentStep = document.querySelector('.container.show').id;
    toggleVisibility(currentStep, previousStep);
}

// 事件監聽器的設定
document.addEventListener('DOMContentLoaded', () => {
    // 考試代碼輸入欄位的 Enter 鍵事件
    const examCodeInput = document.getElementById('examCode');
    examCodeInput.addEventListener('keyup', (event) => {
        if (event.code === 'Enter') {
            event.preventDefault();
            goToStep2();
        }
    });

    // 學生學號輸入欄位的 Enter 鍵事件
    const studentIdInput = document.getElementById('studentId');
    if (studentIdInput) {
        studentIdInput.addEventListener('keyup', (event) => {
            if (event.code === 'Enter') {
                event.preventDefault();
                goToIndividualAnalysis();
            }
        });
    }
});
