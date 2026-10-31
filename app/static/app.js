/**
 * TrustLens AI - Client-side Interactive Application
 * Manages input validation, demo samples, asynchronous API pipeline execution,
 * dynamic results rendering, and Markdown export.
 */

document.addEventListener("DOMContentLoaded", () => {
  // Elements
  const tabFile = document.getElementById("tab-file");
  const tabText = document.getElementById("tab-text");
  const panelFile = document.getElementById("panel-file");
  const panelText = document.getElementById("panel-text");
  const dropZone = document.getElementById("drop-zone");
  const fileInput = document.getElementById("file-input");
  const selectedFileBadge = document.getElementById("selected-file-badge");
  const selectedFileName = document.getElementById("selected-file-name");
  const clearFileBtn = document.getElementById("clear-file-btn");
  const textInput = document.getElementById("text-input");
  const charCount = document.getElementById("char-count");
  const clearTextBtn = document.getElementById("clear-text-btn");
  const analyzeForm = document.getElementById("analyze-form");
  const analyzeBtn = document.getElementById("analyze-btn");
  const analyzeSpinner = document.getElementById("analyze-spinner");
  const analyzeBtnText = document.getElementById("analyze-btn-text");

  const processingCard = document.getElementById("processing-card");
  const resultsDashboard = document.getElementById("results-dashboard");
  const errorCard = document.getElementById("error-card");
  const errorTitle = document.getElementById("error-title");
  const errorMessage = document.getElementById("error-message");
  const dismissErrorBtn = document.getElementById("dismiss-error-btn");

  const healthPill = document.getElementById("service-health-pill");
  const healthStatusText = document.getElementById("health-status-text");
  const activeModelText = document.getElementById("active-model-text");
  const sampleButtonsContainer = document.getElementById("sample-buttons-container");

  const exportMdBtn = document.getElementById("export-md-btn");
  const printReportBtn = document.getElementById("print-report-btn");

  // State
  let currentAnalysis = null;
  let cachedSamples = [];
  let currentFile = null;

  // 1. Check Service Health
  async function checkHealth() {
    try {
      const res = await fetch("/api/health");
      if (!res.ok) throw new Error("Health check failed");
      const data = await res.json();
      healthStatusText.textContent = "Service Ready";
      activeModelText.textContent = `${data.model_configured} ${data.has_api_key ? "" : "(Demo Mode)"}`;
    } catch (err) {
      healthStatusText.textContent = "Offline";
      healthPill.style.borderColor = "rgba(239, 68, 68, 0.4)";
    }
  }
  checkHealth();

  // 2. Load Demo Samples
  async function loadSamples() {
    try {
      const res = await fetch("/api/samples");
      if (!res.ok) return;
      cachedSamples = await res.json();
    } catch (err) {
      console.warn("Could not load samples:", err);
    }
  }
  loadSamples();

  // Sample Buttons Handler
  sampleButtonsContainer.addEventListener("click", (e) => {
    const btn = e.target.closest(".sample-btn");
    if (!btn) return;
    const sampleId = btn.getAttribute("data-sample-id");
    const sample = cachedSamples.find((s) => s.id === sampleId);
    if (!sample) return;

    // Switch to text tab
    switchTab("text");
    textInput.value = sample.content;
    updateCharCount();
    textInput.focus();
  });

  // 3. Tab Switching
  function switchTab(mode) {
    if (mode === "file") {
      tabFile.classList.add("active");
      tabFile.setAttribute("aria-selected", "true");
      tabText.classList.remove("active");
      tabText.setAttribute("aria-selected", "false");
      panelFile.classList.remove("hidden");
      panelText.classList.add("hidden");
    } else {
      tabText.classList.add("active");
      tabText.setAttribute("aria-selected", "true");
      tabFile.classList.remove("active");
      tabFile.setAttribute("aria-selected", "false");
      panelText.classList.remove("hidden");
      panelFile.classList.add("hidden");
    }
  }

  tabFile.addEventListener("click", () => switchTab("file"));
  tabText.addEventListener("click", () => switchTab("text"));

  // 4. File Drag and Drop
  dropZone.addEventListener("click", () => fileInput.click());

  ["dragenter", "dragover"].forEach((eventName) => {
    dropZone.addEventListener(eventName, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropZone.classList.add("dragover");
    });
  });

  ["dragleave", "drop"].forEach((eventName) => {
    dropZone.addEventListener(eventName, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropZone.classList.remove("dragover");
    });
  });

  dropZone.addEventListener("drop", (e) => {
    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      handleFileSelected(files[0]);
    }
  });

  fileInput.addEventListener("change", (e) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFileSelected(e.target.files[0]);
    }
  });

  function handleFileSelected(file) {
    currentFile = file;
    selectedFileName.textContent = `${file.name} (${(file.size / 1024).toFixed(1)} KB)`;
    selectedFileBadge.classList.remove("hidden");
  }

  clearFileBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    currentFile = null;
    fileInput.value = "";
    selectedFileBadge.classList.add("hidden");
  });

  // 5. Text Input Helpers
  function updateCharCount() {
    const count = textInput.value.length;
    charCount.textContent = `${count} characters`;
  }

  textInput.addEventListener("input", updateCharCount);

  clearTextBtn.addEventListener("click", () => {
    textInput.value = "";
    updateCharCount();
  });

  // 6. Form Submission & Pipeline Execution
  analyzeForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    hideError();

    const isTextTab = tabText.classList.contains("active");
    const textContent = textInput.value.trim();

    if (isTextTab) {
      if (!textContent) {
        showError("Input Required", "Please paste the document or message text to analyze.");
        return;
      }
    } else {
      if (!currentFile) {
        showError("File Required", "Please select or drop a PDF document or screenshot image.");
        return;
      }
    }

    // Set UI to loading state
    setLoading(true);
    resultsDashboard.classList.add("hidden");
    processingCard.classList.remove("hidden");

    try {
      const formData = new FormData();
      if (isTextTab) {
        formData.append("text", textContent);
        formData.append("source_label", "Pasted Document");
      } else {
        formData.append("file", currentFile);
      }

      const response = await fetch("/api/analyze", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.detail || `Analysis failed with HTTP status ${response.status}`);
      }

      const result = await response.json();
      currentAnalysis = result;
      renderResults(result);
    } catch (err) {
      console.error("Analysis error:", err);
      showError("Analysis Failed", err.message || "Failed to analyze document. Please check server logs.");
    } finally {
      setLoading(false);
      processingCard.classList.add("hidden");
    }
  });

  function setLoading(loading) {
    if (loading) {
      analyzeBtn.disabled = true;
      analyzeSpinner.classList.remove("hidden");
      analyzeBtnText.textContent = "Analyzing Document...";
    } else {
      analyzeBtn.disabled = false;
      analyzeSpinner.classList.add("hidden");
      analyzeBtnText.textContent = "Run TrustLens Verification";
    }
  }

  function showError(title, msg) {
    errorTitle.textContent = title;
    errorMessage.textContent = msg;
    errorCard.classList.remove("hidden");
    errorCard.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }

  function hideError() {
    errorCard.classList.add("hidden");
  }

  dismissErrorBtn.addEventListener("click", hideError);

  // 7. Render Analysis Results Dashboard
  function renderResults(data) {
    const score = data.score;

    // Risk Meter & Level
    const scoreCircle = document.getElementById("score-circle");
    const scoreNumber = document.getElementById("score-number");
    const riskBadge = document.getElementById("risk-badge");
    const sufficiencyTag = document.getElementById("sufficiency-tag");

    scoreNumber.textContent = score.heuristic_risk_score;
    riskBadge.textContent = score.risk_level;
    sufficiencyTag.textContent = `Evidence Sufficiency: ${score.evidence_sufficiency}`;

    // Styling according to risk
    scoreCircle.className = "score-circle";
    riskBadge.className = "risk-badge-large";

    if (score.risk_level === "High") {
      scoreCircle.style.borderColor = "#ef4444";
      scoreCircle.style.boxShadow = "0 0 20px rgba(239, 68, 68, 0.3)";
      riskBadge.classList.add("badge-high");
    } else if (score.risk_level === "Medium") {
      scoreCircle.style.borderColor = "#f59e0b";
      scoreCircle.style.boxShadow = "0 0 20px rgba(245, 158, 11, 0.3)";
      riskBadge.classList.add("badge-medium");
    } else if (score.risk_level === "Low") {
      scoreCircle.style.borderColor = "#10b981";
      scoreCircle.style.boxShadow = "0 0 20px rgba(16, 185, 129, 0.3)";
      riskBadge.classList.add("badge-low");
    } else {
      scoreCircle.style.borderColor = "#94a3b8";
      scoreCircle.style.boxShadow = "none";
      riskBadge.style.background = "rgba(148, 163, 184, 0.2)";
      riskBadge.style.color = "#cbd5e1";
    }

    // Document Meta
    document.getElementById("meta-filename").textContent = data.extraction.file_name || "Document";
    document.getElementById("meta-type").textContent = `${data.document_type} (${data.extraction.provenance_mode})`;
    document.getElementById("meta-model").textContent = data.model_used;
    document.getElementById("meta-summary").textContent = data.summary;
    document.getElementById("scoring-explanation-text").textContent = score.scoring_notes;

    // Scoring Signals Table
    const signalsTbody = document.getElementById("signals-table-body");
    signalsTbody.innerHTML = "";
    if (score.signals && score.signals.length > 0) {
      score.signals.forEach((sig) => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td><strong>${escapeHtml(sig.name)}</strong></td>
          <td><code>${escapeHtml(sig.category)}</code></td>
          <td style="color: ${sig.points > 20 ? '#f87171' : '#fbbf24'}; font-weight: 600;">+${sig.points}</td>
          <td><span class="provenance-tag">${escapeHtml(sig.source)}</span></td>
          <td>${escapeHtml(sig.description)}</td>
        `;
        signalsTbody.appendChild(tr);
      });
    } else {
      const tr = document.createElement("tr");
      tr.innerHTML = `<td colspan="5" style="color: var(--text-muted); text-align: center;">No negative risk signals were triggered.</td>`;
      signalsTbody.appendChild(tr);
    }

    // Findings Cards
    const findingsContainer = document.getElementById("findings-container");
    findingsContainer.innerHTML = "";
    if (data.findings && data.findings.length > 0) {
      data.findings.forEach((f) => {
        const card = document.createElement("div");
        card.className = `finding-card severity-${f.severity}`;
        card.innerHTML = `
          <div class="finding-header">
            <div class="finding-tags">
              <span class="badge-tag badge-${f.severity}">${f.severity.toUpperCase()}</span>
              <strong>${escapeHtml(f.category.replace("_", " ").toUpperCase())}</strong>
              <span class="provenance-tag">${f.provenance}</span>
            </div>
            <span style="font-size: 0.8rem; color: var(--text-muted);">Conf: ${(f.confidence * 100).toFixed(0)}%</span>
          </div>
          <div class="evidence-quote-box">
            "<em>${escapeHtml(f.evidence_quote)}</em>"
          </div>
          <p class="finding-explanation">${escapeHtml(f.explanation)}</p>
        `;
        findingsContainer.appendChild(card);
      });
    } else {
      findingsContainer.innerHTML = `<p style="color: var(--text-muted);">No specific warning findings were detected by the AI model.</p>`;
    }

    // Quarantined Findings
    const quarantinedCard = document.getElementById("quarantined-card");
    const quarantinedList = document.getElementById("quarantined-list");
    quarantinedList.innerHTML = "";
    if (data.quarantined_findings && data.quarantined_findings.length > 0) {
      quarantinedCard.classList.remove("hidden");
      data.quarantined_findings.forEach((qf) => {
        const item = document.createElement("div");
        item.style.marginBottom = "8px";
        item.innerHTML = `
          <strong>${escapeHtml(qf.id)} (${escapeHtml(qf.category)}):</strong>
          "${escapeHtml(qf.evidence_quote)}" — <em>${escapeHtml(qf.quarantine_reason)}</em>
        `;
        quarantinedList.appendChild(item);
      });
    } else {
      quarantinedCard.classList.add("hidden");
    }

    // Deterministic Rule Hits
    const rulesContainer = document.getElementById("rules-container");
    rulesContainer.innerHTML = "";
    if (data.rule_hits && data.rule_hits.length > 0) {
      data.rule_hits.forEach((r) => {
        const item = document.createElement("div");
        item.className = "finding-card";
        item.style.borderLeftColor = r.severity === "high" ? "#ef4444" : "#f59e0b";
        item.innerHTML = `
          <div class="finding-header">
            <div class="finding-tags">
              <span class="badge-tag badge-${r.severity}">${r.severity.toUpperCase()}</span>
              <strong>${escapeHtml(r.title)}</strong>
              <code>${escapeHtml(r.rule_id)}</code>
            </div>
            <span style="color: #fbbf24; font-weight: 600;">+${r.weight} pts</span>
          </div>
          <div class="evidence-quote-box">Matched: "${escapeHtml(r.matched_evidence)}"</div>
          <p class="finding-explanation">${escapeHtml(r.explanation)}</p>
          <p style="font-size: 0.78rem; color: var(--text-muted); margin-top: 6px;">Rule limits: ${escapeHtml(r.limitations)}</p>
        `;
        rulesContainer.appendChild(item);
      });
    } else {
      rulesContainer.innerHTML = `<p style="color: var(--text-muted);">No independent deterministic rule triggers matched.</p>`;
    }

    // Positive Signals
    const positiveList = document.getElementById("positive-signals-list");
    positiveList.innerHTML = "";
    if (data.positive_signals && data.positive_signals.length > 0) {
      data.positive_signals.forEach((sig) => {
        const li = document.createElement("li");
        li.innerHTML = `✅ ${escapeHtml(sig)}`;
        positiveList.appendChild(li);
      });
    } else {
      positiveList.innerHTML = `<li style="color: var(--text-muted);">No explicit positive signals reported.</li>`;
    }

    // Unverified Claims
    const unverifiedList = document.getElementById("unverified-claims-list");
    unverifiedList.innerHTML = "";
    if (data.unverified_claims && data.unverified_claims.length > 0) {
      data.unverified_claims.forEach((claim) => {
        const li = document.createElement("li");
        li.innerHTML = `❓ ${escapeHtml(claim)}`;
        unverifiedList.appendChild(li);
      });
    } else {
      unverifiedList.innerHTML = `<li style="color: var(--text-muted);">None identified.</li>`;
    }

    // Recommended Verification Steps
    const stepsList = document.getElementById("recommended-steps-list");
    stepsList.innerHTML = "";
    if (data.recommended_checks && data.recommended_checks.length > 0) {
      data.recommended_checks.forEach((step) => {
        const li = document.createElement("li");
        li.textContent = step;
        stepsList.appendChild(li);
      });
    } else {
      stepsList.innerHTML = `
        <li>Verify the entity's domain directly through official business registries.</li>
        <li>Never pay upfront fees or equipment deposits for job or internship opportunities.</li>
      `;
    }

    // Reveal Dashboard & Scroll
    resultsDashboard.classList.remove("hidden");
    resultsDashboard.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  // 8. Markdown Export Handler
  exportMdBtn.addEventListener("click", async () => {
    if (!currentAnalysis) return;
    try {
      const res = await fetch("/api/export/markdown", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(currentAnalysis),
      });

      if (!res.ok) throw new Error("Export generation failed");
      const markdownText = await res.text();

      // Trigger client-side file download
      const blob = new Blob([markdownText], { type: "text/markdown;charset=utf-8" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `trustlens_report_${currentAnalysis.analysis_id.slice(0, 8)}.md`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (err) {
      alert("Failed to export markdown report: " + err.message);
    }
  });

  // 9. Print / PDF Handler
  printReportBtn.addEventListener("click", () => {
    window.print();
  });

  function escapeHtml(str) {
    if (!str) return "";
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }
});
