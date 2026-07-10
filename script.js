document.addEventListener('DOMContentLoaded', () => {
    const greetingElement = document.getElementById('greeting');
    const hour = new Date().getHours();
    
    let greetingText = '你好！';
    
    if (hour >= 5 && hour < 12) {
        greetingText = '早上好！';
    } else if (hour >= 12 && hour < 18) {
        greetingText = '下午好！';
    } else if (hour >= 18 && hour < 22) {
        greetingText = '晚上好！';
    } else {
        greetingText = '夜深了！';
    }

    greetingElement.textContent = greetingText;
});
