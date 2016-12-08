var slyInitialised = false;
var onePerFrameSly;

function CheckInitialiseSly()
{
   if(!slyInitialised)
   {
      slyInitialised= true;

      onePerFrameSly = initializeSly($('#oneperframe'));

      //alert("Sly initialised");
      //alert(JSON.stringify(onePerFrameSly));

      $("#previousButton").click(function()
      {
        onePerFrameSly.prev();
        $("#hhSaveButton").hide();
      });

      $("#nextButton").click(function()
      {
         if(onePerFrameSly.rel.activeItem == 0)
         {
            if(ValidateAttempts())
            {
              onePerFrameSly.next();
            }
         }
         else if(onePerFrameSly.rel.activeItem == 1)
         {
              onePerFrameSly.next();
              $("#hhSaveButton").show();
         }
         else
         {
            onePerFrameSly.next();
         }
      });
   }

   onePerFrameSly.toStart(true);

}
