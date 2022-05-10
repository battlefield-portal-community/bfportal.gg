async function GetPlaygroundInfo(url){
    "use strict";
    const api_url = `https://api.gametools.network/bf2042/playground/?playgroundid=${url.search.split('=').at(-1)}`;
    console.log(api_url);
    const resp = await fetch(api_url);
    return resp.json();
}

$(document).ready(function() {
    "use strict";
    $('#cat-checkboxes input[type="checkbox"]').on('change', function () {
        $('input[type="checkbox"]').not(this).prop('checked', false);
        const selected_label = ($.trim(this.closest('label').textContent));
        const required_asterisk = $('<p class="inline-block text-red-500">*</p>');
        const cat = $('#id_categoriesReason').closest('tr');
        let inp;
        let otherInp;
        if (selected_label !== "Prefab") {
            inp = $('#id_code');
            otherInp = $('#id_exp_url');
        } else {
            inp = $('#id_exp_url');
            otherInp = $('#id_code');
        }
        const req = $(`#${inp.prop('id')}Reason`);
        const otherReq =  $(`#${otherInp.prop('id')}Reason`);
        if (req.siblings().length <= 2) {
            required_asterisk.insertBefore(req);
        }
        if (otherReq.siblings().length > 2) {
            otherReq.prev().remove();
        }
        
        otherInp.prop("required", false);
        inp.prop("required", true);
        cat.after(inp.closest('tr'));


    });

    function toTitleCase(str) {
        return str.replace(
            /\w\S*/g,
            function (txt) {
                return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
            }
        );
    }

    $('#id_exp_url').on('change', function () {
        if ($(this).val()) {
            const url = new URL($(this).val());
            if (url.origin === "https://portal.battlefield.com") {
                if (url.search.split('=').at(0) === "?playgroundId") {
                    if (url.search.split('=').at(-1).length === 36) {
                        GetPlaygroundInfo(url).then(resp => {
                            resp.playgroundName = String;
                            resp.playgroundDescription = String;
                            if (!resp.hasOwnProperty('errors')) {
                                let tags = "";
                                resp.tag.forEach(elm => tags = tags.concat(elm.values[0].readableSettingName, ","));
                                resp = resp.validatedPlayground;
                                document.getElementById("id_title").value = toTitleCase(resp.playgroundName);
                                document.getElementById("id_description").value = resp.playgroundDescription;
                                const tagElm = document.getElementById("id_tags");
                                tagElm.value = tags;
                                if (tags.length > 1) {
                                    tagElm.readOnly = true;
                                    document.getElementById(tagElm.id + "Reason").textContent = "[Auto Completed as Exp Url is Provided]";
                                }
                                document.getElementById("id_no_players").value = resp.mapRotation.maps[0].gameSize;
                                {
                                    document.getElementById("id_no_bots").value = resp.mapRotation.maps[0].gameSize;

                                }
                            }
                        });
                    }
                }
            }
        }
    });
    $('#expUrlSpan').on('click touch', function () {
        navigator.clipboard.writeText($(this).attr('expurl'));
    });
});