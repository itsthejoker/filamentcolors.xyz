let welcomeExperience = $();
let steps = [];
let parent = $();

function goToStep(num) {
    $.each(steps, function (index, item) {
        let count = parseInt(item.classList.value.split('-')[1]);
        item.hidden = count !== num;
    });
    parent.animate({scrollTop: 0}, 'fast');
}

function getCurrentStep() {
    let currentStep = 1;
    $.each(steps, function (index, item) {
        if (item.hidden !== true) {
            currentStep = parseInt(item.classList.value.split('-')[1]);
        }
    });
    return currentStep
}

function resetSteps() {
    $.each(steps, function (index, item) {
        item.hidden = true;
    });
    steps[0].hidden = false;
}

function sleep(time) {
    return new Promise((resolve) => setTimeout(resolve, time));
}

function finishbutton() {
    $("#welcomeExperience").modal('hide');
    sleep(1000).then(() => {
        resetSteps()
    });
}

// this fires on page load to hide all the other steps; otherwise it would
// just render as one gigantic modal with everything in one.
$(document).ready(function () {
    welcomeExperience = $('#welcomeExperienceContent');
    steps = welcomeExperience.children();
    const parent = $('#welcomeExperience');
    resetSteps();

    // I can't believe this actually works
    parent[0].addEventListener('keydown', (e) => {
        if (!e.repeat) {
            if (e.key === "ArrowLeft") {
                cs = getCurrentStep();
                if (cs - 1 < 1) {
                    // sanity check
                    return
                }
                goToStep(cs - 1)
            }
            if (e.key === "ArrowRight") {
                cs = getCurrentStep();
                if (cs + 1 > steps.length) {
                    // sanity check
                    return
                }
                goToStep(cs + 1)
            }
        }
    });
});
