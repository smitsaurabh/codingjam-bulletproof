/**
 * Resume Tailor — Client Workbench Application Logic
 */

document.addEventListener('DOMContentLoaded', () => {
  // --- DOM Elements ---
  const form = document.getElementById('tailor-form');
  const resumeInput = document.getElementById('resume-input');
  const jobInput = document.getElementById('job-input');
  const resumeCounter = document.getElementById('resume-counter');
  const jobCounter = document.getElementById('job-counter');
  const charWarning = document.getElementById('char-warning');
  const submitBtn = document.getElementById('submit-btn');
  const submitBtnText = submitBtn.querySelector('.btn-text');
  const sampleBtn = document.getElementById('sample-btn');
  const clearBtn = document.getElementById('clear-btn');

  // Output Elements
  const emptyState = document.getElementById('empty-state');
  const loadingState = document.getElementById('loading-state');
  const bulletsList = document.getElementById('bullets-list');
  const roleTag = document.getElementById('role-tag');
  const countBadge = document.getElementById('count-badge');
  const copyAllBtn = document.getElementById('copy-all-btn');
  const errorBanner = document.getElementById('error-banner');
  const errorMessage = document.getElementById('error-message');
  const retryBtn = document.getElementById('retry-btn');
  const toast = document.getElementById('toast');

  let currentBullets = [];

  // --- Sample Data ---
  const SAMPLE_RESUME = `• Built backend notifications microservice using Go and Kafka to deliver event alerts to mobile users.
• Led cloud migration from legacy on-premises servers to AWS, reducing database query latencies.
• Collaborated with product managers and frontend teams to deliver core dashboard features on bi-weekly sprints.
• Conducted code reviews and established automated linting tests to improve engineering code quality.`;

  const SAMPLE_JOB = `Senior Staff Distributed Systems Engineer
Company: CloudScale Technologies

We are seeking a Senior Staff Engineer to design and scale our next-generation event streaming infrastructure.

Requirements:
- Deep expertise architecting high-throughput, low-latency distributed microservices (Go, Kafka, or gRPC).
- Experience leading cloud modernization and database performance tuning in AWS environments.
- Track record of mentoring senior engineers and championing automated CI/CD and engineering excellence.
- Strong cross-functional alignment skills with product management and platform stakeholders.`;

  // --- Helpers ---
  function updateCounters() {
    const resumeLen = resumeInput.value.length;
    const jobLen = jobInput.value.length;

    resumeCounter.textContent = `${resumeLen.toLocaleString()} chars`;
    jobCounter.textContent = `${jobLen.toLocaleString()} chars`;

    if (resumeLen > 6000 || jobLen > 6000) {
      charWarning.classList.remove('hidden');
      if (resumeLen > 6000) resumeCounter.classList.add('warning');
      if (jobLen > 6000) jobCounter.classList.add('warning');
    } else {
      charWarning.classList.add('hidden');
      resumeCounter.classList.remove('warning');
      jobCounter.classList.remove('warning');
    }
  }

  function showToast(message = 'Copied to clipboard!') {
    toast.textContent = message;
    toast.classList.remove('hidden');
    clearTimeout(window.__toastTimeout);
    window.__toastTimeout = setTimeout(() => {
      toast.classList.add('hidden');
    }, 2200);
  }

  async function copyText(text) {
    if (navigator.clipboard && window.isSecureContext) {
      try {
        await navigator.clipboard.writeText(text);
        return true;
      } catch (err) {
        console.warn('Navigator clipboard failed, falling back to execCommand:', err);
      }
    }
    // Fallback for non-https or older environments
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.left = '-9999px';
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    try {
      document.execCommand('copy');
      textArea.remove();
      return true;
    } catch (e) {
      textArea.remove();
      return false;
    }
  }

  function renderBullets(response) {
    currentBullets = response.bullets || [];

    // Update metadata header
    if (response.role_title_detected) {
      roleTag.textContent = response.role_title_detected;
      roleTag.classList.remove('hidden');
    } else {
      roleTag.classList.add('hidden');
    }

    countBadge.textContent = `${currentBullets.length} ${currentBullets.length === 1 ? 'Bullet' : 'Bullets'}`;
    countBadge.classList.remove('hidden');
    copyAllBtn.classList.remove('hidden');

    // Build bullet cards
    bulletsList.innerHTML = '';
    currentBullets.forEach((item, index) => {
      const card = document.createElement('article');
      card.className = 'bullet-card';

      card.innerHTML = `
        <div class="card-top">
          <div class="chip-group">
            <span class="skill-chip">🎯 ${escapeHtml(item.skill_tag)}</span>
            ${item.original_reference ? `<span class="ref-chip">Ref: ${escapeHtml(item.original_reference)}</span>` : ''}
          </div>
        </div>
        <p class="bullet-text">${escapeHtml(item.bullet)}</p>
        <div class="card-actions">
          <button type="button" class="btn-copy-card" data-index="${index}">
            📋 Copy Bullet
          </button>
        </div>
      `;

      // Copy individual bullet handler
      const copyBtn = card.querySelector('.btn-copy-card');
      copyBtn.addEventListener('click', async () => {
        const ok = await copyText(item.bullet);
        if (ok) {
          copyBtn.textContent = '✓ Copied!';
          copyBtn.classList.add('copied');
          setTimeout(() => {
            copyBtn.textContent = '📋 Copy Bullet';
            copyBtn.classList.remove('copied');
          }, 1800);
        }
      });

      bulletsList.appendChild(card);
    });

    // Reveal output
    emptyState.classList.add('hidden');
    loadingState.classList.add('hidden');
    bulletsList.classList.remove('hidden');
  }

  function escapeHtml(str) {
    if (!str) return '';
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  function setLoading(isLoading) {
    if (isLoading) {
      submitBtn.disabled = true;
      submitBtnText.textContent = 'Tailoring with Gemini...';
      emptyState.classList.add('hidden');
      bulletsList.classList.add('hidden');
      errorBanner.classList.add('hidden');
      loadingState.classList.remove('hidden');
    } else {
      submitBtn.disabled = false;
      submitBtnText.textContent = 'Tailor Bullets ⚡';
      loadingState.classList.add('hidden');
    }
  }

  function showError(msg) {
    errorMessage.textContent = msg;
    errorBanner.classList.remove('hidden');
    loadingState.classList.add('hidden');
  }

  // --- Actions ---
  async function handleTailor() {
    const resumeText = resumeInput.value.trim();
    const jobText = jobInput.value.trim();

    if (resumeText.length < 20) {
      showError('Please paste at least one full bullet point from your resume (min 20 characters).');
      resumeInput.focus();
      return;
    }

    if (jobText.length < 20) {
      showError('Please paste target job qualifications or responsibilities (min 20 characters).');
      jobInput.focus();
      return;
    }

    setLoading(true);

    try {
      const response = await fetch('/api/tailor', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          resume_text: resumeText,
          job_description: jobText,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Failed to tailor resume bullets.');
      }

      renderBullets(data);
    } catch (err) {
      console.error('Tailor API error:', err);
      showError(err.message || 'An unexpected error occurred while communicating with the AI server.');
      if (currentBullets.length === 0) {
        emptyState.classList.remove('hidden');
      }
    } finally {
      setLoading(false);
    }
  }

  // --- Event Listeners ---
  resumeInput.addEventListener('input', updateCounters);
  jobInput.addEventListener('input', updateCounters);

  form.addEventListener('submit', (e) => {
    e.preventDefault();
    handleTailor();
  });

  retryBtn.addEventListener('click', () => {
    errorBanner.classList.add('hidden');
    handleTailor();
  });

  // Global Keyboard Shortcut: Cmd/Ctrl + Enter
  document.addEventListener('keydown', (e) => {
    if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
      e.preventDefault();
      handleTailor();
    }
  });

  sampleBtn.addEventListener('click', () => {
    resumeInput.value = SAMPLE_RESUME;
    jobInput.value = SAMPLE_JOB;
    updateCounters();
    errorBanner.classList.add('hidden');
    showToast('Loaded sample resume & job posting!');
  });

  clearBtn.addEventListener('click', () => {
    resumeInput.value = '';
    jobInput.value = '';
    updateCounters();
    currentBullets = [];
    bulletsList.innerHTML = '';
    bulletsList.classList.add('hidden');
    roleTag.classList.add('hidden');
    countBadge.classList.add('hidden');
    copyAllBtn.classList.add('hidden');
    errorBanner.classList.add('hidden');
    emptyState.classList.remove('hidden');
  });

  copyAllBtn.addEventListener('click', async () => {
    if (!currentBullets || currentBullets.length === 0) return;
    const allText = currentBullets.map((b) => `• ${b.bullet}`).join('\n\n');
    const ok = await copyText(allText);
    if (ok) {
      showToast(`Copied all ${currentBullets.length} bullets to clipboard!`);
    }
  });

  // Initial setup
  updateCounters();
});
