document.addEventListener('DOMContentLoaded', () => {
    // Add Color Blind styles
    const style = document.createElement('style');
    style.textContent = `
        /* Overrides for Red -> Orange/Amber */
        html.color-blind .text-red-500, html.color-blind .text-red-600, html.color-blind .text-rose-500, html.color-blind .text-rose-400, html.color-blind .text-error { color: #f59e0b !important; }
        html.color-blind .bg-red-500, html.color-blind .bg-red-600, html.color-blind .bg-rose-500, html.color-blind .bg-error { background-color: #f59e0b !important; }
        html.color-blind .border-red-500, html.color-blind .border-rose-500, html.color-blind .border-error { border-color: #f59e0b !important; }
        html.color-blind .border-red-500\\/30, html.color-blind .border-rose-500\\/30 { border-color: rgba(245, 158, 11, 0.3) !important; }
        html.color-blind .bg-red-500\\/5, html.color-blind .bg-rose-500\\/20 { background-color: rgba(245, 158, 11, 0.05) !important; }
        html.color-blind .bg-red-500\\/10 { background-color: rgba(245, 158, 11, 0.1) !important; }
        
        /* Overrides for Green -> Blue */
        html.color-blind .text-emerald-500, html.color-blind .text-green-500 { color: #3b82f6 !important; }
        html.color-blind .bg-emerald-500, html.color-blind .bg-green-500 { background-color: #3b82f6 !important; }
        html.color-blind .border-emerald-500, html.color-blind .border-green-500 { border-color: #3b82f6 !important; }
        html.color-blind .border-emerald-500\\/30 { border-color: rgba(59, 130, 246, 0.3) !important; }
        html.color-blind .bg-emerald-500\\/5, html.color-blind .bg-emerald-500\\/20 { background-color: rgba(59, 130, 246, 0.05) !important; }
        
        /* Map specifics */
        html.color-blind path[stroke="red"] { stroke: #f59e0b !important; }
        html.color-blind path[fill="red"] { fill: #f59e0b !important; }
        html.color-blind path[stroke="green"] { stroke: #3b82f6 !important; }
        html.color-blind path[fill="green"] { fill: #3b82f6 !important; }
    `;
    document.head.appendChild(style);

    // Find nav controls container to inject button
    const themeBtn = document.getElementById('theme-toggle-btn-nav');
    if (themeBtn && themeBtn.parentNode) {
        const cbBtn = document.createElement('button');
        cbBtn.id = 'color-blind-toggle-btn';
        cbBtn.className = themeBtn.className;
        cbBtn.title = "Toggle Color-Blind Safe Mode";
        cbBtn.innerHTML = '<span class="material-symbols-outlined text-lg">palette</span>';
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

    // Centralized Mobile Menu Toggle Logic
    const mobileMenuBtn = document.getElementById('mobile-menu-btn');
    const mobileNavMenu = document.getElementById('mobile-nav-menu');
    if (mobileMenuBtn && mobileNavMenu) {
        mobileMenuBtn.addEventListener('click', () => {
            mobileNavMenu.classList.toggle('hidden');
        });
    }

    // Centralized Theme Toggle Logic
    if (themeBtn) {
        themeBtn.addEventListener('click', () => {
            const isDark = document.documentElement.classList.contains('dark');
            if (isDark) {
                document.documentElement.classList.remove('dark');
                document.documentElement.classList.add('light');
                localStorage.setItem('orca_theme', 'light');
            } else {
                document.documentElement.classList.add('dark');
                document.documentElement.classList.remove('light');
                localStorage.setItem('orca_theme', 'dark');
            }
        });
    }
});
