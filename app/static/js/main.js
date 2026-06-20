/* ===== main.js - Bus Transport System ===== */

'use strict';

// ─── Session Timeout Warning ───────────────────────────────────────────────
(function () {
    const TIMEOUT_MS = 110 * 60 * 1000; // 110 minutes
    let warningTimer;

    function resetTimer() {
        clearTimeout(warningTimer);
        warningTimer = setTimeout(() => {
            Swal.fire({
                title: 'انتهت جلستك قريباً',
                text: 'ستنتهي جلستك خلال دقيقتين. هل تريد الاستمرار؟',
                icon: 'warning',
                showCancelButton: true,
                confirmButtonText: 'نعم، استمر',
                cancelButtonText: 'تسجيل الخروج',
                confirmButtonColor: '#2563eb',
            }).then(result => {
                if (!result.isConfirmed) {
                    window.location.href = '/auth/logout';
                }
            });
        }, TIMEOUT_MS);
    }

    ['mousemove', 'keypress', 'click', 'touchstart'].forEach(evt => {
        document.addEventListener(evt, resetTimer, { passive: true });
    });
    resetTimer();
})();

// ─── Global Helpers ────────────────────────────────────────────────────────

/** Show a toast notification */
function showToast(message, type = 'success') {
    const colors = {
        success: '#16a34a', danger: '#dc2626',
        warning: '#d97706', info: '#0891b2'
    };
    const icons = { success: 'check-circle', danger: 'exclamation-circle', warning: 'exclamation-triangle', info: 'info-circle' };

    const toast = document.createElement('div');
    toast.className = 'toast show align-items-center text-white border-0 mb-2 animate__animated animate__slideInLeft';
    toast.style.cssText = `background:${colors[type] || colors.info};border-radius:12px;min-width:280px;`;
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body fw-semibold">
                <i class="fas fa-${icons[type] || 'info-circle'} me-2"></i>${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" onclick="this.closest('.toast').remove()"></button>
        </div>`;

    let container = document.querySelector('.toast-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'toast-container position-fixed top-0 start-0 p-3';
        container.style.zIndex = '9999';
        document.body.appendChild(container);
    }
    container.appendChild(toast);
    setTimeout(() => toast.classList.add('animate__fadeOut'), 4500);
    setTimeout(() => toast.remove(), 5000);
}

/** Confirm delete with SweetAlert */
function confirmDelete(formId, name) {
    Swal.fire({
        title: 'هل أنت متأكد؟',
        html: `سيتم حذف <strong>"${name}"</strong> نهائياً`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#dc2626',
        cancelButtonColor: '#64748b',
        confirmButtonText: '<i class="fas fa-trash me-1"></i> نعم، احذف',
        cancelButtonText: 'إلغاء',
        customClass: { popup: 'shadow-lg', confirmButton: 'fw-bold', cancelButton: 'fw-bold' }
    }).then(result => {
        if (result.isConfirmed) {
            document.getElementById(formId).submit();
        }
    });
}

/** Initialize DataTable with Arabic locale */
function initDataTable(id, options = {}) {
    if (!$.fn.DataTable) return;
    $(`#${id}`).DataTable({
        language: {
            search: '',
            searchPlaceholder: 'بحث...',
            lengthMenu: 'عرض _MENU_',
            info: '_START_-_END_ من _TOTAL_',
            infoEmpty: 'لا توجد سجلات',
            zeroRecords: 'لا توجد نتائج مطابقة',
            paginate: { first: '««', last: '»»', next: '›', previous: '‹' }
        },
        pageLength: 25,
        order: [],
        dom: 'lrtip',
        ...options
    });
}

/** Toggle theme */
function toggleTheme() {
    const body = document.body;
    const isDark = body.getAttribute('data-theme') === 'dark';
    const newTheme = isDark ? 'light' : 'dark';
    body.setAttribute('data-theme', newTheme);
    const icon = document.getElementById('theme-icon');
    if (icon) icon.className = isDark ? 'fas fa-moon' : 'fas fa-sun';
    localStorage.setItem('theme', newTheme);
}

/** Sidebar toggle (mobile) */
function toggleSidebar() {
    document.getElementById('sidebar')?.classList.toggle('show');
    document.getElementById('sidebarOverlay')?.classList.toggle('show');
}

// ─── On DOM Ready ──────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    // Apply saved theme
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        document.body.setAttribute('data-theme', savedTheme);
        const icon = document.getElementById('theme-icon');
        if (icon) icon.className = savedTheme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
    }

    // Auto-dismiss toasts after 5s
    setTimeout(() => {
        document.querySelectorAll('.toast').forEach(t => t.remove());
    }, 5000);

    // Highlight active nav
    const path = window.location.pathname;
    document.querySelectorAll('.sidebar-nav .nav-link').forEach(link => {
        const href = link.getAttribute('href');
        if (href && path.startsWith(href) && href !== '/') {
            link.classList.add('active');
        }
    });

    // Phone input validation
    document.querySelectorAll('input[type="tel"]').forEach(input => {
        input.addEventListener('input', function () {
            this.value = this.value.replace(/[^\d+\-() ]/g, '');
        });
    });

    // Global ID: digits only, max 8
    document.querySelectorAll('input[name="global_id"]').forEach(input => {
        input.addEventListener('input', function () {
            this.value = this.value.replace(/\D/g, '').slice(0, 8);
        });
    });

    // Confirm before leaving form with unsaved changes
    const forms = document.querySelectorAll('form[data-confirm-leave]');
    forms.forEach(form => {
        let dirty = false;
        form.querySelectorAll('input, select, textarea').forEach(el => {
            el.addEventListener('change', () => dirty = true);
        });
        form.addEventListener('submit', () => dirty = false);
        window.addEventListener('beforeunload', e => {
            if (dirty) { e.preventDefault(); e.returnValue = ''; }
        });
    });
});
