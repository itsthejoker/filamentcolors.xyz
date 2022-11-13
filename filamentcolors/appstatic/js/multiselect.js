$(document).ready(function () {

    window.multiselectArray = [];
    // this is a global variable that is set by the template
    if (preselected !== "") {
        preselect_items(preselected)
    }

    let cards = $(".swatchcard");
    cards.each(function () {
        $(this).on("long-press", function (e) {
            e.preventDefault();

            let card = $(e.target).closest(".swatchcard");
            if (is_selected(card)) {
                return
            }
            select_item(card);
            enableCollectionMode();
        })
    })
})


function showCollectionCounter() {
    updateCounter();
    const el = $("#collection-buttons");
    el.removeClass("way-off-screen");
    el.removeClass("slide-out-left");
    el.addClass("slide-in-left");
}


function hideCollectionCounter() {
    const el = $("#collection-buttons");
    el.removeClass("slide-in-left");
    el.addClass("slide-out-left");
}


function enableCollectionMode() {
    enable_overlays();
    showCollectionCounter();
    swatches = $(".swatchcard")
    swatches.each(function () {
        $(this).closest(".card-img-overlay").css("display", "block")
    })
}


function getID(obj) {
    // expects a jquery obj
    return obj.data()['swatchId']
}


function updateCounter() {
    document.getElementById("multiselect-badge").innerText = window.multiselectArray.length;
}

function getCounter() {
    return window.multiselectArray.length
}


function is_selected(obj) {
    return obj.hasClass("selected-card")
}


function select_item(obj) {
    // this expects a jquery obj of a single swatch
    window.multiselectArray.push(getID(obj));

    obj.addClass("selected-card")
    obj.removeClass("shadow");
    obj.css("transform", "translateZ(0px) scale3d(0.925, 0.925, 1)");
    obj.addClass('big-shadow');
}


function deselect_item(obj) {
    // this expects a jquery obj of a single swatch
    let id = getID(obj)
    window.multiselectArray = window.multiselectArray.filter(item => item !== id)

    obj.removeClass("selected-card")
    obj.addClass("shadow");
    obj.css("transform", "");
    obj.removeClass('big-shadow');
}


function enable_overlays() {
    $(".card-img-overlay").each(function () {
        $(this).css("display", "block").css("height", "100%").css("width", "100%")
    })
}


function disableOverlays() {
    $(".card-img-overlay").each(function () {
        $(this).css("display", "")
    })
}


function preselect_items(ids) {
    ids.forEach(item => {
        obj = $(`#s${item}`);
        select_item(obj)
    });
    updateCounter();
    showCollectionCounter();
    enable_overlays();
}

$(".card-img-overlay").each(function () {
    $(this).on("click", function (evt) {
        let card = $(this).closest(".swatchcard");
        is_selected(card) ? deselect_item(card) : select_item(card)
        updateCounter();
        if (getCounter() === 0) {
            disableOverlays();
            hideCollectionCounter();
        }
    })
})

$('#go-button').on('click', function (evt) {
    url = window.location.origin + "/library/collection/" + window.multiselectArray.join();
    window.location.assign(url);
});

$('#clear-button').on('click', function (evt) {
    window.multiselectArray.forEach(id => deselect_item($(`#s${id}`)));
    updateCounter();
    disableOverlays();
    hideCollectionCounter();
});
