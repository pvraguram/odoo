
// Workspace Management System
class WorkspaceManager {
    constructor() {
        this.projects = this.loadProjects();
        this.currentFilter = 'all';
        this.currentSearch = '';
        this.currentSort = 'updated';
        this.currentProjectId = null;
        this.init();
    }

    init() {
        this.bindEvents();
        this.renderProjects();
        this.updateEmptyState();
    }

    bindEvents() {
        // Create project button
        document.getElementById('createProjectBtn').addEventListener('click', () => this.showCreateModal());
        document.getElementById('emptyStateCreateBtn').addEventListener('click', () => this.showCreateModal());

        // Create project modal
        document.getElementById('closeCreateModal').addEventListener('click', () => this.hideCreateModal());
        document.getElementById('cancelCreateProject').addEventListener('click', () => this.hideCreateModal());
        document.getElementById('createProjectForm').addEventListener('submit', (e) => this.handleCreateProject(e));

        // Project details modal
        document.getElementById('closeDetailsModal').addEventListener('click', () => this.hideDetailsModal());
        document.getElementById('closeDetailsBtn').addEventListener('click', () => this.hideDetailsModal());
        document.getElementById('deleteProjectBtn').addEventListener('click', () => this.deleteCurrentProject());

        // Category filters
        document.querySelectorAll('.category-filter').forEach(btn => {
            btn.addEventListener('click', (e) => this.filterProjects(e.target.dataset.category));
        });

        // Search functionality
        document.getElementById('projectSearch').addEventListener('input', (e) => this.searchProjects(e.target.value));

        // Sort functionality
        document.getElementById('projectSort').addEventListener('change', (e) => this.sortProjects(e.target.value));
    }

    loadProjects() {
        const saved = localStorage.getItem('logiclab_projects');
        return saved ? JSON.parse(saved) : [];
    }

    saveProjects() {
        localStorage.setItem('logiclab_projects', JSON.stringify(this.projects));
    }

    generateId() {
        return Date.now().toString(36) + Math.random().toString(36).substr(2);
    }

    showCreateModal() {
        document.getElementById('createProjectModal').classList.remove('hide');
        document.getElementById('createProjectModal').classList.add('show');
        document.getElementById('projectName').focus();
    }

    hideCreateModal() {
        document.getElementById('createProjectModal').classList.remove('show');
        document.getElementById('createProjectModal').classList.add('hide');
        document.getElementById('createProjectForm').reset();
    }

    showDetailsModal(projectId) {
        this.currentProjectId = projectId;
        const project = this.projects.find(p => p.id === projectId);
        if (!project) return;

        document.getElementById('projectDetailsTitle').textContent = project.name;
        document.getElementById('projectDetailsContent').innerHTML = this.renderProjectDetails(project);
        document.getElementById('projectDetailsModal').classList.remove('hide');
        document.getElementById('projectDetailsModal').classList.add('show');
    }

    hideDetailsModal() {
        document.getElementById('projectDetailsModal').classList.remove('show');
        document.getElementById('projectDetailsModal').classList.add('hide');
        this.currentProjectId = null;
    }

    handleCreateProject(e) {
        e.preventDefault();
        const name = document.getElementById('projectName').value.trim();
        const description = document.getElementById('projectDescription').value.trim();
        const category = document.getElementById('projectCategory').value;

        if (!name) {
            alert('Please enter a project name');
            return;
        }

        const project = {
            id: this.generateId(),
            name: name,
            description: description,
            category: category,
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
            data: null
        };

        this.projects.unshift(project);
        this.saveProjects();
        this.renderProjects();
        this.updateEmptyState();
        this.hideCreateModal();

        // Show success message
        this.showNotification('Project created successfully!', 'success');
    }

    deleteCurrentProject() {
        if (!this.currentProjectId) return;

        if (confirm('Are you sure you want to delete this project? This action cannot be undone.')) {
            this.projects = this.projects.filter(p => p.id !== this.currentProjectId);
            this.saveProjects();
            this.renderProjects();
            this.updateEmptyState();
            this.hideDetailsModal();
            this.showNotification('Project deleted successfully!', 'success');
        }
    }

    filterProjects(category) {
        this.currentFilter = category;

        // Update filter buttons
        document.querySelectorAll('.category-filter').forEach(btn => {
            btn.classList.remove('bg-blue-100', 'text-blue-700', 'border-blue-200');
            btn.classList.add('text-gray-600', 'border-gray-200', 'hover:bg-gray-50');
        });

        const activeBtn = document.querySelector(`[data-category="${category}"]`);
        if (activeBtn) {
            activeBtn.classList.remove('text-gray-600', 'border-gray-200', 'hover:bg-gray-50');
            activeBtn.classList.add('bg-blue-100', 'text-blue-700', 'border-blue-200');
        }

        this.renderProjects();
    }

    searchProjects(query) {
        this.currentSearch = query.toLowerCase();
        this.renderProjects();
    }

    sortProjects(sortBy) {
        this.currentSort = sortBy;
        this.renderProjects();
    }

    renderProjects() {
        const grid = document.getElementById('projectsGrid');

        // Apply filters, search, and sort
        let filteredProjects = this.projects;

        // Apply category filter
        if (this.currentFilter !== 'all') {
            filteredProjects = filteredProjects.filter(p => p.category === this.currentFilter);
        }

        // Apply search filter
        if (this.currentSearch) {
            filteredProjects = filteredProjects.filter(p =>
                p.name.toLowerCase().includes(this.currentSearch) ||
                p.description.toLowerCase().includes(this.currentSearch) ||
                p.category.toLowerCase().includes(this.currentSearch)
            );
        }

        // Apply sorting
        filteredProjects.sort((a, b) => {
            switch (this.currentSort) {
                case 'updated':
                    return new Date(b.updatedAt) - new Date(a.updatedAt);
                case 'created':
                    return new Date(b.createdAt) - new Date(a.createdAt);
                case 'name':
                    return a.name.localeCompare(b.name);
                case 'category':
                    return a.category.localeCompare(b.category);
                default:
                    return 0;
            }
        });

        if (filteredProjects.length === 0) {
            grid.innerHTML = `
                        <div class="col-span-full text-center py-8">
                            <span class="material-icons text-4xl text-gray-300 mb-2">search</span>
                            <p class="text-gray-600">${this.currentSearch ? 'No projects found matching your search' : 'No projects found in this category'}</p>
                        </div>
                    `;
            return;
        }

        grid.innerHTML = filteredProjects.map(project => this.renderProjectCard(project)).join('');

        // Update statistics
        this.updateStatistics();
    }

    updateStatistics() {
        const totalProjects = this.projects.length;
        const projectsWithData = this.projects.filter(p => p.data).length;
        const oneWeekAgo = new Date();
        oneWeekAgo.setDate(oneWeekAgo.getDate() - 7);
        const recentProjects = this.projects.filter(p => new Date(p.createdAt) > oneWeekAgo).length;

        // Calculate storage used (rough estimate)
        const storageUsed = JSON.stringify(this.projects).length;
        const storageKB = Math.round(storageUsed / 1024);

        document.getElementById('totalProjects').textContent = totalProjects;
        document.getElementById('projectsWithData').textContent = projectsWithData;
        document.getElementById('recentProjects').textContent = recentProjects;
        document.getElementById('storageUsed').textContent = `${storageKB} KB`;
    }

    renderProjectCard(project) {
        const categoryIcons = {
            'truth-table': 'table_chart',
            'kmap': 'grid_on',
            'circuit': 'device_hub',
            'simplification': 'functions',
            'whiteboard': 'edit'
        };

        const categoryColors = {
            'truth-table': 'bg-purple-100 text-purple-700 border-purple-200',
            'kmap': 'bg-green-100 text-green-700 border-green-200',
            'circuit': 'bg-blue-100 text-blue-700 border-blue-200',
            'simplification': 'bg-orange-100 text-orange-700 border-orange-200',
            'whiteboard': 'bg-gray-100 text-gray-700 border-gray-200'
        };

        const icon = categoryIcons[project.category] || 'folder';
        const colorClass = categoryColors[project.category] || 'bg-gray-100 text-gray-700 border-gray-200';
        const date = new Date(project.updatedAt).toLocaleDateString();

        return `
                    <div class="card bg-white rounded-xl p-4 hover:shadow-lg transition-all duration-200 cursor-pointer" onclick="workspaceManager.showDetailsModal('${project.id}')">
                        <div class="flex items-start justify-between mb-3">
                            <div class="flex items-center space-x-2">
                                <span class="material-icons text-2xl text-gray-600">${icon}</span>
                                <div>
                                    <h4 class="font-semibold text-gray-900">${project.name}</h4>
                                    <span class="inline-block px-2 py-1 rounded-full text-xs font-medium border ${colorClass}">${project.category.replace('-', ' ')}</span>
                                </div>
                            </div>
                            <button onclick="event.stopPropagation(); workspaceManager.deleteProject('${project.id}')" class="text-gray-400 hover:text-red-500">
                                <span class="material-icons text-sm">delete</span>
                            </button>
                        </div>
                        <p class="text-gray-600 text-sm mb-3 line-clamp-2">${project.description || 'No description'}</p>
                        <div class="flex items-center justify-between text-xs text-gray-500">
                            <span>Updated: ${date}</span>
                            ${project.data ? '<span class="text-green-600">Has data</span>' : '<span class="text-gray-400">Empty</span>'}
                        </div>
                    </div>
                `;
    }

    renderProjectDetails(project) {
        const date = new Date(project.updatedAt).toLocaleString();
        const categoryIcons = {
            'truth-table': 'table_chart',
            'kmap': 'grid_on',
            'circuit': 'device_hub',
            'simplification': 'functions',
            'whiteboard': 'edit'
        };

        return `
                    <div class="space-y-4">
                        <div class="flex items-center space-x-3">
                            <span class="material-icons text-3xl text-gray-600">${categoryIcons[project.category] || 'folder'}</span>
                            <div>
                                <h4 class="text-xl font-semibold text-gray-900">${project.name}</h4>
                                <p class="text-gray-600">${project.description || 'No description'}</p>
                            </div>
                        </div>
                        
                        <div class="grid grid-cols-2 gap-4">
                            <div class="bg-gray-50 p-3 rounded-lg">
                                <p class="text-sm font-medium text-gray-700">Category</p>
                                <p class="text-gray-900">${project.category.replace('-', ' ')}</p>
                            </div>
                            <div class="bg-gray-50 p-3 rounded-lg">
                                <p class="text-sm font-medium text-gray-700">Last Updated</p>
                                <p class="text-gray-900">${date}</p>
                            </div>
                        </div>

                        ${project.data ? `
                            <div class="bg-blue-50 p-4 rounded-lg">
                                <h5 class="font-medium text-blue-900 mb-2">Project Data</h5>
                                <pre class="text-sm text-blue-800 bg-blue-100 p-2 rounded overflow-auto">${JSON.stringify(project.data, null, 2)}</pre>
                            </div>
                        ` : `
                            <div class="bg-yellow-50 p-4 rounded-lg">
                                <h5 class="font-medium text-yellow-900 mb-2">No Data</h5>
                                <p class="text-yellow-800 text-sm">This project doesn't have any saved data yet.</p>
                            </div>
                        `}

                        <div class="flex space-x-3">
                            <button onclick="workspaceManager.openProject('${project.id}')" class="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                                Open Project
                            </button>
                            <button onclick="workspaceManager.exportProject('${project.id}')" class="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50">
                                Export
                            </button>
                        </div>
                    </div>
                `;
    }

    updateEmptyState() {
        const emptyState = document.getElementById('emptyState');
        const projectsGrid = document.getElementById('projectsGrid');

        if (this.projects.length === 0) {
            emptyState.style.display = 'block';
            projectsGrid.style.display = 'none';
        } else {
            emptyState.style.display = 'none';
            projectsGrid.style.display = 'grid';
        }
    }

    deleteProject(projectId) {
        if (confirm('Are you sure you want to delete this project?')) {
            this.projects = this.projects.filter(p => p.id !== projectId);
            this.saveProjects();
            this.renderProjects();
            this.updateEmptyState();
            this.showNotification('Project deleted successfully!', 'success');
        }
    }

    openProject(projectId) {
        const project = this.projects.find(p => p.id === projectId);
        if (!project) return;

        // Navigate to the appropriate page based on category
        const pageMap = {
            'truth-table': 'truthTable',
            'kmap': 'kmap',
            'circuit': 'circuit',
            'simplification': 'simplification',
            'whiteboard': 'whiteboard'
        };

        const targetPage = pageMap[project.category];
        if (targetPage) {
            showPage(targetPage);
            this.hideDetailsModal();
            this.showNotification(`Opening ${project.name}...`, 'info');
        }
    }

    exportProject(projectId) {
        const project = this.projects.find(p => p.id === projectId);
        if (!project) return;

        const dataStr = JSON.stringify(project, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        const url = URL.createObjectURL(dataBlob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `${project.name.replace(/[^a-z0-9]/gi, '_').toLowerCase()}.json`;
        link.click();
        URL.revokeObjectURL(url);

        this.showNotification('Project exported successfully!', 'success');
    }

    saveCurrentWork(category, data) {
        // This function will be called from other parts of the app to save current work
        const project = {
            id: this.generateId(),
            name: `Auto-saved ${category} - ${new Date().toLocaleDateString()}`,
            description: `Auto-saved work from ${category}`,
            category: category,
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
            data: data
        };

        this.projects.unshift(project);
        this.saveProjects();
        this.renderProjects();
        this.updateEmptyState();
        this.showNotification('Work saved to workspace!', 'success');
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `fixed top-4 right-4 z-50 px-4 py-2 rounded-lg text-white font-medium ${type === 'success' ? 'bg-green-500' :
                type === 'error' ? 'bg-red-500' :
                    'bg-blue-500'
            }`;
        notification.textContent = message;

        document.body.appendChild(notification);

        // Remove after 3 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 3000);
    }
}

// Initialize workspace manager
let workspaceManager = new WorkspaceManager();
window.workspaceManager = workspaceManager; // Make it globally accessible

// Working time tracking
let startTime = Date.now();
let workingTimeInterval;

function updateWorkingTime() {
    let seconds = 0;
    setInterval(() => {
        seconds++;
        const h = String(Math.floor(seconds / 3600)).padStart(2, '0');
        const m = String(Math.floor((seconds % 3600) / 60)).padStart(2, '0');
        const s = String(seconds % 60).padStart(2, '0');
        const el = document.getElementById('workingTime');
        if (el) el.textContent = `${h}:${m}:${s}`;
    }, 1000);
}

function startWorkingTime() {
    startTime = Date.now();
    workingTimeInterval = setInterval(updateWorkingTime, 1000);
}

function showPage(page) {
    console.log('Switching to page:', page);

    // Hide all pages
    document.querySelectorAll('.page-content').forEach(pg => pg.classList.add('hidden'));

    // Show selected page
    const pageElement = document.getElementById(`${page}Page`);
    if (pageElement) {
        pageElement.classList.remove('hidden');
        currentPage = page;

        // Update page title
        const titles = {
            home: 'LogicLab Dashboard',
            kmap: 'Truth Table & K-Map Generator',
            circuit: 'Circuit Designer',
            simplifier: 'Boolean Expression Simplifier',
            whiteboard: 'Logic Whiteboard',
            workspace: 'Personal Workspace',
            sequence: 'Sequence Detector',
            flipflops: 'Flip-Flop Conversion'
        };
        pageTitle.textContent = titles[page] || 'LogicLab Dashboard';
    }
}
// Project Timeline Chart
document.addEventListener('DOMContentLoaded', function () {
    // Initialize the timeline chart when workspace page is shown
    document.getElementById('timelineWeek').addEventListener('click', function () {
        updateTimelineButtons('week');
        updateTimelineChart('week');
    });

    document.getElementById('timelineMonth').addEventListener('click', function () {
        updateTimelineButtons('month');
        updateTimelineChart('month');
    });

    document.getElementById('timelineYear').addEventListener('click', function () {
        updateTimelineButtons('year');
        updateTimelineChart('year');
    });
});

let timelineChart;

function initTimelineChart() {
    if (timelineChart) {
        timelineChart.destroy();
    }

    const ctx = document.getElementById('projectTimelineChart').getContext('2d');

    // Sample data for the timeline chart
    const weekData = {
        labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        datasets: [{
            label: 'Projects Created',
            data: [2, 3, 1, 4, 2, 0, 1],
            backgroundColor: 'rgba(59, 130, 246, 0.5)',
            borderColor: 'rgba(59, 130, 246, 1)',
            borderWidth: 2,
            tension: 0.4
        }, {
            label: 'Projects Updated',
            data: [1, 2, 3, 2, 4, 1, 0],
            backgroundColor: 'rgba(139, 92, 246, 0.5)',
            borderColor: 'rgba(139, 92, 246, 1)',
            borderWidth: 2,
            tension: 0.4
        }]
    };

    timelineChart = new Chart(ctx, {
        type: 'line',
        data: weekData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                },
                title: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

function updateTimelineButtons(period) {
    const buttons = ['timelineWeek', 'timelineMonth', 'timelineYear'];
    buttons.forEach(id => {
        const btn = document.getElementById(id);
        if (id === 'timeline' + period.charAt(0).toUpperCase() + period.slice(1)) {
            btn.className = 'px-3 py-1 bg-blue-100 text-blue-700 rounded-lg text-sm font-medium';
        } else {
            btn.className = 'px-3 py-1 bg-gray-100 text-gray-700 rounded-lg text-sm font-medium';
        }
    });
}

function updateTimelineChart(period) {
    if (!timelineChart) return;

    let labels, data1, data2;

    if (period === 'week') {
        labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
        data1 = [2, 3, 1, 4, 2, 0, 1];
        data2 = [1, 2, 3, 2, 4, 1, 0];
    } else if (period === 'month') {
        labels = ['Week 1', 'Week 2', 'Week 3', 'Week 4'];
        data1 = [8, 12, 6, 10];
        data2 = [5, 9, 11, 7];
    } else if (period === 'year') {
        labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
        data1 = [15, 18, 12, 20, 16, 14, 18, 22, 19, 24, 20, 16];
        data2 = [10, 14, 16, 12, 18, 15, 20, 16, 22, 18, 14, 12];
    }

    timelineChart.data.labels = labels;
    timelineChart.data.datasets[0].data = data1;
    timelineChart.data.datasets[1].data = data2;
    timelineChart.update();
}

// API Configuration
const API_BASE_URL = 'http://localhost:8000';  // FastAPI server URL

// Global state
let currentPage = 'home';
let isExpanded = false;

// DOM Elements
const sidebar = document.getElementById('sidebar');
const mainContent = document.getElementById('mainContent');
const menuToggle = document.getElementById('menuToggle');
const pageTitle = document.getElementById('pageTitle');
const loadingModal = document.getElementById('loadingModal');

// Utility Functions
function showLoading() {
    loadingModal.classList.remove('hide');
    loadingModal.classList.add('show');
}

function hideLoading() {
    loadingModal.classList.remove('show');
    loadingModal.classList.add('hide');
}

function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'card bg-red-50 border border-red-200 rounded-xl p-4 mb-4';
    errorDiv.innerHTML = `
                <div class="flex items-center">
                    <span class="material-icons text-red-500 mr-2">error</span>
                    <span class="text-red-700">${message}</span>
                </div>
            `;
    return errorDiv;
}
// API Functions
async function callAPI(endpoint, formData) {
    try {
        showLoading();
        console.log(`Making API call to: ${API_BASE_URL}${endpoint}`);

        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            method: 'POST',
            body: formData
        });

        console.log(`Response status: ${response.status}`);

        if (!response.ok) {
            let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
            try {
                const errorData = await response.json();
                errorMessage = errorData.detail || errorData.message || errorMessage;
            } catch (e) {
                // If we can't parse JSON, use the status text
                console.warn('Could not parse error response as JSON:', e);
            }
            throw new Error(errorMessage);
        }

        const result = await response.json();
        console.log('API response:', result);
        return result;
    } catch (error) {
        console.error('API Error:', error);
        if (error.name === 'TypeError' && error.message.includes('fetch')) {
            throw new Error(`Network error: Unable to connect to server at ${API_BASE_URL}. Please ensure the backend is running.`);
        }
        throw error;
    } finally {
        hideLoading();
    }
}

// Navigation item click handlers
document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', (e) => {
        e.preventDefault();
        console.log('Nav item clicked:', item.dataset.page); // Debug log

        // Remove active class from all items
        document.querySelectorAll('.nav-item').forEach(nav => nav.classList.remove('active'));
        // Add active class to clicked item
        item.classList.add('active');

        // Navigate to page
        const pageName = item.dataset.page;
        if (pageName) {
            showPage(pageName);
        } else {
            console.error('No page name found for nav item:', item);
        }
    });
});

// Feature card and quick action navigation
document.querySelectorAll('[data-navigate]').forEach(element => {
    element.addEventListener('click', () => {
        const targetPage = element.dataset.navigate;

        // Update navigation
        document.querySelectorAll('.nav-item').forEach(nav => nav.classList.remove('active'));
        const targetNav = document.querySelector(`[data-page="${targetPage}"]`);
        if (targetNav) {
            targetNav.classList.add('active');
        }

        showPage(targetPage);
    });
});

// Truth Table Generation
document.getElementById('generateTruthTable').addEventListener('click', async () => {
    const expression = document.getElementById('kmapExpression').value.trim();
    if (!expression) {
        alert('Please enter a Boolean expression');
        return;
    }

    try {
        const formData = new FormData();
        formData.append('expr', expression);

        const result = await callAPI('/truth-table', formData);

        // Display truth table
        const resultsDiv = document.getElementById('kmapResults');
        resultsDiv.innerHTML = '';

        const tableCard = document.createElement('div');
        tableCard.className = 'card bg-white rounded-xl p-6';

        let tableHTML = `
                    <div class="flex justify-between items-center mb-4">
                        <h4 class="text-lg font-semibold text-gray-900">Truth Table for: ${expression}</h4>
                        <button onclick="window.workspaceManager.saveCurrentWork('truth-table', ${JSON.stringify({ expression: expression, result: result })})" class="btn-material bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg flex items-center space-x-2">
                            <span class="material-icons text-sm">save</span>
                            <span>Save to Workspace</span>
                        </button>
                    </div>
                    <div class="overflow-x-auto">
                        <table class="truth-table w-full border-collapse border border-gray-300">
                            <thead>
                                <tr class="bg-gray-50">
                `;

        // Add headers for input variables
        result.variables.forEach(variable => {
            tableHTML += `<th class="border border-gray-300 px-4 py-2 text-center font-bold text-blue-900">${variable}</th>`;
        });
        tableHTML += `<th class="border border-gray-300 px-4 py-2 text-center font-bold text-blue-900">Output</th>`;
        tableHTML += '</tr></thead><tbody>';

        // Add rows with results
        if (result.table && Array.isArray(result.table)) {
            result.table.forEach(row => {
                tableHTML += '<tr>';
                if (row.inputs && typeof row.inputs === 'object') {
                    Object.values(row.inputs).forEach(value => {
                        tableHTML += `<td class="border border-gray-300 px-4 py-2 text-center text-gray-800">${value ? '1' : '0'}</td>`;
                    });
                }
                tableHTML += `<td class="border border-gray-300 px-4 py-2 text-center font-bold ${row.output ? 'text-green-600' : 'text-red-600'}">${row.output ? '1' : '0'}</td>`;
                tableHTML += '</tr>';
            });
        } else {
            tableHTML += '<tr><td colspan="' + (result.variables.length + 1) + '" class="text-center text-red-600">Error: Invalid table data</td></tr>';
        }

        tableHTML += '</tbody></table></div>';
        tableCard.innerHTML = tableHTML;
        resultsDiv.appendChild(tableCard);

    } catch (error) {
        const resultsDiv = document.getElementById('kmapResults');
        resultsDiv.innerHTML = '';
        resultsDiv.appendChild(showError(`Error generating truth table: ${error.message}`));
    }
});
// K-Map Generation
document.getElementById('generateKMap').addEventListener('click', async () => {
    const expression = document.getElementById('kmapExpression').value.trim();
    if (!expression) {
        alert('Please enter a Boolean expression');
        return;
    }

    try {
        const formData = new FormData();
        formData.append('expr', expression);

        const result = await callAPI('/kmap', formData);

        // Display K-Map results
        const resultsDiv = document.getElementById('kmapResults');
        resultsDiv.innerHTML = '';

        const kmapCard = document.createElement('div');
        kmapCard.className = 'card bg-white rounded-xl p-6';

        // Create image URL with cache-busting
        const imageUrl = result.image_url || result.image || `/kmap.png?t=${Date.now()}`;

        kmapCard.innerHTML = `
                    <div class="flex justify-between items-center mb-4">
                        <h4 class="text-lg font-semibold text-gray-900">K-Map & Simplified Expression</h4>
                        <button onclick="window.workspaceManager.saveCurrentWork('kmap', ${JSON.stringify({ expression: expression, result: result }).replace(/"/g, '&quot;')})" class="btn-material bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg flex items-center space-x-2">
                            <span class="material-icons text-sm">save</span>
                            <span>Save to Workspace</span>
                        </button>
                    </div>
                   
                        ${result.kmap && Array.isArray(result.kmap) && result.kmap.length > 0 ?
                `<div class="bg-blue-50 p-4 rounded-lg">
                                <h5 class="font-medium text-blue-700 mb-2">K-Map Grid:</h5>
                                <div class="grid grid-cols-${result.kmap[0].length} gap-1 max-w-md mx-auto">
                                    ${result.kmap.map(row =>
                    row.map(cell =>
                        `<div class="border border-blue-300 p-3 text-center font-mono bg-black">${cell}</div>`
                    ).join('')
                ).join('')}
                                </div>
                            </div>` :
                '<div class="text-red-600 bg-red-50 p-4 rounded-lg">K-Map grid not available for expressions with more than 3 variables</div>'
            }
                        <div class="bg-green-50 p-4 rounded-lg">
                            <h5 class="font-medium text-green-700 mb-2">Simplified Expression:</h5>
                            <p class="text-lg text-blue-900 font-mono bg-white p-3 rounded border">${result.simplified || 'N/A'}</p>
                        </div>
                    </div>
                `;
        resultsDiv.appendChild(kmapCard);

        // Force image refresh by reloading it
        const kmapImage = document.getElementById('kmapImage');
        if (kmapImage && result.timestamp) {
            // Add a small delay to ensure the backend has saved the file
            setTimeout(() => {
                kmapImage.src = kmapImage.src.split('?')[0] + '?t=' + result.timestamp;
            }, 100);
        }

    } catch (error) {
        const resultsDiv = document.getElementById('kmapResults');
        resultsDiv.innerHTML = '';
        resultsDiv.appendChild(showError(`Error generating K-Map: ${error.message}`));
    }
});

// Circuit Generation
document.getElementById('generateCircuit').addEventListener('click', async () => {
    const expression = document.getElementById('circuitExpression').value.trim();
    if (!expression) {
        alert('Please enter a Boolean expression');
        return;
    }

    try {
        const formData = new FormData();
        formData.append('expr', expression);

        const result = await callAPI('/circuit', formData);

        // Display Circuit results
        const resultsDiv = document.getElementById('circuitResults');
        resultsDiv.innerHTML = '';

        const circuitCard = document.createElement('div');
        circuitCard.className = 'card bg-white rounded-xl p-6';
        circuitCard.innerHTML = `
                    <div class="flex justify-between items-center mb-4">
                        <h4 class="text-lg font-semibold text-gray-900">Logic Circuit Analysis</h4>
                        <button onclick="window.workspaceManager.saveCurrentWork('circuit', ${JSON.stringify({ expression: expression, result: result })})" class="btn-material bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg flex items-center space-x-2">
                            <span class="material-icons text-sm">save</span>
                            <span>Save to Workspace</span>
                        </button>
                    </div>
                    <div class="space-y-4">
                        <div class="bg-gray-50 p-4 rounded-lg border border-gray-200">
                            <pre class="whitespace-pre-wrap text-sm font-mono text-pink-900 font-bold">${result.circuit_text}</pre>
                        </div>
                        <div class="text-sm text-gray-600 mt-4">
                            <p><strong>Input Variables:</strong> ${result.variables.join(', ')}</p>
                            <p class="mt-2"><strong>Total Gates:</strong> ${result.gate_count}</p>
                            <p class="mt-2"><strong>Expression:</strong> ${result.expression}</p>
                        </div>
                    </div>
                `;
        resultsDiv.appendChild(circuitCard);

    } catch (error) {
        const resultsDiv = document.getElementById('circuitResults');
        resultsDiv.innerHTML = '';
        resultsDiv.appendChild(showError(`Error generating circuit: ${error.message}`));
    }
});

// Boolean Expression Simplifier
document.getElementById('simplifyExpression').addEventListener('click', async () => {
    const expression = document.getElementById('simplifierExpression').value.trim();
    if (!expression) {
        alert('Please enter a Boolean expression');
        return;
    }

    try {
        const formData = new FormData();
        formData.append('expr', expression);

        const result = await callAPI('/simplify', formData);

        // Display Simplification results
        const resultsDiv = document.getElementById('simplifierResults');
        resultsDiv.innerHTML = '';

        const simplifierCard = document.createElement('div');
        simplifierCard.className = 'card bg-white rounded-xl p-6';
        simplifierCard.innerHTML = `
                    <div class="flex justify-between items-center mb-4">
                        <h4 class="text-lg font-semibold text-gray-900">Boolean Expression Simplification</h4>
                        <button onclick="window.workspaceManager.saveCurrentWork('simplification', ${JSON.stringify({ expression: expression, result: result })})" class="btn-material bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg flex items-center space-x-2">
                            <span class="material-icons text-sm">save</span>
                            <span>Save to Workspace</span>
                        </button>
                    </div>
                    <div class="space-y-4">
                        <div class="bg-gray-50 p-4 rounded-lg">
                            <p class="text-sm text-gray-600">Original Expression:</p>
                            <p class="font-mono mt-1 text-blue-900 font-bold">${result.original || expression}</p>
                        </div>
                        <div class="bg-green-50 p-4 rounded-lg">
                            <p class="text-sm text-green-600">Best Simplified Expression:</p>
                            <p class="font-mono mt-1 text-lg font-semibold text-blue-900">${result.simplified}</p>
                        </div>
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div class="bg-blue-50 p-4 rounded-lg">
                                <p class="text-sm text-blue-600 font-medium">Algebraic SOP Form:</p>
                                <p class="font-mono mt-1 text-red-900 font-bold">${result.algebraic_sop}</p>
                            </div>
                            <div class="bg-purple-50 p-4 rounded-lg">
                                <p class="text-sm text-purple-600 font-medium">Algebraic POS Form:</p>
                                <p class="font-mono mt-1 text-yellow-900 font-bold">${result.algebraic_pos}</p>
                            </div>
                        </div>
                        <div class="bg-yellow-50 p-4 rounded-lg">
                            <p class="text-sm text-yellow-600 font-medium">Manual Simplification:</p>
                            <p class="font-mono mt-1 text-red-900 font-bold">${result.manual}</p>
                        </div>
                        <div class="bg-indigo-50 p-4 rounded-lg">
                            <p class="text-sm text-indigo-600 font-medium">Variables:</p>
                            <p class="font-mono mt-1 text-indigo-900 font-bold">${result.variables ? result.variables.join(', ') : 'None detected'}</p>
                        </div>
                        ${result.complexity_reduction > 0 ? `
                        <div class="bg-emerald-50 p-4 rounded-lg">
                            <p class="text-sm text-emerald-600 font-medium">Complexity Reduction:</p>
                            <p class="font-mono mt-1 text-green-900 font-bold">${result.complexity_reduction} characters reduced</p>
                        </div>
                        ` : ''}
                    </div>
                `;
        resultsDiv.appendChild(simplifierCard);

    } catch (error) {
        console.error('Simplification error:', error);
        const resultsDiv = document.getElementById('simplifierResults');
        resultsDiv.innerHTML = '';

        let errorMessage = 'Error simplifying expression';
        if (error.message) {
            errorMessage += `: ${error.message}`;
        } else if (error.toString) {
            errorMessage += `: ${error.toString()}`;
        }

        resultsDiv.appendChild(showError(errorMessage));
    }
});

// Sequence Detector Functionality
document.getElementById('analyzeSequence').addEventListener('click', async () => {
    const sequence = document.getElementById('targetSequence').value.trim();
    const detectorType = document.getElementById('detectorType').value;
    const testSequence = document.getElementById('testSequence').value.trim();

    if (!sequence) {
        alert('Please enter a target sequence');
        return;
    }
    if (!/^[01]+$/.test(sequence)) {
        alert('Sequence must contain only 0s and 1s');
        return;
    }
    if (sequence.length < 2 || sequence.length > 8) {
        alert('Sequence must be between 2 and 8 bits long');
        return;
    }

    try {
        const formData = new FormData();
        formData.append('sequence_str', sequence);       // ✅ backend expects sequence_str
        formData.append('detector_type', detectorType);
        if (testSequence) {
            formData.append('test_sequence', testSequence);  // ✅ backend expects test_sequence
        }

        const response = await fetch('/sequence-detector', {
            method: 'POST',
            body: formData
        });
        const json = await response.json();
        console.log("DEBUG backend JSON:", json);

        if (!json.success) {
            alert("Error analyzing sequence detector: " + (json.error || json.message));
            return;
        }

        const result = json.data;

        // Display Sequence Detector results
        const resultsDiv = document.getElementById('sequenceResults');
        resultsDiv.innerHTML = '';

        const sequenceCard = document.createElement('div');
        sequenceCard.className = 'card bg-white rounded-xl p-6';
        sequenceCard.innerHTML = `
            <div class="flex justify-between items-center mb-4">
                <h4 class="text-lg font-semibold text-gray-900">
                    ${detectorType.charAt(0).toUpperCase() + detectorType.slice(1)} Sequence Detector Analysis
                </h4>
                <button onclick="window.workspaceManager.saveCurrentWork('sequence-detector', ${JSON.stringify({ sequence: sequence, detectorType: detectorType })})" 
                    class="btn-material bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg flex items-center space-x-2">
                    <span class="material-icons text-sm">save</span>
                    <span>Save to Workspace</span>
                </button>
            </div>
            <div class="space-y-6">

                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div class="bg-blue-50 p-4 rounded-lg">
                        <p class="text-sm text-blue-600 font-medium">Target Sequence:</p>
                        <p class="font-mono mt-1 text-lg font-semibold text-blue-900 font-semibold">${result.sequence}</p>
                    </div>
                    <div class="bg-green-50 p-4 rounded-lg">
                        <p class="text-sm text-green-600 font-medium">Detector Type:</p>
                        <p class="font-mono mt-1 text-lg font-semibold text-black-900 text-blue-900 font-semibold">${detectorType}</p>
                    </div>
                    <div class="bg-purple-50 p-4 rounded-lg">
                        <p class="text-sm text-purple-600 font-medium">Detections Found:</p>
                        <p class="font-mono mt-1 text-lg font-semibold text-blue-900 font-semibold">${result.detections.join(', ') || 'None'}</p>
                    </div>
                </div>

                <div class="bg-gray-50 p-4 rounded-lg">
                    <p class="text-sm text-gray-600 font-medium">State Transition Table:</p>
                    <div class="mt-2 overflow-x-auto">
                        <table class="min-w-full border border-gray-300">
                            <thead>
                                <tr class="bg-gray-100">
                                    <th class="border border-gray-300 px-3 py-2 text-left text-red-900 font-bold">Current State</th>
                                    <th class="border border-gray-300 px-3 py-2 text-left text-red-900 font-bold">Input</th>
                                    <th class="border border-gray-300 px-3 py-2 text-left text-red-900 font-bold">Next State</th>
                                    <th class="border border-gray-300 px-3 py-2 text-left text-red-900 font-bold">Output</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${result.state_table.map(row => `
                                    <tr>
                                        <td class="border border-gray-300 px-3 py-2 font-mono text-yellow-900 font-semibold">${row.current_state}</td>
                                        <td class="border border-gray-300 px-3 py-2 font-mono text-gray-900 font-semibold">${row.input}</td>
                                        <td class="border border-gray-300 px-3 py-2 font-mono text-green-900 font-semibold">${row.next_state}</td>
                                        <td class="border border-gray-300 px-3 py-2 font-mono text-indigo-900 font-semibold">${row.is_output ? 1 : 0}</td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                </div>

               <div class="bg-gray-50 p-4 rounded-lg">
    <p class="text-sm text-gray-600 font-medium">State Diagram:</p>
    <div class="mt-2 border rounded-lg flex justify-center items-center overflow-hidden"">
        <img src="${result.diagram}" 
             alt="State Diagram" 
             class="h-full w-auto transform -rotate-90 object-contain">
    </div>
</div>


                <div class="bg-gray-50 p-4 rounded-lg">
                    <p class="text-sm text-gray-600 font-medium">Truth Table:</p>
                    <img src="${result.truth_table_image}" alt="Truth Table" class="w-full h-auto object-contain">
                </div>
                <div class="bg-blue-50 p-4 rounded-lg height-75%">
    <p class="text-sm text-blue-600 font-medium">K-Maps:</p>
    <div class="mt-2 grid grid-cols-2 gap-4">
        ${Object.entries(result.kmap_images).map(([ff, url]) => `
            <div class="text-center">
                <p class="font-mono text-sm font-medium mb-2">${ff}</p>
                <img src="${url}" alt="K-Map for ${ff}" class="border rounded-lg mx-auto ">
            </div>
        `).join('')}
    </div>
</div>

<div class="bg-yellow-50 p-4 rounded-lg">
    <p class="text-sm text-yellow-600 font-medium">Simplified Logic:</p>
    <ul class="mt-2 space-y-1">
        ${Object.entries(result.simplified_logic).map(([ff, expr]) => `
            <li class="font-mono font-semibold text-blue-900 font-bold">${ff} = ${expr}</li>
        `).join('')}
    </ul>
</div>
            </div>
        `;
        resultsDiv.appendChild(sequenceCard);

    } catch (error) {
        console.error('Sequence detector error:', error);
        alert("Error analyzing sequence detector: " + (error.message || error));
    }
});
// FlipFlop Conversion Functionality
document.addEventListener("DOMContentLoaded", () => {
    const flipBtn = document.getElementById("convertFlipFlop");
    if (!flipBtn) {
        console.warn("Flip-Flop button not found in DOM.");
        return;
    }

    flipBtn.addEventListener("click", async () => {
        const availableFF = document.getElementById("flipflopType")?.value;
        const requiredFF = document.getElementById("requiredFlipFlop")?.value;
        const container = document.getElementById("flipflopsResults");

        if (!availableFF || !requiredFF || !container) {
            console.error("Missing inputs or results container for flip-flop conversion.");
            return;
        }

        container.innerHTML = "<p>Processing...</p>";

        try {
            const formData = new FormData();
            formData.append("available_ff", availableFF);
            formData.append("required_ff", requiredFF);

            const data = await callAPI("/flipflop-convert", formData);

            const makeTable = (objArray) => {
                if (!objArray || objArray.length === 0) return "<p>No data</p>";
                const keys = Object.keys(objArray[0]);
                let html = "<table class='table-auto border border-gray-400 mt-2 mb-4 w-full text-center'><thead><tr>";
                keys.forEach(k => html += `<th class='border px-2 py-1'>${k}</th>`);
                html += "</tr></thead><tbody>";
                objArray.forEach(row => {
                    html += "<tr>";
                    keys.forEach(k => html += `<td class='border px-2 py-1'>${row[k]}</td>`);
                    html += "</tr>";
                });
                html += "</tbody></table>";
                return html;
            };

            const step4Html = Object.entries(data.step4_boolean_equations || {})
                .map(([k, v]) => `<div><strong>${k}</strong> = ${v}</div>`)
                .join("");

            container.innerHTML = `
                <div class="bg-red border rounded-lg p-4 shadow">
                    <h3 class="text-lg font-bold mb-2 text-gray-900">Step 1: Identify Flip-Flops</h3>
                    <p>${data.step1}</p>
                </div>
                <div class="bg-white border rounded-lg p-4 shadow">
                    <h3 class="text-lg font-bold mb-2">Step 2: Characteristic Table (${requiredFF})</h3>
                    ${makeTable(data.step2_characteristic_table)}
                </div>
                <div class="bg-blue border rounded-lg p-4 shadow">
                    <h3 class="text-lg font-bold mb-2">Step 3: Excitation Table (${availableFF})</h3>
                    ${makeTable(data.step3_excitation_table)}
                </div>
                <div class="bg-green border rounded-lg p-4 shadow">
                    <h3 class="text-lg font-bold mb-2">Step 4: Boolean Equations</h3>
                    <div class="bg-gray-100 p-2 rounded space-y-1">${step4Html}</div>
                </div>
                <div class="bg-gray border rounded-lg p-4 shadow">
                    <h3 class="text-lg font-bold mb-2">Step 5: Circuit Diagram</h3>
                    <div class="flex justify-center">
                        <img src="${data.step5_circuit_image}" class="max-w-lg animate-pulse glow">
                    </div>
                </div>
            `;
        } catch (error) {
            console.error(error);
            container.innerHTML = "<p class='text-red-600'>Error converting flip-flop.</p>";
        }
    });
});

// Add fade-in animation to cards on scroll
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('fade-in');
        }
    });
}, observerOptions);

// Observe all cards for animation
document.querySelectorAll('.card, .feature-card').forEach(card => {
    observer.observe(card);
});

// Input validation and suggestions
function setupInputHelpers() {
    const inputs = ['kmapExpression', 'circuitExpression', 'simplifierExpression'];

    inputs.forEach(inputId => {
        const input = document.getElementById(inputId);
        if (input) {
            // Add example expressions on focus
            input.addEventListener('focus', function () {
                if (!this.value) {
                    this.placeholder = 'Try: A & B | C, (A + B) & C, A.B + A.C, A AND B OR NOT C';
                }
            });

            // Reset placeholder on blur
            input.addEventListener('blur', function () {
                this.placeholder = this.getAttribute('data-original-placeholder') || this.placeholder;
            });

            // Store original placeholder
            input.setAttribute('data-original-placeholder', input.placeholder);
        }
    });
}

// API Health Check
document.getElementById("testapi").addEventListener("click", checkAPIConnection);

async function checkAPIConnection() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        if (response.ok) {
            const data = await response.json();
            console.log('✅ API connection successful:', data);

            // Show success indicator
            const successDiv = document.createElement('div');
            successDiv.id = 'api-success';
            successDiv.className = 'fixed top-20 right-4 bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded-lg shadow-lg z-40';
            successDiv.innerHTML = `
                        <div class="flex items-center">
                            <span class="material-icons mr-2">check_circle</span>
                            <div>
                                <p class="font-medium">Backend Connected</p>
                                <p class="text-sm">API server is running on ${API_BASE_URL}</p>
                            </div>
                            <button class="ml-4 text-green-600 hover:text-green-800" onclick="this.parentElement.parentElement.remove()">
                                <span class="material-icons">close</span>
                            </button>
                        </div>
                    `;
            document.body.appendChild(successDiv);

            // Remove any existing warning
            const existingWarning = document.getElementById('api-warning');
            if (existingWarning) {
                existingWarning.remove();
            }
            // Auto-remove after 5 seconds
            setTimeout(() => {
                if (successDiv.parentElement) {
                    successDiv.remove();
                }
            }, 5000);

            return data;
        } else {
            throw new Error('API not responding');
        }
    } catch (error) {
        console.warn('⚠️ API connection failed. Please ensure your FastAPI server is running on', API_BASE_URL);
        // Show connection warning
        const warningDiv = document.createElement('div');
        warningDiv.id = 'api-warning';
        warningDiv.className = 'fixed top-20 right-4 bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3 rounded-lg shadow-lg z-40';
        warningDiv.innerHTML = `
                    <div class="flex items-center">
                        <span class="material-icons mr-2">warning</span>
                        <div>
                            <p class="font-medium">API Server Not Connected</p>
                            <p class="text-sm">Please start your FastAPI server on ${API_BASE_URL}</p>
                            <p class="text-xs mt-1">Run: <code>python main.py</code> or <code>uvicorn main:app --reload</code></p>
                        </div>
                        <button class="ml-4 text-yellow-600 hover:text-yellow-800" onclick="this.parentElement.parentElement.remove()">
                            <span class="material-icons">close</span>
                        </button>
                    </div>
                `;
        document.body.appendChild(warningDiv);

        // Auto-remove after 10 seconds
        setTimeout(() => {
            if (warningDiv.parentElement) {
                warningDiv.remove();
            }
        }, 10000);

        throw error;
    }
}
// ------------------------------
// Manual Test Backend Button
// ------------------------------
window.testAPIConnection = function () {
    console.log('🔄 Manually testing API connection...');
    updateBackendStatus('loading', 'Checking connection...');

    checkAPIConnection()
        .then((data) => {
            console.log('✅ Manual API test successful:', data);
            const msg = (data.endpoints && data.endpoints.length)
                ? `${data.endpoints.length} endpoints available`
                : "Connected";
            updateBackendStatus('connected', msg);
            alert('✅ Backend connection successful!\n\nAvailable endpoints:\n' + (data.endpoints || []).join('\n'));
        })
        .catch((error) => {
            console.error('❌ Manual API test failed:', error);
            updateBackendStatus('disconnected', 'Connection failed');
            alert('❌ Backend connection failed!\n\nError: ' + error.message + '\n\nPlease ensure the backend is running on ' + API_BASE_URL);
        });
};

// ------------------------------
// Auto-check on page load
// ------------------------------
document.addEventListener('DOMContentLoaded', () => {
    console.log('🔄 Auto-checking backend...');

    checkAPIConnection()
        .then((data) => {
            console.log('✅ Backend connected:', data);
            const msg = (data.endpoints && data.endpoints.length)
                ? `${data.endpoints.length} endpoints available`
                : "Connected";
        })
        .catch((error) => {
            console.error('❌ Backend check failed:', error);
        });
});