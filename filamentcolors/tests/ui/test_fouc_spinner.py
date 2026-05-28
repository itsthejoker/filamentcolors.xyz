import pytest
from playwright.sync_api import expect


@pytest.mark.playwright
def test_spinner_resolves_with_undefined_element_outside_app(nwo_page, live_server):
    """The FOUC spinner must clear even when an undefined custom element is
    injected into <body> outside the app container.

    Browser extensions, password managers, and page-translation tools inject
    their own (never-defined) custom elements into the document. The old check
    scanned the whole document for ':not(:defined)', so any such element left
    the spinner overlaying the page forever. Scoping the check to the
    component's own subtree fixes it. A 4s timeout (under the 5s hard fallback)
    asserts the scoping works, not just the safety net.
    """
    # Inject as soon as <body> exists (like an extension at document_start),
    # so the rogue element is present before <main-container> is even parsed.
    nwo_page.add_init_script(
        """
        const id = setInterval(() => {
            if (document.body) {
                clearInterval(id);
                document.body.appendChild(
                    document.createElement('x-rogue-extension-widget')
                );
            }
        }, 5);
        """
    )
    nwo_page.goto(f"{live_server.url}/")

    expect(nwo_page.locator(".fouc-spinner-container")).to_have_count(0, timeout=4000)
    expect(nwo_page.locator("main-container#main")).to_have_css(
        "opacity", "1", timeout=4000
    )
