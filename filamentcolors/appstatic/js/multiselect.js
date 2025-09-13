/** Creates and manages individual tray items that represent swatches. */
var SwatchItem = class SwatchItem {
  constructor(color, id, mfr, name, type, noAnim) {
    this.color = color;
    this.objId = id;
    this.mfr = mfr;
    this.name = name;
    this.type = type;
    this.noAnim = noAnim;

    this.el = null;
    this.active = false;
    this.popover = null;
  }

  setPopover() {
    setTimeout(() => {
      this.popover = bootstrap.Popover.getOrCreateInstance($(this.el).closest("[data-bs-toggle=\"popover\"]"));
    })
  }

  getHtml() {
    let color = this.color.toString();
    if (color.startsWith("#")) {
      color = color.substring(1);
    }
    const prefersDarkScheme = window.matchMedia("(prefers-color-scheme: dark)").matches;
    const currentTheme = localStorage.getItem("bsTheme") || (prefersDarkScheme ? "dark" : "light");
    const holeColor = currentTheme === "dark" ? "%23212529" : "white";

    let div = document.createElement("div")
    div.id = `swatchItem-${this.objId}`
    div.className = `ms-2 swatch-collection-tray-item ${this.noAnim ? '' : 'slide-in-bottom'} grabbable`
    div.onclick = () => {
      this.select()
    }
    div.setAttribute("data-bs-toggle", "popover")
    div.setAttribute("data-swatch-id", this.objId)
    div.setAttribute("data-bs-html", "true")
    div.setAttribute("title", `${this.mfr}<br>${this.name} ${this.type}`)
    div.setAttribute("data-bs-content", `<div class='text-center'><div role='button' class='btn btn-danger swatchtrayRemoveItem'>Remove</button></div>`)
    div.setAttribute("data-bs-trigger", "manual")
    div.setAttribute("data-bs-placement", "top")
    div.setAttribute("data-bs-offset", "0,22")
    div.setAttribute("objId", `${this.objId}`)

    let img = document.createElement("img")
    img.src = `data:image/svg+xml;charset=utf-8,<svg id='a' data-name='L1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink="http://www.w3.org/1999/xlink" width="89px" height="288px" viewBox='0 0 71.79 263.4'><defs><style> .g { opacity: 0.25;fill: %23000 } .g, .h, .i, .j, .k { stroke: %23231f20; stroke-miterlimit: 10; } .h { opacity: 0.45;fill: %23000 } .l { fill: %23${color}; } .i { fill: ${holeColor}; } .j { opacity: 0.35;fill: %23000 } .k { fill: none; } </style></defs><g id='b' data-name='color'><rect class='l' x='.5' y='13.31' width='70.79' height='237.8'/><circle class='l' cx='15.27' cy='15.27' r='14.77'/><circle class='l' cx='56.52' cy='15.27' r='14.77'/><rect class='l' x='14.87' y='.5' width='42.05' height='17.66'/><circle class='l' cx='56.52' cy='248.53' r='14.77'/><circle class='l' cx='15.27' cy='248.53' r='14.77'/><rect class='l' x='14.87' y='245.65' width='42.05' height='17.66' transform='translate(71.79 508.95) rotate(180)'/></g><g id='c' data-name='L6'><path class='k' d='M71.29,14.87v233.66c0,7.93-6.43,14.37-14.37,14.37H14.86'/><path class='k' d='M71.29,14.87c0-7.93-6.43-14.37-14.37-14.37'/><path class='k' d='M.5,248.53V14.87C.5,6.94,6.93.5,14.87.5h42.05'/><path class='k' d='M.5,248.53c0,7.93,6.43,14.37,14.37,14.37'/></g><circle class='i' cx='36.94' cy='18.16' r='11.89'/><g id='d' data-name='L2'><rect class='g' x='9.15' y='99.63' width='53.5' height='51.03'/></g><g id='e' data-name='L3'><rect class='j' x='9.15' y='150.66' width='53.5' height='51.36'/></g><g id='f' data-name='L4'><path class='h' d='M20.46,253.56c-6.25,0-11.31-5.06-11.31-11.31v-40.24h53.5v40.24c0,6.25-5.06,11.31-11.31,11.31'/><line class='k' x1='51.34' y1='253.56' x2='20.46' y2='253.56'/></g></svg>`
    img.alt = `${this.mfr} ${this.name} ${this.type}`

    div.appendChild(img);
    this.el = div;
    this.removeAnimation();
    this.setPopover();
    return div
  }

  select() {
    if (!(this.el)) {
      console.error("Cannot select a swatch that has not spawned.")
    }
    window.multiselect.swatchTray.swatches.forEach(swatch => {
      if (swatch.el !== this.el) {
        swatch.deselect()
      }
    })
    $(this.el).toggleClass("active")
    this.popover.toggle()
  }

  deselect() {
    // force deactivating swatches
    $(this.el).removeClass("active")
    this.popover.hide()
  }

  yeet() {
    this.popover.hide();
    $(this.el).removeClass("slide-in-bottom").addClass("slide-out-bottom");
    setTimeout(() => {
      $(this.el).addClass('fade-out');
      setTimeout(() => {
        $(this.el).remove();
      }, 300);
    }, 150);
  }

  removeAnimation() {
    setTimeout(() => {
      $(this.el).removeClass("slide-in-bottom")
    }, 310)
  }
}


/** Manager for the offcanvas tray that holds the swatch items. */
var SwatchTray = class SwatchTray {
  constructor() {
    this._tray = null;
    this._el = null;

    this.sortableEnabled = false;
    // only used for logging
    this.sortableTouchEventTriggered = false;
    this.eosEnabled = false;
    this.swatches = []
    this.horizontalScrollEnabled = false;
    this.disableSortableOnTouch()

    this.rightButton = this._createNavButton($("#trayRightButton"), this.NavButtonScrollRight);
    this.leftButton = this._createNavButton($("#trayLeftButton"), this.NavButtonScrollLeft);
  }

  // Ensure we always have a live reference to the Bootstrap Offcanvas instance
  get tray() {
    const el = document.getElementById("swatchCollectionTray");
    if (!el) {
      this._tray = null;
      return {
        show: function () {
        },
        hide: function () {
        }
      };
    }
    const instance = bootstrap.Offcanvas.getOrCreateInstance(el);
    this._tray = instance;
    this._tray.show = instance.show;
    this._tray.hide = instance.hide;
    return this._tray;
  }
  get el() {
    if (this._el) {
      // during htmx history snapshots, it's possible for the tray to become orphaned.
      // if that happens, find the new tray and initialize it with the data the old
      // tray had.
      if (document.contains(this._el)) {
        return this._el;
      }
    }
    this._el = document.getElementById("offcanvas-swatchtray");
    this.sortableEnabled = false;
    this.eosEnabled = false;
    this.horizontalScrollEnabled = false;
        try {
        if (this.rightButton) {
          this.rightButton.el = $("#trayRightButton");
          this.rightButton.isVisible = false; // recalc visibility below
        }
        if (this.leftButton) {
          this.leftButton.el = $("#trayLeftButton");
          this.leftButton.isVisible = false;
        }
        // Reinstall click handlers on new elements if not present
        if (this.rightButton && !this.rightButton.el.hasClass('evtInstalled')) {
          this.rightButton.el.addClass('evtInstalled').on('click', this.NavButtonScrollRight);
        }
        if (this.leftButton && !this.leftButton.el.hasClass('evtInstalled')) {
          this.leftButton.el.addClass('evtInstalled').on('click', this.NavButtonScrollLeft);
        }
      } catch (e) {
      }
    this.enableSortable();
    this.disableSortableOnTouch();
    this.enableEOS();
    this.enableHorizontalScroll();
    this.testForNavButtons();

    $(this._el).disableSelection()
    return this._el;
  }

  addItemFromCard($obj) {
    const objId = $obj.attr("id");
    if (window.multiselect.swatchTray.swatches.find(sw => sw.objId === objId)) {
      this.cleanup()
    } else {
      const newSwatchItem = new SwatchItem(
        ...Utils.getSwatchDataFromCard($obj)
      )
      newSwatchItem.removeAnimation()
      this.swatches.push(newSwatchItem);
      this.el.append(newSwatchItem.getHtml());
      this.scrollTrayForNewSwatch()
      this.updateCounter()
    }
  }

  addItemFromBlob(data) {
    const objId = data.i
    if (window.multiselect.swatchTray.swatches.find(sw => sw.objId === objId)) {
      this.cleanup()
    } else {
      const newSwatchItem = new SwatchItem(
        ...Utils.getSwatchDataFromBlob(data)
      )
      newSwatchItem.removeAnimation()
      this.swatches.push(newSwatchItem);
      this.el.append(newSwatchItem.getHtml());
      this.scrollTrayForNewSwatch()
      this.updateCounter()
    }
  }

  _getNewSwatchScrollDistance() {
    // Thanks to iOS's rubber banding effect and it not listening to CSS that's supposed
    // to turn that off, we have to calculate exactly how much to scroll the tray. If we
    // don't, it gets flung off the screen at mach 11. Which, admittedly, is hilarious.
    const $el = $(this.el)
    const left = $el.scrollLeft();
    const innerWidth = $el.innerWidth();
    const scrollWidth = $el.prop("scrollWidth");

    return scrollWidth - (left + innerWidth)
  }

  scrollTrayForNewSwatch() {
    // because the right scroll button is very sensitive to new trays, use a
    // temporary variable to stop it from responding while we're adding a new swatch.
    window.noScrollRightButton = 1

    // Perform the scroll. On iOS Safari, programmatic smooth scrolls may not
    // reliably fire 'scroll' events, so we also proactively run the button
    // visibility checks during and after the animation.
    this.el.scrollBy({
      left: this._getNewSwatchScrollDistance(),
      behavior: "smooth"
    });

    // Immediately update once in case no scroll event is dispatched.
    this.testForNavButtons();

    // For iOS Safari: run a short rAF loop to update button visibility while
    // the smooth scroll animation is in progress, then a final check.
    const start = performance.now();
    const DURATION = 500; // ms, roughly matches the smooth scroll timing
    const tick = (t) => {
      this.testForNavButtons();
      if (t - start < DURATION) {
        requestAnimationFrame(tick);
      }
    };
    try {
      requestAnimationFrame(tick);
    } catch (e) {
      // Fallback if rAF is unavailable for any reason
      setTimeout(() => this.testForNavButtons(), 250);
      setTimeout(() => this.testForNavButtons(), 500);
    }

    setTimeout(() => {
      window.noScrollRightButton = 0
      // Final sanity check after the scroll completes.
      this.testForNavButtons();
    }, 600)
  }

  removeItemByCard($obj) {
    // $obj is a jQuery object of the <swatch-card> custom element
    const objId = $obj.attr("id");
    // Hide any open popovers and deactivate other swatches
    hideAllPopovers();
    $(".swatch-collection-tray-item").removeClass("active");

    // Find and remove the swatch item instance and its DOM element
    const idx = this.swatches.findIndex(sw => sw.objId === objId);
    if (idx !== -1) {
      const sw = this.swatches[idx];
      sw.yeet();
      this.swatches.splice(idx, 1);
    } else {
      // Fallback: remove by DOM id if instance not found
      const $sw = $(`#swatchItem-${objId}`);
      if ($sw && $sw.exists()) {
        $sw.remove();
      }
    }
    this.cleanup()
  }

  removeItemBySwatchItem(objId) {
    hideAllPopovers();
    const card = $(`#${objId}`)
    if (card.exists()) {
      card.get(0).deselect()
    } else {
      const idx = this.swatches.findIndex(sw => sw.objId === objId);
      const sw = this.swatches[idx];
      sw.yeet();
      this.swatches.splice(idx, 1)
    }

    this.cleanup()
  }

  enableSortable() {
    if (this.sortableEnabled) {
      return
    }

    $(this.el).sortable({
      'group': {'name': 'swatch-collections', 'pull': 'clone', 'put': true},
      'draggable': '.swatch-collection-tray-item',
      'handle': '.swatch-collection-tray-item',
      onStart: function (evt) {
        hideAllPopovers();
        $(".swatch-collection-tray-item").removeClass("active");
      },
    });
    this.sortableEnabled = true;
  }

  disableSortable() {
    if (!(this.sortableEnabled)) {
      return
    }
    $(this.el).sortable('destroy')
    this.sortableEnabled = false;
  }

  disableSortableOnTouch() {
    if (window.addEventListener) {
      window.touchEventDetected = false;
      window.addEventListener('touchstart', function () {
        if (!window.touchEventDetected) {
          // Touch devices can't use drag and drop and horizontal scrolling
          // at the same time. Detecting a touch event is way easier than
          // detecting whether a device is touch-capable, so just set
          // everything up. If we get a touch event, tear down sortable
          // and revert to scroll behavior.
          window.touchEventDetected = true;
          window.multiselect.swatchTray.sortableTouchEventTriggered = true;
          window.multiselect.swatchTray.disableSortable();
          $(".swatch-collection-tray-item").removeClass("grabbable");
        }
      }, {once: true});
    }
  }

  enableHorizontalScroll() {
    if (this.horizontalScrollEnabled) {
      return
    }

    const resetSwatchItemsOnScroll = debounce_leading(() => {
      hideAllPopovers();
      this.deactivateAllSwatches()
    });

    // specific catch for mobile devices
    this.el.addEventListener("touchmove", resetSwatchItemsOnScroll);

    // wheel is scroll wheel on a physical mouse
    this.el.addEventListener("wheel", (event) => {
      event.preventDefault();
      hideAllPopovers();
      this.deactivateAllSwatches()

      let [x, y] = [event.deltaX, event.deltaY];
      let magnitude;

      if (x === 0) {
        magnitude = y * 2;
      } else {
        magnitude = x;
      }
      this.el.scrollBy({
        left: magnitude,
        behavior: "smooth"
      });
    });
    this.horizontalScrollEnabled = true;
  }

  NavButtonScrollLeft() {
    window.multiselect.swatchTray.el.scrollBy({
      left: -200,
      behavior: "smooth"
    })
  }

  NavButtonScrollRight() {
    window.multiselect.swatchTray.el.scrollBy({
      left: 200,
      behavior: "smooth"
    })
  }

  _createNavButton(el, evt) {
    const button = {
      isVisible: false,
      evtInstalled: false,
      el: el,
      show: () => {
        // The window.noScrollRightButton is only in place while a new swatch
        // is being added. After which, it's removed.
        // Yes, this affects both buttons, but in practice, it only noticeably
        // affects the right button.
        if (window.noScrollRightButton) return;
        if (button.isVisible) return;
        button.isVisible = true;
        const $btn = button.el;
        $btn.removeClass("d-none").addClass("bounce-in");
        setTimeout(() => {
          $btn.removeClass("bounce-in").addClass('wiggle');
        }, 150);
      },
      hide: () => {
        if (!button.isVisible) return;
        const $btn = button.el;
        $btn.removeClass('wiggle').addClass('bounce-out');
        setTimeout(() => {
          $btn.addClass('d-none').removeClass('bounce-out');
        }, 300);
        button.isVisible = false;
      }
    };
    // Do not bind handlers directly here; we use delegated handlers registered once on document
    return button;
  }

  testForNavButtons() {
    {
      const $el = $(this.el)
      const left = $el.scrollLeft();
      const innerWidth = $el.innerWidth();
      const scrollWidth = $el.prop("scrollWidth");

      if (scrollWidth > innerWidth) {
        // we've filled up the tray. Maybe show the right button.
        (left + innerWidth <= scrollWidth - 20) ? this.rightButton.show() : this.rightButton.hide()
      }
      // the left button is easier.
      left > 20 ? this.leftButton.show() : this.leftButton.hide()
    }
  }

  enableEOS() {
    if (this.eosEnabled) {
      return
    }
    $(this.el).scroll(() => this.testForNavButtons());
    this.eosEnabled = true;
  }

  show() {
    this.tray.show();
    this.enableTrayCancelButton();
    $("#mobileGoButton").removeClass("d-none")
  }

  hide() {
    this.tray.hide();
    $("#mobileGoButton").addClass("d-none")
  }

  clear() {
    hideAllPopovers();
    this.deselectAllCards();
    this.swatches.forEach((el, idx) => {
      try {
        el.remove()
      } catch {
      }
    });
    this.swatches = [];
    this.updateCounter();
    $("#offcanvas-swatchtray").children().remove()
  }

  deselectAllCards() {
    document.querySelectorAll("swatch-card .selected-card").forEach((el, idx) => {
      el.parentElement.deselect()
    })
  }

  enableTrayCancelButton() {
    let trayCancelBtn = $("#swatch-collection-tray-cancel-button")
    if (trayCancelBtn.hasClass("evtEnabled")) return;
    // first event is for mouse, second event is for mobile
    trayCancelBtn.on("click touchstart", (evt) => {
      window.multiselect.swatchTray.clear();
      window.preselected = [];
      window.multiselect.exitCollectionMode();
      return false;  // stop propogation
    });
    trayCancelBtn.addClass("evtEnabled");
  }

  deactivateAllSwatches() {
    this.swatches.forEach(el => {
      el.deselect()
    })
  }

  updateCounter() {
    $(".multiselect-badge").text(this.getCounter())
  }

  getCounter() {
    return window.multiselect.swatchTray.swatches.length.toString();
  }

  cleanup() {
    this.testForNavButtons()
    this.updateCounter();
    if (this.swatches.length === 0) {
      window.multiselect.exitCollectionMode()
    }
  }
}


var Utils = class Utils {
  static fixMobileGoButton() {
    const btn = document.getElementById('mobileGoButton');
    const navbar = document.getElementById('navbar');
    if (!btn || !navbar) return;
    const rect = navbar.getBoundingClientRect();
    const top = Math.max(0, Math.round(rect.height));
    btn.style.top = `${top}px`;
  }

  static getSwatchDataFromBlob(data) {
    return [
      data.c,
      data.i.toString(),
      data.m,
      data.n,
      data.t,
      true
    ]
  }

  static getSwatchDataFromCard($obj, noStartingAnim = false) {
    return [
      $obj.attr("color"),
      $obj.attr("id"),
      $obj.attr('mfr'),
      $obj.attr('name'),
      $obj.attr('type'),
      noStartingAnim
    ];
  }
}

/** Root class for the multiselect functionality.
 * Available at window.multiselect */
var Multiselect = class Multiselect {
  constructor() {
    if (!(this.isValidPage())) {
      console.error("Cannot instantiate multiselect on non-library page.")
      return
    }

    this.swatchTray = new SwatchTray();
    this.swatchTray.enableSortable();
    this.swatchTray.disableSortableOnTouch();
    this.swatchTray.enableEOS();
    this.swatchTray.enableHorizontalScroll();
    try {
      // sometimes this fails during init because the element isn't ready
      this.swatchTray.enableTrayCancelButton();
    } catch (e) {
    }

    this.collectionModeEnabled = false;
    this.preselectMode = false;
  }

  testForPreselected() {
    if (window.preselected.length > 0) {
      this.handlePreselected()
    }
  }

  _forceSelectSwatchCardsByTray() {
    $(window.multiselect.swatchTray.swatches).each((idx, swatch) => {
      const s = document.getElementById(swatch.objId)
      if (s) {
        s.select(false)
      }
    })
  }

  handlePreselected() {
    this.preselectMode = true;
    this.startCollectionMode()
    // reset the sortable detector
    window.touchEventDetected = false;
    this.swatchTray.disableSortableOnTouch()

    setTimeout(() => {
      window.preselected_data.forEach(data => {
        this.swatchTray.addItemFromBlob(data)
      })
      this._forceSelectSwatchCardsByTray()
    }, 100)
    // prevent it from being called again
    window.preselected = []
  }

  startCollectionMode() {
    try {
      // under normal circumstances, this is fine. Explodes when editing
      // a collection, though.
      this.swatchTray.clear();
    } catch (e) {

    }
    Utils.fixMobileGoButton();
    this.enableOverlays();
    this.swatchTray.show();
    this.collectionModeEnabled = true;
  }

  exitCollectionMode() {
    this.collectionModeEnabled = false;
    this.preselectMode = false;
    this.swatchTray.hide();
    this.disableOverlays();
  }

  isValidPage() {
    return $("#swatchCollectionTray").exists()
  }

  enableOverlays() {
    $(".card-img-overlay").css("display", "block").css("height", "100%").css("width", "100%")
  }

  disableOverlays() {
    $(".card-img-overlay").css("display", "")
  }
}

if (!$(document.body).hasClass("popoverRemoveDelegated")) {
  $(document).on("click", ".popover .swatchtrayRemoveItem", function () {
    const popoverEl = this.closest(".popover");
    if (!popoverEl) return;
    // Find the trigger using aria-describedby
    const trigger = document.querySelector('[aria-describedby="' + popoverEl.id + '"]');
    if (!trigger) return;
    const swatchId = trigger.dataset.swatchId;
    if (swatchId) {
      window.multiselect.swatchTray.removeItemBySwatchItem(swatchId);
    }
  });
  $(document.body).addClass("popoverRemoveDelegated");
}

$(".go-button").on("click", function (evt) {
  window.collectionModeEnabled = false;
  const url = window.location.origin + "/library/collection/" + window.multiselect.swatchTray.swatches.map(item => item.objId).join();
  window.location.assign(url);
});

htmx.onLoad(function (t) {
  if (!(window.multiselect)) {
    window.multiselect = new Multiselect();
  }
  if (window.multiselect.preselectMode) {
    window.multiselect._forceSelectSwatchCardsByTray()
  }
  window.multiselect.testForPreselected()
});

htmx.on("htmx:beforeRequest", function (evt) {
  // Check the headers on the requests that HTMX is making. If we're in
  // collection mode, see if the request is related to getting more swatches.
  // If not, exit gracefully
  if (!window.multiselect.collectionModeEnabled) return;
  try {
    const isInfiniteScroll = (
      JSON.parse($(evt.target).attr('hx-headers'))["X-Infinite-Scroll"] ?? null
    )
    const isSearch = (
      JSON.parse($(evt.target).attr('hx-headers'))["X-Searchbar"] ?? null
    )
    if (!(isInfiniteScroll || isSearch)) {
      window.multiselect.exitCollectionMode()
    }
  } catch {
    window.multiselect.exitCollectionMode()
  }
})

// $(document).on('hide.bs.offcanvas', (el) => console.log(el))
//
// htmx.on("htmx:beforeHistorySave", function (evt) {
//   console.log(evt)
//   console.log($(evt.target).attr("hx-headers"))
// })

$(document).ready(function () {
  if (!(window.multiselect)) {
    window.multiselect = new Multiselect();
  }
  window.multiselect.testForPreselected()
  if (!$(document.body).hasClass("navButtonsDelegated")) {
    $(document).on('click', '#trayRightButton', function (e) {
      e.preventDefault();
      if (window.multiselect && window.multiselect.swatchTray) {
        window.multiselect.swatchTray.NavButtonScrollRight();
      }
    });
    $(document).on('click', '#trayLeftButton', function (e) {
      e.preventDefault();
      if (window.multiselect && window.multiselect.swatchTray) {
        window.multiselect.swatchTray.NavButtonScrollLeft();
      }
    });
    $(document.body).addClass('navButtonsDelegated');
  }
});
