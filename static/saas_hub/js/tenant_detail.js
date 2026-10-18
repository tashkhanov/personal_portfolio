// SaaS Command Center - Tenant Detail Page Logic
// Dedicated modular script (separated from HTML template)

function switchDetailTab(tabId, btnEl) {
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.detail-tab-pane').forEach(pane => pane.classList.remove('active'));

    const targetPane = document.getElementById('tab-' + tabId);
    if (targetPane) targetPane.classList.add('active');

    const activeBtn = btnEl || document.querySelector(`.tab-btn[data-tab="${tabId}"]`);
    if (activeBtn) activeBtn.classList.add('active');

    if (window.lucide) {
        window.lucide.createIcons();
    }
}

let isTierSwitching = false;

// Интерактивное переключение тарифа супер-админом с подтверждением
async function selectTenantTier(newTier) {
    if (isTierSwitching) return;
    const appContainer = document.getElementById('tenantDetailView');
    const tenantSlug = appContainer?.dataset?.tenantSlug || '';
    if (!tenantSlug) return;

    const targetCard = document.getElementById(`tier-card-${newTier}`);
    if (targetCard && targetCard.classList.contains('active')) {
        return; // Тариф уже активен
    }

    const tierLabels = {
        'start': 'START (500 000 сум / мес)',
        'pro': 'PRO BUSINESS (1 190 000 сум / мес)',
        'enterprise': 'ENTERPRISE (2 490 000 сум / мес)'
    };
    const tierName = tierLabels[newTier] || newTier.toUpperCase();

    const confirmed = confirm(
        `Подтвердите смену тарифа:\n\nВы действительно хотите переключить тариф заведения на ${tierName}?\n\n• Лимиты мастеров и филиалов обновятся автоматически\n• Сумма абонплаты будет пересчитана`
    );
    if (!confirmed) {
        return;
    }

    // Мгновенная визуальная реакция на карточках
    document.querySelectorAll('.tier-card').forEach(card => card.classList.remove('active'));
    if (targetCard) targetCard.classList.add('active');

    const syncStatusText = document.getElementById('tier-sync-status-text');
    if (syncStatusText) syncStatusText.innerText = 'Синхронизация с ботом...';

    isTierSwitching = true;
    try {
        const isSubdomain = window.location.hostname.startsWith('hub.');
        const url = isSubdomain 
            ? `/tenant/${tenantSlug}/api/set-tier/`
            : `/saas-hub/tenant/${tenantSlug}/api/set-tier/`;

        const resp = await fetch(url, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json', 
                'X-CSRFToken': getCookie('csrftoken') 
            },
            body: JSON.stringify({ tier: newTier })
        });

        const data = await resp.json();
        if (data.status === 'ok') {
            // Обновление бейджей в Hero и переключателе
            const heroBadge = document.getElementById('tenant-tier-badge');
            if (heroBadge) {
                heroBadge.className = `badge ${data.tier_badge_class}`;
                heroBadge.innerText = data.tier_label_short;
            }

            const currentChip = document.getElementById('current-tier-chip');
            if (currentChip) {
                currentChip.className = `badge ${data.tier_badge_class}`;
                currentChip.innerText = data.tier_label_short;
            }

            // Обновление отображения абонплаты
            const heroFeeDisplay = document.getElementById('hero-tariff-fee-display');
            if (heroFeeDisplay) {
                heroFeeDisplay.innerHTML = `${data.formatted_monthly_fee} <span class="fee-period">/ мес</span>`;
            }

            // Обновление полей во вкладке настроек
            const settingFee = document.getElementById('settingFee');
            if (settingFee) settingFee.value = data.monthly_fee;

            const settingTier = document.getElementById('settingTier');
            if (settingTier) settingTier.value = data.tier;

            if (syncStatusText) {
                const now = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
                syncStatusText.innerText = `Синхронизировано (${now})`;
            }

            showToast(`Тариф успешно изменен на ${data.tier_display}!`, 'success');
        } else {
            alert('Ошибка переключения тарифа: ' + (data.message || 'Сбой запроса'));
            if (syncStatusText) syncStatusText.innerText = 'Ошибка синхронизации';
        }
    } catch (err) {
        alert('Сетевая ошибка: ' + err.message);
        if (syncStatusText) syncStatusText.innerText = 'Ошибка сети';
    } finally {
        isTierSwitching = false;
        if (window.lucide) window.lucide.createIcons();
    }
}

function handleSettingTierSelect(selectEl) {
    if (!selectEl) return;
    const selectedOpt = selectEl.options ? selectEl.options[selectEl.selectedIndex] : null;
    const fee = selectedOpt ? selectedOpt.getAttribute('data-fee') : null;
    if (fee) {
        const feeInput = document.getElementById('settingFee');
        if (feeInput) feeInput.value = fee;
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
        tier: document.getElementById('settingTier')?.value || 'PRO',
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
