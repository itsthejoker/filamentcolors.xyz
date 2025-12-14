class TdTextComponent extends HTMLElement {
  constructor() {
    super();
    this.textInput = null;
    this.errorMessage = null;
    this._initialized = false;
  }

  /**
   * Toggles the error state of the text input.
   * @param {boolean} visible - whether to show the error state
   */
  setErrorState(visible) {
    const $el = $(this.textInput);
    $el.toggleClass("is-valid", visible);
    $el.toggleClass("is-invalid", !visible);
  }

  syncValue() {
    if (!this.syncTarget) {
      // lazily resolve in case counterpart isn't ready yet
      this.syncTarget = document.querySelector(this.syncSelector)
    }
    if (this.syncTarget && typeof this.syncTarget.setValue === 'function') {
      this.syncTarget.setValue(this.getValue())
    }
  }

  roundToOneDecimal(value) {
    return Math.round(value * 10) / 10;
  }

  setErrorMessage(message) {
    if (!this.errorMessage) {
      throw new Error('Error message element is not initialized.');
    }
    this.errorMessage.textContent = message;
  }

  /**
   * Sets the value of the text input.
   * @param {string} value - the value to set
   * @returns {boolean}
   */
  setValue(value) {
    if (!this.textInput) {
      throw new Error('Text input is not initialized.');
    }
    const parsedValue = parseFloat(value);
    if (isNaN(parsedValue)) {
      throw new Error('Invalid value. Please provide a valid float.');
    }
    this.textInput.value = parsedValue.toString();
    this.setErrorState(this.validateTdTextBox());
  }

  /**
   * Gets the value of the text input.
   * @returns {number}
   */
  getValue() {
    if (!this.textInput) {
      throw new Error('Text input is not initialized.');
    }
    return parseFloat(this.textInput.value);
  }

  validateTdTextBox() {
    let value = this.textInput.value;
    if (value.endsWith('.')) {
      return false;
    }
    return $.isNumeric(value) && value >= 0 && value <= 100;
  }
}

class TdRangeComponent extends HTMLElement {
  constructor() {
    super();
    this.rangeInput = null;
    this.valueLabel = null;
    this.minpos = 0;
    this.maxpos = 100;
    this.minlval = Math.log(0.1);
    this.maxlval = Math.log(99.9);
    this.scale = (this.maxlval - this.minlval) / (this.maxpos - this.minpos)
    this._initialized = false;
  }

  roundToOneDecimal(value) {
    return Math.round(value * 10) / 10;
  }

  syncValue() {
    if (!this.syncTarget) {
      // lazily resolve in case counterpart isn't ready yet
      this.syncTarget = document.querySelector(this.syncSelector)
    }
    if (this.syncTarget && typeof this.syncTarget.setValue === 'function') {
      this.syncTarget.setValue(this.getValue())
    }
  }

  getValue() {
    if (!this.rangeInput) {
      throw new Error('Range input is not initialized.');
    }
    return this.roundToOneDecimal(parseFloat(this.getLogValueFromPosition()));
  }

  forceMinValue() {
    this.rangeInput.value = this.minpos;
    this.valueLabel.textContent = this.getMinValue().toString();
  }

  forceMaxValue() {
    this.rangeInput.value = this.maxpos;
    this.valueLabel.textContent = this.getMaxValue().toString();
  }

  getMinValue() {
    if (!this.rangeInput) {
      throw new Error('Range input is not initialized.');
    }
    return this.roundToOneDecimal(parseFloat(this.rangeInput.min));
  }

  getMaxValue() {
    if (!this.rangeInput) {
      throw new Error('Range input is not initialized.');
    }
    return this.roundToOneDecimal(parseFloat(this.rangeInput.max));
  }

  getLogValueFromPosition() {
    let position = parseFloat(this.rangeInput.value);
    if (position === this.minpos) {
      return this.getMinValue();
    }
    if (position === this.maxpos) {
      return this.getMaxValue();
    }
    let min = (position - this.minpos);
    if (min <= 0) {
      min = 0.1;
    }
    let logVal = Math.exp(min * this.scale + this.minlval);
    if (logVal > 100) {
      logVal = 100;
    }
    return logVal
  }

  getPositionFromLogValue(value) {
    return this.roundToOneDecimal(
      this.minpos + (Math.log(value) - this.minlval) / this.scale
      );
  }

  setValue(value) {
    if (value === this.minpos) {
      // hell is javascript float math
      // The reason that I'm doing this is that about 1/4 of the time,
      // the min slider freaks out and sets the value to an invalid state
      // when being asked to handle a display value of 0. Not every time,
      // though. That would be too easy. Instead, just detect when a
      // min value is being requested and ram it through.
      this.forceMinValue()
      return
    }
    if (!this.rangeInput || !this.valueLabel) {
      throw new Error('Range input or value label is not initialized.');
    }
    const parsedValue = parseFloat(value);
    if (isNaN(parsedValue)) {
      throw new Error('Invalid value. Please provide a valid float.');
    }
    const roundedValue = this.roundToOneDecimal(parsedValue);
    this.rangeInput.value = this.getPositionFromLogValue(roundedValue);
    this.valueLabel.textContent = this.roundToOneDecimal(
      this.getLogValueFromPosition()
    ).toString()
  }
}

class TdMinRange extends TdRangeComponent {
  constructor() {
    super();
    this.innerHTML = `
      <label for="tdMinRange" class="form-label">
        TD Min: <span class="badge text-bg-secondary" id="tdMinValueLabel">0</span>
      </label>
      <input
        type="range"
        class="form-range"
        value="0.1"
        min="0"
        max="100"
        step="0.1"
        id="tdMinRange"
      >
    `;
    this.syncSelector = 'td-min-text'
  }

  connectedCallback() {
    if (this._initialized) return
    this.maxlval = Math.log(99.9)
    // query within this element; not the whole document
    this.rangeInput = this.querySelector('#tdMinRange')
    this.valueLabel = this.querySelector('#tdMinValueLabel')
    this.syncTarget = document.querySelector(this.syncSelector)
    if (this.rangeInput) {
      this.rangeInput.addEventListener('input', this.updateTdMinRange.bind(this))
    }
    this._initialized = true
  }

  getMinValue() {
    return 0;
  }

  getMaxValue() {
    return 99.9;
  }

  updateTdMinRange(event) {
    let localVal = this.getValue();

    this.valueLabel.textContent = localVal.toString();

    let maxRange = document.querySelector('td-max-range')
    if (localVal > maxRange.getValue()) {
      maxRange.setValue(this.roundToOneDecimal(localVal + 0.1));
      maxRange.syncValue();
    }
    this.syncValue();
  }
}

class TdMaxRange extends TdRangeComponent {
  constructor() {
    super();
    this.innerHTML = `
      <label for="tdMaxRange" class="form-label">
        TD Max: <span class="badge text-bg-secondary" id="tdMaxValueLabel">100</span>
      </label>
      <input
        type="range"
        class="form-range"
        value="100"
        min="0"
        max="100"
        step="0.1"
        id="tdMaxRange"
      >
    `;
    this.syncSelector = 'td-max-text'
  }

  connectedCallback() {
    if (this._initialized) return
    this.maxlval = Math.log(100)
    this.rangeInput = this.querySelector('#tdMaxRange')
    this.valueLabel = this.querySelector('#tdMaxValueLabel')
    this.syncTarget = document.querySelector(this.syncSelector)
    if (this.rangeInput) {
      this.rangeInput.addEventListener('input', this.updateTdMaxRange.bind(this))
    }
    this._initialized = true
  }

  getMinValue() {
    return 0.1;
  }

  updateTdMaxRange(event) {
    let localVal = this.getValue();

    this.valueLabel.textContent = localVal.toString();

    let minRange = document.querySelector('td-min-range')
    if (localVal < minRange.getValue()) {
      minRange.setValue(this.roundToOneDecimal(localVal - 0.1));
      minRange.syncValue();
    }
    this.syncValue();
  }
}

class TdMinText extends TdTextComponent {
  constructor() {
    super();
    this.innerHTML = `
      <div class="input-group mb-3 has-validation">
        <span class="input-group-text" id="tdMinTextAddon">TD Min</span>
        <input
          type="text"
          id="tdMinTextInput"
          class="form-control"
          placeholder="0"
          aria-label="tdMinTextLabel"
          aria-describedby="tdMinTextAddon"
        >
        <div class="invalid-feedback" id="tdMinTextInputFeedback"></div>
      </div>
    `;
    this.syncSelector = 'td-min-range'
  }

  connectedCallback() {
    if (this._initialized) return
    this.textInput = this.querySelector('#tdMinTextInput')
    this.maxTd = document.querySelector('td-max-text')
    this.errorMessage = this.querySelector('#tdMinTextInputFeedback')
    this.syncTarget = document.querySelector(this.syncSelector)
    if (this.textInput) {
      this.textInput.addEventListener('input', this.updateTdMinText.bind(this))
    }
    this._initialized = true
  }

  updateTdMinText(event) {
    if (this.getValue() > this.maxTd.getValue()) {
      this.setErrorMessage("Number must be smaller than TD Max.")
      this.setErrorState(false);
      return
    }

    const isValid = this.validateTdTextBox();
    if (!isValid) {
      this.setErrorMessage("Please enter a number between 0 and 100.")
    } else {
      this.syncValue()
    }

    this.setErrorState(isValid);
  }
}

class TdMaxText extends TdTextComponent {
  constructor() {
    super();
    this.innerHTML = `
      <div class="input-group mb-3 has-validation">
        <span class="input-group-text" id="tdMaxTextAddon">TD Max</span>
        <input
          type="text"
          id="tdMaxTextInput"
          class="form-control"
          placeholder="100"
          aria-label="tdMaxTextLabel"
          aria-describedby="tdMaxTextAddon"
        >
        <div class="invalid-feedback" id="tdMaxTextInputFeedback">
          Please enter a number between 0 and 100.
        </div>
      </div>
    `;
    this.syncSelector = 'td-max-range'
  }

  connectedCallback() {
    if (this._initialized) return
    this.textInput = this.querySelector('#tdMaxTextInput')
    this.minTd = document.querySelector('td-min-text')
    this.errorMessage = this.querySelector('#tdMaxTextInputFeedback')
    this.syncTarget = document.querySelector(this.syncSelector)
    if (this.textInput) {
      this.textInput.addEventListener('input', this.updateTdMaxText.bind(this))
    }
    this._initialized = true
  }

  updateTdMaxText(event) {
    if (this.getValue() < this.minTd.getValue()) {
      this.setErrorMessage("Number must be larger than TD Min.")
      this.setErrorState(false);
      return
    }
    const isValid = this.validateTdTextBox();
    if (!isValid) {
      this.setErrorMessage("Please enter a number between 0 and 100.")
      this.setErrorState(isValid);
    } else {
      this.syncValue()
    }
    this.setErrorState(isValid);
  }
}

customElements.define('td-min-range', TdMinRange);
customElements.define('td-max-range', TdMaxRange);
customElements.define('td-min-text', TdMinText);
customElements.define('td-max-text', TdMaxText);
