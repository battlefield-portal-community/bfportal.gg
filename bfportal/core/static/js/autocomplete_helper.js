function bindTriggers(html_id){
    const deck = $(`#${html_id}_on_deck`);
    deck.bind('added', function () {
        deck.children().last().show({
            duration: 100,
            start: function () {
                deck.children().last().css('display', 'flex')
            }
        })
        if(!deck.hasClass("ml-2")) deck.addClass("ml-2")
    })
    deck.bind('killed', function () {
        if(!deck.children().length) deck.removeClass("ml-2")
    })
}

defer(function initAutoCompleteHelper() {
    $(document).ready(function () {
        const autocompleteContainers = ["tags", "creators"]

        autocompleteContainers.forEach(function (container) {
            const input = $(`#id_${container}_text`),
                inputContainer = $(`#${container}InputContainer`),
                deck = $(`#id_${container}_on_deck`);
            if(deck.children().length){
                if(!deck.hasClass("ml-2")) deck.addClass("ml-2")
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
