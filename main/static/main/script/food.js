var menu;
var choices;
var excludes = [3983, 3758, 283, 4048, 228, 48, 135, 247];

function find(array, id) {
    return $.grep(array, function (e) {
        return e.Id === parseInt(id);
    })[0];
}

function changeOptions(select, options) {
    select.find('option:gt(0)').remove();
    $.each(options, function (index, item) {
        if (!('Name' in item)) {
            item = find(menu.products, item.Id);
        }
        var name;
        if (item.Name === '.') {
            name = item.Syn + ' ';
        } else {
            name = item.Name + ' ';
            if (item.Syn) {
                name += '(' + item.Syn + ') '
            }
        }
        if (('Price' in item) && (item.Price !== 0)) {
            name += '[' + item.Price + 'kr.]';
        }
        if (excludes.indexOf(item.Id) === -1) {
            var option = $("<option></option>")
                .attr("value", item.Id)
                .text(name);
            select.append(option);
        }
    });
    select.next().show();
}

function hideGreater(select) {
    select.parent().find('select:gt(' + select.index() + ')').next().hide();
}

$(function () {
    $('form#food select').select2();
    hideGreater($('form select#category'));
    $.getJSON('https://gist.githubusercontent.com/bomjacob/bd82c4ead494bf7fe8ea8a93d53b9779/raw/1e3f84d722fdf922fd4375e07ffd45f81e3a01ee/byens_burger.json', function (data) {
        menu = data.Menu;
        changeOptions($('form select#category'), menu.Categories);
    });
    $('form#food').on('change', 'select', function () {
        var select = $(this);
        if (select.attr('id') === 'category') {
            hideGreater(select);

            var products = [];
            var items = find(menu.Categories, select.val());
            $.each(items.Items, function (index, item) {
                products = products.concat(item.Products);
            });
            changeOptions(select.nextAll('select').first(), products);
            choices = products;
        } else if (select.attr('id') === 'product') {
            hideGreater(select);

            var product = find(choices, select.val());
            console.log(product);
            var ids = {'Parts': 'part', 'Accs': 'acc'};
            $.each(product, function (key, val) {
                if (key in ids) {
                    $.each(val, function (index, item) {
                        changeOptions($('form#food select#' + ids[key] + index), item);
                    });
                }
            });
        }

    });
});
