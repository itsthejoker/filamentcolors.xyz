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

function getModalContent(id, emailAddress, subject, cc, bcc, body) {
    return `
        <div class="modal fade" id="emailmagic-${id}" tabindex="-1" role="dialog" aria-labelledby="Select your preferred email provider!" aria-hidden="true">
          <div class="modal-dialog modal-dialog-centered modal-sm" role="document">
            <div class="modal-content">
              <div class="modal-header">
                <h5 class="modal-title" id="exampleModalLongTitle">Open email in...</h5>
                <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                  <span aria-hidden="true">&times;</span>
                </button>
              </div>
              <div class="modal-body">
                <a 
                  href="https://mail.google.com/mail/?view=cm&fs=1&to=${emailAddress}&su=${subject}&cc=${cc}&bcc=${bcc}&body=${body}"
                  class="btn btn-block btn-outline-danger"
                  target="_blank"
                >Gmail</a>
                <a 
                  href="https://outlook.office.com/owa/?path=/mail/action/compose&to=${emailAddress}&subject=${subject}&body=${body}"
                  class="btn btn-block btn-outline-primary"
                  target="_blank"
                >Outlook</a>
                <a
                  href="https://compose.mail.yahoo.com/?to=${emailAddress}&subject=${subject}&cc=${cc}&bcc=${bcc}&body=${body}"
                  class="btn btn-block btn-outline-success"
                  target="_blank"
                >Yahoo! Mail</a>
                <a href="mailto:${emailAddress}" class="btn btn-block btn-outline-info" target="_blank">Default</a>
                <hr/>
                <button class="btn btn-block btn-outline-dark" onclick="copyToClipboard('${emailAddress}')">Copy to Clipboard</button>
              </div>
              <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button>
              </div>
            </div>
          </div>
        </div>
    `
}

function copyToClipboard(val){
    navigator.clipboard.writeText(val);
}

function createID() {
    // https://stackoverflow.com/a/3242438
    return Math.random().toString(36).substr(2, 9)
}

function magic(e, id) {
    // Don't let the browser actually start the email opening process
    e.preventDefault();
    // is this actually necessary? Not sure.
    e.stopPropagation();
    // todo: swap out for vanilla js with bootstrap 5
    // jquery is already here because this is for bootstrap and
    // bootstrap 4 requires it.
    $(`#emailmagic-${id}`).modal()
}

function parseMailto(href) {
    let emailAddress,
        subject = "",
        cc = "",
        bcc = "",
        body = "";

    // remove "mailto:"
    cleanedData = href.slice(href.indexOf(":")+1);
    if (cleanedData.indexOf("?") !== -1) {
        let parts = cleanedData.split("?");
        emailAddress = parts[0]

        parts = parts[1].split("&")
        parts.forEach(function (snippet) {
            snippet = snippet.split("=")
            switch (snippet[0]) {
                case "cc":
                    cc = snippet[1];
                    break;
                case "bcc":
                    bcc = snippet[1];
                    break;
                case "subject":
                    subject = snippet[1];
                    break;
                case "body":
                    body = snippet[1];
            }
        });

    } else {
        emailAddress = cleanedData
    }
    return [emailAddress, subject, cc, bcc, body]
}

Array.from(
    document.getElementsByTagName('a')
).forEach(
    function (el, index) {
        if (el.href.indexOf("mailto") !== -1) {
            // If it's a mailto link, break it apart, then generate a modal
            // for each mailto link. Stick that modal at the bottom of the
            // document and let it chill out until it's called for.
            let id = createID();
            let newModal = getModalContent(id, ...parseMailto(el.href))
            document.body.insertAdjacentHTML("beforeend", newModal)
            el.addEventListener(
                'click', function (e) {
                    magic(e, id)
                }
            );
        }
    }
);
