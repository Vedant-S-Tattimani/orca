document.addEventListener('DOMContentLoaded', () => {
    // Add Color Blind styles
    const style = document.createElement('style');
    style.textContent = `
        html.color-blind .text-red-500 { color: #f59e0b !important; }
        html.color-blind .text-red-600 { color: #d97706 !important; }
        html.color-blind .bg-red-500 { background-color: #f59e0b !important; }
        html.color-blind .bg-red-600 { background-color: #d97706 !important; }
        html.color-blind .border-red-500 { border-color: #f59e0b !important; }
        html.color-blind .border-red-500\\/30 { border-color: rgba(245, 158, 11, 0.3) !important; }
        html.color-blind .bg-red-500\\/5 { background-color: rgba(245, 158, 11, 0.05) !important; }
        html.color-blind .bg-red-500\\/10 { background-color: rgba(245, 158, 11, 0.1) !important; }
        
        html.color-blind .text-emerald-500 { color: #3b82f6 !important; }
        html.color-blind .bg-emerald-500 { background-color: #3b82f6 !important; }
        html.color-blind .border-emerald-500 { border-color: #3b82f6 !important; }
        
        /* Map specifics */
        html.color-blind path[stroke="red"] { stroke: #f59e0b !important; }
        html.color-blind path[fill="red"] { fill: #f59e0b !important; }
    `;
    document.head.appendChild(style);

    // Find nav controls container to inject button
    const themeBtn = document.getElementById('theme-toggle-btn-nav');
    if (themeBtn && themeBtn.parentNode) {
        const cbBtn = document.createElement('button');
        cbBtn.id = 'color-blind-toggle-btn';
        cbBtn.className = themeBtn.className;
        cbBtn.title = "Toggle Deuteranopia Safe Mode";
        cbBtn.innerHTML = '<span class="material-symbols-outlined text-lg">visibility</span>';
        themeBtn.parentNode.insertBefore(cbBtn, themeBtn.nextSibling);
        
        // Restore state
        if (localStorage.getItem('colorBlindMode') === 'true') {
            document.documentElement.classList.add('color-blind');
            cbBtn.classList.add('text-cyan-500');
        }

        cbBtn.addEventListener('click', () => {
            document.documentElement.classList.toggle('color-blind');
            const isCB = document.documentElement.classList.contains('color-blind');
            localStorage.setItem('colorBlindMode', isCB);
            if (isCB) {
                cbBtn.classList.add('text-cyan-500');
            } else {
                cbBtn.classList.remove('text-cyan-500');
            }
        });
    }
});
