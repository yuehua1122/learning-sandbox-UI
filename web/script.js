// 根據點擊的按鈕顯示相應的圖片
function showImage(imageName) {
    const imageDisplay = document.getElementById('image-display');
    
    // 清空當前的內容
    imageDisplay.innerHTML = '';

    // 創建新圖片元素
    const img = document.createElement('img');
    img.src = 'img/' + imageName;
    img.alt = "Selected image";
    
    // 創建提示文字
    const h2 = document.createElement('h2');
    h2.textContent = '選擇的圖片';
    
    // 添加圖片和提示文字到顯示區域
    imageDisplay.appendChild(h2);
    imageDisplay.appendChild(img);
}
