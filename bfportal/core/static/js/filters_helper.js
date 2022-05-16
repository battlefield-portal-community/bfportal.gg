defer(function () {
    "use strict";
    $(document).ready(function () {
        const filtersPane = $('#filtersPane'),
            navBar = $('#navBar'),
            url = new URL(window.location.href),
            searchParams = new URLSearchParams(url.search);


        filtersPane.css({
            'top' : `${navBar.innerHeight()}px`,
            // 'left': `-${filtersPane.width()}px`
        });

        ["tags", "cats", "experience", "date", "user"].forEach(elm => {
            const label = $(`#${elm}InputLabel`),
                input = $(`#${elm}Input`);
            const observer = new ResizeObserver(entries =>  {
                label.height(`${input.height()}px`);
            });
            observer.observe(document.getElementById(`${elm}Input`));
        });
        const filtersContainer = $('#filtersContainer'),
            hideFiltersButton = $('#hideFilterButton'),
            mainBtn = $('#mainBtn');
        if ([...searchParams.keys()].length <= 1 && (searchParams.keys().next().value === 'page' || !searchParams.keys().next().value)){
            hideFiltersButton.text("Show Filters");
            filtersContainer.hide();
            filtersContainer.removeClass('visible');
            filtersContainer.addClass('invisible');
            mainBtn.hide();

        } else {

            filtersContainer.removeClass('invisible');
            filtersContainer.addClass('visible');
            hideFiltersButton.text("Hide Filter");
            filtersContainer.show();
            populateFilters();
            mainBtn.show();
        }

    });
    function callSearchApi(searchQuery="") {
        populateGrids("tagsInputHolder", true, searchQuery);

    }
    let searchCallTimeout;
    $('#tagSearchInput').on('input', function(event) {
        const spinner = $('#tagsSearchSpinner');
        spinner.removeClass('hidden');
        if (searchCallTimeout){
            clearTimeout(searchCallTimeout);
        }
        searchCallTimeout = setTimeout(function () {
            callSearchApi(event.target.value);
            spinner.addClass('hidden');
        } , 1000);
    });
    $('#filtersApply').on('click touch', function () {
        let queryParamList = [];
        ["tagsInputHolder", "catsInput"].forEach(grid => {
            const currGrid = $(`#${grid}`);
            $.each(currGrid.find("input:checkbox:checked"), function (index, elm){
                if (grid === "tagsInputHolder") {
                    queryParamList.push(`tag=${encodeURIComponent($(elm).prop('value'))}`);
                } else {
                    queryParamList.push(`category=${encodeURIComponent($(elm).prop('value'))}`);
                }
            });
        });
        ["experience", "user"].forEach(input => {
            const currInput = $(`#${input}NameInput`),
                val = $(currInput).val();
            if (val) {
                queryParamList.push(`${input}=${encodeURIComponent(val)}`);
            }
        });
        ["From", "To"].forEach(date => {
            const val = $(`#date${date}`).val();
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
    "use strict";
    const url = new URL(window.location.href),
    searchParams = new URLSearchParams(url.search);

    populateGrids("tagsInputHolder", false, "");
    populateGrids("catsInput", false, "");
    if (searchParams.has('experience')) {
        $('#experienceNameInput').val(searchParams.get('experience'));
    }
    if (searchParams.has('user')) {
        $('#userNameInput').val(searchParams.get('user'));
    }
    if (searchParams.has('From')) {
        $('#dateFrom').val(searchParams.get('From'));
    }
    if (searchParams.has('From')) {
        $('#dateTo').val(searchParams.get('To'));
    }

}

function addItems(root, dataList=null, dataItem=null) {
    function addItem(elm) {
        let id = elm.replace(/\W/g, '');
        id = root.attr('id') === "catsInput" ? `cat_${id}` : `tag_${id}`;
        if (!document.getElementById(id)){
            const input = document.createElement('input'),
                label = document.createElement('label');
            input.type = 'checkbox';
            input.id = id;
            input.value = elm;
            input.className = "bg-card-bg border-none focus:ring-0";
            label.className = "text-white min-w-max";
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
        let tagsInputHolder;
        if (root === "tagsInput"){
            tagsInputHolder = $('tagsInputHolder');
            tagsInputHolder.hide();
        }
        dataList.forEach(elm => {addItem(elm);});
        tagsInputHolder ? tagsInputHolder.show(100): null;
    }
}

function populateGrids(root, update, searchQuery=""){
        fetch(root === "tagsInputHolder" ? `/api/tags/?q=${searchQuery}` : `/api/categories/?q=${searchQuery}` ).then(resp => {
            resp.json().then(json => {
                const currInput = $(`#${root}`);
                const currQuery = root === "tagsInputHolder" ? `tag` : `category`;
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
        btn = $('#hideFilterButton');
    filtersContainer.toggle(200);
    mainBtn.toggle();
    populateGrids("tagsInputHolder", false, "");
    populateGrids("catsInput", false, "");
    if (btn.text() === "Show Filters") {
        filtersContainer.removeClass('invisible');
        filtersContainer.addClass('visible');
        btn.text("Hide Filters");

    } else {
        filtersContainer.removeClass('visible');
        filtersContainer.addClass('invisible');
        btn.text("Show Filters");
    }

}