/**
 * 智能垃圾分类系统 - 前端JavaScript
 * 处理用户交互和API调用
 */

// 全局变量
let classifyHistory = JSON.parse(localStorage.getItem('classifyHistory') || '[]');
let allRules = [];
let currentEditingRule = null;

// API基础URL
const API_BASE = '/api';

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    loadHistory();
    loadRules();
    loadStatistics();
    
    // 自动聚焦输入框
    document.getElementById('itemInput').focus();
});

/**
 * 显示指定页面
 */
function showSection(sectionName) {
    // 隐藏所有页面
    const sections = ['classify-section', 'manage-section', 'statistics-section'];
    sections.forEach(section => {
        document.getElementById(section).style.display = 'none';
    });
    
    // 显示指定页面
    document.getElementById(sectionName + '-section').style.display = 'block';
    
    // 更新导航状态
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    event.target.classList.add('active');
    
    // 根据页面执行相应操作
    switch(sectionName) {
        case 'manage':
            loadRules();
            break;
        case 'statistics':
            loadStatistics();
            break;
    }
    
    // 滚动到顶部
    window.scrollTo(0, 0);
}

/**
 * 处理回车键
 */
function handleEnterKey(event) {
    if (event.key === 'Enter') {
        classifyItem();
    }
}

/**
 * 快捷输入
 */
function quickInput(itemName) {
    document.getElementById('itemInput').value = itemName;
    classifyItem();
}

/**
 * 分类单个物品
 */
async function classifyItem() {
    const itemInput = document.getElementById('itemInput');
    const itemName = itemInput.value.trim();
    
    if (!itemName) {
        showAlert('请输入物品名称', 'warning');
        return;
    }
    
    // 显示加载状态
    showLoading(true);
    
    try {
        const response = await fetch(`${API_BASE}/classify`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ item_name: itemName })
        });
        
        const result = await response.json();
        
        if (response.ok) {
            displayResult(result);
            addToHistory(result);
            
            // 清空输入框
            itemInput.value = '';
            itemInput.focus();
        } else {
            showAlert(result.error || '分类失败', 'danger');
        }
    } catch (error) {
        console.error('分类错误:', error);
        showAlert('网络错误，请检查连接', 'danger');
    } finally {
        showLoading(false);
    }
}

/**
 * 显示分类结果
 */
function displayResult(result) {
    const resultArea = document.getElementById('resultArea');
    
    if (result.success) {
        resultArea.innerHTML = `
            <div class="col-12">
                <div class="result-card">
                    <div class="row align-items-center">
                        <div class="col-md-2 text-center">
                            <div style="font-size: 4rem;">${result.icon}</div>
                        </div>
                        <div class="col-md-10">
                            <h3 class="mb-3">
                                <strong>${result.item_name}</strong>
                                <span class="badge garbage-type-badge ${getTypeClass(result.garbage_type)} ms-2">
                                    ${result.garbage_type}
                                </span>
                            </h3>
                            
                            <div class="row">
                                <div class="col-md-6">
                                    <h6><i class="fas fa-info-circle me-2"></i>分类依据</h6>
                                    <p class="text-muted">${result.reason}</p>
                                </div>
                                <div class="col-md-6">
                                    <h6><i class="fas fa-lightbulb me-2"></i>处理建议</h6>
                                    <p class="text-muted">${result.suggestion}</p>
                                </div>
                            </div>
                            
                            <div class="text-end">
                                <small class="text-muted">
                                    <i class="fas fa-clock me-1"></i>${result.timestamp}
                                </small>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    } else {
        resultArea.innerHTML = `
            <div class="col-12">
                <div class="result-card border-warning">
                    <div class="row align-items-center">
                        <div class="col-md-2 text-center">
                            <div style="font-size: 4rem;">❓</div>
                        </div>
                        <div class="col-md-10">
                            <h3 class="mb-3">
                                <strong>${result.item_name}</strong>
                                <span class="badge bg-secondary ms-2">未知</span>
                            </h3>
                            
                            <div class="row">
                                <div class="col-md-6">
                                    <h6><i class="fas fa-exclamation-triangle me-2"></i>说明</h6>
                                    <p class="text-muted">${result.reason}</p>
                                </div>
                                <div class="col-md-6">
                                    <h6><i class="fas fa-lightbulb me-2"></i>建议</h6>
                                    <p class="text-muted">${result.suggestion}</p>
                                    <button class="btn btn-sm btn-outline-primary" onclick="showAddRuleModal('${result.item_name}')">
                                        <i class="fas fa-plus me-1"></i>添加规则
                                    </button>
                                </div>
                            </div>
                            
                            <div class="text-end">
                                <small class="text-muted">
                                    <i class="fas fa-clock me-1"></i>${result.timestamp}
                                </small>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
}

/**
 * 获取垃圾类型对应的CSS类
 */
function getTypeClass(garbageType) {
    const typeClasses = {
        '可回收垃圾': 'recyclable',
        '有害垃圾': 'hazardous',
        '厨余垃圾': 'kitchen',
        '其他垃圾': 'other'
    };
    return typeClasses[garbageType] || 'other';
}

/**
 * 添加到历史记录
 */
function addToHistory(result) {
    const historyItem = {
        item_name: result.item_name,
        garbage_type: result.garbage_type,
        success: result.success,
        timestamp: result.timestamp,
        icon: result.icon
    };
    
    classifyHistory.unshift(historyItem);
    
    // 限制历史记录数量
    if (classifyHistory.length > 50) {
        classifyHistory = classifyHistory.slice(0, 50);
    }
    
    // 保存到本地存储
    localStorage.setItem('classifyHistory', JSON.stringify(classifyHistory));
    
    // 更新显示
    loadHistory();
}

/**
 * 加载历史记录
 */
function loadHistory() {
    const historyContainer = document.getElementById('historyContainer');
    
    if (classifyHistory.length === 0) {
        historyContainer.innerHTML = '<p class="text-muted text-center">暂无分类记录</p>';
        return;
    }
    
    const historyHTML = classifyHistory.slice(0, 10).map(item => {
        const statusIcon = item.success ? '✅' : '❌';
        const typeClass = getTypeClass(item.garbage_type);
        
        return `
            <div class="history-item">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <span class="me-3">${statusIcon}</span>
                        <strong>${item.item_name}</strong>
                        <span class="badge ${typeClass} ms-2">${item.garbage_type}</span>
                    </div>
                    <small class="text-muted">${item.timestamp}</small>
                </div>
            </div>
        `;
    }).join('');
    
    historyContainer.innerHTML = historyHTML;
}

/**
 * 清空历史记录
 */
function clearHistory() {
    if (confirm('确定要清空所有历史记录吗？')) {
        classifyHistory = [];
        localStorage.removeItem('classifyHistory');
        loadHistory();
        showAlert('历史记录已清空', 'success');
    }
}

/**
 * 显示批量分类模态框
 */
function showBatchModal() {
    const modal = new bootstrap.Modal(document.getElementById('batchModal'));
    document.getElementById('batchInput').value = '';
    document.getElementById('batchResults').style.display = 'none';
    modal.show();
}

/**
 * 批量分类
 */
async function batchClassify() {
    const batchInput = document.getElementById('batchInput');
    const items = batchInput.value.trim().split('\n').filter(item => item.trim());
    
    if (items.length === 0) {
        showAlert('请输入要分类的物品', 'warning');
        return;
    }
    
    showLoading(true);
    
    try {
        const response = await fetch(`${API_BASE}/batch-classify`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ items: items })
        });
        
        const result = await response.json();
        
        if (response.ok) {
            displayBatchResults(result);
            
            // 添加到历史记录
            result.results.forEach(item => {
                addToHistory({
                    item_name: item.item_name,
                    garbage_type: item.garbage_type,
                    success: item.success,
                    timestamp: result.timestamp,
                    icon: item.icon
                });
            });
        } else {
            showAlert(result.error || '批量分类失败', 'danger');
        }
    } catch (error) {
        console.error('批量分类错误:', error);
        showAlert('网络错误，请检查连接', 'danger');
    } finally {
        showLoading(false);
    }
}

/**
 * 显示批量分类结果
 */
function displayBatchResults(result) {
    const resultsContainer = document.getElementById('batchResultsContainer');
    const resultsDiv = document.getElementById('batchResults');
    
    const resultsHTML = result.results.map(item => {
        const statusIcon = item.success ? '✅' : '❌';
        const typeClass = getTypeClass(item.garbage_type);
        
        return `
            <div class="border rounded p-2 mb-2">
                <div class="row align-items-center">
                    <div class="col-md-6">
                        <span class="me-2">${statusIcon}</span>
                        <strong>${item.item_name}</strong>
                    </div>
                    <div class="col-md-6">
                        <span class="badge ${typeClass}">${item.garbage_type}</span>
                    </div>
                </div>
                <small class="text-muted">${item.reason}</small>
            </div>
        `;
    }).join('');
    
    resultsContainer.innerHTML = `
        <div class="alert alert-info">
            <i class="fas fa-info-circle me-2"></i>
            共处理 ${result.total} 个物品，成功分类 ${result.successful} 个
        </div>
        ${resultsHTML}
    `;
    
    resultsDiv.style.display = 'block';
}

/**
 * 加载所有规则
 */
async function loadRules() {
    const rulesContainer = document.getElementById('rulesContainer');
    
    try {
        const response = await fetch(`${API_BASE}/rules`);
        const result = await response.json();
        
        if (response.ok) {
            allRules = result.rules;
            displayRules(allRules);
        } else {
            rulesContainer.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    加载规则失败: ${result.error}
                </div>
            `;
        }
    } catch (error) {
        console.error('加载规则错误:', error);
        rulesContainer.innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-triangle me-2"></i>
                网络错误，无法加载规则
            </div>
        `;
    }
}

/**
 * 显示规则列表
 */
function displayRules(rules) {
    const rulesContainer = document.getElementById('rulesContainer');
    
    if (rules.length === 0) {
        rulesContainer.innerHTML = `
            <div class="text-center py-4">
                <i class="fas fa-inbox" style="font-size: 3rem; color: #ccc;"></i>
                <h5 class="mt-3 text-muted">暂无规则</h5>
                <button class="btn btn-primary" onclick="showAddRuleModal()">
                    <i class="fas fa-plus me-1"></i>添加第一条规则
                </button>
            </div>
        `;
        return;
    }
    
    const rulesHTML = rules.map(rule => {
        const typeClass = getTypeClass(rule.garbage_type);
        
        return `
            <div class="card mb-3">
                <div class="card-body">
                    <div class="row align-items-center">
                        <div class="col-md-1 text-center">
                            <span style="font-size: 2rem;">${rule.icon}</span>
                        </div>
                        <div class="col-md-8">
                            <h6 class="mb-1">
                                <strong>${rule.item_name}</strong>
                                <span class="badge ${typeClass} ms-2">${rule.garbage_type}</span>
                            </h6>
                            <p class="text-muted mb-0">${rule.reason}</p>
                        </div>
                        <div class="col-md-3 text-end">
                            <button class="btn btn-sm btn-outline-primary me-1" 
                                    onclick="editRule('${rule.item_name}')">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button class="btn btn-sm btn-outline-danger" 
                                    onclick="deleteRule('${rule.item_name}')">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }).join('');
    
    rulesContainer.innerHTML = rulesHTML;
}

/**
 * 筛选规则
 */
function filterRules() {
    const searchText = document.getElementById('searchInput').value.toLowerCase();
    const typeFilter = document.getElementById('typeFilter').value;
    
    let filteredRules = allRules.filter(rule => {
        const matchesSearch = rule.item_name.toLowerCase().includes(searchText) ||
                           rule.reason.toLowerCase().includes(searchText);
        const matchesType = !typeFilter || rule.garbage_type === typeFilter;
        
        return matchesSearch && matchesType;
    });
    
    displayRules(filteredRules);
}

/**
 * 显示添加规则模态框
 */
function showAddRuleModal(itemName = '') {
    currentEditingRule = null;
    
    document.getElementById('ruleModalTitle').innerHTML = '<i class="fas fa-plus me-2"></i>添加规则';
    document.getElementById('ruleItemName').value = itemName;
    document.getElementById('ruleGarbageType').value = '';
    document.getElementById('ruleReason').value = '';
    
    const modal = new bootstrap.Modal(document.getElementById('ruleModal'));
    modal.show();
}

/**
 * 编辑规则
 */
function editRule(itemName) {
    const rule = allRules.find(r => r.item_name === itemName);
    if (!rule) return;
    
    currentEditingRule = itemName;
    
    document.getElementById('ruleModalTitle').innerHTML = '<i class="fas fa-edit me-2"></i>编辑规则';
    document.getElementById('ruleItemName').value = rule.item_name;
    document.getElementById('ruleGarbageType').value = rule.garbage_type;
    document.getElementById('ruleReason').value = rule.reason;
    
    const modal = new bootstrap.Modal(document.getElementById('ruleModal'));
    modal.show();
}

/**
 * 保存规则
 */
async function saveRule() {
    const itemName = document.getElementById('ruleItemName').value.trim();
    const garbageType = document.getElementById('ruleGarbageType').value;
    const reason = document.getElementById('ruleReason').value.trim();
    
    if (!itemName || !garbageType || !reason) {
        showAlert('请填写所有字段', 'warning');
        return;
    }
    
    const ruleData = {
        item_name: itemName,
        garbage_type: garbageType,
        reason: reason
    };
    
    const isEdit = currentEditingRule !== null;
    const method = isEdit ? 'PUT' : 'POST';
    
    try {
        const response = await fetch(`${API_BASE}/rules`, {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(ruleData)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showAlert(isEdit ? '规则更新成功' : '规则添加成功', 'success');
            
            // 关闭模态框
            bootstrap.Modal.getInstance(document.getElementById('ruleModal')).hide();
            
            // 重新加载规则
            loadRules();
        } else {
            showAlert(result.error || '保存失败', 'danger');
        }
    } catch (error) {
        console.error('保存规则错误:', error);
        showAlert('网络错误，保存失败', 'danger');
    }
}

/**
 * 删除规则
 */
async function deleteRule(itemName) {
    if (!confirm(`确定要删除规则 "${itemName}" 吗？`)) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/rules?item_name=${encodeURIComponent(itemName)}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showAlert('规则删除成功', 'success');
            loadRules();
        } else {
            showAlert(result.error || '删除失败', 'danger');
        }
    } catch (error) {
        console.error('删除规则错误:', error);
        showAlert('网络错误，删除失败', 'danger');
    }
}

/**
 * 加载统计信息
 */
async function loadStatistics() {
    try {
        const response = await fetch(`${API_BASE}/statistics`);
        const result = await response.json();
        
        if (response.ok) {
            displayStatistics(result.statistics);
            createCharts(result.statistics);
        } else {
            console.error('加载统计信息失败:', result.error);
        }
    } catch (error) {
        console.error('加载统计信息错误:', error);
    }
}

/**
 * 显示统计信息
 */
function displayStatistics(statistics) {
    const statsCards = document.getElementById('statsCards');
    
    const cardsHTML = statistics.map(stat => {
        const typeClass = getTypeClass(stat.garbage_type);
        
        return `
            <div class="col-md-3 col-sm-6 mb-3">
                <div class="stats-card ${typeClass}">
                    <div style="font-size: 2rem;">${stat.icon}</div>
                    <h4>${stat.count}</h4>
                    <h6>${stat.garbage_type}</h6>
                    <small>${stat.percentage}%</small>
                </div>
            </div>
        `;
    }).join('');
    
    statsCards.innerHTML = cardsHTML;
}

/**
 * 创建图表
 */
function createCharts(statistics) {
    // 饼图
    const pieCtx = document.getElementById('pieChart').getContext('2d');
    new Chart(pieCtx, {
        type: 'pie',
        data: {
            labels: statistics.map(s => s.garbage_type),
            datasets: [{
                data: statistics.map(s => s.count),
                backgroundColor: statistics.map(s => s.color),
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
    
    // 柱状图
    const barCtx = document.getElementById('barChart').getContext('2d');
    new Chart(barCtx, {
        type: 'bar',
        data: {
            labels: statistics.map(s => s.garbage_type),
            datasets: [{
                label: '规则数量',
                data: statistics.map(s => s.count),
                backgroundColor: statistics.map(s => s.color),
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}

/**
 * 显示提示信息
 */
function showAlert(message, type = 'info') {
    // 创建提示元素
    const alertHTML = `
        <div class="alert alert-${type} alert-dismissible fade show position-fixed" 
             style="top: 20px; right: 20px; z-index: 9999; min-width: 300px;">
            <i class="fas fa-${getAlertIcon(type)} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    // 添加到页面
    document.body.insertAdjacentHTML('beforeend', alertHTML);
    
    // 自动消失
    setTimeout(() => {
        const alerts = document.querySelectorAll('.alert');
        if (alerts.length > 0) {
            alerts[alerts.length - 1].remove();
        }
    }, 5000);
}

/**
 * 获取提示图标
 */
function getAlertIcon(type) {
    const icons = {
        'success': 'check-circle',
        'danger': 'exclamation-circle',
        'warning': 'exclamation-triangle',
        'info': 'info-circle'
    };
    return icons[type] || 'info-circle';
}

/**
 * 显示/隐藏加载状态
 */
function showLoading(show) {
    const elements = [
        document.getElementById('itemInput'),
        document.querySelector('button[onclick="classifyItem()"]')
    ];
    
    elements.forEach(el => {
        if (el) {
            if (show) {
                el.classList.add('loading');
                el.disabled = true;
            } else {
                el.classList.remove('loading');
                el.disabled = false;
            }
        }
    });
}

/**
 * 滚动到顶部
 */
function scrollToTop() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
}

// ==================== 图片识别功能 ====================

let selectedImageFile = null;

/**
 * 页面加载时检查图片识别功能状态
 */
document.addEventListener('DOMContentLoaded', function() {
    // 其他初始化...
    checkImageFeatureStatus();
});

/**
 * 检查图片识别功能状态
 */
async function checkImageFeatureStatus() {
    try {
        const response = await fetch(`${API_BASE}/image-status`);
        const result = await response.json();
        
        const statusAlert = document.getElementById('imageStatusAlert');
        const statusMessage = document.getElementById('imageStatusMessage');
        
        if (result.available) {
            statusAlert.className = 'alert alert-success mt-3';
            statusMessage.textContent = '✅ 图片识别功能已启用，模型' + (result.model_loaded ? '已加载' : '待加载');
            statusAlert.style.display = 'block';
        } else {
            statusAlert.className = 'alert alert-warning mt-3';
            statusMessage.innerHTML = `⚠️ 图片识别功能不可用。需要安装: ${result.required_packages.join(', ')}`;
            statusAlert.style.display = 'block';
        }
    } catch (error) {
        console.error('检查图片功能状态失败:', error);
    }
}

/**
 * 处理图片选择
 */
function handleImageSelect(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    // 验证文件类型
    const allowedTypes = ['image/jpeg', 'image/png', 'image/jpg', 'image/gif', 'image/bmp'];
    if (!allowedTypes.includes(file.type)) {
        showAlert('不支持的文件类型，请上传 JPG、PNG、GIF 或 BMP 格式的图片', 'warning');
        return;
    }
    
    // 验证文件大小 (16MB)
    if (file.size > 16 * 1024 * 1024) {
        showAlert('图片文件过大，请上传小于 16MB 的图片', 'warning');
        return;
    }
    
    selectedImageFile = file;
    
    // 显示预览
    const reader = new FileReader();
    reader.onload = function(e) {
        document.getElementById('previewImg').src = e.target.result;
        document.getElementById('imageFileName').textContent = file.name;
        document.getElementById('uploadPlaceholder').style.display = 'none';
        document.getElementById('imagePreview').style.display = 'block';
        document.getElementById('classifyImageBtn').disabled = false;
    };
    reader.readAsDataURL(file);
}

/**
 * 处理拖拽悬停
 */
function handleDragOver(event) {
    event.preventDefault();
    event.stopPropagation();
    event.currentTarget.style.borderColor = '#007bff';
    event.currentTarget.style.backgroundColor = '#f0f8ff';
}

/**
 * 处理拖拽离开
 */
function handleDragLeave(event) {
    event.preventDefault();
    event.stopPropagation();
    event.currentTarget.style.borderColor = '#ccc';
    event.currentTarget.style.backgroundColor = 'transparent';
}

/**
 * 处理拖拽放置
 */
function handleDrop(event) {
    event.preventDefault();
    event.stopPropagation();
    event.currentTarget.style.borderColor = '#ccc';
    event.currentTarget.style.backgroundColor = 'transparent';
    
    const files = event.dataTransfer.files;
    if (files.length > 0) {
        // 模拟文件选择事件
        const fileInput = document.getElementById('imageInput');
        fileInput.files = files;
        handleImageSelect({ target: fileInput });
    }
}

/**
 * 清除选择的图片
 */
function clearImage() {
    selectedImageFile = null;
    document.getElementById('imageInput').value = '';
    document.getElementById('uploadPlaceholder').style.display = 'block';
    document.getElementById('imagePreview').style.display = 'none';
    document.getElementById('classifyImageBtn').disabled = true;
}

/**
 * 对图片进行分类识别
 */
async function classifyImage() {
    if (!selectedImageFile) {
        showAlert('请先选择图片', 'warning');
        return;
    }
    
    const confidenceThreshold = document.getElementById('confidenceThreshold').value / 100;
    const classifyBtn = document.getElementById('classifyImageBtn');
    
    // 显示加载状态
    classifyBtn.disabled = true;
    classifyBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>识别中...';
    
    try {
        // 构建 FormData
        const formData = new FormData();
        formData.append('image', selectedImageFile);
        formData.append('confidence_threshold', confidenceThreshold);
        
        const response = await fetch(`${API_BASE}/classify-image`, {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (response.ok) {
            displayImageResult(result);
            
            // 添加到历史记录
            if (result.success) {
                addToHistory({
                    item_name: result.object_name,
                    garbage_type: result.garbage_type,
                    success: result.success,
                    timestamp: result.timestamp,
                    icon: result.icon
                });
            }
            
            showAlert('图片识别完成', 'success');
        } else if (response.status === 503) {
            showAlert(result.error || '图片识别功能不可用', 'warning');
            const statusMessage = document.getElementById('imageStatusMessage');
            statusMessage.innerHTML = `⚠️ ${result.message || '图片识别功能不可用'}`;
        } else {
            showAlert(result.error || '图片识别失败', 'danger');
        }
    } catch (error) {
        console.error('图片识别错误:', error);
        showAlert('网络错误，请检查连接', 'danger');
    } finally {
        classifyBtn.disabled = false;
        classifyBtn.innerHTML = '<i class="fas fa-robot me-1"></i>开始识别';
    }
}

/**
 * 显示图片识别结果
 */
function displayImageResult(result) {
    const resultArea = document.getElementById('resultArea');
    
    // 构建预测结果表格
    let predictionsHTML = '';
    if (result.predictions && result.predictions.length > 0) {
        predictionsHTML = `
            <div class="mt-3">
                <h6><i class="fas fa-list me-2"></i>详细识别结果 (Top ${result.predictions.length})</h6>
                <div class="table-responsive">
                    <table class="table table-sm table-hover">
                        <thead>
                            <tr>
                                <th>识别物品</th>
                                <th>置信度</th>
                                <th>分类</th>
                                <th>可分类</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${result.predictions.map((pred, idx) => `
                                <tr class="${idx === 0 ? 'table-primary' : ''}">
                                    <td><strong>${pred.object_name}</strong></td>
                                    <td>
                                        <div class="progress" style="height: 20px;">
                                            <div class="progress-bar ${pred.confidence > 50 ? 'bg-success' : 'bg-warning'}" 
                                                 style="width: ${pred.confidence}%">
                                                ${pred.confidence}%
                                            </div>
                                        </div>
                                    </td>
                                    <td>
                                        <span class="badge ${getTypeClass(pred.garbage_type)}">
                                            ${pred.garbage_type}
                                        </span>
                                    </td>
                                    <td>${pred.can_classify ? '✅' : '❌'}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        `;
    }
    
    if (result.success) {
        resultArea.innerHTML = `
            <div class="col-12">
                <div class="result-card">
                    <div class="alert alert-info mb-3">
                        <i class="fas fa-camera me-2"></i>
                        <strong>图片识别模式</strong> - 使用深度学习模型识别垃圾类型
                    </div>
                    <div class="row align-items-center">
                        <div class="col-md-2 text-center">
                            <div style="font-size: 4rem;">${result.icon}</div>
                        </div>
                        <div class="col-md-10">
                            <h3 class="mb-3">
                                <strong>${result.object_name}</strong>
                                <span class="badge garbage-type-badge ${getTypeClass(result.garbage_type)} ms-2">
                                    ${result.garbage_type}
                                </span>
                            </h3>
                            
                            <div class="row">
                                <div class="col-md-6">
                                    <h6><i class="fas fa-robot me-2"></i>识别结果</h6>
                                    <p class="text-muted">${result.reason}</p>
                                </div>
                                <div class="col-md-6">
                                    <h6><i class="fas fa-lightbulb me-2"></i>处理建议</h6>
                                    <p class="text-muted">${result.suggestion}</p>
                                </div>
                            </div>
                            
                            ${predictionsHTML}
                            
                            <div class="text-end">
                                <small class="text-muted">
                                    <i class="fas fa-clock me-1"></i>${result.timestamp}
                                    <span class="ms-2">置信度阈值: ${(result.confidence_threshold * 100).toFixed(0)}%</span>
                                </small>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    } else {
        resultArea.innerHTML = `
            <div class="col-12">
                <div class="result-card border-warning">
                    <div class="alert alert-warning mb-3">
                        <i class="fas fa-camera me-2"></i>
                        <strong>图片识别模式</strong> - 识别结果不确定
                    </div>
                    <div class="row align-items-center">
                        <div class="col-md-2 text-center">
                            <div style="font-size: 4rem;">❓</div>
                        </div>
                        <div class="col-md-10">
                            <h3 class="mb-3">
                                <strong>${result.object_name || '未知物品'}</strong>
                                <span class="badge bg-secondary ms-2">无法分类</span>
                            </h3>
                            
                            <div class="row">
                                <div class="col-md-6">
                                    <h6><i class="fas fa-exclamation-triangle me-2"></i>说明</h6>
                                    <p class="text-muted">${result.reason}</p>
                                </div>
                                <div class="col-md-6">
                                    <h6><i class="fas fa-lightbulb me-2"></i>建议</h6>
                                    <p class="text-muted">
                                        可以尝试：<br>
                                        1. 调低置信度阈值<br>
                                        2. 使用更清晰的图片<br>
                                        3. 切换到文本分类模式
                                    </p>
                                </div>
                            </div>
                            
                            ${predictionsHTML}
                            
                            <div class="text-end">
                                <small class="text-muted">
                                    <i class="fas fa-clock me-1"></i>${result.timestamp}
                                </small>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    // 滚动到结果区域
    resultArea.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}