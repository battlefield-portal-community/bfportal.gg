// https://portal.battlefield.com/experience/package/era?playgroundId=d23be170-33aa-11ed-98f8-9d6912d338ca

$(document).ready(function () {
    "use strict";
    $("body").on('click touch', function (event) {
        animateNavBarPane(true);
    });
    $('#cat-checkboxes input[type="radio"]').on('change', function () {
        $('input[type="radio"]').not(this).prop('checked', false);
        const selected_label = $.trim(this.closest('label').textContent),
            required_asterisk = $('<p class="inline-block text-red-500 ml-2">*</p>');
        let inp, otherInp;
        if (selected_label !== "Prefab") {
            inp = $('#id_code');
            otherInp = $('#id_exp_url');
        } else {
            inp = $('#id_exp_url');
            otherInp = $('#id_code');
        }
        const req = $(`#${inp.prop('id')}Reason`),
            otherReq = $(`#${otherInp.prop('id')}Reason`);

        if (req.siblings().length <= 2) {
            required_asterisk.insertBefore(req);
        }
        if (otherReq.siblings().length > 2) {
            otherReq.prev().remove();
        }
        otherInp.prop("required", false);
        inp.prop("required", true);
    });

    function toTitleCase(str) {
        return str.replace(
            /\w\S*/g,
            function (txt) {
                return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
            }
        );
    }


    async function GetPlaygroundInfo(url = null, experienceCode = null) {
        let api_url;
        if (url) {
            api_url = `https://api.gametools.network/bf2042/playground/?playgroundid=${url.search.split('=').at(-1)}&blockydata=false&lang=en-us&return_ownername=false`;
        } else if (experienceCode) {
            // https://api.gametools.network/bf2042/playground/?experiencecode=aava5b&blockydata=false&lang=en-us
            api_url = `https://api.gametools.network/bf2042/playground/?experiencecode=${experienceCode}&blockydata=false&lang=en-us&return_ownername=false`;
        }
        console.log(api_url);
        const resp = await fetch(api_url);
        return resp.json();
    }

    function fillForm(GTApiResponse) {
        GTApiResponse.playgroundName = String;
        GTApiResponse.playgroundDescription = String;
        if (!GTApiResponse.hasOwnProperty('errors')) {
            GTApiResponse.tag.forEach(elm => {
                addTagToDeck(elm['metadata']['translations'][0]['localizedText'])
            });


            GTApiResponse = GTApiResponse.validatedPlayground;
            document.getElementById("id_title").value = toTitleCase(GTApiResponse.playgroundName);
            document.getElementById("id_description").value = GTApiResponse.playgroundDescription;
            document.getElementById("id_no_players").value = GTApiResponse.mapRotation.maps[0].gameSize;
            {
                document.getElementById("id_no_bots").value = GTApiResponse.mapRotation.maps[0].gameSize;

            }
        }
    }

    $('#autoFillBtn').on('click touch', function () {
        let expUrl = $("#id_exp_url");
        let experienceCode = $("#id_code");

        if (expUrl.val()) {
            expUrl = new URL(expUrl.val());
            if (expUrl.origin === "https://portal.battlefield.com" && expUrl.search.split('=').at(0) === "?playgroundId" && expUrl.search.split('=').at(-1).length === 36) {
                GetPlaygroundInfo(expUrl).then(resp => {
                    fillForm(resp);

                });
            }
        } else if (experienceCode.val()) {
            experienceCode = experienceCode.val();
            if (experienceCode.length === 6) {
                GetPlaygroundInfo(null, experienceCode).then(resp => {
                    fillForm(resp);
                });
            }
        }
    });

    const navBarPane = $('#nav-bar-pane');
    navBarPane.css({
        'right': `-${navBarPane.width()}px`
    });
    navBarPane.on('click touch', function (event) {
        event.stopPropagation();
    });


    function animateNavBarPane(hide = null) {
        if (hide) {
            navBarPane.animate({'right': `-${navBarPane.width()}px`}, 100, function () {
                navBarPane.addClass("hidden");
            });
        } else {
            if (navBarPane.css('right') === '0px') {
                navBarPane.animate({'right': `-${navBarPane.width()}px`}, 100, function () {
                    navBarPane.addClass("hidden");
                });
            } else {
                navBarPane.removeClass("hidden");
                navBarPane.animate({'right': '0px'}, 300);
            }
        }
    }

    $('#menuIcon').on('click touch', function (e) {
        e.stopPropagation();
        showPopUpBackGround();
        $('#nav-bar-pane').height($('#main').height() - 2);
        animateNavBarPane();
    });


    $('#expUrlSpan').on('click touch', function () {
        navigator.clipboard.writeText($(this).attr('expurl'));
    });

    addDropDownPair("profileButton", "accountNavBarDropdown")

});

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
