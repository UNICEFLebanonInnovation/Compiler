var slyInitialised = false;
var onePerFrameSly;

function CheckInitialiseSly()
{
   if(!slyInitialised)
   {
      slyInitialised= true;

      onePerFrameSly = initializeSly($('#oneperframe'));

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
              if (visit_status=='completed')
              {

                 $("#hhSaveButton").hide();
              }
              else
              {
                 $("#hhSaveButton").show();
              }
         }
         else
         {
            onePerFrameSly.next();
         }
      });

   }

   onePerFrameSly.toStart(true);

}
