/**
 * Created by Ali on 2016-08-26.
 */

var protocol = 'http://';
var host = protocol;
var synchro_path_extra = host+'/api/eav/attributes/';
var synchro_path_extra2 = host+'/api/eav/values/';
var incremental_id = 0;

function push_column_values_to_server(item)
{
    $.ajax({
        type: "POST",
        url: synchro_path_extra2,
        data: item,
        cache: false,
        async: false,
        headers: getHeader(),
        dataType: 'json',
        success: function (response) {
            if(response.status == '201'){
                update_one_by_index('name', item.name, 'synchronized', true, 'eav-columns-values');
                update_one_by_index('name', item.name, 'original_id', response.data.id, 'eav-columns-values');
            }
        },
        error: function (response) {
            console.log(response);
        }
    });
}

function push_extra_columns_to_server(item)
{
    $.ajax({
        type: "POST",
        url: synchro_path_extra,
        data: item,
        cache: false,
        async: false,
        headers: getHeader(),
        dataType: 'json',
        success: function (response) {
            if(response.status == '201'){
                update_one_by_index('name', item.name, 'synchronized', true, 'eav-columns');
                update_one_by_index('name', item.name, 'original_id', response.data.id, 'eav-columns');
                update_items_by_index('column', parseInt(item.id), 'attribute', response.data.id, 'eav-columns-values');
            }
        },
        error: function (response) {
            console.log(response);
        }
    });
}

function delete_extra_column(column, user_id)
{
    var col_name = 'extra-column-'+user_id+'-'+column;
    update_one_by_index('name', col_name, 'deleted', true, 'eav-columns');
    $('#'+col_name).remove();
}

function delete_column_values(column)
{
    var store = getStoreByName('eav-columns-values');
    var request = store.index('column').getAll(parseInt(column));
    request.onsuccess = function() {
        var result = request.result;
        if(result){
            $(result).each(function(i, item){
                $('#'+item.name).parent().remove();
                item.deleted = true;
                store.put(item);
            });
        }
    };
}

function create_extra_columns_html(column, delete_icon)
{
    var th = $('<th>').attr('rowspan', 2)
                    .attr('id', column.name)
                    .addClass('extra-column')
                    .attr('itemscope', column.id)
                    .attr('itemref', column.owner)
                    .text(column.label);
    if(delete_icon){
        th.addClass('extra-column');
        var btn = $('<button class="btn-sm btn-danger delete-column"><i class="icon-delete icon-white"></i></a>');
        th.append(btn);
    }else{
        th.addClass('extra-shared-column');
    }
    $('#thead-line-1').append(th);
}

function create_extra_field_html(column, itemid, user_id)
{
    var td = $('<td>').append(
            $('<input>').attr('type', 'text')
                    .attr('name', 'extra-field-'+user_id+'-'+column+'-'+itemid)
                    .attr('id', 'extra-field-'+user_id+'-'+column+'-'+itemid)
                    .attr('class', 'outreach-field extra-field')
                    .addClass('extra-field-'+column)
                    .attr('itemscope', itemid)
                    .attr('itemid', column)
    );

    return td;
}

function add_extra_columns()
{
    var store1 = getStoreByName('eav-shared-columns');
    var request1 = store1.getAll();
    request1.onsuccess = function(){
        var result1 = request1.result;
        $(result1).each(function(i, col){
            create_extra_columns_html(col, false);
        });
    };

    var store = getStoreByName('eav-columns');
    var request = store.getAll();
    request.onsuccess = function(){
        var result = request.result;
        $(result).each(function(i, col){
            columns = col.id;
            if(col.deleted == false){
                create_extra_columns_html(col, true);
            }
        });
        columns = columns + 1;
    };
}

function add_fill_extra_fields_data(entity)
{
    var store = getStoreByName('eav-columns-values');
    var request = store.index('entity').getAll(parseInt(entity));
    request.onsuccess = function(){
        var result = request.result;
        if(result){
            $(result).each(function(i, item){
                $('#'+item.name).val(item.value_text);
            });
        }
    };
}

function create_column_values(item, name, column)
{
    var store = getStoreByName('eav-columns-values');
    store.put({entity_ct: entity_ct, entity: item.id, entity_id: item.original_id, value_text: '', column: column.id, attribute: column.original_id, name: name, synchronized: false, deleted: false});
}

function add_column_to_store(column)
{
    var store = getStoreByName('eav-columns');
    store.put(column);
}

function add_table_newline(itemid, prototype, table)
{
    var total_records = $('#registrations-table').find('tr.registration-line').length;
    incremental_id = total_records + 1;
    var line_html =  prototype.find('tbody').html().replace(/\$\$itemscope_id\$\$/g, itemid);
    table.find('tbody').append(line_html);

    $('#line-'+itemid).find('.incremental_number').text(incremental_id);

    var extra_columns = table.find('.extra-column');
    $(extra_columns).each(function(i, col){
        var td = create_extra_field_html($(this).attr('itemscope'), itemid, $(this).attr('itemref'));
        $('#line-'+itemid).append(td);
    });
}
