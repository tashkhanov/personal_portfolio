// SaaS Central Hub - Executive Control Scripts

// Dynamic Host and Endpoint Routing Configuration
const isSubdomain = window.location.hostname.startsWith('hub.');
window.HUB_CONFIG = window.HUB_CONFIG || {
    isSubdomain: isSubdomain,
    killswitchUrl: isSubdomain ? '/api/killswitch/' : '/saas-hub/api/killswitch/',
    extendUrl: isSubdomain ? '/api/extend/' : '/saas-hub/api/extend/',
    addTenantUrl: isSubdomain ? '/api/tenants/add/' : '/saas-hub/api/tenants/add/',
    dashboardUrl: isSubdomain ? '/' : '/saas-hub/',
};

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

function showToast(message, type = 'success') {
    const toast = document.getElementById('hubToast');
    const toastMsg = document.getElementById('hubToastMsg');
    if (!toast || !toastMsg) return;

    toastMsg.innerText = message;
    toast.className = 'toast-box show ' + type;

    setTimeout(() => {
        toast.className = 'toast-box';
    }, 3500);
}

// Kill Switch Toggle
async function toggleKillswitch(tenantId, currentActive, tenantName) {
    const nextAction = currentActive ? 'заблокировать' : 'разблокировать';
    const confirmed = confirm(`Вы уверены, что хотите ${nextAction} заведение "${tenantName}"?\n\nБот и WebApp моментально ${currentActive ? 'прекратят' : 'возобновят'} обслуживание клиентов.`);
    if (!confirmed) return;

    const btn = document.getElementById(`ks-btn-${tenantId}`);
    if (btn) btn.disabled = true;

    try {
        const endpoint = window.HUB_CONFIG ? window.HUB_CONFIG.killswitchUrl : '/saas-hub/api/killswitch/';
        const resp = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
            body: JSON.stringify({
                tenant_id: tenantId,
                activate: !currentActive
            })
        });

        const data = await resp.json();
        if (data.status === 'ok') {
            showToast(`Статус заведения "${tenantName}" успешно изменен!`);
            setTimeout(() => window.location.reload(), 600);
        } else {
            alert('Ошибка: ' + (data.message || 'Не удалось выполнить запрос'));
            if (btn) btn.disabled = false;
        }
    } catch (err) {
        alert('Сетевая ошибка: ' + err.message);
        if (btn) btn.disabled = false;
    }
}

// Extend Subscription Modal
function openExtendModal(tenantId, tenantName, monthlyFee) {
    document.getElementById('extendTenantId').value = tenantId;
    document.getElementById('extendTenantName').innerText = tenantName;
    document.getElementById('extendAmount').value = monthlyFee;
    
    const modal = document.getElementById('extendModal');
    if (modal) modal.classList.add('active');
}

function closeExtendModal() {
    const modal = document.getElementById('extendModal');
    if (modal) modal.classList.remove('active');
}

async function submitExtendForm(e) {
    e.preventDefault();
    const btn = document.getElementById('btnSubmitExtend');
    if (btn) btn.disabled = true;

    const tenantId = document.getElementById('extendTenantId').value;
    const days = document.getElementById('extendDays').value;
    const amount = document.getElementById('extendAmount').value;
    const method = document.getElementById('extendMethod').value;
    const comment = document.getElementById('extendComment').value;

    try {
        const endpoint = window.HUB_CONFIG ? window.HUB_CONFIG.extendUrl : '/saas-hub/api/extend/';
        const resp = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
            body: JSON.stringify({
                tenant_id: tenantId,
                days: parseInt(days),
                amount: parseFloat(amount),
                method: method,
                comment: comment
            })
        });

        const data = await resp.json();
        if (data.status === 'ok') {
            closeExtendModal();
            showToast(`Подписка успешно продлена до ${data.new_expiry}!`);
            setTimeout(() => window.location.reload(), 700);
        } else {
            alert('Ошибка продления: ' + (data.message || 'Ошибка сервера'));
            if (btn) btn.disabled = false;
        }
    } catch (err) {
        alert('Ошибка сети: ' + err.message);
        if (btn) btn.disabled = false;
    }
}

// Add Tenant Modal
function openAddTenantModal() {
    const modal = document.getElementById('addTenantModal');
    if (modal) modal.classList.add('active');
}

function closeAddTenantModal() {
    const modal = document.getElementById('addTenantModal');
    if (modal) modal.classList.remove('active');
}

async function submitAddTenantForm(e) {
    e.preventDefault();
    const btn = document.getElementById('btnAddTenantSubmit');
    if (btn) btn.disabled = true;

    const payload = {
        name: document.getElementById('newTenantName').value,
        slug: document.getElementById('newTenantSlug').value,
        bot_username: document.getElementById('newTenantBot').value,
        owner_name: document.getElementById('newTenantOwner').value,
        phone: document.getElementById('newTenantPhone').value,
        monthly_fee: document.getElementById('newTenantFee').value,
        api_base_url: document.getElementById('newTenantUrl').value,
        api_secret_token: document.getElementById('newTenantToken').value,
    };

    try {
        const endpoint = window.HUB_CONFIG ? window.HUB_CONFIG.addTenantUrl : '/saas-hub/api/tenants/add/';
        const resp = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
            body: JSON.stringify(payload)
        });

        const data = await resp.json();
        if (data.status === 'ok') {
            closeAddTenantModal();
            showToast('Новое заведение успешно зарегистрировано в сети!');
            setTimeout(() => window.location.reload(), 700);
        } else {
            alert('Ошибка регистрации: ' + (data.message || 'Проверьте данные'));
            if (btn) btn.disabled = false;
        }
    } catch (err) {
        alert('Ошибка сети: ' + err.message);
        if (btn) btn.disabled = false;
    }
}

// Auto-fill slug from name
document.addEventListener('DOMContentLoaded', () => {
    const nameInput = document.getElementById('newTenantName');
    const slugInput = document.getElementById('newTenantSlug');
    if (nameInput && slugInput) {
        nameInput.addEventListener('input', () => {
            if (!slugInput.dataset.manual) {
                slugInput.value = nameInput.value.toLowerCase().replace(/[^a-z0-9]/g, '-').replace(/-+/g, '-').replace(/^-|-$/g, '');
            }
        });
        slugInput.addEventListener('input', () => {
            slugInput.dataset.manual = 'true';
        });
    }

    if (window.lucide) {
        window.lucide.createIcons();
    }
});

// Dynamic Instant Filter & Search for Salons
let currentStatusFilter = 'all';

function setFilter(status, elem) {
    currentStatusFilter = status;
    document.querySelectorAll('.filter-chip').forEach(c => c.classList.remove('active'));
    if (elem) elem.classList.add('active');
    filterTenants();
}

function filterTenants() {
    const input = document.getElementById('hubSearchInput');
    const query = (input ? input.value : '').toLowerCase().trim();
    const cards = document.querySelectorAll('.tenant-card');

    cards.forEach(card => {
        const name = (card.dataset.name || '').toLowerCase();
        const slug = (card.dataset.slug || '').toLowerCase();
        const owner = (card.dataset.owner || '').toLowerCase();
        const status = (card.dataset.status || '').toUpperCase();

        const matchesQuery = !query || name.includes(query) || slug.includes(query) || owner.includes(query);
        let matchesStatus = true;
        if (currentStatusFilter === 'active') {
            matchesStatus = status === 'ACTIVE';
        } else if (currentStatusFilter === 'warning') {
            matchesStatus = status === 'WARNING' || status === 'GRACE_PERIOD';
        } else if (currentStatusFilter === 'locked') {
            matchesStatus = status === 'LOCKED';
        }

        if (matchesQuery && matchesStatus) {
            card.style.display = 'flex';
        } else {
            card.style.display = 'none';
        }
    });
}
