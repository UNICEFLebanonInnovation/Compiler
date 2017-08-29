/**
 * Created by ali on 7/22/17.
 */

var arabic_fields = "#id_student_first_name, #id_student_father_name, #id_student_last_name, #id_student_mother_fullname";
var protocol = window.location.protocol;
var host = protocol+window.location.host;
var moved_student_path = host+'/api/logging-student-move/';

$(document).ready(function(){

    // $('#id_registration_date').datepicker({dateFormat: "yy-mm-dd"});

    reorganizeForm();

    $(document).on('click', 'input[name=new_registry], input[name=student_outreached], input[name=have_barcode]', function(){
        reorganizeForm();
    });

    $(document).on('blur', arabic_fields, function(){
        checkArabicOnly($(this));
    });

    $(document).on('click', '.moved-registration-row', function(){
        var item = $(this);
        console.log('ok');
        bootbox.confirm(
            "Are you sure you want to tag this student as moved?", function(result) {
            if(result == true){
                moved_student(item.attr('itemscope'));
                item.parents('tr').remove();
            }
        });
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
    var outreached = $('input[name=student_outreached]:checked').val();
    var have_barcode = $('input[name=have_barcode]:checked').val();

    console.log(new_registry);
    console.log(outreached);

    if(new_registry == '1' && outreached == '1' && (have_barcode == '1' || have_barcode == '0')){
        $('#register_by_barcode').removeClass('d-none');
        $('#search_options').addClass('d-none');
        $('.child_data').addClass('d-none');
        return true;
    }

    if(new_registry == '1' && outreached == '0'){
        $('#register_by_barcode').addClass('d-none');
        $('#search_options').addClass('d-none');
        $('.child_data').removeClass('d-none');
        return true;
    }

    if(new_registry == '0' && outreached == '0'){
        $('#register_by_barcode').addClass('d-none');
        $('#search_options').removeClass('d-none');
        $('.child_data').addClass('d-none');
        return true;
    }

    if(new_registry == '0' && outreached == '1' && have_barcode == '1'){
        $('#register_by_barcode').addClass('d-none');
        $('#search_options').removeClass('d-none');
        $('.child_data').addClass('d-none');
        return true;
    }
}


function moved_student(item)
{
    data = {moved: item};

    $.ajax({
        type: "POST",
        url: moved_student_path,
        data: data,
        cache: false,
        async: false,
        headers: getHeader(),
        dataType: 'json',
        success: function (response) {
            console.log(response);
        },
        error: function(response) {
            console.log(response);
        }
    });
}
