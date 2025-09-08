class Card extends HTMLElement {

  constructor() {
    super();
    this.retrieveAttrs();
  }

  // component attributes
  static get observedAttributes() {
    return [
      'selected',
      'objId',
      'showColormatchExtras',
      'hexColor',
      'mfr',
      'name',
      'type',
      'slug',
      'td',
      'available',
      'cardImgUrl',
      'distance'
    ];
  }

  retrieveAttrs() {
    this.color = this.getAttribute('color') || '#000000';
    this.objId = this.getAttribute('id') || '';
    this.mfr = this.getAttribute('mfr') || '';
    this.name = this.getAttribute('name') || '';
    this.type = this.getAttribute('type') || '';
    this.td = this.getAttribute('td') === "None" ? null : this.getAttribute('td');
    this.showColormatchExtras = this.getAttribute('showColormatchExtras') || '';
    this.slug = this.getAttribute('slug') || '';
    this.available = this.getAttribute('available') || '';
    this.cardImgUrl = this.getAttribute('cardImgUrl') || '';
  }

  attributeChangedCallback(property, oldValue, newValue) {
    if (oldValue === newValue) return;
    this[property] = newValue;
  }


  // constructor(objId, showColormatchExtras, hexColor, mfr, name, type, slug, td = null, available = null) {
  //   super();
  //   this.objId = `s${objId}`
  //   this.showColormatchExtras = false;
  //   this.swatchId = objId;
  //   this.color = hexColor.toString();
  //   this.mfr = mfr;
  //   this.name = name;
  //   this.type = type;
  //   this.slug = slug;
  //
  //   this.td = td === "None" ? null : td;
  //   this.available = available !== "True";
  //
  //   this.selected = false;
  //   this.showDeltaEDistanceWarning = false;
  // }

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
    htmx.process(this);
    this.render();
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
      <div class="card-img-overlay p-0" onclick="this.select()"></div>
       ${this.getDeltaEWarning()}
      <a
        href="/swatch/${this.slug}"
        hx-swap="morph:innerHTML show:window:top"
        hx-target="#main"
        hx-indicator="#loading"
        hx-push-url="true"
      >
        <div class="card-img-container">
          <div class="card-img-top img-fluid layer position-relative" style="background-color: #${this.color}; height: 89px;border-top-left-radius: var(--bs-border-radius-xl); border-top-right-radius: 2em">
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
  }

  select() {
    console.log("selected!")
  }

}


customElements.define('swatch-card', Card);
