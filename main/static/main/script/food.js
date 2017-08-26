var menu;
var choices;

function find(array, id) {
    return $.grep(array, function (e) {
        return e.Id === parseInt(id);
    })[0];
}

function changeOptions(select, options) {
    select.find('option:gt(0)').remove();
    $.each(options, function (index, item) {
        var price;
        if (!('Name' in item)) {
            item = find(menu.products, item.Id);
        }
        var name;
        if ($.isEmptyObject(item)) { // Item was excluded
            return true; // Continue
        }
        if (item.Name === '.') {
            name = item.Syn;
        } else {
            name = item.Name;
            if (item.Syn) {
                name += ' (' + item.Syn + ')'
            }
        }
        var baseName = name;
        if (('Price' in item) && (item.Price !== 0)) {
            name += ' [' + item.Price + 'kr.]';
            price = item.Price;
        } else {
            select.attr('price', null);
        }
        var option = $("<option></option>")
            .attr("value", item.Id)
            .text(name)
            .attr('name', baseName);
        if (price) {
            option.attr('price', price)
        }
        select.append(option);
    });
    select.next().show();
}

function hideGreater(select) {
    var selects = select.closest('form').children('select');
    var index = selects.index(select);
    selects.slice(index + 1).next().hide();
}

function checkPrice(menu) {
    var price = 0;
    $('form#food select option:checked').each(function () {
        var p = $(this).attr('price');
        if (p !== undefined) {
            price += parseFloat(p);
        }
    });
    $('h4#price span').text(price);
    $('form#food input#id_price').val(price);
}

function toggleButton() {
    var show = true;
    $('form#food .select2').each(function () {
        if ($(this).css('display') !== 'none') {
            var select = $(this).prev();
            if (select.val() === "") {
                show = false;
            }
        }
    });
    $('form#food input[type="submit"]').toggle(show);
}

$(function () {
    $('form#food select').select2();
    hideGreater($('form select#id_category'));
    $.getJSON(foodJsonUrl, function (data) {
        menu = data.Menu;
        changeOptions($('form select#id_category'), menu.Categories);
        toggleButton();
    });
    var form = $('form#food');
    form.on('change', 'select', function () {
        var select = $(this);
        if (select.attr('id') === 'id_category') {
            hideGreater(select);

            var products = [];
            var items = find(menu.Categories, select.val());
            $.each(items.Items, function (index, item) {
                products = products.concat(item.Products);
            });
            changeOptions(select.nextAll('select').first(), products);
            choices = products;
        } else if (select.attr('id') === 'id_product') {
            hideGreater(select);

            var product = find(choices, select.val());
            var ids = {'Parts': 'id_part', 'Accs': 'id_acc'};
            $.each(product, function (key, val) {
                if (key in ids) {
                    $.each(val, function (index, item) {
                        changeOptions($('form#food select#' + ids[key] + index), item);
                    });
                }
            });
        }
        checkPrice(menu);
        toggleButton();
    });
    form.on('submit', function (e) {
        $('select option:checked').each(function () {
            $(this).val($(this).attr('name'));
        });
        return true;
    });
});
