class ColorMatch extends HTMLElement {
  constructor() {
    super()
    this._boundOnLoad = this._onLoad.bind(this)
  }

  connectedCallback() {
    // Enhance existing light DOM so styles apply
    // Expect the markup from colormatch.html to be inside this component
    // Wire up behaviors once when connected
    if (this._initialized) return
    this._initialized = true

    // Expose functions expected by server-rendered HTML/buttons
    // Keep names to preserve functionality used by templates and tests
    window.flipButtonToRemove = this.flipButtonToRemove.bind(this)
    window.flipButtonToGrab = this.flipButtonToGrab.bind(this)
    window.grabSwatch = this.grabSwatch.bind(this)
    window.generateCollection = this.generateCollection.bind(this)
    window.invalid_color = this.invalid_color.bind(this)
    window.rgbToHex = this.rgbToHex.bind(this)
    window.changeHexColorPicker = this.changeHexColorPicker.bind(this)
    window.changeRGBColorPicker = this.changeRGBColorPicker.bind(this)
    window.changeHSVColorPicker = this.changeHSVColorPicker.bind(this)
    window.changeLABColorPicker = this.changeLABColorPicker.bind(this)
    window.updateHex = this.updateHex.bind(this)
    window.updateRGB = this.updateRGB.bind(this)
    window.updateHSV = this.updateHSV.bind(this)
    window.updateLAB = this.updateLAB.bind(this)
    window.updateAll = this.updateAll.bind(this)
    window.updateGrabBag = this.updateGrabBag.bind(this)
    window.nukeFromGrabBag = this.nukeFromGrabBag.bind(this)
    window.nuke = this.nuke.bind(this)

    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', this._boundOnLoad)
    } else {
      this._onLoad()
    }
  }

  disconnectedCallback() {
    document.removeEventListener('DOMContentLoaded', this._boundOnLoad)
  }

  // ====== Original functions, scoped to this component's DOM ======
  $(sel) {
    // Scope jQuery-like selection to inside this component
    return window.jQuery ? window.jQuery(sel, this) : window.$(sel, this)
  }

  q(sel) { return this.querySelector(sel) }

  flipButtonToRemove(el) {
    let $el = window.$(el)
    $el.removeClass('btn-primary').addClass('btn-danger')
    $el.text('Remove')
    $el.attr('onclick', 'nukeFromGrabBag(this)')
  }

  flipButtonToGrab(el) {
    let $el = window.$(el)
    $el.removeClass('btn-danger').addClass('btn-primary')
    $el.text('Grab Swatch')
    $el.attr('onclick', 'grabSwatch(this)')
  }

  grabSwatch(el) {
    let $el = window.$(el)
    this.flipButtonToRemove(el)

    let swatchcard = window.$($el.parent().siblings()[0]).clone()
    let swatch_id = $el.attr('id').split('-')[1]
    const parentDiv = document.createElement('div')
    parentDiv.id = `saved-swatch-${swatch_id}`
    parentDiv.classList.add(
      'col-md-6',
      'col-lg-4',
      'col-xl-4',
      'col-xxl-3',
      `singleSwatch-${swatch_id}`,
      'singleSelectableSwatch'
    )
    parentDiv.dataset.swatchId = swatch_id
    parentDiv.appendChild(swatchcard[0])
    const buttonHolder = document.createElement('div')
    buttonHolder.classList.add('text-center')
    const buttonDiv = document.createElement('div')
    buttonDiv.classList.add('btn', 'btn-outline-danger', 'mb-3')
    buttonDiv.innerText = 'Remove'
    buttonDiv.onclick = (evt) => {
      this.nuke(window.$(evt.target))
    }
    buttonHolder.appendChild(buttonDiv)
    parentDiv.appendChild(buttonHolder)
    // Append to the global container id to match template expectations
    const collection = document.getElementById('saved_swatches_collection') || this.q('#saved_swatches_collection')
    if (collection) collection.appendChild(parentDiv)
    this.updateGrabBag()
  }

  generateCollection() {
    let swatch_ids = []
    window.$('.singleSelectableSwatch').each(function() {
      swatch_ids.push(window.$(this).data()['swatchId'])
    })
    window.location.href = `/library/collection/${swatch_ids.join(',')}`
  }

  invalid_color() {
    if (window.Toastify) {
      window.Toastify({ text: 'Please enter a valid color value.', duration: 5000, backgroundColor: '#d9534f' }).showToast()
    }
  }

  sanitizeByte(n) {
    const num = typeof n === 'number' ? n : parseFloat(n)
    if (!isFinite(num)) return 0
    const rounded = Math.round(num + 1e-6)
    if (rounded < 0) return 0
    if (rounded > 255) return 255
    return rounded
  }

  rgbToHex(r, g, b) {
    const R = this.sanitizeByte(r)
    const G = this.sanitizeByte(g)
    const B = this.sanitizeByte(b)
    return '#' + ((1 << 24) | (R << 16) | (G << 8) | (B)).toString(16).slice(1)
  }

  changeHexColorPicker() {
    let el = this.$('#hex-input')
    let value = (el && typeof el.val === 'function') ? el.val() : (window.inputs && window.inputs['hex'] ? window.inputs['hex'].value : '')
    if (!value) return this.invalid_color()
    value = ('' + value).trim()
    if (value[0] !== '#') {
      if (value.length === 3 || value.length === 6) {
        value = `#${value}`
      }
    }
    try {
      // Build base color directly from HEX input
      const base = new window.Color(value)
      // Update picker from the normalized hex
      window.picker.fromString(value)
      // Update other fields directly from base (not via picker)
      const srgb = base.to('srgb')
      const R = this.sanitizeByte(srgb.r * 255)
      const G = this.sanitizeByte(srgb.g * 255)
      const B = this.sanitizeByte(srgb.b * 255)
      window.inputs['rgb_r'].value = R
      window.inputs['rgb_g'].value = G
      window.inputs['rgb_b'].value = B
      const hsv = base.to('hsv')
      {
        const isBlack = typeof hsv.v === 'number' && !isNaN(hsv.v) && Number(hsv.v.toFixed ? hsv.v.toFixed(6) : hsv.v) === 0
        window.inputs['hsv_h'].value = isBlack ? '—' : (isFinite(hsv.h) ? hsv.h.toFixed(3) : '—')
        window.inputs['hsv_s'].value = isFinite(hsv.s) ? hsv.s.toFixed(3) : '0.000'
        window.inputs['hsv_v'].value = isFinite(hsv.v) ? hsv.v.toFixed(3) : '0.000'
      }
      const lab = base.to('lab')
      window.inputs['lab_l'].value = lab.l.toFixed(3)
      window.inputs['lab_a'].value = lab.a.toFixed(3)
      window.inputs['lab_b'].value = lab.b.toFixed(3)
      // Also normalize HEX display
      window.inputs['hex'].value = window.picker.toHEXString()
    } catch (e) {
      this.invalid_color()
    }
  }

  changeRGBColorPicker() {
    let r = parseInt(this.$('#red-input').val(), 10)
    let g = parseInt(this.$('#green-input').val(), 10)
    let b = parseInt(this.$('#blue-input').val(), 10)
    if ([r,g,b].some(n => Number.isNaN(n))) return this.invalid_color()
    try {
      // Sanitize and reflect back to inputs to prevent fractional/off-range values
      const R = this.sanitizeByte(r)
      const G = this.sanitizeByte(g)
      const B = this.sanitizeByte(b)
      window.inputs['rgb_r'].value = R
      window.inputs['rgb_g'].value = G
      window.inputs['rgb_b'].value = B
      const base = new window.Color('srgb', [R, G, B])
      // Update picker from base sRGB -> HEX (rgbToHex sanitizes too)
      window.picker.fromString(this.rgbToHex(R, G, B))
      // Update other fields directly from base
      const hsv = base.to('hsv')
      {
        const isBlack = typeof hsv.v === 'number' && !isNaN(hsv.v) && Number(hsv.v.toFixed ? hsv.v.toFixed(6) : hsv.v) === 0
        window.inputs['hsv_h'].value = isBlack ? '—' : (isFinite(hsv.h) ? hsv.h.toFixed(3) : '—')
        window.inputs['hsv_s'].value = isFinite(hsv.s) ? hsv.s.toFixed(3) : '0.000'
        window.inputs['hsv_v'].value = isFinite(hsv.v) ? hsv.v.toFixed(3) : '0.000'
      }
      const lab = base.to('lab')
      window.inputs['lab_l'].value = lab.l.toFixed(3)
      window.inputs['lab_a'].value = lab.a.toFixed(3)
      window.inputs['lab_b'].value = lab.b.toFixed(3)
      // Normalize HEX display from picker
      window.inputs['hex'].value = window.picker.toHEXString()
    } catch (e) {
      this.invalid_color()
    }
  }

  changeHSVColorPicker() {
    let h = parseFloat(this.$('#hue-input').val())
    let s = parseFloat(this.$('#saturation-input').val())
    let v = parseFloat(this.$('#value-input').val())
    if ([h,s,v].some(n => Number.isNaN(n))) return this.invalid_color()
    try {
      const base = new window.Color('hsv', [h, s, v])
      // Update picker from base->sRGB
      const srgb = base.to('srgb')
      window.picker.fromString(this.rgbToHex(srgb.r * 255, srgb.g * 255, srgb.b * 255))
      // Update other fields directly from base
      const lab = base.to('lab')
      window.inputs['lab_l'].value = lab.l.toFixed(3)
      window.inputs['lab_a'].value = lab.a.toFixed(3)
      window.inputs['lab_b'].value = lab.b.toFixed(3)
      const hsv = base.to('hsv')
      {
        const isBlack = typeof hsv.v === 'number' && !isNaN(hsv.v) && Number(hsv.v.toFixed ? hsv.v.toFixed(6) : hsv.v) === 0
        window.inputs['hsv_h'].value = isBlack ? '—' : (isFinite(hsv.h) ? hsv.h.toFixed(3) : '—')
        window.inputs['hsv_s'].value = isFinite(hsv.s) ? hsv.s.toFixed(3) : '0.000'
        window.inputs['hsv_v'].value = isFinite(hsv.v) ? hsv.v.toFixed(3) : '0.000'
      }
      const R = this.sanitizeByte(srgb.r * 255)
      const G = this.sanitizeByte(srgb.g * 255)
      const B = this.sanitizeByte(srgb.b * 255)
      window.inputs['rgb_r'].value = R
      window.inputs['rgb_g'].value = G
      window.inputs['rgb_b'].value = B
      // Normalize HEX display from picker
      window.inputs['hex'].value = window.picker.toHEXString()
    } catch (e) {
      this.invalid_color()
    }
  }

  changeLABColorPicker() {
    // Parse numeric LAB inputs; accept floats and clamp L to [0,100]
    let lRaw = this.$('#l-input').val()
    let aRaw = this.$('#a-input').val()
    let bRaw = this.$('#b-input').val()
    let l = parseFloat(lRaw)
    let a = parseFloat(aRaw)
    let b = parseFloat(bRaw)
    if (Number.isNaN(l) || Number.isNaN(a) || Number.isNaN(b)) {
      return this.invalid_color()
    }
    if (l < 0) l = 0; if (l > 100) l = 100
    try {
      const base = new window.Color('lab', [l, a, b])
      const srgb = base.to('srgb')
      // Update picker from base->sRGB
      window.picker.fromString(this.rgbToHex(srgb.r * 255, srgb.g * 255, srgb.b * 255))
      // Update other fields directly from base
      const R = this.sanitizeByte(srgb.r * 255)
      const G = this.sanitizeByte(srgb.g * 255)
      const B = this.sanitizeByte(srgb.b * 255)
      window.inputs['rgb_r'].value = R
      window.inputs['rgb_g'].value = G
      window.inputs['rgb_b'].value = B
      const hsv = base.to('hsv')
      window.inputs['hsv_h'].value = hsv.h.toFixed(3)
      window.inputs['hsv_s'].value = hsv.s.toFixed(3)
      window.inputs['hsv_v'].value = hsv.v.toFixed(3)
      // Normalize HEX display from picker
      window.inputs['hex'].value = window.picker.toHEXString()
      // Normalize LAB display too
      const lab = base.to('lab')
      window.inputs['lab_l'].value = lab.l.toFixed(3)
      window.inputs['lab_a'].value = lab.a.toFixed(3)
      window.inputs['lab_b'].value = lab.b.toFixed(3)
    } catch (e) {
      this.invalid_color()
    }
  }

  updateHex() {
    window.inputs['hex'].value = window.picker.toHEXString()
  }
  updateRGB() {
    let hex_base = window.picker.toHEXString()
    let rgb = new window.Color(hex_base)
    const R = this.sanitizeByte(rgb.r * 255)
    const G = this.sanitizeByte(rgb.g * 255)
    const B = this.sanitizeByte(rgb.b * 255)
    window.inputs['rgb_r'].value = R
    window.inputs['rgb_g'].value = G
    window.inputs['rgb_b'].value = B
  }
  updateHSV() {
    let hex_base = window.picker.toHEXString()
    let rgb = new window.Color(hex_base)
    let hsv = rgb.to('hsv')
    // If pure black (value == 0), hue is undefined; show m-dash instead of NaN
    const isBlack = typeof hsv.v === 'number' && !isNaN(hsv.v) && Number(hsv.v.toFixed ? hsv.v.toFixed(6) : hsv.v) === 0
    window.inputs['hsv_h'].value = isBlack ? '—' : (isFinite(hsv.h) ? hsv.h.toFixed(3) : '—')
    window.inputs['hsv_s'].value = isFinite(hsv.s) ? hsv.s.toFixed(3) : '0.000'
    window.inputs['hsv_v'].value = isFinite(hsv.v) ? hsv.v.toFixed(3) : '0.000'
  }
  updateLAB() {
    let hex_base = window.picker.toHEXString()
    let rgb = new window.Color(hex_base)
    let lab = rgb.to('lab')
    window.inputs['lab_l'].value = lab.l.toFixed(3)
    window.inputs['lab_a'].value = lab.a.toFixed(3)
    window.inputs['lab_b'].value = lab.b.toFixed(3)
  }
  updateAll() {
    this.updateHex()
    this.updateRGB()
    this.updateHSV()
    this.updateLAB()
  }

  updateGrabBag() {
    // target outside or inside component
    const $parent = window.$('#saved_swatches').length ? window.$('#saved_swatches') : this.$('#saved_swatches')
    const $collection = window.$('#saved_swatches_collection').length ? window.$('#saved_swatches_collection') : this.$('#saved_swatches_collection')
    if ($collection.children().length > 0) {
      $parent.css('display', '')
    } else {
      $parent.css('display', 'none')
    }
  }

  nukeFromGrabBag(element) {
    let $el = window.$(element)
    // In results, the button id is in the form "grab-<swatchId>"; prefer parsing it directly
    let idAttr = $el.attr('id') || ''
    let swatchId = ''
    if (idAttr && idAttr.indexOf('-') !== -1) {
      swatchId = idAttr.split('-').pop()
    } else {
      // Fallback: try to find a nearby element with an id starting with grab-
      const closest = $el.closest('[id^="grab-"]')
      if (closest && closest.length) {
        swatchId = closest.attr('id').split('-').pop()
      }
    }

    if (!swatchId) {
      // As a last resort, do nothing but return
      return
    }

    let $swatch = window.$(`#saved-swatch-${swatchId}`)
    $swatch.remove()
    let $swatchButton = window.$(`#grab-${swatchId}`)
    $swatchButton.removeClass('btn-danger').addClass('btn-primary')
    $swatchButton.text('Grab Swatch')
    $swatchButton.attr('onclick', 'grabSwatch(this)')
    this.updateGrabBag()
  }

  nuke(element) {
    // Called when user clicks remove inside grab bag
    let swatchId = window.$(element).parent().parent().data()['swatchId']
    this.flipButtonToGrab(window.$(`#grab-${swatchId}`))
    window.$(element).parent().parent().remove()
    this.updateGrabBag()
  }

  _bindGrabBagEvents() {
    const container = document.getElementById('saved_swatches_collection') || this.q('#saved_swatches_collection')
    if (!container || container._fc_bound) return
    container._fc_bound = true
    container.addEventListener('click', (ev) => {
      const target = ev.target
      if (!target) return
      // Match the dynamically created remove buttons inside the grab bag
      // Buttons have class 'btn-outline-danger' and innerText 'Remove'
      if (target.classList && target.classList.contains('btn-outline-danger')) {
        const text = (target.textContent || '').trim().toLowerCase()
        if (text === 'remove') {
          // Use existing nuke API with a jQuery-wrapped element
          this.nuke(window.$(target))
        }
      }
    })
  }

  _onLoad() {
    // initialize picker and inputs
    try {
      window.picker = new window.JSColor('#color-picker', {
        format: 'hex',
        previewSize: 0.1,
        preset: 'large thick',
        value: '#45FFC1',
        random: true,
      })
      window.picker.onInput = this.updateAll.bind(this)
    } catch (e) {
      // If JSColor is unavailable, fail quietly in tests that don't exercise UI
    }
    window.inputs = {}
    window.inputs['hex'] = document.getElementById('hex-input') || this.q('#hex-input')
    window.inputs['rgb_r'] = document.getElementById('red-input') || this.q('#red-input')
    window.inputs['rgb_g'] = document.getElementById('green-input') || this.q('#green-input')
    window.inputs['rgb_b'] = document.getElementById('blue-input') || this.q('#blue-input')
    window.inputs['hsv_h'] = document.getElementById('hue-input') || this.q('#hue-input')
    window.inputs['hsv_s'] = document.getElementById('saturation-input') || this.q('#saturation-input')
    window.inputs['hsv_v'] = document.getElementById('value-input') || this.q('#value-input')
    window.inputs['lab_l'] = document.getElementById('l-input') || this.q('#l-input')
    window.inputs['lab_a'] = document.getElementById('a-input') || this.q('#a-input')
    window.inputs['lab_b'] = document.getElementById('b-input') || this.q('#b-input')

    // Ensure LAB inputs are included in form submissions
    try {
      if (window.inputs['lab_l']) window.inputs['lab_l'].setAttribute('name', 'lab_l')
      if (window.inputs['lab_a']) window.inputs['lab_a'].setAttribute('name', 'lab_a')
      if (window.inputs['lab_b']) window.inputs['lab_b'].setAttribute('name', 'lab_b')
    } catch (e) {
      // no-op if inputs are not present
    }

    // Initial sync
    this.updateAll()

    // Bind delegated events for existing grab bag content (e.g., restored from cache)
    this._bindGrabBagEvents()

    if (window.htmx && window.htmx.onLoad) {
      window.htmx.onLoad(() => {
        this._bindGrabBagEvents()
        this.updateGrabBag()
      })
    } else {
      // Fallback
      this.updateGrabBag()
    }

    // Rebind on page show (back/forward cache)
    window.addEventListener('pageshow', () => {
      this._bindGrabBagEvents()
    })
  }
}

customElements.define('fc-colormatch', ColorMatch)
