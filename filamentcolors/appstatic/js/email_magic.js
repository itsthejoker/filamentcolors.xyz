function getBootstrapModalContent(data) {
    return `
        <div class="modal fade" id="exampleModalCenter" tabindex="-1" role="dialog" aria-labelledby="exampleModalCenterTitle" aria-hidden="true">
          <div class="modal-dialog modal-dialog-centered modal-sm" role="document">
            <div class="modal-content">
              <div class="modal-header">
                <h5 class="modal-title" id="exampleModalLongTitle">Modal title</h5>
                <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                  <span aria-hidden="true">&times;</span>
                </button>
              </div>
              <div class="modal-body">
                ...
              </div>
              <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button>
                <button type="button" class="btn btn-primary">Save changes</button>
              </div>
            </div>
          </div>
        </div>
    `
}

function getOrCreateModalAnchor() {

}

function createID() {
    return Math.random().toString(36).substr(2, 9)
}

function magic(e) {
    e.preventDefault();
    e.stopPropagation();
    console.log(e.target.href);
    console.log("fuck");
    // todo: swap out for vanilla js with bootstrap 5
    $('#patreonModal').modal()
}

Array.from(
    document.getElementsByTagName('a')
).forEach(
    function (el, index) {
        if (el.href.indexOf("mailto") !== -1) {
            el.addEventListener(
                'click', function (e) {
                    magic(e)
                }
            );
            // el.setAttribute("data-toggle", "modal");
            // el.setAttribute("href", "#patreonModal");
            // el.setAttribute("data-target", "#patreonModal")
        }
    }
);
