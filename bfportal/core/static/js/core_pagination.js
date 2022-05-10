function applyFilters() {
    const urlParams = new URLSearchParams(window.location.search),
        checked_cats = document.querySelectorAll('input[id^=cat_]:checked'),
        checked_tags = document.querySelectorAll('input[id^=tag_]:checked');

    // will work as clear if no tag or cat is selected

    urlParams.delete('category');
    urlParams.delete('tag');
    [...checked_cats].forEach(elm => {
        urlParams.append('category', elm.value)
    });
    [...checked_tags].forEach(elm => {
        urlParams.append('tag', elm.value)
    });
    window.location.search = urlParams;
};
function clearFilters() {
    const urlParams = new URLSearchParams(window.location.search);
    urlParams.delete('category');
    urlParams.delete('tag');
    window.location.search = urlParams;
}

function addItems(root, dataList) {
    dataList.forEach(elm => {

        const input = document.createElement('input'),
            label = document.createElement('label'),
            container = document.createElement('div');
        input.type = 'checkbox';
        if (root.id === "categoriesList") {
            input.id = `cat_${elm}`;
        } else {
            input.id = `tag_${elm}`;
        }
        input.value = elm;
        input.className = "form-check-input appearance-none h-4 w-4 border border-gray-300 rounded-sm bg-white checked:bg-blue-600 checked:border-blue-600 focus:outline-none transition duration-200 my-1 align-top bg-no-repeat bg-center bg-contain float-left cursor-pointer";
        label.setAttribute('for', input.id);
        label.appendChild(input);
        label.innerHTML = `${input.outerHTML}&nbsp;${elm}`
        container.className = 'bg-card-bg rounded-lg p-1';
        container.appendChild(label);
        root.appendChild(container);
    })
}

function makeCheckboxList(root, dataList) {
    const urlParams = new URLSearchParams(window.location.search),
        checked_cats = urlParams.getAll('category'),
        checked_tags = urlParams.getAll('tag');
    if (root.id === "categoriesList") {
        if (checked_cats.length > 0) addItems(root, checked_cats)
        dataList['results'].forEach(elm => {
            if (!checked_cats.includes(elm['text'])) addItems(root, [elm['text']])
        })
    }
    if (root.id === "tagsList") {
        if (checked_tags.length > 0) addItems(root, checked_tags)
        dataList['results'].forEach(elm => {
            if (!checked_tags.includes(elm['text'])) addItems(root, [elm['text']])
        })
    }


}

function animateFilters(root, listElement) {
    if (root.style.opacity !== "" && root.style.opacity > 0) {
        anime({
            targets: `#${root.id}`,
            opacity: '0',
            easing: 'easeOutExpo',
            complete: function () {
                root.classList.add('invisible');
                root.style.left = "50%"
            }
        });
    } else {
        if (!listElement.children.length > 0) {
            fetch((root.id === "categoriesPane") ? '/api/categories/' : '/api/tags/?q=')
                .then(resp => resp.json())
                .then(data => {
                    makeCheckboxList(listElement, data)
                }).then(data => {
                const searchParams = new URLSearchParams(window.location.search);
                if (root.id === "categoriesPane") {
                    const cats = document.querySelectorAll('input[id^=cat_]');
                    [...cats].forEach(elm => {
                        if (searchParams.getAll('category').includes(elm.value)) {
                            elm.checked = true;
                        }
                    });
                } else {
                    const tags = document.querySelectorAll('input[id^=tag_]');
                    [...tags].forEach(elm => {
                        if (searchParams.getAll('tag').includes(elm.value)) {
                            elm.checked = true;
                        }
                    })
                }
            })
        }
        root.classList.remove('invisible');
        anime({
            targets: `#${root.id}`,
            left: '100%',
            opacity: '100%',
            easing: 'easeOutQuint',
            begin: function () {
                document.getElementById("tagsInputBox").focus();
            }
        });
    }
}

function showTags() {
    animateFilters(
        document.getElementById('tagsPane'),
        document.getElementById('tagsList')
    )
}

function populateTags() {
    const tagList = document.getElementById('tagsList');
    tagList.innerHTML = ''
    fetch(`/api/tags/?q=${document.getElementById('tagsInputBox').value}`)
        .then(resp => resp.json())
        .then(data => {
            makeCheckboxList(document.getElementById('tagsList'), data)
        })
        .then(function () {
                const searchParams = new URLSearchParams(window.location.search),
                    tags = document.querySelectorAll('input[id^=tag_]');
                [...tags].forEach(elm => {
                    if (searchParams.getAll('tag').includes(elm.value)) {
                        elm.checked = true;
                    }
                })
            }
        )
}

function capitalize(s) {
    return s && s[0].toUpperCase() + s.slice(1);
}

async function showCategories() {
    animateFilters(
        document.getElementById("categoriesPane"),
        document.getElementById('categoriesList')
    );
}

document.getElementById("categoriesPane").addEventListener('click', function (event) {
    event.stopPropagation();
});
document.getElementById("tagsPane").addEventListener('click', function (event) {
    event.stopPropagation();
});

window.onclick = function (event) {
    const pageIdList = ['categories', 'tags'];
    pageIdList.forEach(elm => {
        if (!event.target.closest(`#show${capitalize(elm)}Button`)) {
            const pane = document.getElementById(`${elm}Pane`);
            if (!pane.classList.contains('invisible')) {
                pane.classList.add('invisible');
                pane.style.opacity = '0%';
                pane.style.left = '50%';
            }
        }
    });
};
function innerDimensions(elem) {
    "use strict";
  let computedStyle = getComputedStyle(elem);

  let width = elem.clientWidth; // width with padding
  let height = elem.clientHeight; // height with padding

  height -= parseFloat(computedStyle.paddingTop) + parseFloat(computedStyle.paddingBottom);
  width -= parseFloat(computedStyle.paddingLeft) + parseFloat(computedStyle.paddingRight);
  return { height, width };
}

function resizeTagsInput() {
    let elm = document.getElementById("tagsPane");
    console.log(innerDimensions(elm));
}
const observer = new ResizeObserver(entries => {
  entries.forEach(entry => {
        document.getElementById("tagsInputBox").style.width = `${innerDimensions(entry.target).width}px`;
  });
});
observer.observe(document.getElementById("tagsPane"));