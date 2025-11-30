document.addEventListener('DOMContentLoaded', () => {
    const cvContainer = document.getElementById('cv-container');
    const downloadCvButton = document.getElementById('download-cv');
    const mainNav = document.getElementById('main-nav');
    let currentData;
    let currentLang = 'en'; // Default language

    const updateDownloadLink = (lang) => {
        downloadCvButton.href = `static/CV_${lang.toUpperCase()}.pdf`;
    };

    const renderCV = (lang) => {
        if (!currentData) return;

        const sections = currentData.sections;
        const profile = currentData.profile;
        const contact = currentData.contact;
        const skills = currentData.skills.map(skill => skill[lang]);
        const languages = currentData.languages.map(l => ({ name: l[lang], level: l.level }));
        const interests = currentData.interests.map(interest => interest[lang]);
        const experiences = currentData.experiences.sort((a, b) => {
            const dateA = new Date(a.date.split(' - ')[0].replace(/(\w{3})\./, '$1')); // Handle "Jan."
            const dateB = new Date(b.date.split(' - ')[0].replace(/(\w{3})\./, '$1')); // Handle "Jan."
            return dateB - dateA;
        });
        const certifications = currentData.certifications.sort((a, b) => {
            const dateA = new Date(a.start_date.replace(/(\w{3})\./, '$1'));
            const dateB = new Date(b.start_date.replace(/(\w{3})\./, '$1'));
            return dateB - dateA;
        });


        let navHtml = '<ul>';
        for (const key in sections) {
            navHtml += `<li><a href="#${key}">${sections[key][lang]}</a></li>`;
        }
        navHtml += '</ul>';
        mainNav.innerHTML = navHtml;

        let html = `
            <div class="grid">
                <div class="left-column">
                    <section id="profile">
                        <img src="static/images/portrait.webp" alt="Danny Waser" class="portrait">
                    </section>
                    <section>
                        <h2>${sections.profile[lang].toUpperCase()}</h2>
                        <p>${profile[lang].content}</p>
                    </section>
                    <section id="contact">
                        <h2>${sections.contact[lang].toUpperCase()}</h2>
                        <p>
                            <i class="fas fa-map-marker-alt"></i> ${contact.address}<br>
                            <i class="fas fa-phone"></i> ${contact.phone}<br>
                            <i class="fas fa-envelope"></i> <a href="mailto:${contact.email}">${contact.email}</a><br>
                            <i class="fas fa-globe"></i> <a href="${contact.website}" target="_blank">${contact.website}</a><br>
                            <i class="fab fa-github"></i> <a href="${contact.github}" target="_blank">${contact.github}</a><br>
                            <i class="fab fa-gitlab"></i> <a href="${contact.gitlab}" target="_blank">${contact.gitlab}</a><br>
                            <i class="fab fa-linkedin"></i> <a href="${contact.linkedin}" target="_blank">${contact.linkedin}</a>
                        </p>
                    </section>
                    <section id="technical_skills">
                        <h2>${sections.technical_skills[lang].toUpperCase()}</h2>
                        <p>${skills.join(', ')}</p>
                    </section>
                    <section id="languages">
                        <h2>${sections.languages[lang].toUpperCase()}</h2>
                        <ul>
                            ${languages.map(l => `<li>${l.name} (${l.level})</li>`).join('')}
                        </ul>
                    </section>
                    <section id="personal_interests">
                        <h2>${sections.personal_interests[lang].toUpperCase()}</h2>
                        <p>${interests.join(', ')}</p>
                    </section>
                </div>
                <div class="right-column">
                    <section id="professional_experience">
                        <h2>${sections.professional_experience[lang].toUpperCase()}</h2>
                        ${experiences.map(exp => `
                            <article>
                                <h3>${exp[lang].title}</h3>
                                <p><em>${exp[lang].company} | ${exp.date}</em></p>
                                <div>${exp[lang].details.replace(/- /g, '• ').replace(/\n/g, '<br>')}</div>
                            </article>
                        `).join('')}
                    </section>
                    <section id="certification">
                        <h2>${sections.certification[lang].toUpperCase()}</h2>
                        ${certifications.map(cert => `
                            <article>
                                <h3>${cert[lang].title}</h3>
                                <p><em>${cert[lang].issuer} | ${cert.start_date} - ${cert.end_date}</em></p>
                                <a href="${cert.image}" target="_blank" class="button">View Certificate</a>
                            </article>
                        `).join('')}
                    </section>
                </div>
            </div>
        `;
        cvContainer.innerHTML = html;
        updateDownloadLink(lang);
    };

    const loadData = () => {
        fetch('static/cv_data.json')
            .then(response => response.json())
            .then(data => {
                currentData = data;
                renderCV(currentLang);
            });
    };

    document.querySelectorAll('.lang-switch').forEach(el => {
        el.addEventListener('click', (e) => {
            e.preventDefault();
            currentLang = e.target.dataset.lang;
            renderCV(currentLang);
        });
    });

    loadData();
});