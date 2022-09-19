defer(function filter_helper_defer() {
    "use strict";
    $(document).ready(function () {
        const filtersPane = $('#filtersPane'),
            navBar = $('#navBar'),
            url = new URL(window.location.href),
            searchParams = new URLSearchParams(url.search);

        console.log(searchParams)
        filtersPane.css({
            'top' : `${navBar.innerHeight()}px`,
            // 'left': `-${filtersPane.width()}px`
        });

        const filtersContainer = $('#filtersContainer'),
            hideFiltersButton = $('#toggleFilterButton'),
            mainBtn = $('#mainBtn');

        if ([...searchParams.keys()].length <= 1 && (searchParams.keys().next().value === 'page' || !searchParams.keys().next().value)){
            hideFiltersButton.text("Show Filters");
            populateFilters();
            filtersContainer.hide();
            filtersContainer.removeClass('visible');
            filtersContainer.addClass('invisible');

            mainBtn.hide();

        } else {
            filtersContainer.removeClass('invisible');
            filtersContainer.addClass('visible');
            hideFiltersButton.text("Hide Filter");
            hideFiltersButton.removeClass("bg-bf2042-4")
            hideFiltersButton.addClass("bg-bf2042-6")
            filtersContainer.show();
            populateFilters();
            mainBtn.show();
        }

    });
    function callSearchApi(searchQuery="") {
        populateGrids("tagsContainer", true, searchQuery);

    }
    let searchCallTimeout;
    $('#tagsInput').on('input', function(event) {
        // const spinner = $('#tagsSearchSpinner');
        // spinner.removeClass('hidden');
        // if (searchCallTimeout){
        //     clearTimeout(searchCallTimeout);
        // }
        // searchCallTimeout = setTimeout(function () {
        //     spinner.addClass('hidden');
        // } , 1000);
        console.log(event.target.value)
        callSearchApi(event.target.value);
    });
    $('#filtersApply').on('click touch', function () {
        let queryParamList = [];
        ["tagsContainer", "categoriesContainer"].forEach(grid => {
            const currGrid = $(`#${grid}`);
            $.each(currGrid.find("input:checkbox:checked"), function (index, elm){
                if (grid === "tagsContainer") {
                    queryParamList.push(`tag=${encodeURIComponent($(elm).prop('value'))}`);
                } else {
                    queryParamList.push(`category=${encodeURIComponent($(elm).prop('value'))}`);
                }
            });
        });
        ["experience", "creator"].forEach(input => {
            const currInput = $(`#${input}NameInput`),
                val = $(currInput).val();
            if (val) {
                queryParamList.push(`${input}=${encodeURIComponent(val)}`);
            }
        });
        ["from", "to"].forEach(date => {
            const val = $(`#${date}Date`).val();
            if (val) {
                queryParamList.push(`${date}=${encodeURIComponent(val)}`);
            }
        });
        // window.history.replaceState({}, '', `${location.pathname}?${queryParamList.join("&")}`);
        console.log(`?${queryParamList.join("&")}`);
        document.location = `?${queryParamList.join("&")}`;

    });
    $('#filtersClear').on('click touch', function () {
        window.location.href = window.location.href.split('?')[0];
    });
});

function populateFilters(){
    console.log("Populating Filters")
    "use strict";
    const url = new URL(window.location.href),
    searchParams = new URLSearchParams(url.search);

    populateGrids("tagsContainer", false, "");
    populateGrids("categoriesContainer", false, "");
    if (searchParams.has('experience')) {
        $('#experienceNameInput').val(searchParams.get('experience'));
    }
    if (searchParams.has('user')) {
        $('#userNameInput').val(searchParams.get('user'));
    }
    if (searchParams.has('From')) {
        $('#dateFrom').val(searchParams.get('From'));
    }
    if (searchParams.has('To')) {
        $('#dateTo').val(searchParams.get('To'));
    }

}

function addItems(root, dataList=null, dataItem=null) {
    function addItem(elm) {
        let id = elm.replace(/\W/g, '');
        console.log(id)
        id = root.attr('id') === "categoriesContainer" ? `cat_${id}` : `tag_${id}`;
        if (!document.getElementById(id)){
            const input = document.createElement('input'),
                label = document.createElement('label');
            input.type = 'checkbox';
            input.id = id;
            input.value = elm;
            input.className = "rounded border-0 bg-default text-bf2042-4 shadow-none mr-1 focus:ring focus:ring-offset-0 focus:ring-bf2042-4 focus:ring-opacity-0";
            label.className = "text-sm text-white font-medium flex flex-row items-center gap-x-1";
            label.setAttribute('for', input.id);
            label.appendChild(input);
            label.innerHTML = `${input.outerHTML}&nbsp;${elm}`;
            root.append(label);
            if (dataList !== null) {
                document.getElementById(input.id).checked = true;
            }
        }
    }
    if (dataItem) {
        addItem(dataItem);
    }
    if (dataList) {
        let tagsContainer;
        if (root === "tagsInput"){
            tagsContainer = $('tagsContainer');
            tagsContainer.hide();
        }
        dataList.forEach(elm => {addItem(elm);});
        tagsContainer ? tagsContainer.show(100): null;
    }
}

function populateGrids(root, update, searchQuery=""){
        fetch(root === "tagsContainer" ? `/api/tags/?q=${searchQuery}` : `/api/categories/?q=${searchQuery}` ).then(resp => {
            resp.json().then(json => {
                const currInput = $(`#${root}`);
                const currQuery = root === "tagsContainer" ? `tag` : `category`;
                if (!update){
                    const searchParams = new URLSearchParams(window.location.search);
                    if (searchParams.has(currQuery)) {
                        addItems(currInput, searchParams.getAll(currQuery));
                    }
                }
                currInput.find("input:checkbox:not(:checked)").closest('label').remove();
                $.each(json.results, function (index, value) { addItems(currInput, null, value.text);});
            });
        });

}

function showFiltersPane() {
    "use strict";
    ["tagsInputHolder", "catsInput"].forEach(grid => {populateGrids(grid, false);});
}

function setFilterLabelHeight(base_name){
    // label.height(`${input.height()}px`);
    const label = $(`#${base_name}InputLabel`);
    label.height(`${$(`#${base_name}Input`).height()}px`);
    label.css('align-items', 'center');
}

function hideAllFilters() {
    const filtersContainer = $('#filtersContainer'),
        mainBtn = $('#mainBtn'),
        btn = $('#toggleFilterButton');
    filtersContainer.toggle(200);
    mainBtn.toggle();
    if (btn.text() === "Show Filters") {
        populateGrids("tagsInputHolder", false, "");
        populateGrids("catsInput", false, "");
        filtersContainer.removeClass('invisible');
        filtersContainer.addClass('visible');
        anime({
            targets: '#toggleFilterButton',
            backgroundColor: "#FF2C10",
            easing: 'easeOutQuint',
            duration: "500"
        });
        btn.text("Hide Filters");


    } else {
        filtersContainer.removeClass('visible');
        filtersContainer.addClass('invisible');
        btn.text("Show Filters");
        anime({
            targets: '#toggleFilterButton',
            backgroundColor: '#26FFDF',
            easing: 'easeOutQuint',
            duration: "500"
        });
    }

}
