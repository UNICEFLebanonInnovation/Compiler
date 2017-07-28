/**
 * Created by ali on 7/22/17.
 */

var arabic_fields = "#id_first_name, #id_father_name, #id_last_name, #id_mother_fullname";

$(document).ready(function(){

    // $('#id_registration_date').datetimepicker({
    //     "format": "mm/dd/yyyy",
    //     "pickTime": false,
    //     "viewMode": "years",
    //     "stepping": 0,
    //     "showClear": true,
    //     "showClose": true,
    //     "disabledHours": true
    // });

    $(document).on('blur', arabic_fields, function(){
        checkArabicOnly($(this));
    });

    $("#id_search_student").autocomplete({
      source: function( request, response ) {
        $.ajax( {
          url: '/api/students/',
          dataType: "json",
          data: {
            term: request.term
          },
          success: function( data ) {
            response(data);
          }
        } );
      },
      minLength: 3,
      select: function( event, ui ) {
          $("#id_search_student").val('');
          // get_registration(ui.item);
          return false;
      }
    }).autocomplete( "instance" )._renderMenu = function( ul, items ) {
         var that = this;
         $.each( items, function( index, item ) {
             that._renderItemData( ul, item );
        });
        $( ul ).find( "li:odd" ).addClass( "odd" );
    };

    $("#id_search_student").autocomplete( "instance" )._renderItem = function( ul, item ) {
          return $( "<li>" )
            .append( "<div style='border: 1px solid;'>"
                            +  "<b>Base Data:</b> " + item.full_name + " - " + item.mother_fullname + " - " + item.id_number
                            + "<br/> <b>Gender - Birthday:</b> " + item.sex + " - " + item.birthday
                            + "<br/> <b>Last education year:</b> " + item.enrollment.education_year_name
                            + "<br/> <b>Last education school:</b> " + item.enrollment.school_name + " - " + item.enrollment.school_number
                            + "<br/> <b>Class / Section:</b> " + item.enrollment.classroom_name + " / " + item.enrollment.section_name
                            + "</div>" )
            .appendTo( ul );
    };



    $("#id_search_barcode").autocomplete({
      source: function( request, response ) {
        $.ajax( {
          url: '/api/students/',
          dataType: "json",
          data: {
            term: request.term
          },
          success: function( data ) {
            response( data);
          }
        } );
      },
      minLength: 3,
      select: function( event, ui ) {
          $("#id_search_barcode").val('');
          // get_registration(ui.item);
          return false;
      }
    }).autocomplete( "instance" )._renderMenu = function( ul, items ) {
         var that = this;
         $.each( items, function( index, item ) {
             that._renderItemData( ul, item );
        });
        $( ul ).find( "li:odd" ).addClass( "odd" );
    };

    $("#id_search_barcode").autocomplete( "instance" )._renderItem = function( ul, item ) {
          return $( "<li>" )
            .append( "<div style='border: 1px solid;'>" + item.student_full_name + " - " + item.student_mother_fullname + " (" + item.student_sex + " - " + item.student_age + ") "
                           + "<br>" + '{% trans "Current situation" %}: '+ item.school_name + " - " + item.school_number + " / " + item.classroom_name + " / " + item.section_name
                           + "</div>" )
            .appendTo( ul );
    };
});
