// appstatic/js/library-pagination.js
(function() {
  // Global namespace to prevent duplicate event bindings across HTMX navigations
  const GLOBAL_NS_KEY = "__FC_LIBPAG";
  window[GLOBAL_NS_KEY] = window[GLOBAL_NS_KEY] || {};
  const NS = window[GLOBAL_NS_KEY];

  function qs(sel, root = document) {
    return root.querySelector(sel);
  }

  function qsa(sel, root = document) {
    return Array.from(root.querySelectorAll(sel));
  }

  const API_BASE = "/api/swatch/";
  let nextUrl = null;
  let loading = false;
  let observer = null;

  function parseFilterValues() {
    try {
      const el = qs("#filterValues");
      if (!el) return {};
      const txt = el.textContent || el.innerText || "{}";
      let data = JSON.parse(txt);
      // If the server accidentally double-encoded the JSON, parse again
      if (typeof data === "string") {
        try {
          data = JSON.parse(data);
        } catch {/* leave as string */
        }
      }
      // Support legacy key 'f' for search; normalize to 'q' if present
      if (data && data.f && !data.q) data.q = data.f;
      return (data && typeof data === "object") ? data : {};
    } catch {
      return {};
    }
  }

  function toQuery(params) {
    const u = new URLSearchParams();
    Object.entries(params).forEach(([k, v]) => {
      if (v !== undefined && v !== null && v !== "") u.set(k, v);
    });
    return u.toString();
  }

  function createCardElement(s) {
    const el = document.createElement("swatch-card");
    el.setAttribute("id", s.id);
    el.setAttribute("color", s.hex_color);
    el.setAttribute("mfr", s.manufacturer?.name || "");
    el.setAttribute("name", s.color_name);
    el.setAttribute("type", s.filament_type?.name || "");
    if (s.slug) el.setAttribute("slug", s.slug);
    el.setAttribute("td", s.td == null ? "None" : String(s.td));
    // Always set an explicit boolean string so the custom element can parse deterministically
    // This avoids cases where a missing attribute is treated as unavailable by default
    el.setAttribute("available", String(Boolean(s.is_available)));
    if (s.card_img) el.setAttribute("cardImgUrl", s.card_img);
    if (typeof s.distance !== "undefined") el.setAttribute("distance", String(s.distance));
    return el;
  }

  function createCardBox(s) {
    // Mirror the server-rendered structure so Masonry treats each card as an item
    const box = document.createElement("div");
    box.className = "col-md-6 col-lg-4 col-xl-4 col-xxl-3 swatchbox";
    const card = createCardElement(s);
    box.appendChild(card);
    return box;
  }

  function showSpinner() {
    const sp = qs("#infiniteLoadSpinner");
    if (!sp) return;
    sp.classList.add("htmx-request"); // emulate htmx indicator
    sp.setAttribute("aria-busy", "true");
  }

  function hideSpinner() {
    const sp = qs("#infiniteLoadSpinner");
    if (!sp) return;
    sp.classList.remove("htmx-request");
    sp.removeAttribute("aria-busy");
  }

  function afterAppend(newBoxes) {
    // Re-process HTMX in case there are any attributes inside cards
    const grid = qs("#deck-of-many-things");
    if (window.htmx && grid) window.htmx.process(grid);

    // Re-init lazy loader for images if available
    if (typeof window.lazyloadimages === "function") {
      try {
        window.lazyloadimages();
      } catch {/* noop */
      }
    }

    // Notify Masonry about new items
    try {
      if (window.jQuery) {
        const $deck = window.jQuery("#deck-of-many-things");
        if ($deck && $deck.length && typeof $deck.masonry === "function") {
          $deck.masonry("appended", window.jQuery(newBoxes));
        }
      }
    } catch (e) {
      console.warn("Masonry append failed", e);
    }
  }

  async function fetchWithRetry(url, opts = {}, retries = 2, backoffMs = 400) {
    let lastErr;
    for (let attempt = 0; attempt <= retries; attempt++) {
      try {
        const res = await fetch(url, { credentials: "same-origin", ...opts });
        if (!res.ok) {
          const err = new Error("HTTP " + res.status);
          err.status = res.status;
          err.response = res;
          throw err;
        }
        return res;
      } catch (e) {
        lastErr = e;
        // Do not retry on 404 — treat as terminal (e.g., end of pagination)
        if (e && e.status === 404) break;
        if (attempt === retries) break;
        const delay = backoffMs * Math.pow(2, attempt);
        await new Promise(r => setTimeout(r, delay));
      }
    }
    throw lastErr;
  }

  async function fetchAndAppend(url) {
    if (loading || !url) return;
    loading = true;
    showSpinner();
    try {
      const res = await fetchWithRetry(url);
      const data = await res.json();
      const grid = qs("#deck-of-many-things");
      if (!grid) return;
      const frag = document.createDocumentFragment();
      const newBoxes = [];
      for (const s of (data.results || [])) {
        const box = createCardBox(s);
        newBoxes.push(box);
        frag.appendChild(box);
      }
      grid.appendChild(frag);
      afterAppend(newBoxes);
      nextUrl = data.next;
      if (data[window.__FC_NO_MORE_CONSTANT]) {
        const container = qs("#swatch-container");
        if (container) container.setAttribute("data-" + window.__FC_NO_MORE_CONSTANT, "true");
      }
      if (!nextUrl) observer && observer.disconnect();
    } catch (e) {
      if (e && e.status === 404) {
        // Gracefully end infinite scroll on 404 without showing an error toast
        nextUrl = null;
        const container = qs("#swatch-container");
        if (container) container.setAttribute("data-" + window.__FC_NO_MORE_CONSTANT, "true");
        try {
          if (observer && typeof observer.disconnect === "function") observer.disconnect();
        } catch {/* noop */}
        console.info("No more swatches to load (404).");
      } else {
        console.error("Failed to load more swatches", e);
        showToastError("Failed to load more swatches. Please try again later.");
      }
      // retries are handled in fetchWithRetry; surface error toast after final failure
    } finally {
      hideSpinner();
      loading = false;
    }
  }

  function installObserver() {
    const sentinel = qs("#infinite-scroll-sentinel");
    if (!sentinel) return;
    // Disconnect any prior observer to avoid duplicate fetch triggers
    if (observer && typeof observer.disconnect === "function") {
      try {
        observer.disconnect();
      } catch {/* noop */
      }
    }
    observer = new IntersectionObserver((entries) => {
      for (const entry of entries) {
        if (entry.isIntersecting && nextUrl) fetchAndAppend(nextUrl);
      }
    });
    observer.observe(sentinel);
  }

  function removeHTMXInfinite() {
    const lastBox = qsa("#deck-of-many-things .swatchbox").pop();
    if (!lastBox) return;
    // Remove known htmx infinite-scroll attributes to prevent double-loading
    const attrs = ["hx-get", "hx-trigger", "hx-swap", "hx-headers", "hx-target", "hx-push-url", "hx-vals", "hx-indicator"];
    attrs.forEach(a => lastBox.removeAttribute(a));
  }

  function init() {
    const container = qs("#swatch-container");
    if (!container || container.dataset.jsonPagination !== "true") return;

    // If we've already reached the end, or if we've already initialized, don't restart.
    if (container.getAttribute("data-" + window.__FC_NO_MORE_CONSTANT) === "true") return;
    if (nextUrl !== null) return;

    // Always reset when (re)initializing after HTMX swaps
    try {
      if (observer && typeof observer.disconnect === "function") observer.disconnect();
    } catch {/* noop */
    }
    observer = null;
    loading = false;
    nextUrl = null;

    const filters = parseFilterValues(); // { m, cf, mfr, ft, td, q/f, ... }

    // Map legacy/route params to API filter params
    const apiFilters = { ...filters };
    if (apiFilters.mfr && !apiFilters["manufacturer__slug"]) {
      apiFilters["manufacturer__slug"] = apiFilters.mfr;
    }

    // Align client page size with API (SmallPageNumberPagination.page_size = 15)
    const params = { ...apiFilters, page: 1, page_size: 15 };

    // Hybrid mode: first page is server-rendered; start at next page after whatever the server rendered
    const startPage = Number(window.infiniteScrollStartPage || 1);
    // Avoid leaking the previous value across future inits if a new page doesn't set it
    try {
      delete window.infiniteScrollStartPage;
    } catch {/* noop */
    }
    nextUrl = API_BASE + "?" + toQuery({ ...params, page: startPage + 1 });

    removeHTMXInfinite();
    installObserver();
  }

  // Expose to window so templates can call it
  window.initLibraryPagination = init;

  // Auto-init on DOMContentLoaded and HTMX onLoad (bind once per session)
  if (!NS.eventsBound) {
    document.addEventListener("DOMContentLoaded", function() {
      try {
        init();
      } catch {/* noop */
      }
    });
    if (window.htmx && window.htmx.onLoad) {
      window.htmx.onLoad(function() {
        try {
          init();
        } catch {/* noop */
        }
      });
    }
    NS.eventsBound = true;
  }

  // Fallback: if the script loads after DOMContentLoaded (common on first page load),
  // ensure initialization still happens immediately.
  if (document.readyState === "interactive" || document.readyState === "complete") {
    try {
      init();
    } catch {/* noop */}
  }

  // Proactive cleanup before HTMX swaps to avoid any lingering observers
  if (!NS.cleanupBound) {
    document.body.addEventListener("htmx:beforeSwap", function(evt) {
      const target = evt.detail.target;
      if (!target) return;
      // Only reset if the swap is actually going to replace or include our container
      if (target.id !== "swatch-container" && !target.querySelector("#swatch-container")) return;

      try {
        if (observer && typeof observer.disconnect === "function") observer.disconnect();
      } catch {/* noop */
      }
      observer = null;
      loading = false;
      nextUrl = null;
    });
    NS.cleanupBound = true;
  }
})();
