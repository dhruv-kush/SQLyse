"use strict";

document.documentElement.classList.add("js-enabled");

const body = document.body;
const sidebar = document.getElementById("primarySidebar");
const sidebarToggle = document.getElementById("sidebarToggle");
const mobileMenuButton = document.getElementById("mobileMenuButton");
const drawerBackdrop = document.getElementById("drawerBackdrop");
const desktopMedia = window.matchMedia("(min-width: 761px)");
const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
const navigationLinks = [...document.querySelectorAll(".nav-link")];

let desktopExpanded = false;
let mobileOpen = false;

function isDesktopViewport() {
  return window.innerWidth >= 761;
}

function syncNavigation() {
  const isDesktop = isDesktopViewport();

  body.classList.toggle("sidebar-expanded", isDesktop && desktopExpanded);
  body.classList.toggle("nav-open", !isDesktop && mobileOpen);

  sidebarToggle.setAttribute("aria-expanded", String(isDesktop ? desktopExpanded : mobileOpen));
  sidebarToggle.setAttribute("aria-label", isDesktop
    ? `${desktopExpanded ? "Collapse" : "Expand"} navigation`
    : "Close navigation");
  mobileMenuButton.setAttribute("aria-expanded", String(mobileOpen));
  mobileMenuButton.setAttribute("aria-label", mobileOpen ? "Close navigation" : "Open navigation");

  sidebar.setAttribute("aria-hidden", String(!isDesktop && !mobileOpen));
  sidebar.toggleAttribute("inert", !isDesktop && !mobileOpen);

  if (!isDesktop && mobileOpen) {
    drawerBackdrop.hidden = false;
    requestAnimationFrame(() => drawerBackdrop.classList.add("is-visible"));
  } else {
    drawerBackdrop.classList.remove("is-visible");
    window.setTimeout(() => {
      if (!mobileOpen || isDesktopViewport()) drawerBackdrop.hidden = true;
    }, 340);
  }
}

function closeMobileNavigation(returnFocus = true) {
  if (!mobileOpen) return;
  mobileOpen = false;
  syncNavigation();
  if (returnFocus) mobileMenuButton.focus();
}

sidebarToggle.addEventListener("click", () => {
  if (isDesktopViewport()) {
    desktopExpanded = !desktopExpanded;
    syncNavigation();
  } else {
    closeMobileNavigation();
  }
});

mobileMenuButton.addEventListener("click", () => {
  mobileOpen = true;
  syncNavigation();
  window.setTimeout(() => sidebarToggle.focus(), 50);
});

drawerBackdrop.addEventListener("click", () => closeMobileNavigation());

function setActiveNavigation(sectionId) {
  navigationLinks.forEach((link) => {
    const isActive = link.getAttribute("href") === `#${sectionId}`;
    link.closest(".nav-item")?.classList.toggle("is-active", isActive);
    if (isActive) link.setAttribute("aria-current", "page");
    else link.removeAttribute("aria-current");
  });
}

navigationLinks.forEach((link) => {
  link.addEventListener("click", (event) => {
    const sectionId = link.getAttribute("href")?.slice(1);
    const section = sectionId ? document.getElementById(sectionId) : null;
    if (!section) return;

    event.preventDefault();
    if (!isDesktopViewport()) closeMobileNavigation(false);
    setActiveNavigation(sectionId);
    section.scrollIntoView({ behavior: reducedMotion.matches ? "auto" : "smooth", block: "start" });
    try {
      if (window.history?.replaceState) window.history.replaceState(null, "", `#${sectionId}`);
    } catch {
      // Smooth section navigation still works when history updates are unavailable.
    }
  });
});

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && mobileOpen) closeMobileNavigation();
});

desktopMedia.addEventListener("change", () => {
  mobileOpen = false;
  syncNavigation();
});

syncNavigation();

const shieldScene = document.getElementById("shieldScene");
const middleShield = document.getElementById("middleShield");
const leftShield = document.getElementById("leftShield");
const rightShield = document.getElementById("rightShield");

function startShieldEntrance() {
  if (reducedMotion.matches) return;

  window.setTimeout(() => middleShield.classList.add("is-lifted"), 300);
  window.setTimeout(() => leftShield.classList.add("is-visible"), 660);
  window.setTimeout(() => leftShield.classList.add("is-positioned"), 740);
  window.setTimeout(() => rightShield.classList.add("is-visible"), 1040);
  window.setTimeout(() => rightShield.classList.add("is-positioned"), 1120);
  window.setTimeout(() => shieldScene.classList.add("is-floating"), 2150);
}

startShieldEntrance();

const scanForm = document.getElementById("scanForm");
const targetUrl = document.getElementById("targetUrl");
const scanControl = document.getElementById("scanControl");
const scanButton = document.getElementById("scanButton");
const scanButtonLabel = document.getElementById("scanButtonLabel");
const urlError = document.getElementById("urlError");
const scanTargetStatus = document.getElementById("scanTargetStatus");
const scanWorkflow = document.getElementById("scanWorkflow");
const monitoringGrid = document.getElementById("monitoringGrid");
const scanProgress = document.getElementById("scanProgress");
const progressStage = document.getElementById("progressStage");
const progressPercent = document.getElementById("progressPercent");
const progressTrack = document.getElementById("progressTrack");
const progressFill = document.getElementById("progressFill");
const elapsedTime = document.getElementById("elapsedTime");
const currentTarget = document.getElementById("currentTarget");
const phaseList = document.getElementById("phaseList");
const scanStateMessage = document.getElementById("scanStateMessage");
const cancelScanButton = document.getElementById("cancelScanButton");
const activityLog = document.getElementById("activityLog");
const activityEmpty = document.getElementById("activityEmpty");
const copyLogsButton = document.getElementById("copyLogsButton");
const scanErrorPanel = document.getElementById("scanErrorPanel");
const scanErrorMessage = document.getElementById("scanErrorMessage");
const retryScanButton = document.getElementById("retryScanButton");
const completionContent = document.getElementById("completionContent");
const scanId = document.getElementById("scanId");
const overviewMetrics = document.getElementById("overviewMetrics");
const findingCount = document.getElementById("findingCount");
const findingsToolbar = document.getElementById("findingsToolbar");
const findingSearch = document.getElementById("findingSearch");
const severityFilter = document.getElementById("severityFilter");
const statusFilter = document.getElementById("statusFilter");
const filteredExportButton = document.getElementById("filteredExportButton");
const findingsTableWrap = document.getElementById("findingsTableWrap");
const findingsTableBody = document.getElementById("findingsTableBody");
const filteredEmpty = document.getElementById("filteredEmpty");
const clearFiltersButton = document.getElementById("clearFiltersButton");
const noFindingsState = document.getElementById("noFindingsState");
const analysisGrid = document.getElementById("analysisGrid");
const analysisFindingTitle = document.getElementById("analysisFindingTitle");
const analysisCopy = document.getElementById("analysisCopy");
const verificationNote = document.getElementById("verificationNote");
const remediationList = document.getElementById("remediationList");
const downloadPdfButton = document.getElementById("downloadPdfButton");
const exportJsonButton = document.getElementById("exportJsonButton");
const exportCsvButton = document.getElementById("exportCsvButton");
const copySummaryButton = document.getElementById("copySummaryButton");
const newScanButton = document.getElementById("newScanButton");
const reportFeedback = document.getElementById("reportFeedback");
const findingBackdrop = document.getElementById("findingBackdrop");
const findingDrawer = document.getElementById("findingDrawer");
const detailTitle = document.getElementById("detailTitle");
const detailSeverity = document.getElementById("detailSeverity");
const detailConfidence = document.getElementById("detailConfidence");
const detailStatus = document.getElementById("detailStatus");
const technicalContext = document.getElementById("technicalContext");
const detailObserved = document.getElementById("detailObserved");
const detailRisk = document.getElementById("detailRisk");
const detailImpact = document.getElementById("detailImpact");
const detailVerification = document.getElementById("detailVerification");
const evidenceMetadata = document.getElementById("evidenceMetadata");
const responseExcerpt = document.getElementById("responseExcerpt");
const closeDetailButton = document.getElementById("closeDetailButton");
const markReviewedButton = document.getElementById("markReviewedButton");
const markReviewedLabel = document.getElementById("markReviewedLabel");
const copyFindingButton = document.getElementById("copyFindingButton");
const downloadFindingButton = document.getElementById("downloadFindingButton");
const appToast = document.getElementById("appToast");
const teamGrid = document.getElementById("teamGrid");
const projectContactActions = document.getElementById("projectContactActions");
const footerGithub = document.getElementById("footerGithub");
const currentYear = document.getElementById("currentYear");

const APP_STATES = Object.freeze({
  IDLE: "IDLE",
  VALIDATION_ERROR: "VALIDATION_ERROR",
  SCANNING: "SCANNING",
  COMPLETE: "COMPLETE",
  NO_FINDINGS: "NO_FINDINGS",
  SCAN_ERROR: "SCAN_ERROR"
});

const API_BASE_URL = "http://127.0.0.1:5000/api";
const STATUS_POLL_INTERVAL_MS = 600;

// Frontend-only display labels for the scan pipeline. The backend does not
// send a "phases" array — it sends a free-text "phase" string plus a
// numeric "progress" percentage on every /status response. This list is
// purely for rendering the step indicator UI; it must tolerate any phase
// string the backend sends, including ones not listed here (see
// resolvePhaseIndex below).
const SCAN_PHASES = [
  "Initializing",
  "Crawling Target",
  "Discovering Inputs",
  "Testing Parameters",
  "Analyzing Responses",
  "Building Findings",
  "Scan Complete"
];

/**
 * Maps a backend phase label + progress percentage to an index into
 * SCAN_PHASES for the step indicator. Falls back to a progress-based
 * estimate when the phase string doesn't match a known label, so unknown
 * or future backend phase names never crash the UI.
 */
function resolvePhaseIndex(phaseLabel, progressPercent) {
  const normalized = String(phaseLabel || "").trim().toLowerCase();
  const matchIndex = SCAN_PHASES.findIndex((label) => label.toLowerCase() === normalized);
  if (matchIndex !== -1) return matchIndex;

  const safePercent = Number.isFinite(progressPercent) ? progressPercent : 0;
  const estimatedIndex = Math.floor((safePercent / 100) * (SCAN_PHASES.length - 1));
  return Math.min(SCAN_PHASES.length - 1, Math.max(0, estimatedIndex));
}

const METRIC_DEFINITIONS = [
  { key: "pagesScanned", label: "Pages Scanned", icon: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 3h9l4 4v14H6V3Zm9 0v5h4M9 12h7M9 16h5"/></svg>' },
  { key: "formsDiscovered", label: "Forms Discovered", icon: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 5h16v14H4V5Zm4 4h8M8 13h5M8 17h3"/></svg>' },
  { key: "parametersTested", label: "Parameters Tested", icon: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h10M18 7h2M4 12h3m4 0h9M4 17h7m4 0h5"/><circle cx="16" cy="7" r="2"/><circle cx="9" cy="12" r="2"/><circle cx="13" cy="17" r="2"/></svg>' },
  { key: "findingsCount", label: "Findings", icon: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3 3.5 19h17L12 3Zm0 6v4m0 3h.01"/></svg>' },
  { key: "overallRisk", label: "Overall Risk", isRisk: true, icon: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3 4 6v5c0 5 3.2 8.5 8 10 4.8-1.5 8-5 8-10V6l-8-3Z"/></svg>' }
];

const LOG_ICONS = {
  info: '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 11v5m0-8h.01"/></svg>',
  success: '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="m8 12 2.5 2.5L16 9"/></svg>',
  warning: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3 3.5 19h17L12 3Zm0 6v4m0 3h.01"/></svg>',
  error: '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M15 9l-6 6m0-6 6 6"/></svg>'
};

// Edit team members and public project contact destinations here.
const teamMembers = [
  {
    name: "Rohan Sharma",
    role: "Frontend & Interface",
    github: "",
    linkedin: "",
    email: ""
  },
  {
    name: "Team Member 2",
    role: "Crawler & Scanner Engine",
    github: "",
    linkedin: "",
    email: ""
  },
  {
    name: "Team Member 3",
    role: "Backend, Analysis & Reports",
    github: "",
    linkedin: "",
    email: ""
  }
];

const projectContact = {
  github: "",
  email: ""
};

const CONTACT_ICONS = {
  github: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 19c-4.5 1.4-4.5-2.5-6-3m12 6v-3.9a3.4 3.4 0 0 0-.9-2.6c3 0 6.1-1.5 6.1-6.8a5.3 5.3 0 0 0-1.4-3.7 5 5 0 0 0-.1-3.7S17.6.9 15 2.7a12.8 12.8 0 0 0-6 0C6.4.9 5.3 1.3 5.3 1.3A5 5 0 0 0 5.2 5a5.3 5.3 0 0 0-1.4 3.7c0 5.3 3.1 6.8 6.1 6.8a3.4 3.4 0 0 0-.9 2.6V22"/></svg>',
  linkedin: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 9v11M6 5.5v.01M10 20v-6.5a4 4 0 0 1 8 0V20M10 9v11"/><circle cx="6" cy="5.5" r="1.5"/></svg>',
  email: '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m4 7 8 6 8-6"/></svg>'
};

function getInitials(name) {
  return name
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase())
    .join("") || "SQ";
}

function createContactAction(type, label, value, owner, className = "contact-action") {
  const isAvailable = Boolean(value?.trim());
  const action = document.createElement(isAvailable ? "a" : "span");
  action.className = `${className}${isAvailable ? "" : " is-disabled"}`;
  action.innerHTML = CONTACT_ICONS[type] || "";

  const actionLabel = document.createElement("span");
  actionLabel.textContent = label;
  action.appendChild(actionLabel);

  if (isAvailable) {
    action.href = type === "email" ? `mailto:${value.trim()}` : value.trim();
    action.setAttribute("aria-label", `${label} for ${owner}`);
    if (type !== "email") {
      action.target = "_blank";
      action.rel = "noreferrer noopener";
    }
  } else {
    action.setAttribute("role", "link");
    action.setAttribute("aria-disabled", "true");
    action.setAttribute("aria-label", `${label} for ${owner} is not available yet`);
    action.setAttribute("title", "Not available yet");
    action.tabIndex = 0;
  }

  return action;
}

function renderTeamMembers() {
  teamGrid.innerHTML = "";
  teamMembers.forEach((member) => {
    const card = document.createElement("article");
    card.className = "team-card";

    const header = document.createElement("div");
    header.className = "team-card-header";
    const avatar = document.createElement("span");
    avatar.className = "team-avatar";
    avatar.setAttribute("aria-hidden", "true");
    avatar.textContent = getInitials(member.name);

    const identity = document.createElement("div");
    const name = document.createElement("h3");
    name.textContent = member.name;
    const role = document.createElement("p");
    role.className = "team-role";
    role.textContent = member.role;
    identity.append(name, role);
    header.append(avatar, identity);

    const actions = document.createElement("div");
    actions.className = "contact-actions";
    actions.append(
      createContactAction("github", "GitHub", member.github, member.name),
      createContactAction("linkedin", "LinkedIn", member.linkedin, member.name),
      createContactAction("email", "Email", member.email, member.name)
    );

    card.append(header, actions);
    teamGrid.appendChild(card);
  });
}

function renderProjectContact() {
  projectContactActions.innerHTML = "";
  projectContactActions.append(
    createContactAction("github", "GitHub repository", projectContact.github, "SQLyse"),
    createContactAction("email", "Project email", projectContact.email, "SQLyse")
  );

  footerGithub.innerHTML = "";
  footerGithub.appendChild(createContactAction("github", "GitHub", projectContact.github, "SQLyse", "footer-github"));
}

function setupContentReveals() {
  const revealElements = [...document.querySelectorAll(".content-reveal")];
  if (reducedMotion.matches || !("IntersectionObserver" in window)) {
    revealElements.forEach((element) => element.classList.add("is-revealed"));
    return;
  }

  const revealObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;
      entry.target.classList.add("is-revealed");
      observer.unobserve(entry.target);
    });
  }, { rootMargin: "0px 0px -10% 0px", threshold: 0.06 });

  revealElements.forEach((element) => revealObserver.observe(element));
}

function setupActiveNavigationTracking() {
  const observedSections = [
    { element: document.getElementById("dashboard"), sectionId: "dashboard" },
    { element: scanWorkflow, sectionId: "dashboard" },
    { element: document.getElementById("learn-sqli"), sectionId: "learn-sqli" },
    { element: document.getElementById("about-sqlyse"), sectionId: "about-sqlyse" },
    { element: document.getElementById("contact"), sectionId: "contact" }
  ].filter(({ element }) => element);

  if (!("IntersectionObserver" in window)) {
    setActiveNavigation("dashboard");
    return;
  }

  const visibleEntries = new Map();
  const navigationObserver = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) visibleEntries.set(entry.target, entry);
      else visibleEntries.delete(entry.target);
    });

    const match = [...observedSections].reverse().find(({ element }) => visibleEntries.has(element));
    if (match) setActiveNavigation(match.sectionId);
  }, { rootMargin: "-18% 0px -68% 0px", threshold: 0 });

  observedSections.forEach(({ element }) => navigationObserver.observe(element));
}

let applicationState = APP_STATES.IDLE;
let currentScanResult = null;
let selectedFindingId = null;
let lastSubmittedUrl = "";
let revealTimers = [];
let elapsedTimer = null;
let scanStartedAt = 0;
let logEntries = [];
let lastFocusedElement = null;
let toastTimer = null;

// --- API scan state -------------------------------------------------------
let activeScanId = null;
let pollTimer = null;
let pollInFlight = false;
let scanOperationToken = 0; // bumped on every reset/new scan/retry so stale
// async responses (poll ticks, results fetches) belonging to a superseded
// scan are detected and ignored instead of overwriting current UI state.
let renderedLogCount = 0; // how many backend log entries have already been
// appended to the activity log, so polling never re-renders duplicates.
let cancelInFlight = false;

async function parseJsonResponse(response) {
  try {
    return await response.json();
  } catch {
    throw new Error("The backend returned an unexpected response.");
  }
}

async function readErrorMessage(response, fallback) {
  try {
    const body = await response.json();
    if (body && typeof body.error === "string" && body.error.trim()) {
      return body.error;
    }
  } catch {
    // Response body wasn't valid JSON; fall back to the generic message.
  }
  return fallback;
}

function showValidationError(message) {
  transitionTo(APP_STATES.VALIDATION_ERROR);
  urlError.textContent = message;
  scanControl.classList.add("has-error");
  targetUrl.setAttribute("aria-invalid", "true");
  targetUrl.focus();
}

function clearValidationError() {
  urlError.textContent = "";
  scanControl.classList.remove("has-error");
  targetUrl.removeAttribute("aria-invalid");
}

function validateTarget(value) {
  if (!value) return "Enter a target URL to begin a scan.";

  try {
    const parsed = new URL(value);
    if (!["http:", "https:"].includes(parsed.protocol) || !parsed.hostname) {
      return "Use a complete HTTP or HTTPS URL, such as https://example.com.";
    }
  } catch {
    return "Use a complete HTTP or HTTPS URL, such as https://example.com.";
  }

  return "";
}

function transitionTo(nextState) {
  applicationState = nextState;
  body.dataset.scanState = nextState;

  const isIdleState = nextState === APP_STATES.IDLE || nextState === APP_STATES.VALIDATION_ERROR;
  const isScanning = nextState === APP_STATES.SCANNING;
  const isComplete = nextState === APP_STATES.COMPLETE || nextState === APP_STATES.NO_FINDINGS;
  const isError = nextState === APP_STATES.SCAN_ERROR;

  scanWorkflow.hidden = isIdleState;
  monitoringGrid.hidden = isError;
  scanErrorPanel.hidden = !isError;
  completionContent.hidden = !isComplete;
  cancelScanButton.hidden = !isScanning;

  targetUrl.disabled = isScanning;
  scanButton.disabled = isScanning;
  scanButton.classList.toggle("is-scanning", isScanning);
  scanButtonLabel.textContent = isScanning ? "SCANNING" : "SCAN";
  scanProgress.setAttribute("aria-busy", String(isScanning));

  if (isIdleState) {
    scanProgress.classList.remove("is-visible");
    completionContent.classList.remove("is-visible");
  } else if (!isError) {
    requestAnimationFrame(() => scanProgress.classList.add("is-visible"));
  }
}

function clearScheduledWork() {
  revealTimers.forEach(window.clearTimeout);
  revealTimers = [];
  if (elapsedTimer !== null) {
    window.clearInterval(elapsedTimer);
    elapsedTimer = null;
  }
  stopPolling();
}

function stopPolling() {
  if (pollTimer !== null) {
    window.clearTimeout(pollTimer);
    pollTimer = null;
  }
  pollInFlight = false;
}

function formatElapsed(seconds) {
  const safeSeconds = Math.max(0, Math.floor(seconds));
  return `00:${String(safeSeconds).padStart(2, "0")}`;
}

function setProgress(percent, label, currentIndex, allComplete = false) {
  progressFill.style.width = `${percent}%`;
  progressPercent.textContent = `${percent}%`;
  progressStage.textContent = label.toUpperCase();
  progressTrack.setAttribute("aria-valuenow", String(percent));
  progressTrack.setAttribute("aria-valuetext", `${percent} percent, ${label.toLowerCase()}`);
  updatePhaseIndicators(currentIndex, allComplete);
}

function renderPhaseIndicators() {
  phaseList.innerHTML = "";
  SCAN_PHASES.forEach((label, index) => {
    const item = document.createElement("li");
    item.className = "phase-item";
    item.dataset.phaseIndex = String(index);
    item.innerHTML = `
      <span class="phase-marker" aria-hidden="true">
        <svg viewBox="0 0 24 24"><path d="m6 12 4 4 8-9"/></svg>
      </span>
      <span>${escapeHtml(label)}</span>
    `;
    phaseList.appendChild(item);
  });
}

function updatePhaseIndicators(currentIndex, allComplete = false) {
  phaseList.querySelectorAll(".phase-item").forEach((item, index) => {
    const isComplete = allComplete || index < currentIndex;
    const isCurrent = !allComplete && index === currentIndex;
    item.classList.toggle("is-complete", isComplete);
    item.classList.toggle("is-current", isCurrent);
    if (isCurrent) item.setAttribute("aria-current", "step");
    else item.removeAttribute("aria-current");
  });
}

function resetActivityLog() {
  logEntries = [];
  activityLog.querySelectorAll(".log-entry").forEach((entry) => entry.remove());
  activityEmpty.hidden = false;
}

function addActivityEntry(second, entry) {
  activityEmpty.hidden = true;
  const timestamp = formatElapsed(second);
  logEntries.push({ timestamp, ...entry });

  const row = document.createElement("div");
  row.className = `log-entry is-${entry.type}`;
  row.innerHTML = `
    ${LOG_ICONS[entry.type] || LOG_ICONS.info}
    <span class="log-time">[${timestamp}]</span>
    <span class="log-message">${escapeHtml(entry.message)}</span>
  `;
  activityLog.appendChild(row);
  activityLog.scrollTop = activityLog.scrollHeight;
}

function startElapsedClock() {
  scanStartedAt = performance.now();
  elapsedTime.textContent = "00:00";
  elapsedTimer = window.setInterval(() => {
    if (applicationState !== APP_STATES.SCANNING) return;
    const realSeconds = (performance.now() - scanStartedAt) / 1000;
    elapsedTime.textContent = formatElapsed(realSeconds);
  }, 100);
}

function scrollToProgressOnce() {
  const behavior = reducedMotion.matches ? "auto" : "smooth";
  window.setTimeout(() => scanProgress.scrollIntoView({ behavior, block: "start" }), 80);
}

/**
 * Starts a real scan against the Flask backend: POSTs the target URL,
 * resets all scan UI state, and begins status polling. This replaces the
 * former setTimeout-based mock workflow entirely.
 */
async function startApiScan(url) {
  const operationToken = ++scanOperationToken; // invalidates any in-flight
  // poll/result requests from a previous scan that might still resolve.

  clearScheduledWork();
  closeFindingDetails(false);
  clearValidationError();
  hideTargetStatus();
  resetCompletedDashboard();

  lastSubmittedUrl = url;
  currentScanResult = null;
  selectedFindingId = null;
  activeScanId = null;
  cancelInFlight = false;
  renderedLogCount = 0;

  currentTarget.textContent = url;
  scanStateMessage.textContent = "Starting scan…";
  resetActivityLog();
  renderPhaseIndicators();
  setProgress(0, "Initializing", 0);
  transitionTo(APP_STATES.SCANNING);
  startElapsedClock();
  scrollToProgressOnce();

  let response;
  try {
    response = await fetch(`${API_BASE_URL}/scans`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ targetUrl: url })
    });
  } catch {
    if (operationToken !== scanOperationToken) return;
    showScanError(new Error("Could not reach the SQLyse backend. Confirm it is running at " + API_BASE_URL + "."));
    return;
  }

  if (operationToken !== scanOperationToken) return;

  if (!response.ok) {
    const message = await readErrorMessage(response, "The backend scan could not be completed.");
    showScanError(new Error(message));
    return;
  }

  let payload;
  try {
    payload = await parseJsonResponse(response);
  } catch (error) {
    if (operationToken !== scanOperationToken) return;
    showScanError(error);
    return;
  }

  if (operationToken !== scanOperationToken) return;

  if (!payload?.scanId) {
    showScanError(new Error("The backend scan could not be completed."));
    return;
  }

  activeScanId = payload.scanId;
  scanStateMessage.textContent = "Scan running…";
  pollScanStatus(operationToken);
}

/**
 * Polls /api/scans/<id>/status on a fixed interval, guarding against
 * overlapping requests and against stale responses from a superseded scan
 * (tracked via operationToken / scanOperationToken).
 */
function pollScanStatus(operationToken) {
  if (operationToken !== scanOperationToken) return;

  pollTimer = window.setTimeout(async () => {
    if (operationToken !== scanOperationToken || pollInFlight) return;
    pollInFlight = true;

    let response;
    try {
      response = await fetch(`${API_BASE_URL}/scans/${encodeURIComponent(activeScanId)}/status`);
    } catch {
      pollInFlight = false;
      if (operationToken !== scanOperationToken) return;
      showScanError(new Error("Lost connection to the SQLyse backend while checking scan status."));
      return;
    }

    pollInFlight = false;
    if (operationToken !== scanOperationToken) return;

    if (!response.ok) {
      const message = await readErrorMessage(response, "The backend scan could not be completed.");
      showScanError(new Error(message));
      return;
    }

    let status;
    try {
      status = await parseJsonResponse(response);
    } catch (error) {
      if (operationToken !== scanOperationToken) return;
      showScanError(error);
      return;
    }

    if (operationToken !== scanOperationToken) return;
    applyStatusUpdate(status);

    if (status.status === "completed") {
      await finishApiScan(operationToken);
      return;
    }
    if (status.status === "failed") {
      showScanError(new Error(status.error || "The backend scan could not be completed."));
      return;
    }
    if (status.status === "cancelled") {
      handleScanCancelledExternally();
      return;
    }

    pollScanStatus(operationToken);
  }, STATUS_POLL_INTERVAL_MS);
}

/** Applies one /status response to the progress bar, phase indicators,
 * elapsed timer, state message, and activity log. */
function applyStatusUpdate(status) {
  const percent = Number.isFinite(status.progress) ? Math.max(0, Math.min(100, Math.round(status.progress))) : 0;
  const phaseLabel = status.phase || "Running";
  const phaseIndex = resolvePhaseIndex(status.phase, percent);
  setProgress(percent, phaseLabel, phaseIndex);

  if (Number.isFinite(status.elapsedSeconds)) {
    elapsedTime.textContent = formatElapsed(status.elapsedSeconds);
  }

  scanStateMessage.textContent = `${phaseLabel}…`;
  renderNewLogs(Array.isArray(status.logs) ? status.logs : []);
}

/** Appends only log entries the UI hasn't rendered yet, tracked by count,
 * so repeated polls never duplicate activity log rows. */
function renderNewLogs(logs) {
  if (logs.length <= renderedLogCount) return;
  const newEntries = logs.slice(renderedLogCount);
  newEntries.forEach((entry) => {
    const elapsedSecondsForEntry = (performance.now() - scanStartedAt) / 1000;
    addActivityEntry(elapsedSecondsForEntry, {
      type: ["info", "success", "warning", "error"].includes(entry.type) ? entry.type : "info",
      message: entry.message || ""
    });
  });
  renderedLogCount = logs.length;
}

/** Fetches the finished scan's results and renders the completed dashboard. */
async function finishApiScan(operationToken) {
  clearScheduledWork();

  let response;
  try {
    response = await fetch(`${API_BASE_URL}/scans/${encodeURIComponent(activeScanId)}/results`);
  } catch {
    if (operationToken !== scanOperationToken) return;
    showScanError(new Error("Lost connection to the SQLyse backend while fetching results."));
    return;
  }

  if (operationToken !== scanOperationToken) return;

  if (!response.ok) {
    const message = await readErrorMessage(response, "The backend scan could not be completed.");
    showScanError(new Error(message));
    return;
  }

  let result;
  try {
    result = await parseJsonResponse(response);
  } catch (error) {
    if (operationToken !== scanOperationToken) return;
    showScanError(error);
    return;
  }

  if (operationToken !== scanOperationToken) return;

  currentScanResult = result;
  selectedFindingId = result.findings?.[0]?.id || null;
  elapsedTime.textContent = formatElapsed(result.durationSeconds ?? 0);
  setProgress(100, "Scan Complete", SCAN_PHASES.length - 1, true);
  scanStateMessage.textContent = result.isMockData
    ? "Backend mock scan complete. Review the generated findings below."
    : "Scan complete. Review the findings below.";
  renderCompletedDashboard();

  const nextState = (result.findings?.length || 0) > 0 ? APP_STATES.COMPLETE : APP_STATES.NO_FINDINGS;
  transitionTo(nextState);
  requestAnimationFrame(() => completionContent.classList.add("is-visible"));

  document.querySelectorAll(".reveal-section").forEach((section, index) => {
    const timer = window.setTimeout(() => section.classList.add("is-revealed"), reducedMotion.matches ? 0 : index * 110);
    revealTimers.push(timer);
  });
}

/** Cancels the active scan via the backend, then returns the UI to IDLE. */
async function cancelApiScan() {
  if (applicationState !== APP_STATES.SCANNING || cancelInFlight) return;
  if (!activeScanId) {
    handleScanCancelledExternally();
    return;
  }

  cancelInFlight = true;
  const scanIdToCancel = activeScanId;

  try {
    const response = await fetch(`${API_BASE_URL}/scans/${encodeURIComponent(scanIdToCancel)}/cancel`, {
      method: "POST"
    });

    if (!response.ok) {
      // The scan may have completed or failed just before this request
      // landed — that's not an error worth surfacing, just stop trying to
      // cancel and let the next poll (if any) reflect the true state.
      const body = await response.json().catch(() => null);
      if (body?.error && /already (completed|cancelled|failed)/i.test(body.error)) {
        cancelInFlight = false;
        return;
      }
    }
  } catch {
    // Backend unreachable during cancellation; still return the UI to a
    // safe idle state rather than leaving the user stuck mid-scan.
  }

  cancelInFlight = false;
  handleScanCancelledExternally();
}

/** Shared cleanup for both user-initiated and backend-reported cancellation. */
function handleScanCancelledExternally() {
  scanOperationToken++; // invalidate any in-flight poll/result requests
  clearScheduledWork();
  currentScanResult = null;
  selectedFindingId = null;
  activeScanId = null;
  transitionTo(APP_STATES.IDLE);
  showTargetStatus("Scan cancelled.");
  targetUrl.focus();
}

function showScanError(error) {
  scanOperationToken++; // invalidate any in-flight poll/result requests
  clearScheduledWork();
  scanErrorMessage.textContent = error?.message || "The backend scan could not be completed.";
  transitionTo(APP_STATES.SCAN_ERROR);
  const behavior = reducedMotion.matches ? "auto" : "smooth";
  scanErrorPanel.scrollIntoView({ behavior, block: "center" });
}

function showTargetStatus(message) {
  scanTargetStatus.textContent = message;
  scanTargetStatus.hidden = false;
}

function hideTargetStatus() {
  scanTargetStatus.textContent = "";
  scanTargetStatus.hidden = true;
}

function resetCompletedDashboard() {
  completionContent.hidden = true;
  completionContent.classList.remove("is-visible");
  document.querySelectorAll(".reveal-section").forEach((section) => section.classList.remove("is-revealed"));
  overviewMetrics.innerHTML = "";
  findingsTableBody.innerHTML = "";
  noFindingsState.hidden = true;
  filteredEmpty.hidden = true;
  analysisGrid.hidden = false;
  reportFeedback.textContent = "";
}

function renderCompletedDashboard() {
  if (!currentScanResult) return;
  scanId.textContent = currentScanResult.scanId;
  renderOverviewMetrics();

  const hasFindings = currentScanResult.findings.length > 0;
  findingCount.textContent = `${currentScanResult.findings.length} ${currentScanResult.findings.length === 1 ? "finding" : "findings"}`;
  findingsToolbar.hidden = !hasFindings;
  findingsTableWrap.hidden = !hasFindings;
  noFindingsState.hidden = hasFindings;
  analysisGrid.hidden = !hasFindings;

  if (hasFindings) {
    renderFindingsTable();
    renderSelectedAnalysis();
  }
}

function renderOverviewMetrics() {
  overviewMetrics.innerHTML = "";
  METRIC_DEFINITIONS.forEach((definition) => {
    const value = currentScanResult[definition.key];
    const card = document.createElement("article");
    card.className = "metric-card";
    const riskClass = definition.isRisk ? ` risk-${String(value).toLowerCase()}` : "";
    card.innerHTML = `
      <span class="metric-label">${definition.label}</span>
      <strong class="metric-value${riskClass}">${escapeHtml(String(value))}</strong>
      <span class="metric-icon${riskClass}" aria-hidden="true">${definition.icon}</span>
    `;
    overviewMetrics.appendChild(card);
  });
}

function getFilteredFindings() {
  if (!currentScanResult) return [];
  const query = findingSearch.value.trim().toLowerCase();
  return currentScanResult.findings.filter((finding) => {
    const searchable = [finding.title, finding.endpoint, finding.parameter, finding.detection].join(" ").toLowerCase();
    const matchesSearch = !query || searchable.includes(query);
    const matchesSeverity = severityFilter.value === "all" || finding.severity === severityFilter.value;
    const matchesStatus = statusFilter.value === "all" || finding.status === statusFilter.value;
    return matchesSearch && matchesSeverity && matchesStatus;
  });
}

function renderFindingsTable() {
  const findings = getFilteredFindings();
  findingsTableBody.innerHTML = "";
  filteredEmpty.hidden = findings.length > 0;
  findingsTableWrap.hidden = findings.length === 0;

  findings.forEach((finding) => {
    const row = document.createElement("tr");
    row.className = "finding-row";
    row.dataset.findingId = finding.id;
    row.tabIndex = 0;
    row.setAttribute("aria-label", `View details for ${finding.title}`);
    row.setAttribute("aria-expanded", "false");
    if (finding.id === selectedFindingId) row.classList.add("is-selected");
    row.innerHTML = `
      <td data-label="Finding"><span class="finding-name">${escapeHtml(finding.title)}</span></td>
      <td data-label="Endpoint">${escapeHtml(finding.endpoint)}</td>
      <td data-label="Parameter">${escapeHtml(finding.parameter)}</td>
      <td data-label="Detection">${escapeHtml(finding.detection)}</td>
      <td data-label="Severity"><span class="severity-badge risk-${finding.severity.toLowerCase()}">${escapeHtml(finding.severity)}</span></td>
      <td data-label="Confidence">${finding.confidence}%</td>
      <td data-label="Status"><span class="status-badge${finding.status === "Reviewed" ? " is-reviewed" : ""}">${escapeHtml(finding.status)}</span></td>
      <td data-label="Action"><button class="view-details-button" type="button" data-finding-id="${finding.id}" aria-controls="findingDrawer" aria-expanded="false">View details</button></td>
    `;
    findingsTableBody.appendChild(row);
  });
}

function clearFindingFilters() {
  findingSearch.value = "";
  severityFilter.value = "all";
  statusFilter.value = "all";
  renderFindingsTable();
}

function getFindingById(id) {
  return currentScanResult?.findings.find((finding) => finding.id === id) || null;
}

function getAffectedUrl(finding) {
  try {
    return new URL(finding.endpoint, currentScanResult.targetUrl).href;
  } catch {
    return `${currentScanResult.targetUrl}${finding.endpoint}`;
  }
}

function renderSelectedAnalysis() {
  const finding = getFindingById(selectedFindingId) || currentScanResult?.findings[0];
  if (!finding) return;
  selectedFindingId = finding.id;
  analysisFindingTitle.textContent = finding.title;
  analysisCopy.textContent = finding.analysis;
  verificationNote.textContent = finding.verification;
  remediationList.innerHTML = "";

  finding.recommendations.forEach((recommendation) => {
    const item = document.createElement("li");
    item.className = "remediation-item";
    item.innerHTML = `
      <h3>${escapeHtml(recommendation.title)}</h3>
      <span class="priority-label is-${recommendation.priority.toLowerCase()}">${escapeHtml(recommendation.priority)} priority</span>
      <p>${escapeHtml(recommendation.explanation)}</p>
    `;
    remediationList.appendChild(item);
  });
}

function renderDefinitionList(container, entries) {
  container.innerHTML = "";
  entries.forEach(([label, value]) => {
    const item = document.createElement("div");
    const term = document.createElement("dt");
    const description = document.createElement("dd");
    term.textContent = label;
    description.textContent = value;
    item.append(term, description);
    container.appendChild(item);
  });
}

function renderFindingDetails(finding) {
  detailTitle.textContent = finding.title;
  detailSeverity.textContent = finding.severity;
  detailSeverity.className = `severity-badge risk-${finding.severity.toLowerCase()}`;
  detailConfidence.textContent = `${finding.confidence}% confidence`;
  detailStatus.textContent = finding.status;
  detailStatus.className = `status-badge${finding.status === "Reviewed" ? " is-reviewed" : ""}`;

  renderDefinitionList(technicalContext, [
    ["Affected URL", getAffectedUrl(finding)],
    ["HTTP method", finding.httpMethod],
    ["Parameter", finding.parameter],
    ["Detection method", finding.detection],
    ["Response status comparison", finding.responseStatusComparison],
    ["Response length difference", finding.responseLengthDifference],
    ["Observed database error family", finding.databaseErrorFamily]
  ]);

  detailObserved.textContent = finding.observed;
  detailRisk.textContent = finding.risk;
  detailImpact.textContent = finding.impact;
  detailVerification.textContent = finding.verification;

  renderDefinitionList(evidenceMetadata, [
    ["Baseline response", `${finding.evidence.baselineStatus} · ${finding.evidence.baselineLength}`],
    ["Modified response", `${finding.evidence.modifiedStatus} · ${finding.evidence.modifiedLength}`]
  ]);
  responseExcerpt.textContent = finding.evidence.excerpt;
  markReviewedButton.disabled = finding.status === "Reviewed";
  markReviewedLabel.textContent = finding.status === "Reviewed" ? "Reviewed" : "Mark as Reviewed";
}

function openFindingDetails(id, trigger = document.activeElement) {
  const finding = getFindingById(id);
  if (!finding) return;
  selectedFindingId = finding.id;
  lastFocusedElement = trigger;
  renderSelectedAnalysis();
  syncSelectedFindingRows();
  renderFindingDetails(finding);

  findingBackdrop.hidden = false;
  findingDrawer.hidden = false;
  findingDrawer.setAttribute("aria-hidden", "false");
  body.classList.add("detail-open");
  updateDetailExpandedState(true);

  requestAnimationFrame(() => {
    findingBackdrop.classList.add("is-visible");
    findingDrawer.classList.add("is-open");
  });
  window.setTimeout(() => closeDetailButton.focus(), reducedMotion.matches ? 0 : 80);
}

function closeFindingDetails(returnFocus = true) {
  if (findingDrawer.hidden) return;
  findingBackdrop.classList.remove("is-visible");
  findingDrawer.classList.remove("is-open");
  findingDrawer.setAttribute("aria-hidden", "true");
  body.classList.remove("detail-open");
  updateDetailExpandedState(false);

  window.setTimeout(() => {
    findingBackdrop.hidden = true;
    findingDrawer.hidden = true;
  }, reducedMotion.matches ? 0 : 340);

  if (returnFocus) {
    const fallbackFocusTarget = document.querySelector(`.view-details-button[data-finding-id="${selectedFindingId}"]`)
      || document.querySelector(`.finding-row[data-finding-id="${selectedFindingId}"]`);
    const focusTarget = lastFocusedElement instanceof HTMLElement && lastFocusedElement.isConnected
      ? lastFocusedElement
      : fallbackFocusTarget;
    focusTarget?.focus();
  }
}

function syncSelectedFindingRows() {
  document.querySelectorAll(".finding-row").forEach((row) => {
    row.classList.toggle("is-selected", row.dataset.findingId === selectedFindingId);
  });
}

function updateDetailExpandedState(isExpanded) {
  document.querySelectorAll(".finding-row, .view-details-button").forEach((element) => {
    const id = element.dataset.findingId;
    element.setAttribute("aria-expanded", String(isExpanded && id === selectedFindingId));
  });
}

function markSelectedFindingReviewed() {
  const finding = getFindingById(selectedFindingId);
  if (!finding || finding.status === "Reviewed") return;
  finding.status = "Reviewed";
  renderFindingsTable();
  syncSelectedFindingRows();
  updateDetailExpandedState(true);
  renderFindingDetails(finding);
  renderSelectedAnalysis();
  showToast("Finding marked as reviewed.");
}

function getFindingExport(finding) {
  return {
    isMockData: currentScanResult.isMockData,
    disclaimer: currentScanResult.disclaimer,
    scanId: currentScanResult.scanId,
    targetUrl: currentScanResult.targetUrl,
    affectedUrl: getAffectedUrl(finding),
    ...finding
  };
}

async function copyText(text, successMessage) {
  const copyWithFallback = () => {
    const textarea = document.createElement("textarea");
    textarea.value = text;
    textarea.setAttribute("readonly", "");
    textarea.style.position = "fixed";
    textarea.style.opacity = "0";
    document.body.appendChild(textarea);
    textarea.select();
    const copied = document.execCommand("copy");
    textarea.remove();
    if (!copied) throw new Error("Copy command was not available.");
  };

  try {
    if (navigator.clipboard && window.isSecureContext) {
      try {
        await navigator.clipboard.writeText(text);
      } catch {
        copyWithFallback();
      }
    } else {
      copyWithFallback();
    }
    showToast(successMessage);
    return true;
  } catch {
    showToast("Copy was not available. Select and copy the content manually.");
    return false;
  }
}

function showToast(message) {
  window.clearTimeout(toastTimer);
  appToast.textContent = message;
  appToast.hidden = false;
  toastTimer = window.setTimeout(() => {
    appToast.hidden = true;
  }, 2600);
}

function downloadBlob(content, filename, type) {
  const blob = new Blob([content], { type });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.setTimeout(() => URL.revokeObjectURL(link.href), 0);
}

function toCsvCell(value) {
  return `"${String(value ?? "").replaceAll('"', '""')}"`;
}

function exportFindingsCsv(findings, suffix = "findings") {
  const headers = ["Finding", "Endpoint", "Parameter", "Detection", "Severity", "Confidence", "Status"];
  const rows = findings.map((finding) => [
    finding.title,
    finding.endpoint,
    finding.parameter,
    finding.detection,
    finding.severity,
    `${finding.confidence}%`,
    finding.status
  ]);
  const csv = [headers, ...rows].map((row) => row.map(toCsvCell).join(",")).join("\r\n");
  downloadBlob(csv, `${currentScanResult.scanId}-${suffix}.csv`, "text/csv;charset=utf-8");
}

function buildSummary() {
  const lines = [
    "SQLyse scan summary",
    `Scan ID: ${currentScanResult.scanId}`,
    `Target: ${currentScanResult.targetUrl}`,
    `Duration: ${currentScanResult.durationSeconds} seconds`,
    `Pages scanned: ${currentScanResult.pagesScanned}`,
    `Forms discovered: ${currentScanResult.formsDiscovered}`,
    `Parameters tested: ${currentScanResult.parametersTested}`,
    `Findings requiring review: ${currentScanResult.findings.length}`,
    `Overall risk: ${currentScanResult.overallRisk}`
  ];
  if (currentScanResult.disclaimer) lines.push(currentScanResult.disclaimer);
  return lines.join("\n");
}

/**
 * Downloads a generated report from the backend for the completed scan.
 * Verifies response.ok, converts to a Blob, and triggers a browser
 * download using the server's Content-Disposition filename when present.
 */
async function downloadReport(format) {
  if (!currentScanResult?.scanId) return;
  const scanIdForReport = currentScanResult.scanId;

  try {
    const response = await fetch(
      `${API_BASE_URL}/scans/${encodeURIComponent(scanIdForReport)}/report?format=${encodeURIComponent(format)}`
    );

    if (!response.ok) {
      const message = await readErrorMessage(response, `Could not download the ${format.toUpperCase()} report.`);
      reportFeedback.textContent = message;
      showToast(message);
      return;
    }

    const blob = await response.blob();
    let filename = `${scanIdForReport}.${format}`;
    const disposition = response.headers.get("Content-Disposition") || "";
    const filenameMatch = disposition.match(/filename="?([^";]+)"?/i);
    if (filenameMatch?.[1]) filename = filenameMatch[1].trim();

    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.setTimeout(() => URL.revokeObjectURL(link.href), 0);

    const message = `${format.toUpperCase()} report downloaded.`;
    reportFeedback.textContent = message;
    showToast(message);
  } catch {
    const message = `Could not download the ${format.toUpperCase()} report. Confirm the backend is running.`;
    reportFeedback.textContent = message;
    showToast(message);
  }
}

function resetForNewScan() {
  scanOperationToken++; // invalidate any in-flight poll/result requests
  clearScheduledWork();
  closeFindingDetails(false);
  currentScanResult = null;
  selectedFindingId = null;
  activeScanId = null;
  cancelInFlight = false;
  renderedLogCount = 0;
  lastSubmittedUrl = "";
  resetActivityLog();
  resetCompletedDashboard();
  clearFindingFilters();
  clearValidationError();
  hideTargetStatus();
  targetUrl.value = "";
  setProgress(0, "Initializing", 0);
  transitionTo(APP_STATES.IDLE);

  const behavior = reducedMotion.matches ? "auto" : "smooth";
  document.querySelector(".scan-target").scrollIntoView({ behavior, block: "center" });
  window.setTimeout(() => targetUrl.focus(), reducedMotion.matches ? 0 : 450);
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

scanForm.addEventListener("submit", (event) => {
  event.preventDefault();
  if (applicationState === APP_STATES.SCANNING) return;

  const value = targetUrl.value.trim();
  const validationMessage = validateTarget(value);
  if (validationMessage) {
    showValidationError(validationMessage);
    return;
  }

  startApiScan(value);
});

targetUrl.addEventListener("input", () => {
  if (urlError.textContent) {
    clearValidationError();
    if (applicationState === APP_STATES.VALIDATION_ERROR) transitionTo(APP_STATES.IDLE);
  }
  hideTargetStatus();
});

cancelScanButton.addEventListener("click", cancelApiScan);
retryScanButton.addEventListener("click", () => {
  if (lastSubmittedUrl) startApiScan(lastSubmittedUrl);
});

copyLogsButton.addEventListener("click", () => {
  if (!logEntries.length) {
    showToast("No scan activity is available to copy yet.");
    return;
  }
  const logs = logEntries.map((entry) => `[${entry.timestamp}] ${entry.message}`).join("\n");
  copyText(logs, "Scan activity copied.");
});

[findingSearch, severityFilter, statusFilter].forEach((control) => {
  control.addEventListener("input", renderFindingsTable);
  control.addEventListener("change", renderFindingsTable);
});

clearFiltersButton.addEventListener("click", clearFindingFilters);
filteredExportButton.addEventListener("click", () => exportFindingsCsv(getFilteredFindings(), "filtered-findings"));

findingsTableBody.addEventListener("click", (event) => {
  const row = event.target.closest(".finding-row");
  if (!row) return;
  const trigger = event.target.closest("button") || row;
  openFindingDetails(row.dataset.findingId, trigger);
});

findingsTableBody.addEventListener("keydown", (event) => {
  if (!event.target.classList.contains("finding-row")) return;
  if (event.key === "Enter" || event.key === " ") {
    event.preventDefault();
    openFindingDetails(event.target.dataset.findingId, event.target);
  }
});

closeDetailButton.addEventListener("click", () => closeFindingDetails());
findingBackdrop.addEventListener("click", () => closeFindingDetails());
markReviewedButton.addEventListener("click", markSelectedFindingReviewed);
copyFindingButton.addEventListener("click", () => {
  const finding = getFindingById(selectedFindingId);
  if (finding) copyText(JSON.stringify(getFindingExport(finding), null, 2), "Finding copied.");
});
downloadFindingButton.addEventListener("click", () => {
  const finding = getFindingById(selectedFindingId);
  if (finding) downloadBlob(JSON.stringify(getFindingExport(finding), null, 2), `${finding.id}.json`, "application/json");
});

downloadPdfButton.addEventListener("click", () => downloadReport("pdf"));
exportJsonButton.addEventListener("click", () => downloadReport("json"));
exportCsvButton.addEventListener("click", () => downloadReport("csv"));

copySummaryButton.addEventListener("click", () => {
  if (currentScanResult) copyText(buildSummary(), "Scan summary copied.");
});

newScanButton.addEventListener("click", resetForNewScan);

document.addEventListener("keydown", (event) => {
  if (!findingDrawer.classList.contains("is-open")) return;

  if (event.key === "Escape") {
    event.preventDefault();
    closeFindingDetails();
    return;
  }

  if (event.key === "Tab") {
    const focusable = [...findingDrawer.querySelectorAll("button:not(:disabled), a[href], input:not(:disabled), select:not(:disabled), [tabindex]:not([tabindex='-1'])")];
    if (!focusable.length) return;
    const first = focusable[0];
    const last = focusable[focusable.length - 1];
    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first.focus();
    }
  }
});

renderTeamMembers();
renderProjectContact();
currentYear.textContent = String(new Date().getFullYear());
setupContentReveals();
setupActiveNavigationTracking();
transitionTo(APP_STATES.IDLE);