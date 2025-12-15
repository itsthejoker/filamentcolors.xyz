class Card extends HTMLElement {

  constructor() {
    super();
    this.retrieveAttrs();
    this.selected = this.hasAttribute('selected');
    this._didLongPress = false;
    this._preventContextMenu = (e) => e.preventDefault();
    // Touch tracking for scroll-vs-tap discrimination
    this._touchMoved = false;
    this._touchStartX = 0;
    this._touchStartY = 0;
    this._suppressClickUntil = 0;
    this._onTouchStartOverlay = (e) => {
      const t = e.touches && e.touches[0];
      if (!t) return;
      this._touchMoved = false;
      this._touchStartX = t.clientX;
      this._touchStartY = t.clientY;
    };
    this._onTouchMoveOverlay = (e) => {
      const t = e.touches && e.touches[0];
      if (!t) return;
      const dx = Math.abs(t.clientX - this._touchStartX);
      const dy = Math.abs(t.clientY - this._touchStartY);
      if (dx > 10 || dy > 10) {
        this._touchMoved = true;
        // Suppress potential synthetic click after a touch-scroll
        this._suppressClickUntil = Date.now() + 1000;
      }
    };
    this._onTouchCancelOverlay = () => {
      this._touchMoved = true;
    };
    this._onLongPress = (e) => {
      e.preventDefault();
      e.stopPropagation();
      this._didLongPress = true;
      if (!window.multiselect.collectionModeEnabled) {
        window.multiselect.startCollectionMode()
      }
      this.select();
    };
    // Bind once so we can add/remove reliably
    this._onHostClick = (e) => {
      const overlay = e.target.closest('.card-img-overlay');
      // Ensure the overlay is inside this component instance
      if (!overlay || !this.contains(overlay)) return;
      e.preventDefault();
      e.stopPropagation();
      this.handleSelect();
    };

    // Passthrough handler for the click overlay: forward taps to anchor
    this._onClickOverlayActivate = (e) => {
      // If a long-press just happened, consume this activation
      if (this._didLongPress) {
        this._didLongPress = false;
        e.preventDefault();
        e.stopPropagation();
        return;
      }
      // Ignore synthetic click after a scroll gesture within suppression window
      if (e.type === 'click' && Date.now() < this._suppressClickUntil) {
        e.preventDefault();
        e.stopPropagation();
        return;
      }
      // If the user scrolled, do not treat as a tap
      if (e.type === 'touchend' && this._touchMoved) {
        this._touchMoved = false;
        return;
      }
      // In collection mode, the img-overlay (above) handles selection; do nothing here
      if (window.multiselect && window.multiselect.collectionModeEnabled) return;
      const anchor = this.querySelector('a');
      if (!anchor) return;
      e.preventDefault();
      e.stopPropagation();
      // Programmatically trigger navigation
      anchor.click();
      // Reset movement state after handling
      this._touchMoved = false;
    };

    // Prevent accidental navigation if a long-press happened on the anchor itself
    this._onAnchorClick = (e) => {
      if (this._didLongPress) {
        this._didLongPress = false;
        e.preventDefault();
        e.stopPropagation();
      }
    };
  }

  // component attributes
  static get observedAttributes() {
    return ['selected', 'objId', 'showColormatchExtras', 'hexColor', 'mfr', 'name', 'type', 'slug', 'td', 'available', 'cardImgUrl', 'distance'];
  }

  retrieveAttrs() {
    // normalize color to hex without leading '#'
    const rawColor = this.getAttribute('color') || '000000'
    this.color = ('' + rawColor).replace(/^#/, '')
    this.objId = this.getAttribute('id') || ''
    this.mfr = this.getAttribute('mfr') || ''
    this.name = this.getAttribute('name') || ''
    this.type = this.getAttribute('type') || ''
    this.td = this.getAttribute('td') === "None" ? null : this.getAttribute('td')
    this.showColormatchExtras = this.getAttribute('showColormatchExtras') || ''
    this.slug = this.getAttribute('slug') || ''
    // Availability: two sources
    // - SSR: available="True" or "False" (string)
    // - JSON/DOM: boolean presence attribute (available="" or just present)
    const availAttr = this.getAttribute('available')
    if (availAttr === '') {
      // Presence-only attribute => available
      this.available = true
    } else if (availAttr === null) {
      // Not present
      this.available = false
    } else {
      // String value from SSR; accept common truthy tokens
      this.available = /^(true|1|yes)$/i.test(String(availAttr))
    }
    this.cardImgUrl = this.getAttribute('cardImgUrl') || ''
  }

  attributeChangedCallback(property, oldValue, newValue) {
    if (oldValue === newValue) return;
    // Special handling for 'available' to ensure proper boolean conversion
    if (property === 'available') {
      if (newValue === '') {
        this.available = true;
      } else if (newValue === null) {
        this.available = false;
      } else {
        this.available = /^(true|1|yes)$/i.test(String(newValue));
      }
    } else {
      this[property] = newValue;
    }
  }

  deltaEWarning5To10() {
    return `
      <span
        data-bs-toggle="tooltip"
        data-bs-title="This color will be noticeably different from your target color"
        class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-warning text-black"
        style="z-index: 30"
      >
        <span class="icon-warning me-1"></span>ΔE > 5
        <span class="visually-hidden">
          Delta E distance greater than five! This color will be noticeably different
          from your target color.
        </span>
      </span>
    `
  }

  deltaEWarningMoreThan10() {
    return `
      <span
        data-bs-toggle="tooltip"
        data-bs-title="This color will be VERY different from your target color"
        class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger"
        style="z-index: 30"
      >
        <span class="icon-warning me-1"></span>ΔE > 10
        <span class="visually-hidden">
          Delta E distance is greater than 10! This color will be VERY different from
          your target color!
        </span>
      </span>
    `
  }

  getDeltaEWarning() {
    if (!(this.distance)) {
      return ''
    }
    if (this.distance < 5) {
      return ''
    }
    if (this.distance >= 5 && this.distance < 10) {
      return this.deltaEWarning5To10()
    }
    return this.deltaEWarningMoreThan10()
  }

  getTdBadge() {
    if (!(this.td)) {
      return ''
    }

    return `
      <span
        class="badge text-bg-secondary align-self-end"
        style="font-size:0.6em;margin-bottom:2px"
      >TD: ${this.td}</span>
    `
  }

  getUnavailableBadge() {
    if (this.available) {
      return ''
    }
    return `
      <div class="row">
        <div class="col text-center mb-3 mt-2 d-grid">
          <div
            class="badge text-bg-secondary text-uppercase"
            data-bs-toggle="tooltip"
            data-bs-placement="top"
            data-container="body"
            data-animation="true"
            title="This swatch is not available for purchase from the manufacturer or Amazon.">
            Unavailable
          </div>
        </div>
      </div>
    `
  }

  // connect component
  connectedCallback() {
    this.retrieveAttrs();
    if (!this._rendered) {
      this.render();
      htmx.process(this);
      this._rendered = true;
    }
    if (!this._eventsBound) {
      this.addEventListener('click', this._onHostClick);
      const $clickOverlay = $(this).find('.card-click-overlay');
      $clickOverlay.on('long-press', this._onLongPress);
      // Forward taps/clicks from the overlay to the anchor (passthrough)
      const clickOverlayEl = this.querySelector('.card-click-overlay');
      if (clickOverlayEl) {
        clickOverlayEl.addEventListener('click', this._onClickOverlayActivate, { passive: false });
        clickOverlayEl.addEventListener('touchend', this._onClickOverlayActivate, { passive: false });
        // Track touch movement to distinguish scroll from tap
        clickOverlayEl.addEventListener('touchstart', this._onTouchStartOverlay, { passive: true });
        clickOverlayEl.addEventListener('touchmove', this._onTouchMoveOverlay, { passive: true });
        clickOverlayEl.addEventListener('touchcancel', this._onTouchCancelOverlay, { passive: true });
      }
      // Bind as fallback on the anchor as well
      const anchor = this.querySelector('a');
      if (anchor) {
        $(anchor).on('long-press', this._onLongPress);
        anchor.addEventListener('click', this._onAnchorClick, { passive: false });
        anchor.addEventListener('contextmenu', this._preventContextMenu, { passive: false });
      }
      // fix mobile devices triggering link previews
      this.addEventListener('contextmenu', this._preventContextMenu, { passive: false })
      this._eventsBound = true;
    }

    // Install IntersectionObserver to sync selection when the card becomes visible
    if (!this._ioInstalled) {
      try {
        const onIntersect = (entries, obs) => {
          for (const entry of entries) {
            if (entry.isIntersecting && entry.intersectionRatio > 0) {
              // Determine the swatch/card id to check in the tray
              const idToCheck = this.getAttribute('id') || this.objId || this.id;
              const multiselect = window.multiselect;
              const tray = multiselect && multiselect.swatchTray;
              if (tray && Array.isArray(tray.swatches)) {
                const exists = tray.swatches.some(sw => String(sw.objId) === String(idToCheck));
                // If collection mode is disabled, never allow selection
                if (multiselect && multiselect.collectionModeEnabled === false) {
                  this.deselect(false);
                } else if (exists) {
                  // Select without re-adding to the tray
                  this.select(false);
                } else {
                  this.deselect(false);
                }
              }
              // Fire this check every time the element becomes visible; do not disconnect here
              break;
            }
          }
        };
        this._io = new IntersectionObserver(onIntersect, { root: null, threshold: [0, 0.01, 0.1] });
        this._io.observe(this);
        this._ioInstalled = true;
      } catch (e) {
        // Fail silently if IntersectionObserver is unavailable
        this._ioInstalled = true;
      }
    }
  }

  disconnectedCallback() {
    if (this._eventsBound) {
      this.removeEventListener('click', this._onHostClick);
      // Unbind long-press from overlay
      $(this).find('.card-click-overlay').off('long-press', this._onLongPress);
      // Remove passthrough listeners
      const clickOverlayEl = this.querySelector('.card-click-overlay');
      if (clickOverlayEl) {
        clickOverlayEl.removeEventListener('click', this._onClickOverlayActivate);
        clickOverlayEl.removeEventListener('touchend', this._onClickOverlayActivate);
        clickOverlayEl.removeEventListener('touchstart', this._onTouchStartOverlay);
        clickOverlayEl.removeEventListener('touchmove', this._onTouchMoveOverlay);
        clickOverlayEl.removeEventListener('touchcancel', this._onTouchCancelOverlay);
      }
      // Unbind from anchor
      const anchor = this.querySelector('a');
      if (anchor) {
        $(anchor).off('long-press', this._onLongPress);
        anchor.removeEventListener('click', this._onAnchorClick);
        anchor.removeEventListener('contextmenu', this._preventContextMenu);
      }
      // Remove contextmenu prevention on host
      this.removeEventListener('contextmenu', this._preventContextMenu);
      this._eventsBound = false;
    }
    // Clean up IntersectionObserver if present
    if (this._io && typeof this._io.disconnect === 'function') {
      try { this._io.disconnect(); } catch (e) {}
      this._io = null;
    }
  }

  render() {
    this.innerHTML = `
    <div
      id="${this.objId}"
      class="card ${this.showColormatchExtras ? "mb-2" : "mb-4"} shadow-sm swatchcard cardBox rounded-4 anim mx-auto position-relative"
      style="width: 18rem; min-width: 18rem"
      data-swatch-id="${this.swatchId}"
      data-color="${this.color.toUpperCase()}"
      data-mfr="${this.mfr}"
      data-name="${this.name}"
      data-type="${this.type}"
    >
      <div class="card-img-overlay p-0"></div>
      <div class="card-click-overlay p-0"></div>
       ${this.getDeltaEWarning()}
      <a
        href="/swatch/${this.slug}"
        hx-swap="morph:innerHTML show:window:top"
        hx-target="#main"
        hx-indicator="#loading"
        hx-push-url="true"
      >
        <div class="card-img-container">
          <div 
            class="card-img-top img-fluid layer position-relative"
            style="background-color: #${this.color}; height: 89px;border-top-left-radius: var(--bs-border-radius-xl); border-top-right-radius: 2em"
           >
            <div class="position-absolute end-0" style="background-color: white; height: 89px; width: 89px;border-top-left-radius: var(--bs-border-radius-xl); border-top-right-radius: var(--bs-border-radius-xl)"></div>
            <img class="lazy-load-image position-absolute end-0"
               src='data:image/svg+xml;charset=utf-8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 287.1 89"><defs><style>.c1 {fill: %23fff} .c1, .c2, .c3, .c4, .c5 {stroke: %23231f20;stroke-miterlimit: 10} .c2 {fill: %23${this.color}} .c3 {opacity: 0.35;fill: %23000} .c4 {opacity: 0.25;fill: %23000} .c5 {opacity: 0.45;fill: %23000}</style></defs><g id="L6" data-name="L6"><path class="c2" d="M264.57,78.41H30.91c-7.93,0-14.37-6.43-14.37-14.37V21.99c0-7.93,6.43-14.37,14.37-14.37h233.66c7.93,0,14.37,6.43,14.37,14.37v42.06c0,7.93-6.43,14.37-14.37,14.37"/><circle class="c1" cx="34.2" cy="41.97" r="11.89"/></g><g id="L2" data-name="L2"><rect class="c4" x="115.67" y="16.26" width="51.03" height="53.5"/></g><g id="L3" data-name="L3"><rect class="c3" x="166.7" y="16.26" width="51.36" height="53.5"/></g><g id="L4" data-name="L4"><path class="c5" d="M269.6,58.45c0,6.25-5.06,11.31-11.31,11.31h-40.24V16.26h40.24c6.25,0,11.31,5.06,11.31,11.31"/><line class="c5" x1="269.6" y1="27.57" x2="269.6" y2="58.45"/></g></svg>'
               data-src="${this.cardImgUrl}"
               style="height:89px; width:89px; transform: rotate(90deg); overflow: hidden; object-fit: cover; border-top-left-radius: var(--bs-border-radius-xl); object-position: -10px 0px"
               alt="Card image for ${this.mfr} - ${this.name} ${this.type}">
            </div>
        </div>
    
        <div class="card-body text-start">
          <div>
            <h5 class="card-title d-flex justify-content-between">
              #${this.color.toUpperCase()}
              
              ${this.getTdBadge()}
            </h5>
            ${this.getUnavailableBadge()}
          </div>
          <p class="card-text">${this.mfr} - ${this.name} ${this.type}</p>
        </div>
      </a>
    </div>
    `;
    if (window.multiselect && window.multiselect.collectionModeEnabled) {
      const $overlay = $(this.querySelector(".card-img-overlay"))
      $overlay.css("display", "block").css("height", "100%").css("width", "100%")
    }

  }

  handleSelect() {
    this.selected ? this.deselect() : this.select();
  }

  select(addCard=true) {
    this.selected = true;
    const affectedEl = $(this).find(".swatchcard").first()
    affectedEl.addClass("selected-card");
    affectedEl.removeClass("shadow-sm");
    affectedEl.css("transform", "translateY(-10px) scale3d(1.05, 1.05, 1)");
    affectedEl.addClass("big-shadow");
    if (addCard) window.multiselect.swatchTray.addItemFromCard($(this));
  }

  deselect(removeCard=true) {
    this.selected = false;
    if (removeCard) window.multiselect.swatchTray.removeItemByCard($(this));
    const affectedEl = $(this).find(".swatchcard").first()
    affectedEl.removeClass("selected-card");
    affectedEl.addClass("shadow-sm");
    affectedEl.css("transform", "translateY(0px) scale3d(1, 1, 1)");
    affectedEl.removeClass("big-shadow");
  }
}

customElements.define('swatch-card', Card);
