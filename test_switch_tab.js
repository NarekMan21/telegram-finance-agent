// Тестовая функция switchTab
function testSwitchTab(tab) {
    const pages = {
        'dashboard': 'index.html',
        'transactions': 'transactions.html',
        'analytics': 'analytics.html',
        'settings': 'settings.html'
    };
    
    console.log('Switching to tab:', tab);
    console.log('Available pages:', pages);
    
    if (pages[tab]) {
        console.log('Redirecting to:', pages[tab]);
        // В реальном приложении здесь будет:
        // window.location.href = pages[tab];
        return pages[tab];
    } else {
        console.log('Page not found for tab:', tab);
        return null;
    }
}

// Тестирование функции
console.log('Testing switchTab function:');
console.log('Result for "settings":', testSwitchTab('settings'));
console.log('Result for "dashboard":', testSwitchTab('dashboard'));
console.log('Result for "unknown":', testSwitchTab('unknown'));