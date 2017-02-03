

        function AddChildRow(entry)
        {
           var childIDCell = "<td style = \"display:none\">"+(entry.id)+"</td>";

           var childNameCell = "<td>"+(entry.first_name +' '+entry.father_name+' '+entry.last_name)+"</td>";

           var schoolCell = "<td>"+(entry.child_school)+"</td>";

           var gradeCell = "<td>"+(entry.child_grade)+"</td>";

           var ageCell = "<td>"+(entry.calculate_age)+"</td>";

           var mainReasonCell = "<td style = \"display:none;\">"+(entry.main_reason_id!=null?entry.main_reason_id:'')+"</td>";
           var subReasonCell = "<td style = \"display:none;\">"+(entry.specific_reason_id!=null?entry.specific_reason_id:'')+"</td>";

           var isEnrolled = (entry.child_enrolled_in_another_school==null?false:entry.child_enrolled_in_another_school);
           var isEnrolledCell = "<td style = \"display:none;\">"+isEnrolled+"</td>";

           var otherReasonCell = "<td style = \"display:none;\">"+(entry.specific_reason_other_specify!=null?entry.specific_reason_other_specify:'')+"</td>";

           $("#household-visit-child-table tbody").append
           (
              "<tr class = \"child-row-class\" >"+childIDCell+childNameCell+schoolCell+gradeCell+ageCell+mainReasonCell+subReasonCell+isEnrolledCell+otherReasonCell+"</tr>"

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


                          if(ValidateServices(editForm))
                          {
                            var mainReasonID = editForm.find("[name=childMainReason]").val();

                            row.find("td:nth-child(6)").html(mainReasonID!=null?mainReasonID:'');

                            var specificReasonID = editForm.find("[name=childSpecificReason]").val();

                            row.find("td:nth-child(7)").html(specificReasonID!=null?specificReasonID:'');

                            var isEnrolled =
                            GetBooleanSelection
                            (
                               editForm.find('.child_enrolled_in_another_school_block')
                            );

                            row.find("td:nth-child(8)").html(isEnrolled);


                            var specific_reason_other_specify = editForm.find("[name=specific_reason_other_specify]").val();
                            row.find("td:nth-child(9)").html(specific_reason_other_specify!=null?specific_reason_other_specify:'');

                            var childID = row.find("td:first-child").text();
                            var childServiceData = CreateChildServiceData(childID, editForm);

                            UpdateChildVisitServiceData( childID, childServiceData);
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

              updateDropDownValue(editForm.find("[name=childMainReason]"),childRowRecord.main_reason_id );

              FilterSpecificReasons(editForm, childRowRecord.main_reason_id);
              InitialiseReasonDropdowns(editForm);

              updateDropDownValue(editForm.find("[name=childSpecificReason]"),childRowRecord.specific_reason_id );

              UpdateOthersSpecifyVisibility(editForm);

              updateDropDownValue(editForm.find("[name=specific_reason_other_specify]"),childRowRecord.specific_reason_other_specify );

              ChangeBooleanSelection
              (
                 editForm.find('.child_enrolled_in_another_school_block'),
                 childRowRecord.child_enrolled_in_another_school
              );

              childVisit.child_visit_service.forEach
              (
                 function(entry)
                 {
                    AddServiceRow(editForm, entry);
                 }
              );

              InitialiseServiceDeleting(editForm);
           }

           function InitialiseReasonDropdowns(editForm)
           {
              editForm.on
              (
                 'change', '[name=childMainReason]',
                 function()
                 {
                    FilterSpecificReasons(editForm, parseInt($(this).val()));

                    updateDropDownValue(editForm.find("[name=childSpecificReason]"),null );

                    UpdateOthersSpecifyVisibility(editForm);
                 }
              );


              editForm.on
              (
                 'change', '[name=childSpecificReason]',
                 function()
                 {
                    UpdateOthersSpecifyVisibility(editForm);

                    if(!editForm.find("[name='otherReason']").visible())
                    {
                       editForm.find("[name='specific_reason_other_specify']").text("");
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
                   editForm.find("[name='otherReason']").show();
                }
                else
                {
                   editForm.find("[name='otherReason']").hide();
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

        }
