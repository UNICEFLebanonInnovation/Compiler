$(document).ready(function(){

    $("#quick-search").focus(function() { $(this).select(); });

    $("#quick-search").autocomplete({
        search: function( event, ui ) { $('#search-loader').removeClass('hidden'); },
        focus: function( event, ui ) { },
        response: function( event, ui ) { $('#search-loader').addClass('hidden'); },
        source: function (request, response) {
            $.ajax({
                url: '/MSCC/Quick-Search/',
                dataType: "json",
                data: {
                    term: request.term
                },
                success: function (data) {
                   if(JSON.parse(data.result).length == 0){
                        var result = [{ error: 'No matches found',  value: response.term }];
                        response(result);
                     }else{
                        response(JSON.parse(data.result));
                    }
                }
            });
        },
        minLength: 3,
        autoFocus: true,
    }).autocomplete("instance")._renderMenu = function (ul, items) {
        var that = this;
        $(ul).addClass("list-group");

        $.each(items, function (index, item) {
            that._renderItemData(ul, item);
        });
        $(ul).find("li:odd").addClass("odd");
        $(ul).appendTo('#quick-search-result');
    };

    $("#quick-search").autocomplete("instance")._renderItem = function (ul, item) {
        if(item.error) {
            var item_list =  $('<li class="list-group-item">');
            var widget = $('<div class="widget-content p-0">');
            var wrapper = $('<div class="widget-content-wrapper">').append('<div class="widget-content-left mr-3"><i class="fa fa-user"></i>');

            var content = $('<div class="widget-content-left">');
            var heading = $('<div class="widget-heading">')
            var href = $('<a>').append('No result found');
            var subheading = $('<div class="widget-subheading">');

            item_list.append(widget);
            widget.append(wrapper);
            wrapper.append(content);
            content.append(heading);
            content.append(subheading);
            heading.append(href);

            return item_list.appendTo(ul);
        }

        var item_list =  $('<li class="list-group-item">');
        var widget = $('<div class="widget-content p-0">');
        var wrapper = $('<div class="widget-content-wrapper">').append('<div class="widget-content-left mr-3"><i class="fa fa-user"></i>');
//            .append('<img width="42" class="rounded-circle" src="/static/images/user.png" alt="">');

        var content = $('<div class="widget-content-left">');
        var heading = $('<div class="widget-heading">');
        var full_name = item.child__first_name + " " + item.child__father_name + " " + item.child__last_name;
        var href = $('<a>').attr('href', '/MSCC/Child-Profile/'+item.id+'/').append(full_name);
        var subheading = $('<div class="widget-subheading">').append(item.child__mother_fullname);

        item_list.append(widget);
        widget.append(wrapper);
        wrapper.append(content);
        content.append(heading);
        content.append(subheading);
        heading.append(href);

        return item_list.appendTo(ul);
    };

});
