

        function AddChildRow(entry)
        {
           var childIDCell = "<td style = \"display:none\">"+(entry.id)+"</td>";

           var childNameCell = "<td>"+(entry.first_name +' '+entry.father_name+' '+entry.last_name)+"</td>";

           var schoolCell = "<td>"+(entry.child_school)+"</td>";

           var gradeCell = "<td>"+(entry.child_classroom)+"</td>";

           var ageCell = "<td>"+(entry.calculate_age)+"</td>";


           var isEnrolled = (entry.child_enrolled_in_another_school==null?false:entry.child_enrolled_in_another_school);
           var isEnrolledCell = "<td style = \"display:none;\">"+isEnrolled+"</td>";

           var ispilot = (entry.child_no_longer_living_in_the_pilot_area==null?false:entry.child_no_longer_living_in_the_pilot_area);
           var ispilotCell = "<td style = \"display:none;\">"+ispilot+"</td>";



           $("#household-visit-child-table tbody").append
           (
              "<tr class = \"child-row-class\" >"+childIDCell+childNameCell+schoolCell+gradeCell+ageCell+isEnrolledCell+ispilotCell+"</tr>"

           );
        }

        function ShowChildForm(row)
        {
           bootbox.dialog
           (
              {
                 title: "Child",
                 message: $('[name=childFormParent]').html(),
                 buttons:
                 {
                    success:
                    {
                       label: saveText,
                       className: "btn-success",
                       callback: function ()
                       {
                          var editForm = $('.bootbox-body').find('[name=childForm]');


                          if
                          (
                              ValidateServices(editForm) &&
                              ValidateReasons(editForm)
                          )
                          {

                            var isEnrolled =
                            GetBooleanSelection
                            (
                               editForm.find('.child_enrolled_in_another_school_block')
                            );
                            var isPilot =
                            GetBooleanSelection
                            (
                               editForm.find('.child_no_longer_living_in_the_pilot_area_block')
                            );

                            row.find("td:nth-child(6)").html(isEnrolled);
                             row.find("td:nth-child(7)").html(isPilot);
                            var childID = row.find("td:first-child").text();
                            var childServiceData = CreateChildServiceData(childID, editForm);
                            var childReasonData = CreateChildReasonData(childID, editForm);

                            UpdateChildVisitServiceData( childID, childServiceData);
                            UpdateChildVisitReasonData( childID, childReasonData);
                          }
                          else
                          {
                             return false;
                          }

                       },
                       cancel:
                       {
                          label: cancelText,
                          className: "btn-default",
                          callback: function ()
                          {
                             bootbox.hideAll();
                          }
                       }
                    }
                 }
              }
           );

           var editForm = $('.bootbox-body').find('[name=childForm]');

           var childID = row.find("td:first-child").text();

           var childVisits = visitDataRecord.children_visits.filter
           (
              function(childVisit)
              {
                 return childVisit.id == childID;
              }
           );

           if(childVisits.length > 0)
           {
              var childVisit = childVisits[0];

              var childRowRecord = CreateChildDataRecord(row);

              editForm.find("[name=childName]").html( childVisit.first_name +' '+childVisit.father_name+' '+childVisit.last_name );
              editForm.find("[name=child_absence_period]").html( childVisit.child_absence_period );

              // updateDropDownValue(editForm.find("[name=childMainReason]"),childRowRecord.main_reason_id );
              //
              // FilterSpecificReasons(editForm, childRowRecord.main_reason_id);
              // InitialiseReasonDropdowns(editForm);
              //
              // updateDropDownValue(editForm.find("[name=childSpecificReason]"),childRowRecord.specific_reason_id );
              //
              // UpdateOthersSpecifyVisibility(editForm);
              //
              // updateDropDownValue(editForm.find("[name=specific_reason_other_specify]"),childRowRecord.specific_reason_other_specify );

              ChangeBooleanSelection
              (
                 editForm.find('.child_enrolled_in_another_school_block'),
                 childRowRecord.child_enrolled_in_another_school
              );

              ChangeBooleanSelection
              (
                 editForm.find('.child_no_longer_living_in_the_pilot_area_block'),
                 childRowRecord.child_no_longer_living_in_the_pilot_area
              );

              childVisit.child_visit_service.forEach
              (
                 function(entry)
                 {
                    AddReadonlyServiceRow(editForm, entry);
                 }
              );

              InitialiseServiceDeleting(editForm);

              childVisit.child_visit_reason.forEach
              (
                 function(entry)
                 {
                    AddReadonlyReasonRow(editForm, entry);
                 }
              );

              InitialiseReasonDeleting(editForm);

              InitialiseReasonDropdowns(editForm);

           }

           function InitialiseReasonDropdowns(editForm)
           {
              editForm.on
              (
                 'change', '[name=childMainReason]',
                 function()
                 {
                    var parentRow = $(this).parent().parent();

                    FilterSpecificReasons(parentRow, parseInt($(this).val()));

                    updateDropDownValue(parentRow.find("[name=childSpecificReason]"),null );

                    UpdateOthersSpecifyVisibility(parentRow);
                 }
              );


              editForm.on
              (
                 'change', '[name=childSpecificReason]',
                 function()
                 {
                    var parentRow = $(this).parent().parent();

                    UpdateOthersSpecifyVisibility(parentRow);

                    if(!parentRow.find("[name='otherReason']").is(":disabled") )
                    {
                       parentRow.find("[name='otherReason']").text("");
                    }
                 }
              );
           }

           function UpdateOthersSpecifyVisibility(editForm)
           {
                var specificReasonDropdown = editForm.find("[name=childSpecificReason]");

                var specificReasonText = getDropDownValueText(specificReasonDropdown, specificReasonDropdown.val()).trim();

                if(specificReasonText == "Other (specify)")
                {
                   editForm.find("[name='otherReason']").prop( "disabled", false );;
                }
                else
                {
                   editForm.find("[name='otherReason']").prop( "disabled", true );;
                }
           }

           function getDropDownValueText(dropDownElement, value)
           {
              return dropDownElement.find('option[value="'+value+'"]').text();
           }

           function FilterSpecificReasons(editForm, mainReasonID)
           {
              editForm.find("[name=childSpecificReason] option[main-reason-id!="+mainReasonID+"]").hide();
              editForm.find("[name=childSpecificReason] option[main-reason-id="+mainReasonID+"],[value='']").show();
           }

           function UpdateChildVisitData(row)
           {
              var childID = row.find("td:first-child").text();

              var childVisits = visitDataRecord.children_visits.filter
              (
                 function(childVisit)
                 {
                    return childVisit.id == childID;
                 }
              );

              childRecord = CreateChildDataRecord(row);

              if(childVisits.length > 0)
              {
                 var childVisit = childVisits[0];

                 console.log(JSON.stringify(visitDataRecord.children_visits));

                 RemoveArrayElement(visitDataRecord.children_visits,childVisit);
                 visitDataRecord.children_visits.push(childRecord);

                 console.log(JSON.stringify(visitDataRecord.children_visits));
              }
           }

           function RemoveArrayElement(a,e)
           {
              var index = a.indexOf(e);

              if (index > -1)
              {
                 a.splice(index, 1);
              }
           }

           function GetBooleanSelection(element)
           {
              return element.find('a.active').attr('data-title')==1 ? "true":"false";
           }

           function ChangeBooleanSelection(element, isSelected)
           {
              ChangeBooleanSelectionOption(element.find('a[data-title=1]'),isSelected);
              ChangeBooleanSelectionOption(element.find('a[data-title=0]'),!isSelected);
           }

           function ChangeBooleanSelectionOption(element, isSelected)
           {
              if(isSelected)
              {
                 element.addClass("active");
                 element.removeClass("notActive");
              }
              else
              {
                 element.removeClass("active");
                 element.addClass("notActive");
              }
           }


            editForm.on
            (
               'click',
               '[name=addServiceButton]',
               function()
               {
                  AddServiceEmptyRow(editForm);
               }
             );

           editForm.on
            (
               'click',
               '[name=addReasonButton]',
               function()
               {
                  AddReasonEmptyRow(editForm);
               }
             );

        }
