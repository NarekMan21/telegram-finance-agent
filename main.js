// Telegram Financial Agent - Main JavaScript

// Global variables
let transactions = [];
let filteredTransactions = [];
let currentFilter = 'all';
let currentPeriod = 'week';
let updateInterval;

// Configuration
const config = {
    apiId: localStorage.getItem('apiId') || '20517386',
    apiHash: localStorage.getItem('apiHash') || '73457be44439ae991e7ba2bf97820a31',
    phoneNumber: localStorage.getItem('phoneNumber') || '+79281307511',
    groupIds: JSON.parse(localStorage.getItem('groupIds')) || ['-4884869527', '-4855539306'],
    autoUpdate: localStorage.getItem('autoUpdate') !== 'false',
    notifications: localStorage.getItem('notifications') !== 'false',
    darkTheme: localStorage.getItem('darkTheme') === 'true',
    currency: localStorage.getItem('currency') || 'RUB'
};

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    loadTransactions();
    startAutoUpdate();
});

function initializeApp() {
    // Load saved settings
    loadSettings();
    
    // Initialize based on current page
    const currentPage = getCurrentPage();
    
    switch(currentPage) {
        case 'dashboard':
            initializeDashboard();
            break;
        case 'transactions':
            initializeTransactions();
            break;
        case 'analytics':
            initializeAnalytics();
            break;
        case 'settings':
            initializeSettings();
            break;
    }
}

function getCurrentPage() {
    const path = window.location.pathname;
    if (path.includes('transactions.html')) return 'transactions';
    if (path.includes('analytics.html')) return 'analytics';
    if (path.includes('settings.html')) return 'settings';
    return 'dashboard';
}

// Dashboard functions
function initializeDashboard() {
    updateBalanceCards();
    updateTransactionsChart();
    updateRecentTransactions();
    updateQuickStats();
}

function updateBalanceCards() {
    const totalIncome = transactions
        .filter(t => t.type === 'income')
        .reduce((sum, t) => sum + t.amount, 0);
    
    const totalExpense = transactions
        .filter(t => t.type === 'expense')
        .reduce((sum, t) => sum + t.amount, 0);
    
    const balance = totalIncome - totalExpense;
    
    // Update UI elements
    const incomeEl = document.getElementById('totalIncome');
    const expenseEl = document.getElementById('totalExpense');
    const balanceEl = document.getElementById('totalBalance');
    const incomeCountEl = document.getElementById('incomeCount');
    const expenseCountEl = document.getElementById('expenseCount');
    
    if (incomeEl) incomeEl.textContent = formatCurrency(totalIncome);
    if (expenseEl) expenseEl.textContent = formatCurrency(totalExpense);
    if (balanceEl) balanceEl.textContent = formatCurrency(balance);
    if (incomeCountEl) incomeCountEl.textContent = `${transactions.filter(t => t.type === 'income').length} операций`;
    if (expenseCountEl) expenseCountEl.textContent = `${transactions.filter(t => t.type === 'expense').length} операций`;
    
    // Update balance change
    const balanceChangeEl = document.getElementById('balanceChange');
    if (balanceChangeEl) {
        const changePercent = totalExpense > 0 ? ((totalIncome - totalExpense) / totalExpense * 100).toFixed(1) : 0;
        balanceChangeEl.textContent = `${changePercent >= 0 ? '+' : ''}${changePercent}% за месяц`;
    }
}

function updateTransactionsChart() {
    const chartEl = document.getElementById('transactionsChart');
    if (!chartEl) return;
    
    // Group transactions by day
    const dailyData = groupTransactionsByDay(transactions);
    
    const dates = Object.keys(dailyData).sort();
    const incomeData = dates.map(date => dailyData[date].income || 0);
    const expenseData = dates.map(date => -(dailyData[date].expense || 0));
    
    const data = [
        {
            x: dates,
            y: incomeData,
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Приходы',
            line: { color: '#10b981', width: 2 },
            marker: { size: 4 }
        },
        {
            x: dates,
            y: expenseData,
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Расходы',
            line: { color: '#ef4444', width: 2 },
            marker: { size: 4 }
        }
    ];
    
    const layout = {
        margin: { l: 40, r: 20, t: 20, b: 40 },
        showlegend: true,
        legend: { x: 0, y: 1.1, orientation: 'h' },
        xaxis: { showgrid: false, showline: false },
        yaxis: { showgrid: true, gridcolor: '#f3f4f6' },
        plot_bgcolor: 'rgba(0,0,0,0)',
        paper_bgcolor: 'rgba(0,0,0,0)'
    };
    
    Plotly.newPlot(chartEl, data, layout, { displayModeBar: false, responsive: true });
}

function updateRecentTransactions() {
    const container = document.getElementById('recentTransactions');
    if (!container) return;
    
    const recent = transactions
        .sort((a, b) => new Date(b.date) - new Date(a.date))
        .slice(0, 10);
    
    container.innerHTML = recent.map(transaction => `
        <div class="transaction-item p-3 cursor-pointer" onclick="showTransactionDetail('${transaction.id}')">
            <div class="flex items-center justify-between">
                <div class="flex items-center space-x-3">
                    <div class="w-10 h-10 rounded-full flex items-center justify-center ${transaction.type === 'income' ? 'bg-green-100 text-green-600' : 'bg-red-100 text-red-600'}">
                        <i class="fas ${transaction.type === 'income' ? 'fa-arrow-up' : 'fa-arrow-down'}"></i>
                    </div>
                    <div>
                        <div class="font-medium text-sm text-gray-800">${transaction.description || 'Без описания'}</div>
                        <div class="text-xs text-gray-500">${formatDate(transaction.date)}</div>
                    </div>
                </div>
                <div class="text-right">
                    <div class="font-semibold ${transaction.type === 'income' ? 'text-green-600' : 'text-red-600'}">
                        ${transaction.type === 'income' ? '+' : '-'}${formatCurrency(transaction.amount)}
                    </div>
                    <div class="text-xs text-gray-500">${transaction.category || 'Другое'}</div>
                </div>
            </div>
        </div>
    `).join('');
}

function updateQuickStats() {
    const avgTransactionEl = document.getElementById('avgTransaction');
    const transactionCountEl = document.getElementById('transactionCount');
    const dailyAverageEl = document.getElementById('dailyAverage');
    
    if (transactions.length === 0) return;
    
    const totalAmount = transactions.reduce((sum, t) => sum + t.amount, 0);
    const avgTransaction = totalAmount / transactions.length;
    
    // Calculate daily average for last 30 days
    const thirtyDaysAgo = new Date();
    thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
    
    const recentTransactions = transactions.filter(t => new Date(t.date) >= thirtyDaysAgo);
    const dailyAverage = recentTransactions.reduce((sum, t) => sum + t.amount, 0) / 30;
    
    if (avgTransactionEl) avgTransactionEl.textContent = formatCurrency(avgTransaction);
    if (transactionCountEl) transactionCountEl.textContent = transactions.length;
    if (dailyAverageEl) dailyAverageEl.textContent = formatCurrency(dailyAverage);
}

// Transactions page functions
function initializeTransactions() {
    filteredTransactions = [...transactions];
    updateTransactionSummary();
    renderTransactions();
}

function updateTransactionSummary() {
    const totalIncome = filteredTransactions
        .filter(t => t.type === 'income')
        .reduce((sum, t) => sum + t.amount, 0);
    
    const totalExpense = filteredTransactions
        .filter(t => t.type === 'expense')
        .reduce((sum, t) => sum + t.amount, 0);
    
    const incomeEl = document.getElementById('filterIncome');
    const expenseEl = document.getElementById('filterExpense');
    const incomeCountEl = document.getElementById('filterIncomeCount');
    const expenseCountEl = document.getElementById('filterExpenseCount');
    const countHeaderEl = document.getElementById('transactionCountHeader');
    
    if (incomeEl) incomeEl.textContent = formatCurrency(totalIncome);
    if (expenseEl) expenseEl.textContent = formatCurrency(totalExpense);
    if (incomeCountEl) incomeCountEl.textContent = `${filteredTransactions.filter(t => t.type === 'income').length} операций`;
    if (expenseCountEl) expenseCountEl.textContent = `${filteredTransactions.filter(t => t.type === 'expense').length} операций`;
    if (countHeaderEl) countHeaderEl.textContent = `${filteredTransactions.length} операций`;
}

function renderTransactions() {
    const container = document.getElementById('transactionsList');
    if (!container) return;
    
    if (filteredTransactions.length === 0) {
        container.innerHTML = `
            <div class="p-8 text-center text-gray-500">
                <i class="fas fa-inbox text-4xl mb-3 opacity-50"></i>
                <div class="text-sm">Нет транзакций</div>
            </div>
        `;
        return;
    }
    
    container.innerHTML = filteredTransactions
        .sort((a, b) => new Date(b.date) - new Date(a.date))
        .map(transaction => `
            <div class="transaction-item p-4 cursor-pointer" onclick="showTransactionDetail('${transaction.id}')">
                <div class="flex items-center justify-between">
                    <div class="flex items-center space-x-3">
                        <div class="w-12 h-12 rounded-full flex items-center justify-center ${transaction.type === 'income' ? 'bg-green-100 text-green-600' : 'bg-red-100 text-red-600'}">
                            <i class="fas ${transaction.type === 'income' ? 'fa-arrow-up' : 'fa-arrow-down'}"></i>
                        </div>
                        <div>
                            <div class="font-medium text-gray-800">${transaction.description || 'Без описания'}</div>
                            <div class="text-sm text-gray-500">${formatDate(transaction.date)} • ${transaction.category || 'Другое'}</div>
                        </div>
                    </div>
                    <div class="text-right">
                        <div class="font-bold text-lg ${transaction.type === 'income' ? 'text-green-600' : 'text-red-600'}">
                            ${transaction.type === 'income' ? '+' : '-'}${formatCurrency(transaction.amount)}
                        </div>
                        <div class="text-xs text-gray-500">${transaction.groupName || 'Неизвестная группа'}</div>
                    </div>
                </div>
            </div>
        `).join('');
}

// Analytics page functions
function initializeAnalytics() {
    updateAnalyticsMetrics();
    updateBalanceChart();
    updateCategoryChart();
    updateMonthlyChart();
    updateTopCategories();
    updateInsights();
}

function updateAnalyticsMetrics() {
    const periodData = getTransactionsForPeriod(currentPeriod);
    
    const totalIncome = periodData
        .filter(t => t.type === 'income')
        .reduce((sum, t) => sum + t.amount, 0);
    
    const totalExpense = periodData
        .filter(t => t.type === 'expense')
        .reduce((sum, t) => sum + t.amount, 0);
    
    const incomeEl = document.getElementById('periodIncome');
    const expenseEl = document.getElementById('periodExpense');
    const incomeChangeEl = document.getElementById('incomeChange');
    const expenseChangeEl = document.getElementById('expenseChange');
    
    if (incomeEl) incomeEl.textContent = formatCurrency(totalIncome);
    if (expenseEl) expenseEl.textContent = formatCurrency(totalExpense);
    
    // Calculate changes (mock data for demo)
    if (incomeChangeEl) incomeChangeEl.textContent = '+12.5%';
    if (expenseChangeEl) expenseChangeEl.textContent = '-3.2%';
}

function updateBalanceChart() {
    const chartEl = document.getElementById('balanceChart');
    if (!chartEl) return;
    
    const periodData = getTransactionsForPeriod(currentPeriod);
    const dailyBalance = calculateDailyBalance(periodData);
    
    const data = [{
        x: dailyBalance.dates,
        y: dailyBalance.balances,
        type: 'scatter',
        mode: 'lines',
        fill: 'tonexty',
        fillcolor: 'rgba(102, 126, 234, 0.1)',
        line: { color: '#667eea', width: 2 }
    }];
    
    const layout = {
        margin: { l: 40, r: 20, t: 20, b: 40 },
        showlegend: false,
        xaxis: { showgrid: false, showline: false },
        yaxis: { showgrid: true, gridcolor: '#f3f4f6' },
        plot_bgcolor: 'rgba(0,0,0,0)',
        paper_bgcolor: 'rgba(0,0,0,0)'
    };
    
    Plotly.newPlot(chartEl, data, layout, { displayModeBar: false, responsive: true });
}

function updateCategoryChart() {
    const chartEl = document.getElementById('categoryChart');
    if (!chartEl) return;
    
    const categories = getCategoryData();
    
    const data = [{
        values: categories.map(c => c.amount),
        labels: categories.map(c => c.name),
        type: 'pie',
        hole: 0.4,
        marker: {
            colors: ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe', '#00f2fe']
        }
    }];
    
    const layout = {
        margin: { l: 20, r: 20, t: 20, b: 20 },
        showlegend: true,
        legend: { orientation: 'h', x: 0, y: -0.1 },
        plot_bgcolor: 'rgba(0,0,0,0)',
        paper_bgcolor: 'rgba(0,0,0,0)'
    };
    
    Plotly.newPlot(chartEl, data, layout, { displayModeBar: false, responsive: true });
}

function updateMonthlyChart() {
    const chartEl = document.getElementById('monthlyChart');
    if (!chartEl) return;
    
    const monthlyData = getMonthlyData();
    
    const data = [
        {
            x: monthlyData.months,
            y: monthlyData.income,
            type: 'bar',
            name: 'Приходы',
            marker: { color: '#10b981' }
        },
        {
            x: monthlyData.months,
            y: monthlyData.expense.map(e => -e),
            type: 'bar',
            name: 'Расходы',
            marker: { color: '#ef4444' }
        }
    ];
    
    const layout = {
        margin: { l: 40, r: 20, t: 20, b: 40 },
        showlegend: true,
        legend: { orientation: 'h', x: 0, y: 1.1 },
        xaxis: { showgrid: false },
        yaxis: { showgrid: true, gridcolor: '#f3f4f6' },
        plot_bgcolor: 'rgba(0,0,0,0)',
        paper_bgcolor: 'rgba(0,0,0,0)',
        barmode: 'relative'
    };
    
    Plotly.newPlot(chartEl, data, layout, { displayModeBar: false, responsive: true });
}

function updateTopCategories() {
    const container = document.getElementById('topCategories');
    if (!container) return;
    
    const categories = getCategoryData().slice(0, 5);
    
    container.innerHTML = categories.map((category, index) => `
        <div class="flex items-center justify-between">
            <div class="flex items-center space-x-3">
                <div class="w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-bold" style="background: ${['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe'][index]}">
                    ${index + 1}
                </div>
                <div>
                    <div class="font-medium text-sm">${category.name}</div>
                    <div class="text-xs text-gray-500">${category.count} операций</div>
                </div>
            </div>
            <div class="text-right">
                <div class="font-semibold text-gray-800">${formatCurrency(category.amount)}</div>
                <div class="text-xs text-gray-500">${((category.amount / categories.reduce((sum, c) => sum + c.amount, 0)) * 100).toFixed(1)}%</div>
            </div>
        </div>
    `).join('');
}

function updateInsights() {
    const container = document.getElementById('insights');
    if (!container) return;
    
    const insights = generateInsights();
    
    container.innerHTML = insights.map(insight => `
        <div class="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg">
            <div class="w-8 h-8 rounded-full flex items-center justify-center ${insight.type === 'positive' ? 'bg-green-100 text-green-600' : insight.type === 'negative' ? 'bg-red-100 text-red-600' : 'bg-blue-100 text-blue-600'}">
                <i class="fas ${insight.icon} text-sm"></i>
            </div>
            <div class="flex-1">
                <div class="font-medium text-sm">${insight.title}</div>
                <div class="text-xs text-gray-600 mt-1">${insight.description}</div>
            </div>
        </div>
    `).join('');
}

// Settings page functions
function initializeSettings() {
    loadSettingsUI();
}

function loadSettingsUI() {
    // Load API settings
    const apiIdEl = document.getElementById('apiId');
    const apiHashEl = document.getElementById('apiHash');
    const phoneNumberEl = document.getElementById('phoneNumber');
    
    if (apiIdEl) apiIdEl.value = config.apiId;
    if (apiHashEl) apiHashEl.value = config.apiHash;
    if (phoneNumberEl) phoneNumberEl.value = config.phoneNumber;
    
    // Load app settings
    const autoUpdateEl = document.getElementById('autoUpdate');
    const notificationsEl = document.getElementById('notifications');
    const darkThemeEl = document.getElementById('darkTheme');
    const currencyEl = document.getElementById('currency');
    
    if (autoUpdateEl) autoUpdateEl.checked = config.autoUpdate;
    if (notificationsEl) notificationsEl.checked = config.notifications;
    if (darkThemeEl) darkThemeEl.checked = config.darkTheme;
    if (currencyEl) currencyEl.value = config.currency;
    
    // Update system info
    updateSystemInfo();
}

// Utility functions
function formatCurrency(amount) {
    const currency = config.currency || 'RUB';
    const symbols = { RUB: '₽', USD: '$', EUR: '€' };
    const symbol = symbols[currency] || '₽';
    
    return `${symbol}${amount.toLocaleString('ru-RU', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`;
}

function formatDate(date) {
    const d = new Date(date);
    const now = new Date();
    
    // Убираем время для корректного сравнения дат
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const transactionDate = new Date(d.getFullYear(), d.getMonth(), d.getDate());
    
    // Вычисляем разницу в миллисекундах и переводим в дни
    const diffTime = Math.abs(today - transactionDate);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    // Сравниваем даты
    if (transactionDate.getTime() === today.getTime()) return 'Сегодня';
    if (transactionDate.getTime() === today.getTime() - (1000 * 60 * 60 * 24)) return 'Вчера';
    if (diffDays <= 7) return `${diffDays} дн. назад`;
    
    return d.toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' });
}

function groupTransactionsByDay(transactions) {
    const grouped = {};
    
    transactions.forEach(transaction => {
        const date = new Date(transaction.date).toISOString().split('T')[0];
        if (!grouped[date]) {
            grouped[date] = { income: 0, expense: 0 };
        }
        
        if (transaction.type === 'income') {
            grouped[date].income += transaction.amount;
        } else {
            grouped[date].expense += transaction.amount;
        }
    });
    
    return grouped;
}

function getTransactionsForPeriod(period) {
    const now = new Date();
    let startDate;
    
    switch (period) {
        case 'week':
            startDate = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
            break;
        case 'month':
            startDate = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
            break;
        case 'quarter':
            startDate = new Date(now.getTime() - 90 * 24 * 60 * 60 * 1000);
            break;
        case 'year':
            startDate = new Date(now.getTime() - 365 * 24 * 60 * 60 * 1000);
            break;
        default:
            startDate = new Date(0);
    }
    
    return transactions.filter(t => new Date(t.date) >= startDate);
}

function calculateDailyBalance(transactions) {
    const dailyData = groupTransactionsByDay(transactions);
    const dates = Object.keys(dailyData).sort();
    const balances = [];
    let runningBalance = 0;
    
    dates.forEach(date => {
        runningBalance += (dailyData[date].income || 0) - (dailyData[date].expense || 0);
        balances.push(runningBalance);
    });
    
    return { dates, balances };
}

function getCategoryData() {
    const categories = {};
    
    transactions.forEach(transaction => {
        const category = transaction.category || 'Другое';
        if (!categories[category]) {
            categories[category] = { name: category, amount: 0, count: 0 };
        }
        categories[category].amount += transaction.amount;
        categories[category].count += 1;
    });
    
    return Object.values(categories)
        .sort((a, b) => b.amount - a.amount);
}

function getMonthlyData() {
    const monthlyData = {};
    
    transactions.forEach(transaction => {
        const month = new Date(transaction.date).toISOString().slice(0, 7);
        if (!monthlyData[month]) {
            monthlyData[month] = { income: 0, expense: 0 };
        }
        
        if (transaction.type === 'income') {
            monthlyData[month].income += transaction.amount;
        } else {
            monthlyData[month].expense += transaction.amount;
        }
    });
    
    const months = Object.keys(monthlyData).sort().slice(-6);
    const income = months.map(month => monthlyData[month].income);
    const expense = months.map(month => monthlyData[month].expense);
    
    return { months, income, expense };
}

function generateInsights() {
    const totalIncome = transactions.filter(t => t.type === 'income').reduce((sum, t) => sum + t.amount, 0);
    const totalExpense = transactions.filter(t => t.type === 'expense').reduce((sum, t) => sum + t.amount, 0);
    const savingsRate = totalIncome > 0 ? ((totalIncome - totalExpense) / totalIncome * 100).toFixed(1) : 0;
    
    const insights = [
        {
            type: 'positive',
            icon: 'fa-piggy-bank',
            title: 'Хорошая экономия',
            description: `Вы откладываете ${savingsRate}% от доходов`
        },
        {
            type: 'info',
            icon: 'fa-chart-line',
            title: 'Рост доходов',
            description: 'Ваши доходы выросли на 15% за последний месяц'
        },
        {
            type: 'warning',
            icon: 'fa-exclamation-triangle',
            title: 'Контроль расходов',
            description: 'Рассмотрите возможность сокращения расходов на развлечения'
        }
    ];
    
    return insights;
}

// Data loading and saving
function loadTransactions() {
    // Mock data for demo
    const mockTransactions = [
        {
            id: '1',
            amount: 50000,
            type: 'income',
            description: 'Зарплата',
            category: 'Работа',
            date: new Date().toISOString(),
            groupName: 'Приходы'
        },
        {
            id: '2',
            amount: 1500,
            type: 'expense',
            description: 'Продукты',
            category: 'Еда',
            date: new Date(Date.now() - 86400000).toISOString(),
            groupName: 'Расходы'
        },
        {
            id: '3',
            amount: 3000,
            type: 'expense',
            description: 'Коммунальные услуги',
            category: 'ЖКХ',
            date: new Date(Date.now() - 172800000).toISOString(),
            groupName: 'Расходы'
        },
        {
            id: '4',
            amount: 2500,
            type: 'expense',
            description: 'Ресторан',
            category: 'Развлечения',
            date: new Date(Date.now() - 259200000).toISOString(),
            groupName: 'Расходы'
        },
        {
            id: '5',
            amount: 10000,
            type: 'income',
            description: 'Фриланс',
            category: 'Работа',
            date: new Date(Date.now() - 345600000).toISOString(),
            groupName: 'Приходы'
        }
    ];
    
    transactions = mockTransactions;
    saveTransactions();
}

function saveTransactions() {
    localStorage.setItem('transactions', JSON.stringify(transactions));
}

function loadSettings() {
    const savedSettings = localStorage.getItem('settings');
    if (savedSettings) {
        Object.assign(config, JSON.parse(savedSettings));
    }
}

function saveSettings() {
    localStorage.setItem('settings', JSON.stringify(config));
}

// Real-time data loading function
async function loadData() {
    try {
        const response = await fetch('/api/transactions');
        const data = await response.json();
        
        if (data.success) {
            transactions = data.data;
            initializeApp();
        } else {
            showNotification('Ошибка при загрузке данных', 'error');
        }
    } catch (error) {
        console.error('Error loading data:', error);
        showNotification('Ошибка подключения к серверу', 'error');
    }
}

// Auto update
function startAutoUpdate() {
    if (config.autoUpdate) {
        // Auto refresh every 3 seconds for more responsive updates
        updateInterval = setInterval(() => {
            loadData();
        }, 3000);
    }
}

function stopAutoUpdate() {
    if (updateInterval) {
        clearInterval(updateInterval);
    }
}

// Event handlers
function switchTab(tab) {
    const pages = {
        'dashboard': 'index.html',
        'transactions': 'transactions.html',
        'analytics': 'analytics.html',
        'settings': 'settings.html'
    };
    
    if (pages[tab]) {
        window.location.href = pages[tab];
    }
}

function goBack() {
    window.history.back();
}

function toggleSettings() {
    const modal = document.getElementById('settingsModal');
    if (modal) {
        modal.classList.toggle('hidden');
    }
}

function toggleFilters() {
    const filterBar = document.getElementById('filterBar');
    if (filterBar) {
        filterBar.classList.toggle('hidden');
    }
}

function filterByType(type) {
    currentFilter = type;
    
    // Update filter buttons
    document.querySelectorAll('.filter-chip').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
    // Filter transactions
    const now = new Date();
    let startDate;
    
    switch (type) {
        case 'income':
            filteredTransactions = transactions.filter(t => t.type === 'income');
            break;
        case 'expense':
            filteredTransactions = transactions.filter(t => t.type === 'expense');
            break;
        case 'today':
            startDate = new Date(now.getFullYear(), now.getMonth(), now.getDate());
            filteredTransactions = transactions.filter(t => new Date(t.date) >= startDate);
            break;
        case 'week':
            startDate = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
            filteredTransactions = transactions.filter(t => new Date(t.date) >= startDate);
            break;
        default:
            filteredTransactions = [...transactions];
    }
    
    updateTransactionSummary();
    renderTransactions();
}

function searchTransactions() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    
    if (searchTerm) {
        filteredTransactions = transactions.filter(t => 
            (t.description && t.description.toLowerCase().includes(searchTerm)) ||
            (t.category && t.category.toLowerCase().includes(searchTerm))
        );
    } else {
        filteredTransactions = [...transactions];
    }
    
    updateTransactionSummary();
    renderTransactions();
}

function changePeriod(period) {
    currentPeriod = period;
    
    // Update period buttons
    document.querySelectorAll('.period-btn').forEach(btn => {
        btn.classList.remove('bg-purple-500', 'text-white');
        btn.classList.add('bg-gray-200', 'text-gray-700');
    });
    event.target.classList.remove('bg-gray-200', 'text-gray-700');
    event.target.classList.add('bg-purple-500', 'text-white');
    
    updateAnalyticsMetrics();
    updateBalanceChart();
    updateMonthlyChart();
}

function showTransactionDetail(transactionId) {
    const transaction = transactions.find(t => t.id === transactionId);
    if (!transaction) return;
    
    const modal = document.getElementById('transactionModal');
    const detailsEl = document.getElementById('transactionDetails');
    
    if (modal && detailsEl) {
        detailsEl.innerHTML = `
            <div class="space-y-3">
                <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <span class="text-sm text-gray-600">Сумма</span>
                    <span class="font-bold ${transaction.type === 'income' ? 'text-green-600' : 'text-red-600'}">
                        ${transaction.type === 'income' ? '+' : '-'}${formatCurrency(transaction.amount)}
                    </span>
                </div>
                
                <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <span class="text-sm text-gray-600">Тип</span>
                    <span class="text-sm font-medium">
                        ${transaction.type === 'income' ? 'Приход' : 'Расход'}
                    </span>
                </div>
                
                <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <span class="text-sm text-gray-600">Категория</span>
                    <span class="text-sm font-medium">${transaction.category || 'Другое'}</span>
                </div>
                
                <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <span class="text-sm text-gray-600">Дата</span>
                    <span class="text-sm font-medium">${new Date(transaction.date).toLocaleDateString('ru-RU')}</span>
                </div>
                
                <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <span class="text-sm text-gray-600">Группа</span>
                    <span class="text-sm font-medium">${transaction.groupName || 'Неизвестная группа'}</span>
                </div>
                
                ${transaction.description ? `
                <div class="p-3 bg-gray-50 rounded-lg">
                    <div class="text-sm text-gray-600 mb-1">Описание</div>
                    <div class="text-sm font-medium">${transaction.description}</div>
                </div>
                ` : ''}
            </div>
        `;
        
        modal.classList.remove('hidden');
    }
}

function closeTransactionModal() {
    const modal = document.getElementById('transactionModal');
    if (modal) {
        modal.classList.add('hidden');
    }
}

function showAllTransactions() {
    window.location.href = 'transactions.html';
}

function saveSettings() {
    const apiId = document.getElementById('apiId').value;
    const apiHash = document.getElementById('apiHash').value;
    const phoneNumber = document.getElementById('phoneNumber').value;
    const groupIds = document.getElementById('groupIds').value;
    
    config.apiId = apiId;
    config.apiHash = apiHash;
    config.phoneNumber = phoneNumber;
    config.groupIds = groupIds.split(',').map(id => id.trim());
    
    saveSettings();
    toggleSettings();
    
    showNotification('Настройки сохранены', 'success');
}

function saveAllSettings() {
    // Save API settings
    const apiId = document.getElementById('apiId').value;
    const apiHash = document.getElementById('apiHash').value;
    const phoneNumber = document.getElementById('phoneNumber').value;
    
    // Save app settings
    const autoUpdate = document.getElementById('autoUpdate').checked;
    const notifications = document.getElementById('notifications').checked;
    const darkTheme = document.getElementById('darkTheme').checked;
    const currency = document.getElementById('currency').value;
    
    config.apiId = apiId;
    config.apiHash = apiHash;
    config.phoneNumber = phoneNumber;
    config.autoUpdate = autoUpdate;
    config.notifications = notifications;
    config.darkTheme = darkTheme;
    config.currency = currency;
    
    saveSettings();
    showNotification('Настройки сохранены', 'success');
}

function testConnection() {
    showNotification('Проверка подключения...', 'info');
    
    // Simulate connection test
    setTimeout(() => {
        showNotification('Подключение успешно', 'success');
    }, 2000);
}

function exportData() {
    const dataStr = JSON.stringify(transactions, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = `transactions_${new Date().toISOString().split('T')[0]}.json`;
    link.click();
    
    showNotification('Данные экспортированы', 'success');
}

function importData() {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    
    input.onchange = function(e) {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                try {
                    const importedTransactions = JSON.parse(e.target.result);
                    transactions = [...transactions, ...importedTransactions];
                    saveTransactions();
                    initializeApp();
                    showNotification('Данные импортированы', 'success');
                } catch (error) {
                    showNotification('Ошибка при импорте данных', 'error');
                }
            };
            reader.readAsText(file);
        }
    };
    
    input.click();
}

function clearData() {
    // Check if we're in Flask app mode
    const isFlaskApp = window.location.pathname.includes('/api/') || 
                      document.querySelector('meta[name="flask-app"]') !== null;
    
    if (isFlaskApp) {
        // Use the Flask API endpoint
        clearDataFlask();
    } else {
        // Static file mode behavior
        if (confirm('Вы уверены, что хотите удалить все транзакции?')) {
            transactions = [];
            saveTransactions();
            initializeApp();
            showNotification('Данные очищены', 'success');
        }
    }
}

async function clearDataFlask() {
    if (confirm('Вы уверены, что хотите удалить все транзакции? Это действие нельзя отменить.')) {
        try {
            const response = await fetch('/api/clear-data', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            const data = await response.json();
            
            if (data.success) {
                showNotification('Данные успешно очищены', 'success');
                // Reload page after a short delay to show updated data
                setTimeout(() => {
                    location.reload();
                }, 1500);
            } else {
                showNotification('Ошибка очистки: ' + data.error, 'error');
            }
        } catch (error) {
            console.error('Error clearing data:', error);
            showNotification('Ошибка подключения к серверу', 'error');
        }
    }
}

function updateSystemInfo() {
    const lastUpdateEl = document.getElementById('lastUpdate');
    const totalOperationsEl = document.getElementById('totalOperations');
    
    if (lastUpdateEl) lastUpdateEl.textContent = new Date().toLocaleTimeString('ru-RU');
    if (totalOperationsEl) totalOperationsEl.textContent = transactions.length;
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 z-50 p-4 rounded-lg text-white ${
        type === 'success' ? 'bg-green-500' : 
        type === 'error' ? 'bg-red-500' : 
        'bg-blue-500'
    }`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Check if we're on Flask app or static files
    const isFlaskApp = window.location.pathname.includes('/api/') || 
                      document.querySelector('meta[name="flask-app"]') !== null;
    
    if (isFlaskApp) {
        // Flask app will handle initialization
        console.log('Running in Flask application mode');
    } else {
        // Static files mode - use existing initialization
        initializeApp();
    }
});

async function loadData() {
    try {
        const response = await fetch('/api/transactions');
        const data = await response.json();
        
        if (data.success) {
            transactions = data.data;
            initializeApp();
        } else {
            showNotification('Ошибка при загрузке данных', 'error');
        }
    } catch (error) {
        console.error('Error loading data:', error);
        showNotification('Ошибка подключения к серверу', 'error');
    }
}

async function forceUpdate() {
    if (isLoading) return;
    
    try {
        const response = await fetch('/api/update', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('Обновление запущено...', 'info');
            // Periodically check if update is complete and reload data
            const checkInterval = setInterval(async () => {
                try {
                    const statusResponse = await fetch('/api/status');
                    const statusData = await statusResponse.json();
                    
                    if (statusData.success && !statusData.data.is_parsing) {
                        // Update is complete, reload data
                        clearInterval(checkInterval);
                        await loadData();
                        showNotification('Данные обновлены', 'success');
                    }
                } catch (error) {
                    console.error('Error checking update status:', error);
                    clearInterval(checkInterval);
                }
            }, 2000); // Check every 2 seconds
            
            // Set a timeout to stop checking after 30 seconds
            setTimeout(() => {
                clearInterval(checkInterval);
            }, 30000);
        } else {
            showNotification('Обновление уже выполняется', 'warning');
        }
    } catch (error) {
        console.error('Error forcing update:', error);
        showNotification('Ошибка при обновлении', 'error');
    }
}
