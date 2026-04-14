/**
 * A custom web component that acts as a main container and protects against
 * Flash of Unstyled Content (FOUC).
 *
 * It displays a loading spinner in the center of the page while waiting for all
 * custom elements to be defined. Once all custom elements are ready, it fades
 * out the spinner and fades in the container.
 *
 * The component expects to be manually styled to zero opacity initially:
 * `main-container { opacity: 0; }`
 *
 * @element main-container
 *
 * @slot - Default slot for the main content of the page.
 */
class MainContainer extends HTMLElement {
  constructor() {
    super();
    this._initialized = false;
    this._spinner = null;
    this._interval = null;
  }

  connectedCallback() {
    if (this._initialized) return;

    // Use a timeout to ensure that child elements are fully parsed before rendering.
    setTimeout(() => {
      this._render();
    }, 0);
  }

  _render() {
    if (this._initialized) return;
    this._initialized = true;

    // Ensure the host element is display: block as it's a 'main' container
    this.style.display = 'block';

    // Create the internal 'main' wrapper
    const main = document.createElement('main');

    // Copy any classes set by the end user to the main element
    if (this.className) {
      main.className = this.className;
    }

    // Move all children into the main wrapper
    while (this.firstChild) {
      main.appendChild(this.firstChild);
    }
    this.appendChild(main);

    // Create and show the loading spinner
    this._showSpinner();

    // Start the check for custom elements
    this._startCheck();
  }

  /**
   * Creates a full-screen spinner overlay.
   * @private
   */
  _showSpinner() {
    // Create a spinner container that covers the viewport
    const container = document.createElement('div');
    container.style.position = 'fixed';
    container.style.top = '0';
    container.style.left = '0';
    container.style.width = '100vw';
    container.style.height = '100vh';
    container.style.display = 'flex';
    container.style.justifyContent = 'center';
    container.style.alignItems = 'center';
    container.style.zIndex = '10000'; // High z-index to stay on top
    container.style.backgroundColor = 'var(--bs-body-bg, white)';
    container.style.transition = 'opacity 0.3s ease-out';
    container.className = 'fouc-spinner-container';

    const spinner = document.createElement('div');
    spinner.className = 'spinner-border text-primary';
    spinner.setAttribute('role', 'status');
    spinner.style.width = '3rem';
    spinner.style.height = '3rem';

    const label = document.createElement('span');
    label.className = 'visually-hidden';
    label.textContent = 'Loading...';

    spinner.appendChild(label);
    container.appendChild(spinner);
    document.body.appendChild(container);

    this._spinner = container;
  }

  /**
   * Runs a check every 50ms to see if all custom elements are defined.
   * @private
   */
  _startCheck() {
    this._interval = setInterval(() => {
      // Find all custom elements that are not yet defined
      const undefinedElements = document.querySelectorAll(':not(:defined)');

      // Check if any of these undefined elements are custom elements (have a hyphen)
      const pendingCustomElements = Array.from(undefinedElements).some(el => el.tagName.includes('-'));
      // console.log('Waiting for the following custom elements to be defined: ', pendingCustomElements ? Array.from(undefinedElements) : 'none')
      if (!pendingCustomElements) {
        setInterval(() => {
          this._finishLoading();
        }, Math.random() * 500);
      }
    }, 50);
  }

  /**
   * Fades out the spinner and fades in the container.
   * @private
   */
  _finishLoading() {
    if (this._interval) {
      clearInterval(this._interval);
      this._interval = null;
    }

    // Fade out the spinner
    if (this._spinner) {
      this._spinner.style.opacity = '0';
      setTimeout(() => {
        if (this._spinner && this._spinner.parentNode) {
          this._spinner.parentNode.removeChild(this._spinner);
        }
      }, 300); // Match transition duration
    }

    // Fade in the container
    // We expect the user to have set 'transition: opacity ...' on main-container
    // Setting it to 1 will trigger any CSS transition.
    this.style.opacity = '1';
  }

  disconnectedCallback() {
    if (this._interval) {
      clearInterval(this._interval);
    }
    if (this._spinner && this._spinner.parentNode) {
      this._spinner.parentNode.removeChild(this._spinner);
    }
  }
}

// Define the custom element
if (!customElements.get('main-container')) {
  customElements.define('main-container', MainContainer);
}
