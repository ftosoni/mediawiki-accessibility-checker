document.addEventListener('DOMContentLoaded', async () => {
    // State
    let mwProjects = [];
    let lastResults = null;
    let lastAuditedUrl = null;

    // Load projects
    try {
        const response = await fetch('/static/projects.json');
        mwProjects = await response.json();
    } catch (e) {
        console.error("Failed to load projects.json", e);
    }

    // Tab switching logic
    const tabs = document.querySelectorAll('.cdx-tabs__item');
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const container = tab.parentElement;
            const isFilter = container.classList.contains('results-filter');
            
            // Handle active state for tabs
            container.querySelectorAll('.cdx-tabs__item').forEach(t => t.classList.remove('cdx-tabs__item--active'));
            tab.classList.add('cdx-tabs__item--active');

            // Handle content visibility
            if (isFilter) {
                const filter = tab.getAttribute('data-filter');
                document.querySelectorAll('.filter-content').forEach(c => c.classList.remove('active'));
                document.getElementById(`${filter}-list`).classList.add('active');
            } else {
                const target = tab.getAttribute('data-tab');
                document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
                document.getElementById(target).classList.add('active');
            }
        });
    });

    // MediaWiki Project Lookup
    const projectInput = document.getElementById('mw_project_input');
    const projectMenu = document.getElementById('mw_project_menu');
    const projectUrlHidden = document.getElementById('mw_project_url');

    projectInput.addEventListener('input', () => {
        const query = projectInput.value.toLowerCase().trim();
        if (!query) {
            projectMenu.style.display = 'none';
            return;
        }

        const filtered = mwProjects.filter(p => 
            p.name.toLowerCase().includes(query) || 
            p.code.toLowerCase().includes(query) ||
            (p.aliases && p.aliases.some(a => a.toLowerCase().includes(query)))
        ).slice(0, 10);

        if (filtered.length > 0) {
            projectMenu.innerHTML = '';
            filtered.forEach(p => {
                const item = document.createElement('div');
                item.className = 'cdx-lookup__item';
                item.style.padding = '8px 12px';
                item.style.cursor = 'pointer';
                item.innerHTML = `
                    <div style="font-weight: bold;">${p.name}</div>
                    <div style="font-size: 0.8em; color: #72777d;">${p.url}</div>
                `;
                item.addEventListener('click', () => {
                    projectInput.value = p.name;
                    projectUrlHidden.value = p.url;
                    projectMenu.style.display = 'none';
                });
                projectMenu.appendChild(item);
            });
            projectMenu.style.display = 'block';
        } else {
            projectMenu.style.display = 'none';
        }
    });

    // Close menu on click outside
    document.addEventListener('click', (e) => {
        if (!projectInput.contains(e.target) && !projectMenu.contains(e.target)) {
            projectMenu.style.display = 'none';
        }
    });

    // Audit logic
    const auditButtons = document.querySelectorAll('.btn-run-audit');
    const loadingArea = document.getElementById('loading-area');
    const resultsArea = document.getElementById('results-area');

    async function runAudit(data) {
        const selectedGuideline = document.querySelector('input[name="guideline"]:checked').value;
        data.standard = selectedGuideline;

        loadingArea.style.display = 'flex';
        resultsArea.style.display = 'none';
        
        try {
            const response = await fetch('/api/check', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            if (!response.ok) {
                const err = await response.json();
                throw new Error(err.detail || 'Audit failed');
            }

            lastResults = await response.json();
            lastAuditedUrl = data.url || null;
            displayResults(lastResults, lastAuditedUrl);
        } catch (error) {
            alert(`Error: ${error.message}`);
        } finally {
            loadingArea.style.display = 'none';
        }
    }

    auditButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const activeTab = document.querySelector('.tab-content.active').id;
            
            if (activeTab === 'AC_by_mediawiki') {
                const projectUrl = projectUrlHidden.value;
                const title = document.getElementById('mw_title').value;
                if (!projectUrl || !title) return alert('Please select a project and enter a title');
                
                const baseUrl = projectUrl.endsWith('/wiki/') ? projectUrl : projectUrl + '/wiki/';
                const url = baseUrl + encodeURIComponent(title.replace(/ /g, '_'));
                runAudit({ url });
            } else if (activeTab === 'AC_by_uri') {
                const url = document.getElementById('checkuri').value;
                if (!url) return alert('Please enter a URL');
                runAudit({ url });
            } else if (activeTab === 'AC_by_paste') {
                const html = document.getElementById('checkpaste').value;
                if (!html) return alert('Please paste some HTML');
                runAudit({ html });
            }
        });
    });

    // Export logic
    const btnExport = document.getElementById('btn-export');
    btnExport.addEventListener('click', async () => {
        if (!lastResults) return;
        
        const format = document.getElementById('export-format').value;
        const originalText = btnExport.textContent;
        btnExport.disabled = true;
        btnExport.textContent = 'Generating...';

        try {
            const response = await fetch('/api/export', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ results: lastResults, format })
            });
            
            if (!response.ok) {
                const err = await response.json();
                throw new Error(err.detail || 'Export failed');
            }
            
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            
            // Filename construction
            let ext = format;
            if (format === 'wikitext') ext = 'txt';
            const timestamp = new Date().toISOString().split('T')[0];
            a.download = `accessibility_report_${timestamp}.${ext}`;
            
            document.body.appendChild(a);
            a.click();
            a.remove();
            window.URL.revokeObjectURL(url);
        } catch (error) {
            alert(`Export Error: ${error.message}`);
        } finally {
            btnExport.disabled = false;
            btnExport.textContent = originalText;
        }
    });

    function displayResults(results, baseUrl) {
        resultsArea.style.display = 'block';
        
        document.getElementById('count-violations').textContent = results.summary.violations;
        document.getElementById('count-incomplete').textContent = results.summary.incomplete;
        document.getElementById('count-passes').textContent = results.summary.passes;

        renderList('violations-list', results.violations, 'violation', baseUrl);
        renderList('incomplete-list', results.incomplete, 'incomplete', baseUrl);
        renderList('passes-list', results.passes, 'pass', baseUrl);
        
        resultsArea.scrollIntoView({ behavior: 'smooth' });
    }

    function renderList(containerId, items, type, baseUrl) {
        const container = document.getElementById(containerId);
        container.innerHTML = '';

        if (items.length === 0) {
            container.innerHTML = `<div class="cdx-message cdx-message--success">No items found in this category.</div>`;
            return;
        }

        items.forEach(item => {
            const card = document.createElement('div');
            card.className = `issue-card ${type}`;
            const impactClass = item.impact ? `impact-${item.impact}` : '';
            
            card.innerHTML = `
                <div class="issue-header">
                    <h3 class="issue-title">${escapeHtml(item.help)}</h3>
                    ${item.impact ? `<span class="issue-impact ${impactClass}">${escapeHtml(item.impact)}</span>` : ''}
                </div>
                <p class="issue-description">${escapeHtml(item.description)}</p>
                <div class="issue-meta">
                    <a href="${item.helpUrl}" target="_blank" class="cdx-button cdx-button--weight-quiet">Learn more</a>
                    <span class="cdx-button cdx-button--weight-quiet" style="font-size: 0.8em; color: #777;">${escapeHtml(item.id)}</span>
                </div>
                <div class="nodes-container">
                    ${item.nodes.map(node => {
                        let imgPreview = '';
                        const imgTagMatch = node.html.match(/<img[^>]+>/i);
                        
                        if (imgTagMatch) {
                            const imgTag = imgTagMatch[0];
                            let src = (imgTag.match(/src=["'](.*?)["']/i) || 
                                       imgTag.match(/data-src=["'](.*?)["']/i) || 
                                       imgTag.match(/srcset=["'](.*?)["']/i) || [])[1];
                            
                            if (src) {
                                src = src.split(',')[0].split(' ')[0].trim();
                                let resolvedSrc = src;
                                if (baseUrl) {
                                    try {
                                        resolvedSrc = new URL(src, baseUrl).href;
                                    } catch (e) {
                                        if (src.startsWith('//')) resolvedSrc = 'https:' + src;
                                    }
                                } else if (src.startsWith('//')) {
                                    resolvedSrc = 'https:' + src;
                                }
                                
                                imgPreview = `
                                    <div class="node-preview">
                                        <img src="${resolvedSrc}" 
                                             alt="Preview" 
                                             loading="lazy"
                                             referrerpolicy="no-referrer"
                                             style="max-width: 140px; max-height: 140px; border: 1px solid #eaecf0; border-radius: 2px; margin-bottom: 8px; display: block; background: #fff;" 
                                             onerror="this.parentElement.style.display='none';" />
                                    </div>`;
                            }
                        }
                        
                        const displayHtml = node.html.length > 200 ? node.html.substring(0, 200) + '...' : node.html;

                        return `
                        <div class="node-item">
                            <code class="node-selector">${escapeHtml(Array.isArray(node.target) ? node.target.join(' > ') : node.target)}</code>
                            ${imgPreview}
                            <pre class="node-html"><code>${escapeHtml(displayHtml)}</code></pre>
                            ${node.failureSummary ? `<div class="failure-summary"><strong>Fix:</strong> ${escapeHtml(node.failureSummary)}</div>` : ''}
                        </div>
                    `}).join('')}
                </div>
            `;
            container.appendChild(card);
        });
    }

    function escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
});
