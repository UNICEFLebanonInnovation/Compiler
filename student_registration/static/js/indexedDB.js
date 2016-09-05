/**
 * Created by Ali on 2016-08-26.
 */

var db = null;

function createDataStore(database_name, version,  store_name)
{
    var request = indexedDB.open(database_name, version);

    request.onupgradeneeded = function() {
        // The database did not previously exist, so create object stores and indexes.
        db = request.result;
        var flag = false;
        try {
            if(!db.objectStoreNames().contains(store_name)) {
                flag = true;
            }
        }catch(err) {
            flag = true;
        }
        if(flag){
            db.createObjectStore(store_name, {keyPath: "id", autoIncrement:true});
        }
    };

    request.onsuccess = function() {
        db = request.result;
    };
}

function getStoreByName(name)
{
    var store = db.transaction([name], "readwrite").objectStore(name);
    return store;
}

function getRecord(itemid, store_name)
{
    var store = getStoreByName(store_name);
    var request = store.get(parseInt(itemid));
    return request;
}

function update_item_store(itemid, name, value, store_name)
{
    var store = getStoreByName(store_name);
    var request = store.get(itemid);
    request.onsuccess = function(){
        var item = request.result;
        item[name] = value;
        store.put(item);
    };
}

function update_one_by_index(index_name, index_value, name, value, store_name)
{
    var store = getStoreByName(store_name);
    var request = store.index(index_name).get(index_value);
    request.onsuccess = function(){
        var item = request.result;
        if(item){
            item[name] = value;
            store.put(item);
        }
    };
}

function update_items_by_index(index_name, index_value, name, value, store_name)
{
    var store = getStoreByName(store_name);
    var request = store.index(index_name).getAll(index_value);
    request.onsuccess = function(){
        var result = request.result;
        if(result){
            $(result).each(function(i, item){
                item[name] = value;
                store.put(item);
            });
        }
    };
}

function delete_from_store(itemid, store_name)
{
    var store = getStoreByName(store_name);
    var request = store.get(parseInt(itemid));
    request.onsuccess = function(){
        result = request.result;
        if(result.synchronized == true){
            update_item_store(parseInt(itemid), 'deleted', true, store_name);
        }else{
            store.delete(parseInt(itemid));
        }
    }
}
