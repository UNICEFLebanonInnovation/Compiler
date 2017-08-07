/**
 * Created by ali on 7/22/17.
 */

var arabic_fields = "#id_student_first_name, #id_student_father_name, #id_student_last_name, #id_student_mother_fullname";

$(document).ready(function(){

    $(document).on('click', 'input[name=new_registry], input[name=outreached], input[name=have_barcode]', function(){
        reorganizeForm();
    });

    $(document).on('blur', arabic_fields, function(){
        checkArabicOnly($(this));
    });

    $("#id_search_student").autocomplete({
      source: function( request, response ) {
          var school = $('#id_search_school').val();
          if(school == ''){
              school = 0;
          }
        $.ajax( {
          url: '/api/students/?school='+school+'&school_type='+$('#id_school_type').val(),
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
          window.location = '/enrollments/add/?enrollment_id='+ui.item.enrollment.id;
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
          url: '/api/child/',
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
          window.location = '/enrollments/add/?child_id='+ui.item.child_id;
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
            .append( "<div style='border: 1px solid;'>"
                            +  "<b>Base Data:</b> " + item.student_full_name + " - " + item.stduent_mother_fullname + " - " + item.student_id_number
                            + "<br/> <b>Gender - Birthday:</b> " + item.student_sex + " - " + item.student_birthday
                            + "</div>" )
            .appendTo( ul );
    };

    $("#id_outreach_barcode").autocomplete({
      source: function( request, response ) {
        $.ajax( {
          url: '/api/child/',
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
          $('#id_outreach_barcode').val(ui.item.barcode_subset);
          return false;
      }
    }).autocomplete( "instance" )._renderMenu = function( ul, items ) {
         var that = this;
         $.each( items, function( index, item ) {
             that._renderItemData( ul, item );
        });
        $( ul ).find( "li:odd" ).addClass( "odd" );
    };

    $("#id_outreach_barcode").autocomplete( "instance" )._renderItem = function( ul, item ) {
          return $( "<li>" )
            .append( "<div style='border: 1px solid;'>"
                            +  "<b>Base Data:</b> " + item.student_full_name + " - " + item.stduent_mother_fullname + " - " + item.student_id_number
                            + "<br/> <b>Gender - Birthday:</b> " + item.student_sex + " - " + item.student_birthday
                            + "</div>" )
            .appendTo( ul );
    };
});


function reorganizeForm()
{
    var new_registry = $('input[name=new_registry]:checked').val();
    var outreached = $('input[name=outreached]:checked').val();
    var have_barcode = $('input[name=have_barcode]:checked').val();

    if(new_registry == '1'){
        $('.child_data').removeClass('invisible');
    }else{
        $('.child_data').removeClass('invisible');
        $('#search_options').removeClass('invisible');

        if(have_barcode == '1') {
            $('#register_by_barcode').removeClass('invisible');
        }
    }

    if(outreached == '1') {
        $('#have_barcode_option').removeClass('invisible');
    }

    if(have_barcode == '1') {
        $('#register_by_barcode').removeClass('invisible');
    }
}
