/**
 * @license
 * Copyright (c) Joe Kaufeld -- github.com/itsthejoker.
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

document.addEventListener("DOMContentLoaded", function (event) {
    const anchorElements = Array.from(document.querySelectorAll('a'));
    const modalElements = {};

    anchorElements.forEach(el => {
        // don't run on a tags that aren't mail links
        if (el.href.includes("mailto") === false) return;

        // If it's a mailto link, break it apart, then generate a modal
        // for each mailto link. Stick that modal at the bottom of the
        // document and let it chill out until it's called for.
        const id = createID();
        const newModal = getModalContent({id, ...parseMailto(el.href)});
        document.body.insertAdjacentHTML("beforeend", newModal);

        // bootstrap 5 only
        modalElements[id] = new bootstrap.Modal(document.getElementById(`emailmagic-${id}`));

        el.addEventListener('click', e => {
            e.preventDefault();
            modalElements[id].show();
        });
    });
});

function getModalContent({id, emailAddress, subject, cc, bcc, body}) {
    return `
        <div class="modal fade" id="emailmagic-${id}" tabindex="-1" role="dialog" aria-label="Select your preferred email provider!" aria-hidden="true">
          <div class="modal-dialog modal-dialog-centered modal-sm" role="document">
            <div class="modal-content">
              <div class="modal-header">
                <h5 class="modal-title" id="exampleModalLongTitle">Open email in...</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"><i class="fas fa-times" style="color:black"></i></button>
              </div>
              <div class="modal-body">
                <div class="d-grid gap-2">
                    <a
                      href="https://mail.google.com/mail/?view=cm&fs=1&to=${emailAddress}&su=${subject}&cc=${cc}&bcc=${bcc}&body=${body}"
                      class="btn bg-gradient-warning"
                      target="_blank"
                    >Gmail</a>
                    <a
                      href="https://outlook.office.com/owa/?path=/mail/action/compose&to=${emailAddress}&subject=${subject}&body=${body}"
                      class="btn bg-gradient-info"
                      target="_blank"
                    >Outlook</a>
                    <a
                      href="https://compose.mail.yahoo.com/?to=${emailAddress}&subject=${subject}&cc=${cc}&bcc=${bcc}&body=${body}"
                      class="btn bg-gradient-secondary"
                      target="_blank"
                    >Yahoo! Mail</a>
                    <a href="mailto:${emailAddress}" class="btn bg-gradient-success" target="_blank">Default</a>
                    <hr/>
                    <button class="btn bg-gradient-dark" onclick="copyToClipboard('${emailAddress}')">Copy to Clipboard</button>
                </div>
              </div>
              <div class="modal-footer">
                <button type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal">Close</button>
              </div>
            </div>
          </div>
        </div>
    `
}

function copyToClipboard(val) {
    navigator.clipboard.writeText(val);
}

function createID() {
    // https://stackoverflow.com/a/3242438
    return Math.random().toString(36).substr(2, 9)
}

function parseMailto(href) {
    const mailto = new URL(href);

    return {
        emailAddress: mailto.pathname,
        subject: mailto.searchParams.get("subject") || "",
        cc: mailto.searchParams.get("cc") || "",
        bcc: mailto.searchParams.get("bcc") || "",
        body: mailto.searchParams.get("body") || "",
    }
}
