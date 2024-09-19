// 設定視窗大小
window.resizeTo(1500, 900);

function goToStep2() {
    const examCode = document.getElementById('examCode').value;
    if (examCode.trim() === "") {
        document.getElementById('examCodeError').style.display = 'block';
        return;
    }
    document.getElementById('examCodeError').style.display = 'none';
    toggleVisibility('step1', 'step2');
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
    const studentId = document.getElementById('studentId').value;
    if (studentId.trim() === "") {
        document.getElementById('studentIdError').style.display = 'block';
        return;
    }
    document.getElementById('studentIdError').style.display = 'none';

    // 添加動畫效果
    document.getElementById('step3-individual').classList.add('fade-out');

    // 延遲跳轉以顯示動畫
    setTimeout(() => {
        window.location.href = 'personal_analyze.html';
    }, 500); // 0.5秒後跳轉
}

function goBack(previousStep) {
    const currentStep = document.querySelector('.container.show').id;
    toggleVisibility(currentStep, previousStep);
}

// 通用的顯示與隱藏切換
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
