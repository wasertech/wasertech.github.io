document.addEventListener('DOMContentLoaded', () => {
    const app = document.getElementById('app');
    let currentData;
    let currentLang = 'en';

    // Helper: Format large numbers (1.2K)
    const formatStars = (count) => {
        if (count >= 1000) return (count / 1000).toFixed(1) + 'K';
        return count.toString();
    };

    // Helper: Parse markdown-like links [text](url)
    const parseMarkdown = (text) => {
        if (!text) return '';
        return text
            .replace(/- /g, '') // Remove list bullets for cleaner look
            .replace(/\n/g, '<br>')
            .replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank">$1</a>');
    };

    const getSocialLinksHtml = (contact, whitelist = null) => {
        let links = [
            { key: 'github', icon: 'fab fa-github', title: 'GitHub' },
            { key: 'gitlab', icon: 'fab fa-gitlab', title: 'GitLab' },
            { key: 'linkedin', icon: 'fab fa-linkedin', title: 'LinkedIn' },
            { key: 'docker', icon: 'fab fa-docker', title: 'Docker Hub' },
            { key: 'youtube', icon: 'fab fa-youtube', title: 'YouTube' },
            { key: 'discourse', icon: 'fab fa-firefox', title: 'Discourse' }, // Using firefox icon for mozilla discourse as in old index
            { key: 'matrix', icon: 'fas fa-comments', title: 'Matrix' }
        ];

        if (whitelist) {
            links = links.filter(l => whitelist.includes(l.key));
        }

        return `
            <div class="social-links">
                ${links.map(l => contact[l.key] ? `
                    <a href="${contact[l.key]}" class="social-icon" target="_blank" title="${l.title}">
                        <i class="${l.icon}"></i>
                    </a>
                ` : '').join('')}
            </div>
        `;
    };

    const renderApp = (lang) => {
        if (!currentData) return;
        const d = currentData;
        const s = d.sections;

        // Data Helpers
        const getSkillName = (skill) => skill[lang] || skill.en; // Fallback
        const getExpTitle = (exp) => exp[lang]?.title || '';
        const getExpCompany = (exp) => exp[lang]?.company || '';
        const getExpDetails = (exp) => parseMarkdown(exp[lang]?.details || '');

        // --- SIDEBAR ---
        const sidebarHtml = `
            <aside class="sidebar">
                <div class="profile-section">
                    <img src="static/images/portrait.webp" alt="Profile" class="profile-image">
                    <h1 class="profile-name">Danny Waser</h1>
                    <p class="profile-tagline">AI Engineer & Full Stack Dev</p>
                    ${getSocialLinksHtml(d.contact, ['github', 'gitlab', 'linkedin'])}
                </div>

                <nav class="nav-menu">
                    <a href="#about" class="nav-link"><i class="fas fa-user-circle"></i> ${s.profile[lang]}</a>
                    <a href="#experience" class="nav-link"><i class="fas fa-briefcase"></i> ${s.professional_experience[lang]}</a>
                    <a href="#contributions" class="nav-link"><i class="fas fa-code-branch"></i> ${s.contributions[lang]}</a>
                    <a href="#portfolio" class="nav-link"><i class="fas fa-laptop-code"></i> ${s.portfolio[lang]}</a>
                    <a href="#media" class="nav-link"><i class="fas fa-photo-video"></i> ${s.media[lang]}</a>
                </nav>

                <div class="lang-switch-container">
                    <button class="lang-btn ${lang === 'en' ? 'active' : ''}" data-lang="en">EN</button>
                    <button class="lang-btn ${lang === 'fr' ? 'active' : ''}" data-lang="fr">FR</button>
                </div>
                
                <div class="qr-container">
                    <img src="static/images/qrc.png" alt="Contact QR Code" title="Scan to save contact">
                    <div class="qr-label">${s.scan_contact[lang]}</div>
                </div>
                
                <div style="margin-top: 2rem; text-align: center;">
                    <a href="static/CV_${lang.toUpperCase()}.pdf" class="cta-button" download>
                        <i class="fas fa-file-download"></i> PDF
                    </a>
                </div>
            </aside>
        `;

        // --- MAIN CONTENT ---
        // 1. About / Profile
        const aboutSection = `
            <section id="about">
                <h2 class="section-title">${s.profile[lang]}</h2>
                <div class="card">
                    <p class="lead">${d.profile[lang].content}</p>
                    <div style="margin-top: 2rem;" class="grid-2">
                         <div>
                            <h3>${s.contact[lang]}</h3>
                            <ul style="margin-top: 1rem; color: var(--text-secondary);">
                                <li style="margin-bottom: 0.5rem;"><i class="fas fa-map-marker-alt" style="width:20px"></i> ${d.contact.address}</li>
                                <li style="margin-bottom: 0.5rem;"><i class="fas fa-envelope" style="width:20px"></i> <a href="mailto:${d.contact.email}">${d.contact.email}</a></li>
                                <li><i class="fas fa-globe" style="width:20px"></i> <a href="${d.contact.website}" target="_blank">waser.tech</a></li>
                            </ul>
                            ${getSocialLinksHtml(d.contact)}
                         </div>
                         <div>
                            <h3>${s.technical_skills[lang]}</h3>
                            <div class="skills-container" style="margin-top: 1rem;">
                                ${d.skills.map(skill => `<span class="skill-tag">${getSkillName(skill)}</span>`).join('')}
                            </div>
                         </div>
                    </div>
                </div>
            </section>
        `;

        // 2. Experience & Education
        // Sort experiences
        const sortedExp = d.experiences.sort((a, b) => {
            const getYear = (str) => {
                const match = str.match(/\d{4}/);
                return match ? parseInt(match[0]) : 0;
            };
            return getYear(b.date) - getYear(a.date);
        });

        const expSection = `
            <section id="experience">
                <h2 class="section-title">${s.professional_experience[lang]}</h2>
                <div class="card">
                    ${sortedExp.map(exp => `
                        <div class="timeline-item">
                            <div class="timeline-date">${exp.date}</div>
                            <h3 class="timeline-title">${getExpTitle(exp)}</h3>
                            <div class="timeline-company">${getExpCompany(exp)}</div>
                            <div>${getExpDetails(exp)}</div>
                        </div>
                    `).join('')}
                    
                    <h3 style="margin-top: 3rem; margin-bottom: 1.5rem;">${s.education[lang]}</h3>
                    ${(d.education || []).map(edu => `
                        <div class="timeline-item">
                            <div class="timeline-date">${edu.date}</div>
                            <h3 class="timeline-title">${edu[lang].title}</h3>
                            <div class="timeline-company">${edu[lang].institution}</div>
                            <small>${edu[lang].location}</small>
                        </div>
                    `).join('')}
                </div>
            </section>
        `;

        // 3. OSS Contributions
        const renderContribs = () => {
            const github = d.contributions?.github || [];
            const manual = d.contributions?.manual || [];
            if (github.length === 0 && manual.length === 0) return '';

            return `
                <section id="contributions">
                    <h2 class="section-title">${s.contributions[lang]}</h2>
                    <div class="grid-2">
                        ${github.map(repo => `
                            <article class="card">
                                <div class="contrib-header">
                                    <a href="${repo.url}" target="_blank"><strong>${repo.project}</strong></a>
                                    <span class="contrib-stars"><i class="fas fa-star"></i> ${formatStars(repo.stars)}</span>
                                </div>
                                <p class="contrib-stats">
                                    ${repo.pr_count} PR${repo.pr_count > 1 ? 's' : ''} merged
                                </p>
                                <ul class="pr-list">
                                    ${repo.prs.slice(0, 3).map(pr => `<li><a href="${pr.url}" target="_blank">${pr.title}</a></li>`).join('')}
                                </ul>
                            </article>
                        `).join('')}
                        ${manual.map(c => `
                            <article class="card">
                                <div class="contrib-header">
                                    <a href="${c.url}" target="_blank"><strong>${c.project}</strong></a>
                                    <span class="contrib-stars"><i class="fas fa-check"></i> Contrib</span>
                                </div>
                                <p><strong>${c[lang].title}</strong></p>
                                <p style="font-size: 0.9rem; color: var(--text-secondary);">${c[lang].details}</p>
                            </article>
                        `).join('')}
                    </div>
                </section>
            `;
        };

        // 4. Portfolio
        const renderPortfolio = () => {
            if (!d.portfolio || d.portfolio.length === 0) return '';
            return `
                <section id="portfolio">
                    <h2 class="section-title">${s.portfolio[lang]}</h2>
                    <div class="grid-3">
                        ${d.portfolio.map(p => `
                            <div class="card project-card">
                                <a href="${p.url}" target="_blank">
                                    <img src="${p.image}" alt="${p.name}" loading="lazy">
                                    <span class="project-category">${p.category}</span>
                                    <h4>${p.name}</h4>
                                </a>
                            </div>
                        `).join('')}
                    </div>
                </section>
            `;
        };

        // 5. Media/Articles
        const renderMedia = () => {
            const media = d.media || [];
            if (media.length === 0) return '';
            return `
                <section id="media">
                    <h2 class="section-title">${s.media[lang]}</h2>
                    <div class="grid-2">
                        ${media.map(m => `
                            <div class="card" style="padding: 0; overflow: hidden;">
                                <div class="video-container" style="position: relative; padding-bottom: 56.25%; height: 0;">
                                    <iframe src="${m.embed_url}" 
                                        style="position: absolute; top:0; left:0; width:100%; height:100%; border:none;" 
                                        allowfullscreen></iframe>
                                </div>
                                <div style="padding: 1rem;">
                                    <h4>${m.title}</h4>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </section>
             `;
        };

        // Assemble Layout
        const mainHtml = `
            <main class="main-content">
                ${aboutSection}
                ${expSection}
                ${renderContribs()}
                ${renderPortfolio()}
                ${renderMedia()}
                
                <footer style="margin-top: 5rem; text-align: center; color: var(--text-secondary); font-size: 0.9rem;">
                    <p>&copy; ${new Date().getFullYear()} Danny Waser. Built with 🧠 by Antigravity.</p>
                </footer>
            </main>
        `;

        app.innerHTML = sidebarHtml + mainHtml;

        // Re-attach listeners
        document.querySelectorAll('.lang-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                currentLang = e.target.dataset.lang;
                renderApp(currentLang);
            });
        });

        // Active link highlighting
        const navLinks = document.querySelectorAll('.nav-link');
        const sectionsTags = document.querySelectorAll('section');

        window.addEventListener('scroll', () => {
            let current = '';
            sectionsTags.forEach(section => {
                const sectionTop = section.offsetTop;
                if (window.scrollY >= sectionTop - 200) {
                    current = section.getAttribute('id');
                }
            });
            navLinks.forEach(li => {
                li.classList.remove('active');
                if (li.getAttribute('href').includes(current)) {
                    li.classList.add('active');
                }
            });
        });
    };

    // Load Data
    fetch('static/cv_data.json')
        .then(res => res.json())
        .then(data => {
            currentData = data;
            renderApp(currentLang);
        });
});