function getID(flow) {
    h = flow.s.parentElement.href;
    return h.slice(h.lastIndexOf('/') + 1);
}

function updateCounter() {
    document.getElementById("multiselect-badge").innerText = window.multiselectArray.length;
}

function preselect_items(ids) {
    ids.forEach(
        item => {
            element = $(`#s${item} .multiselector`)
            console.log(element)
            element[0].click()
        }
    );
}

const eventContract = new jsaction.EventContract();

// Events will be handled for all elements under this container.
eventContract.addContainer(document.getElementById('deck-of-many-things'));

// Register the event types we care about.
eventContract.addEvent('click');
//eventContract.addEvent('mousedown');

// Create the dispatcher and connect it to the event contract. The event contract queues events
// while the dispatcher takes events and dispatches them to the correct handler.
const dispatcher = new jsaction.Dispatcher();
eventContract.dispatchTo(dispatcher.dispatch.bind(dispatcher));

const handleSelection = function (flow) {
    flow.C.preventDefault();
    if (
        flow.s.getAttribute('aria-checked') === "false"
    ) {
        window.multiselectArray.push(getID(flow));
        flow.s.setAttribute('aria-checked', 'true');
        el = flow.s.nextElementSibling.getElementsByClassName('card-img-overlay')[0];
        el.style.backgroundImage = "url('https://img.icons8.com/dusk/30/000000/checked.png'), linear-gradient(to bottom,rgba(0, 0, 0, 0.26),transparent 30px,transparent)";
        el.style.color = "#007bff";
        flow.s.parentElement.style.transform = "translateZ(0px) scale3d(0.95, 0.95, 1)";
        flow.s.parentElement.className = "card mb-4 anim big-shadow";
        updateCounter();
    } else {

        flow.s.setAttribute('aria-checked', 'false');
        el = flow.s.nextElementSibling.getElementsByClassName('card-img-overlay')[0];
        el.style.backgroundImage = "url('https://img.icons8.com/cotton/30/000000/plus.png'), linear-gradient(to bottom,rgba(0, 0, 0, 0.26),transparent 30px,transparent)";
        el.style.color = "";
        flow.s.parentElement.className = "card mb-4 anim shadow";
        flow.s.parentElement.style.transform = '';
        id = getID(flow);
        result = window.multiselectArray.filter(item => item !== id);
        window.multiselectArray = result;
        updateCounter();
    }
    b = document.getElementById("collection-buttons");
    fs = document.getElementsByClassName("card-img-overlay");
    if (
        window.multiselectArray.length > 0
    ) {
        if (!(b.getAttribute('class').includes('slide-in-left'))) {
            b.setAttribute('class', 'collection-buttons slide-in-left');
            for (i = 0; i < fs.length; i++) {
                fs[i].style.display = 'block';
                fs[i].parentElement.previousElementSibling.style.width = "300px";
                fs[i].parentElement.previousElementSibling.style.height = "105%";
                fs[i].parentElement.previousElementSibling.style.top = "-5px";
                fs[i].parentElement.previousElementSibling.style.left = "-7px";
            }
        }
    } else {
        b.setAttribute('class', 'collection-buttons slide-out-left');
        for (i = 0; i < fs.length; i++) {
            fs[i].style.display = '';
            fs[i].parentElement.previousElementSibling.style.width = "36px";
            fs[i].parentElement.previousElementSibling.style.height = "36px";
            fs[i].parentElement.previousElementSibling.style.top = "0px";
            fs[i].parentElement.previousElementSibling.style.left = "0px";
        }
    }
};

dispatcher.registerHandlers(
    'card',                          // the namespace
    null,                            // handler object
    {                                // action map
        'select': handleSelection,
    });

$('#go-button').on('click', function (evt) {
    url = window.location.origin + "/library/collection/" + window.multiselectArray.join();
    window.location.assign(url);
});

$('#clear-button').on('click', function (evt) {
    fs = document.getElementsByClassName("card-img-overlay");
    for (i = 0; i < fs.length; i++) {
        fs[i].style.display = '';
        fs[i].parentElement.previousElementSibling.style.width = 30;
        fs[i].parentElement.previousElementSibling.style.height = 30;
        fs[i].parentElement.previousElementSibling.style.top = 0;
        fs[i].parentElement.previousElementSibling.style.left = 0;
        fs[i].parentElement.previousElementSibling.setAttribute('aria-checked', 'false');
        fs[i].style.backgroundImage = "url('https://img.icons8.com/cotton/30/000000/plus.png'), linear-gradient(to bottom,rgba(0, 0, 0, 0.26),transparent 30px,transparent)";
        fs[i].style.color = "";
        fs[i].parentElement.parentElement.className = "card mb-4 anim shadow";
        fs[i].parentElement.parentElement.style.transform = '';
    }
    window.multiselectArray = [];
    d = document.getElementById("collection-buttons");
    d.setAttribute('class', 'collection-buttons slide-out-left');
});

$(document).ready(function () {
    window.multiselectArray = [];
    // this is a global variable that is set by the template
    if (preselected !== "") {
        preselect_items(preselected)
    }
});
