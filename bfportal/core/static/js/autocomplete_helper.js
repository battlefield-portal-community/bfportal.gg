function bindTriggers(html_id) {
    const deck = $(`#${html_id}_on_deck`);
    deck.bind('added', function () {
        deck.children().last().show({
            duration: 100,
            start: function () {
                deck.children().last().css('display', 'flex')
            }
        })
        if (!deck.hasClass("ml-2")) deck.addClass("ml-2")
    })
    deck.bind('killed', function () {
        if (!deck.children().length) deck.removeClass("ml-2")
    })
}

function addTagToDeck(tagName) {
    fetch(`/ajax_select/ajax_lookup/tags?term=${tagName}`).then(
        resp => resp.json().then(json => {
            return addTag(json[0])
        })
    )
    function addTag(tag){
        const pk = tag.pk,
            id = "id_tags",
            $deck = $("#id_tags_on_deck"),
            $text = $("#id_tags_text"),
            $this = $('#id_tags'),
            prev = $this.val();

        if (prev.indexOf('|' + pk + '|') === -1) {
            $this.val((prev ? prev : '|') + pk + '|');
            addKiller(tag.repr, pk);
            $text.val('');
            $deck.trigger('added', [tag.pk, tag]);
            $this.trigger('change');
        }

        function addKiller(repr, pk) {
            const killId = 'kill_' + pk + id,
                killButton = '<span class="ui-icon ui-icon-trash" id="' + killId + '">X</span> ';
            $deck.append('<div id="' + id + '_on_deck_' + pk + '">' + killButton + repr + ' </div>');

            $('#' + killId).click(function () {
                kill(pk);
                $deck.trigger('killed', [pk]);
            });
        }

        function kill(pk) {
            $this.val($this.val().replace('|' + pk + '|', '|'));
            $('#' + id + '_on_deck_' + pk).fadeOut().remove();
        }
        return false;
    }
}


defer(function initAutoCompleteHelper() {
    $(document).ready(function () {
        const autocompleteContainers = ["tags", "creators"]

        autocompleteContainers.forEach(function (container) {
            const input = $(`#id_${container}_text`),
                inputContainer = $(`#${container}InputContainer`),
                deck = $(`#id_${container}_on_deck`);
            if (deck.children().length) {
                if (!deck.hasClass("ml-2")) deck.addClass("ml-2")
                deck.children().each(function () {
                    $(this).css('display', 'flex')
                })
            }
            input.focus(function () {
                inputContainer.addClass("border-1/2 border-bf2042-4")
            })
            input.focusout(function () {
                inputContainer.removeClass("border-1/2 border-bf2042-4")
            })
            bindTriggers(`id_${container}`)
        })
        const markdownContainer = $('#markdown_container'),
            input = $("#id_description");
        input.focus(function () {
            markdownContainer.addClass("border-1/2 border-bf2042-4")
        })
        input.focusout(function () {
            markdownContainer.removeClass("border-1/2 border-bf2042-4")
        })
    })
})

function handleKeyDown(elm, event) {
    if (!elm.value && event.keyCode === 8) {
        const deck = $(`#${$(elm).parent().attr('id') === "tagsInputContainer" ? 'id_tags' : 'id_creators'}_on_deck`),
            children = deck.children();
        if (children.length) {
            const c = children.last().children();
            //c.last is the label for last element in deck
            //c.first is the trash icon (it's hidden by default)
            c.last().hide(100, function () {
                c.first().click()
            })
        }
    }
}
