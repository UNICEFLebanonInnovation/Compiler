

function initialise_absence_form()
{
    $(document).ready(
        function(){
            $( "#button-id-exportabsentees" ).click(function() {
                absence_export();
             }
          );
       }
    );
}

function absence_export() {
    var number_of_absences = $('#id_absence_days').val();
    if (number_of_absences !='' ) {

       url = '/attendances/absence-export/'+number_of_absences;
       download(url);

    }
    else
    {
        alert ('Number Of Absences is mandatory')
    }

}

function download(link) {
  var element = document.createElement('a');
  element.setAttribute('href', link);

  element.style.display = 'none';
  document.body.appendChild(element);

  element.click();

  document.body.removeChild(element);
}
