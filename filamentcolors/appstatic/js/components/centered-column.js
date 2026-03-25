/**
 * A custom web component that creates a centered column using Bootstrap's grid system.
 *
 * The component wraps its content in a `.row.justify-content-center` and a column div.
 * It automatically extracts column-related classes (e.g., `col-8`, `col-md-6`) from the
 * host element and applies them to the internal column div.
 *
 * @element centered-column
 *
 * @example
 * <!-- Default (col-8) -->
 * <centered-column>Centred content</centered-column>
 *
 * @example
 * <!-- Custom widths -->
 * <centered-column class="col-10 col-md-8 col-lg-6">
 *   Responsive centered content
 * </centered-column>
 *
 * @example
 * <!-- With additional Bootstrap utilities -->
 * <centered-column class="col-8 mt-5 text-center">
 *   Centered column with margin top and centered text
 * </centered-column>
 */
class CenteredColumn extends HTMLElement {
  constructor() {
    super();
    this._initialized = false;
  }

  connectedCallback() {
    if (this._initialized) return;

    // Use a timeout to ensure that child elements are fully parsed before rendering.
    // This is a common pattern for components that manipulate their children.
    setTimeout(() => {
      this._render();
    }, 0);
  }

  _render() {
    if (this._initialized) return;
    this._initialized = true;

    // 1. Identify column classes and other classes from the host element
    const colClasses = [];
    const classList = Array.from(this.classList);

    classList.forEach(cls => {
      if (cls === 'col' || cls.startsWith('col-')) {
        colClasses.push(cls);
      }
    });

    // Default to col-8 if no column classes are provided
    if (colClasses.length === 0) {
      colClasses.push('col-8');
    }

    // 2. Set up host element
    // Custom elements are display: inline by default; we need block for the row to work correctly.
    this.style.display = 'block';

    // Remove column-specific classes from the host element to prevent double-application
    // if the component is placed inside another Bootstrap row.
    colClasses.forEach(cls => this.classList.remove(cls));

    // 3. Prepare the grid structure
    const row = document.createElement('div');
    row.className = 'row justify-content-center';

    const col = document.createElement('div');
    col.className = colClasses.join(' ');

    // 4. Move all current children (including text nodes) into the column div
    while (this.firstChild) {
      col.appendChild(this.firstChild);
    }

    // 5. Build the final structure
    row.appendChild(col);
    this.appendChild(row);
  }
}

// Define the custom element if it hasn't been defined yet
if (!customElements.get('centered-column')) {
  customElements.define('centered-column', CenteredColumn);
}
