// mobile menu
const mt = document.getElementById('mtog');
const mn = document.getElementById('mnav');
if (mt && mn) {
    mt.addEventListener('click', () => { mt.classList.toggle('on'); mn.classList.toggle('on'); });
    mn.querySelectorAll('a').forEach(a => a.addEventListener('click', () => { mt.classList.remove('on'); mn.classList.remove('on'); }));
}

// theme
const themeBtn = document.getElementById('themeToggle');
if (themeBtn) {
    themeBtn.addEventListener('click', () => {
        document.documentElement.classList.toggle('dark-theme');
        const isDark = document.documentElement.classList.contains('dark-theme');
        localStorage.setItem('theme', isDark ? 'dark' : 'light');
    });
}

// scroll events
window.addEventListener('scroll', () => {
    const s = window.scrollY;
    const m = document.documentElement.scrollHeight - window.innerHeight;
    const progress = document.getElementById('progress');
    if (progress) progress.style.width = (s / m * 100) + '%';

    const fab = document.getElementById('chatFab');
    if (fab) {
        if (s > 400) {
            fab.classList.add('visible');
        } else {
            if (!fab.classList.contains('open')) {
                fab.classList.remove('visible');
            }
        }
    }
});

// observer
const ro = new IntersectionObserver(entries => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('on');
            entry.target.querySelectorAll('.counter').forEach(counter => {
                if (counter.dataset.animated) return;
                counter.dataset.animated = '1';
                const targetStr = counter.dataset.target;
                const target = parseFloat(targetStr);
                const suffix = counter.dataset.suffix || '';
                const hasDecimal = targetStr.includes('.');
                const duration = 2000;
                const start = performance.now();

                function animate(now) {
                    const elapsed = now - start;
                    const progress = Math.min(elapsed / duration, 1);
                    const eased = 1 - Math.pow(1 - progress, 3);
                    let current = target * eased;

                    if (hasDecimal) {
                        counter.textContent = current.toFixed(1) + suffix;
                    } else {
                        counter.textContent = Math.round(current) + suffix;
                    }

                    if (progress < 1) requestAnimationFrame(animate);
                }
                requestAnimationFrame(animate);
            });
        }
    });
}, { threshold: 0.15 });

// modal
window.openProjectModal = function (id) {
    document.getElementById('modal-' + id).classList.add('active');
    document.body.style.overflow = 'hidden';

    const swiperEl = document.querySelector('.modal-swiper-' + id);
    if (swiperEl && !swiperEl.swiper) {
        new Swiper(swiperEl, {

            pagination: {
                el: swiperEl.querySelector('.swiper-pagination'),
                type: 'fraction',
            },
            navigation: {
                nextEl: swiperEl.querySelector('.swiper-button-next'),
                prevEl: swiperEl.querySelector('.swiper-button-prev'),
            },
            
            grabCursor: true,
            spaceBetween: 30,
            loop: false
        });
    }
};

window.closeProjectModal = function (id) {
    document.getElementById('modal-' + id).classList.remove('active');
    document.body.style.overflow = '';
};

document.addEventListener('click', function (e) {
    if (e.target.classList.contains('project-modal')) {
        e.target.classList.remove('active');
        document.body.style.overflow = '';
    }
});


// init
function initPage() {
    // smooth scroll
    document.querySelectorAll('a[href^="#"]').forEach(a => {
        a.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) target.scrollIntoView({ behavior: 'smooth' });
        });
    });

    // observer bind
    document.querySelectorAll('.reveal, .stats, .prj, .svc, .card').forEach(el => ro.observe(el));

    // filter
    document.querySelectorAll('.filter').forEach(f => {
        f.addEventListener('click', (e) => {
            e.preventDefault();
            document.querySelectorAll('.filter').forEach(b => b.classList.remove('on'));
            f.classList.add('on');
            const cat = f.dataset.filter;
            document.querySelectorAll('.card').forEach(c => {
                if (cat === 'all' || c.dataset.category === cat) {
                    c.style.display = '';
                    setTimeout(() => {
                        c.style.opacity = '1';
                        c.style.transform = 'translateY(0)';
                    }, 50);
                } else {
                    c.style.opacity = '0';
                    c.style.transform = 'translateY(15px)';
                    setTimeout(() => c.style.display = 'none', 300);
                }
            });
        });
    });

    // detail
    if (typeof PROJECTS_DATA !== 'undefined') {
        const urlParams = new URLSearchParams(window.location.search);
        const projectId = urlParams.get('id') || '1';
        const p = PROJECTS_DATA[projectId] || PROJECTS_DATA[1];

        if (p) {
            const fields = {
                pTitle: p.t, bcTitle: p.t, pCat: p.cat, pDesc: p.d, pLongDesc: p.ld,
                pYear: p.y, pCatName: p.cn, pStatus: p.s
            };

            Object.entries(fields).forEach(([id, val]) => {
                const el = document.getElementById(id);
                if (el) el.textContent = val;
            });

            const pImg = document.getElementById('pImg');
            if (pImg) { pImg.textContent = p.ico; pImg.style.background = p.grad; }

            const pTags = document.getElementById('pTags');
            if (pTags) pTags.innerHTML = p.tags.map(t => `<span class="tech-tag">${t}</span>`).join('');
            document.title = p.t + ' | Khan';
        }
    }

    // animations
    if (typeof gsap !== 'undefined' && typeof ScrollTrigger !== 'undefined' && window.innerWidth > 768) {
        ScrollTrigger.getAll().forEach(t => t.kill());
        gsap.registerPlugin(ScrollTrigger);

        const pinSection = document.querySelector('.gsap-pin-section');
        if (pinSection) {
            const panels = gsap.utils.toArray('.geo-panel');
            const contentWrap = document.querySelector('.services-content-wrap');
            const fadeElements = gsap.utils.toArray('.gsap-fade');
            const svcs = gsap.utils.toArray('.gsap-svc');

            let tl = gsap.timeline({
                scrollTrigger: {
                    trigger: pinSection,
                    start: "top 75%",
                }
            });

            tl.to(panels, { x: "0%", duration: 0.8, stagger: 0.1, ease: "power2.out" });
            tl.to(contentWrap, { opacity: 1, duration: 0.1 }, "-=0.2");
            tl.fromTo(fadeElements, { y: 30, opacity: 0 }, { opacity: 1, y: 0, duration: 0.5, stagger: 0.1, ease: "power2.out" }, "-=0.1");
            tl.fromTo(svcs, { y: 30, opacity: 0 }, {
                opacity: 1, y: 0, duration: 0.5, stagger: 0.1, ease: "power2.out",
                onComplete: function () { gsap.set(svcs, { clearProps: "transform" }); }
            }, "-=0.2");
        }
    }

    // icons
    if (typeof lucide !== 'undefined') lucide.createIcons();

    // reviews
    document.querySelectorAll('.rev').forEach(rev => {
        const text = rev.querySelector('.rev-text');
        const btn = rev.querySelector('.read-more-btn');
        if (text && btn) {
            if (text.scrollHeight > text.clientHeight) {
                btn.style.display = 'block';
            }
        }
    });

    // hover
    document.querySelectorAll('.prj, .svc, .rev, .card').forEach(card => {
        card.addEventListener('mouseenter', function () {
            this.style.transition = 'transform 0.1s ease-out';
        });
        card.addEventListener('mousemove', function (e) {
            const rect = this.getBoundingClientRect();
            const x = (e.clientX - rect.left) / rect.width - 0.5;
            const y = (e.clientY - rect.top) / rect.height - 0.5;
            this.style.transform = `perspective(1000px) rotateY(${x * 6}deg) rotateX(${-y * 6}deg)`;
        });
        card.addEventListener('mouseleave', function () {
            this.style.transition = 'transform 0.5s cubic-bezier(0.2, 0.8, 0.2, 1)';
            this.style.transform = '';
            setTimeout(() => { this.style.transition = ''; }, 500);
        });
    });

    // contact
    const contactForm = document.getElementById('contactForm');
    if (contactForm) {
        contactForm.addEventListener('submit', async function (e) {
            e.preventDefault();
            const form = this;
            const resultDiv = document.getElementById('formResult');
            const btn = form.querySelector('button[type="submit"]');

            btn.disabled = true;
            btn.textContent = 'Отправка...';

            try {
                const formData = new FormData(form);
                const res = await fetch("/contact/submit/", {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                });
                const data = await res.json();

                resultDiv.style.display = 'block';
                if (data.status === 'ok') {
                    resultDiv.style.color = '#4CAF50';
                    resultDiv.textContent = data.message;
                    form.reset();
                } else {
                    resultDiv.style.color = '#f44336';
                    resultDiv.textContent = data.message;
                }
            } catch (err) {
                resultDiv.style.display = 'block';
                resultDiv.style.color = '#f44336';
                resultDiv.textContent = 'Ошибка соединения. Попробуйте позже.';
            } finally {
                btn.disabled = false;
                btn.textContent = 'Отправить';
                setTimeout(() => resultDiv.style.display = 'none', 5000);
            }
        });
    }
}

document.addEventListener('DOMContentLoaded', () => {
    initPage();
    if (typeof Swup !== 'undefined') {
        const swup = new Swup({
            containers: ["#swup"],
            plugins: typeof SwupHeadPlugin !== 'undefined' ? [new SwupHeadPlugin()] : []
        });
        swup.hooks.on('page:view', initPage);
    }
});

// copy protection
document.addEventListener('selectstart', e => e.preventDefault());
document.addEventListener('dragstart', e => e.preventDefault());

// devtools block
document.addEventListener('keydown', (e) => {
    // unlock
    if (e.ctrlKey && e.altKey && e.code === 'KeyK') {
        const isUnlocked = localStorage.getItem('devUnlocked');
        if (isUnlocked) {
            localStorage.removeItem('devUnlocked');
            alert('🔒 DevTools заблокированы');
        } else {
            localStorage.setItem('devUnlocked', '1');
            alert('🔓 DevTools разблокированы (Секретный режим Khan)');
        }
    }

    if (localStorage.getItem('devUnlocked') === '1') {
        return;
    }

    if (e.keyCode === 123 || e.key === 'F12') {
        e.preventDefault();
    }
    if (e.ctrlKey && e.shiftKey && (e.code === 'KeyI' || e.code === 'KeyJ' || e.code === 'KeyC')) {
        e.preventDefault();
    }
    if (e.ctrlKey && e.code === 'KeyU') {
        e.preventDefault();
    }
    if ((e.ctrlKey || e.metaKey) && (e.code === 'KeyS' || e.code === 'KeyP')) {
        e.preventDefault();
    }
});

// media block
function protectMedia() {
    document.querySelectorAll('img, video').forEach(media => {
        media.setAttribute('draggable', 'false');
        if (media.tagName.toLowerCase() === 'video') {
            media.setAttribute('controlsList', 'nodownload');
        }
    });
}
protectMedia();
document.addEventListener('swup:contentReplaced', protectMedia);



document.addEventListener('DOMContentLoaded', () => {
    if ('modelContext' in navigator) {
        try {
            const mcpController = new AbortController();
            navigator.modelContext.registerTool({
                name: "get_portfolio_info",
                description: "Retrieves information about Ibrohim Asatkhanov's projects and services",
                inputSchema: {
                    type: "object",
                    properties: {
                        query: { type: "string", description: "What to search for" }
                    }
                },
                execute: async (params) => {
                    return { status: "success", info: "To view projects, navigate to the Projects section." };
                }
            }, { signal: mcpController.signal });
            console.log("WebMCP tool 'get_portfolio_info' registered successfully.");
        } catch (e) {
            console.error("Failed to register WebMCP tool:", e);
        }
    }
});
