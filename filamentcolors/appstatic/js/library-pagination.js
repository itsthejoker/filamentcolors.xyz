// appstatic/js/library-pagination.js
(function(){
  function qs(sel, root=document){ return root.querySelector(sel) }
  function qsa(sel, root=document){ return Array.from(root.querySelectorAll(sel)) }

  const API_BASE = '/api/swatch/'
  let nextUrl = null
  let loading = false
  let observer = null

  function parseFilterValues(){
    try {
      const el = qs('#filterValues')
      if (!el) return {}
      const txt = el.textContent || el.innerText || '{}'
      let data = JSON.parse(txt)
      // If the server accidentally double-encoded the JSON, parse again
      if (typeof data === 'string') {
        try { data = JSON.parse(data) } catch {/* leave as string */}
      }
      // Support legacy key 'f' for search; normalize to 'q' if present
      if (data && data.f && !data.q) data.q = data.f
      return (data && typeof data === 'object') ? data : {}
    } catch { return {} }
  }

  function toQuery(params){
    const u = new URLSearchParams()
    Object.entries(params).forEach(([k,v]) => {
      if (v !== undefined && v !== null && v !== '') u.set(k, v)
    })
    return u.toString()
  }

  function createCardElement(s){
    const el = document.createElement('swatch-card')
    el.setAttribute('id', s.id)
    el.setAttribute('color', s.hex_color)
    el.setAttribute('mfr', s.manufacturer?.name || '')
    el.setAttribute('name', s.color_name)
    el.setAttribute('type', s.filament_type?.name || '')
    if (s.slug) el.setAttribute('slug', s.slug)
    el.setAttribute('td', s.td == null ? 'None' : String(s.td))
    if (s.is_available) el.setAttribute('available', '')
    if (s.card_img) el.setAttribute('cardImgUrl', s.card_img)
    if (typeof s.distance !== 'undefined') el.setAttribute('distance', String(s.distance))
    return el
  }

  function createCardBox(s){
    // Mirror the server-rendered structure so Masonry treats each card as an item
    const box = document.createElement('div')
    box.className = 'col-md-6 col-lg-4 col-xl-4 col-xxl-3 swatchbox'
    const card = createCardElement(s)
    box.appendChild(card)
    return box
  }

  function showSpinner(){
    const sp = qs('#infiniteLoadSpinner')
    if (!sp) return
    sp.classList.add('htmx-request') // emulate htmx indicator
    sp.setAttribute('aria-busy', 'true')
  }
  function hideSpinner(){
    const sp = qs('#infiniteLoadSpinner')
    if (!sp) return
    sp.classList.remove('htmx-request')
    sp.removeAttribute('aria-busy')
  }

  function afterAppend(newBoxes){
    // Re-process HTMX in case there are any attributes inside cards
    const grid = qs('#deck-of-many-things')
    if (window.htmx && grid) window.htmx.process(grid)

    // Re-init lazy loader for images if available
    if (typeof window.lazyloadimages === 'function') {
      try { window.lazyloadimages() } catch {/* noop */}
    }

    // Notify Masonry about new items
    try {
      if (window.jQuery) {
        const $deck = window.jQuery('#deck-of-many-things')
        if ($deck && $deck.length && typeof $deck.masonry === 'function') {
          $deck.masonry('appended', window.jQuery(newBoxes))
        }
      }
    } catch (e) {
      console.warn('Masonry append failed', e)
    }
  }

  async function fetchAndAppend(url){
    if (loading || !url) return
    loading = true
    showSpinner()
    try {
      const res = await fetch(url, { credentials: 'same-origin' })
      if (!res.ok) throw new Error('HTTP '+res.status)
      const data = await res.json()
      const grid = qs('#deck-of-many-things')
      if (!grid) return
      const frag = document.createDocumentFragment()
      const newBoxes = []
      for (const s of (data.results || [])) {
        const box = createCardBox(s)
        newBoxes.push(box)
        frag.appendChild(box)
      }
      grid.appendChild(frag)
      afterAppend(newBoxes)
      nextUrl = data.next
      if (!nextUrl) observer && observer.disconnect()
    } catch (e) {
      console.error('Failed to load more swatches', e)
      // TODO: render an inline alert with retry
    } finally {
      hideSpinner()
      loading = false
    }
  }

  function installObserver(){
    const sentinel = qs('#infinite-scroll-sentinel')
    if (!sentinel) return
    // Disconnect any prior observer to avoid duplicate fetch triggers
    if (observer && typeof observer.disconnect === 'function') {
      try { observer.disconnect() } catch {/* noop */}
    }
    observer = new IntersectionObserver((entries) => {
      for (const entry of entries) {
        if (entry.isIntersecting && nextUrl) fetchAndAppend(nextUrl)
      }
    })
    observer.observe(sentinel)
  }

  function removeHTMXInfinite(){
    const lastBox = qsa('#deck-of-many-things .swatchbox').pop()
    if (!lastBox) return
    // Remove known htmx infinite-scroll attributes to prevent double-loading
    const attrs = ['hx-get','hx-trigger','hx-swap','hx-headers','hx-target','hx-push-url','hx-vals','hx-indicator']
    attrs.forEach(a => lastBox.removeAttribute(a))
  }

  function init(){
    const container = qs('#swatch-container')
    if (!container || container.dataset.jsonPagination !== 'true') return

    // Single-init guard to prevent duplicate observers/fetches on DOMContentLoaded + htmx.onLoad
    if (window.__libraryPaginationInitDone) return
    window.__libraryPaginationInitDone = true

    const filters = parseFilterValues() // { m, cf, mfr, ft, td, q/f, ... }

    // Map legacy/route params to API filter params
    const apiFilters = { ...filters }
    if (apiFilters.mfr && !apiFilters['manufacturer__slug']) {
      apiFilters['manufacturer__slug'] = apiFilters.mfr
    }

    // Align client page size with API (SmallPageNumberPagination.page_size = 15)
    const params = { ...apiFilters, page: 1, page_size: 15 }

    // Hybrid mode: first page is server-rendered; start at next page after whatever the server rendered
    const startPage = Number(window.infiniteScrollStartPage || 1)
    nextUrl = API_BASE + '?' + toQuery({ ...params, page: startPage + 1 })

    removeHTMXInfinite()
    installObserver()
  }

  // Expose to window so templates can call it
  window.initLibraryPagination = init

  // Auto-init on DOMContentLoaded and HTMX onLoad
  document.addEventListener('DOMContentLoaded', function(){
    try { init() } catch {/* noop */}
  })
  if (window.htmx && window.htmx.onLoad) {
    window.htmx.onLoad(function(){
      try { init() } catch {/* noop */}
    })
  }
})()
