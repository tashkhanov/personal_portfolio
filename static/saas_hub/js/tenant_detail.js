// SaaS Command Center - Tenant Detail Page Logic
// Dedicated modular script (separated from HTML template)

function switchDetailTab(tabId) {
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.detail-tab-pane').forEach(pane => pane.classList.remove('active'));

    const targetPane = document.getElementById('tab-' + tabId);
    if (targetPane) targetPane.classList.add('active');

    if (window.event && window.event.currentTarget) {
        window.event.currentTarget.classList.add('active');
    }
    if (window.lucide) {
        window.lucide.createIcons();
    }
}

// Сохранение параметров заведения
async function submitTenantSettings(e) {
    e.preventDefault();
    const btn = document.getElementById('btnSaveSettings');
    if (btn) btn.disabled = true;

    const appContainer = document.getElementById('tenantDetailView');
    const tenantSlug = appContainer?.dataset?.tenantSlug || '';

    const payload = {
        name: document.getElementById('settingName').value,
        phone: document.getElementById('settingPhone').value,
        owner_name: document.getElementById('settingOwner').value,
        bot_username: document.getElementById('settingBot').value,
        monthly_fee: document.getElementById('settingFee').value,
        subscription_expires_at: document.getElementById('settingExpires').value,
        api_base_url: document.getElementById('settingApiUrl').value,
        api_secret_token: document.getElementById('settingToken').value,
        notes: document.getElementById('settingNotes').value,
    };

    try {
        const isSubdomain = window.location.hostname.startsWith('hub.');
        const url = isSubdomain 
            ? `/tenant/${tenantSlug}/api/settings/`
            : `/saas-hub/tenant/${tenantSlug}/api/settings/`;

        const resp = await fetch(url, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json', 
                'X-CSRFToken': getCookie('csrftoken') 
            },
            body: JSON.stringify(payload)
        });
        const data = await resp.json();
        if (data.status === 'ok') {
            showToast('Параметры заведения успешно сохранены!');
            setTimeout(() => window.location.reload(), 600);
        } else {
            alert('Ошибка сохранения: ' + (data.message || 'Сбой запроса'));
            if (btn) btn.disabled = false;
        }
    } catch (err) {
        alert('Сетевая ошибка: ' + err.message);
        if (btn) btn.disabled = false;
    }
}
