$(document).ready(function() {


     var emailDateJobDetails;
         var emailCronJobDetails;
         var emailIntervalJobDetails;

         var smsDateJobDetails;
         var smsCronJobDetails;
         var smsIntervalJobDetails;

         var emailRecipientCounter = 0;
          var smsRecipientCounter = 0;

         const recipients = JSON.parse($("#recipients").attr("data-recipients"));
        const fuse = new Fuse(recipients, {keys: ['recipient_last_name','recipient_first_name', 'recipient_tags']});

         //change paste keyup
            $('#emailSearchInput').on('input', function(event) {
                let emailSearchValue = event.target.value;
                console.log(emailSearchValue);
                let emailSearchResults = fuse.search(emailSearchValue);
                $('#emailSearchResults').empty();

                var email_recipients_options = "";

                for(var key in emailSearchResults) {
                    result = emailSearchResults[key];

                    email_recipient_option_value = result.item['recipient_first_name']+" "+result.item['recipient_last_name']+" - "+result.item['recipient_email'];
                    email_recipient_option_visible_content = result.item['recipient_first_name']+" "+result.item['recipient_last_name']+" (email: "+result.item['recipient_email']+")"+" (type: "+result.item['recipient_type']+")"+" (tags: "+result.item['recipient_tags']+")";
                     email_recipients_options += '<option value="'+email_recipient_option_value+'">'+email_recipient_option_visible_content+'</option>';
                }
                 $('#emailSearchResults').append(email_recipients_options);

            });


     $('#addAsIndividualEmailRecipients').on('click', function(event) {

                var selectedRecipients = $('#emailSearchResults').val();

                for(var key in selectedRecipients) {
                    recipient = selectedRecipients[key];

                    emailRecipientCounter = Number(emailRecipientCounter) + 1;

                    emailRecipientsTable.row.add( ['<span name="recipient">'+recipient+'</span>','<div class="d-flex btn-group justify-content-center"><button type="button"  name="removeEmailRecipient" id="removeEmailRecipient_'+emailRecipientCounter+'" class="btn btn-outline-info btn-sm"><i class="fa-solid fa-stop"></i></button></div>'] ).draw( false );
                     $('#removeEmailRecipient_'+emailRecipientCounter).on('click', function() {
                         emailRecipientsTable.row( $(this).parents('tr')).remove().draw();
                     });
                }

            });

    $('#addAsGroupToEmailRecipients').on('click', function(event) {
                var selectedRecipients = $('#emailSearchResults').val();
                var groupToAddToEmailRecipientsTable = '';
                for(var key in selectedRecipients) {
                    recipient = selectedRecipients[key];
                    groupToAddToEmailRecipientsTable += recipient+',';
                }

                emailRecipientCounter = Number(emailRecipientCounter) + 1;
                emailRecipientsTable.row.add( ['<span name="recipient">'+groupToAddToEmailRecipientsTable+'</span>','<div class="d-flex btn-group justify-content-center"><button type="button"  name="removeEmailRecipient" id="removeEmailRecipient_'+emailRecipientCounter+'" class="btn btn-outline-info btn-sm"><i class="fa-solid fa-stop"></i></button></div>'] ).draw( false );
                     $('#removeEmailRecipient_'+emailRecipientCounter).on('click', function() {
                         emailRecipientsTable.row( $(this).parents('tr')).remove().draw();
                     });


            });

     $('input[name="emailJobType"]').change(function() {

         //alert("there is a change");

         var jobDetailsHTML = $("#emailJobDetails");
         if ($(this).val() == 'emailDateJob')
         {
             if ($('#emailIntervalJobDetails').is("html *")) {
                  emailIntervalJobDetails =  $("#emailIntervalJobDetails").detach();
             }

             if ($('#emailCronJobDetails').is("html *")) {
                   emailCronJobDetails =  $("#emailCronJobDetails").detach();
             }

        emailDateJobDetails.appendTo("#emailJobDetails");

         }
         else if ($(this).val() == 'emailIntervalJob')
         {

                  if ($('#emailDateJobDetails').is("html *")) {
                  emailDateJobDetails =  $("#emailDateJobDetails").detach();
             }

             if ($('#emailCronJobDetails').is("html *")) {
                   emailCronJobDetails =  $("#emailCronJobDetails").detach();
             }
        emailIntervalJobDetails.appendTo("#emailJobDetails");

         }

         else if ($(this).val() == 'emailCronJob')
         {
                 if ($('#emailIntervalJobDetails').is("html *")) {
                  emailIntervalJobDetails =  $("#emailIntervalJobDetails").detach();
             }

             if ($('#emailDateJobDetails').is("html *")) {
                   emailDateJobDetails =  $("#emailDateJobDetails").detach();
             }
        emailCronJobDetails.appendTo("#emailJobDetails");

         }

     });

     $('#emailResetButton').on('click', function(event) {
         // $("#allEmailInformation:input, #allEmailInformation select")

                $(':input','#allEmailInformation')
  .not(':button, :submit, :reset, :hidden, :radio')
  .val('')
  .prop('checked', false)
  .prop('selected', false);

               $('#emailSearchResults').empty()

              emailRecipientsTable.clear().destroy();
emailRecipientsTable = $('#emailRecipientsTable').DataTable({
           bAutoWidth: false, aoColumns : [{ sWidth: '75%' }, { sWidth: '25%' }],
           columnDefs: [ {targets: [1], orderable: false}],
       });

$( "#emailRecipientsTable_filter" ).addClass( "my-5 px-3" );
$( "#emailRecipientsTable_paginate" ).addClass( "my-5 px-3" );
$( "#emailRecipientsTable_length" ).addClass( "my-5 px-3" );


            });


      $('#disableEmailMessage').on('click', function(event) {

          if($("#disableEmailMessage").is(':checked'))
          {
           $(':input','#allEmailInformation')
  .not('#disableEmailMessage')
.prop('disabled', true);


var emailRecipientsTableData  =emailRecipientsTable.rows().data();
              emailRecipientsTable.clear().destroy();

emailRecipientsTable = $('#emailRecipientsTable').DataTable({
           bAutoWidth: false, aoColumns : [{ sWidth: '75%' }, { sWidth: '25%' }],
           columnDefs: [ {targets: [0,1], orderable: false}],
            data: emailRecipientsTableData
       });

$( "#emailRecipientsTable_filter" ).addClass( "my-5 px-3" );
$( "#emailRecipientsTable_paginate" ).addClass( "my-5 px-3" );
$( "#emailRecipientsTable_length" ).addClass( "my-5 px-3" );

           $("#emailRecipientsTable").find("*").attr("disabled", "disabled");
            $("#emailRecipientsTable").find("*").css("background-color", "grey");
             $("#emailRecipientsTable > thead > tr > th").removeClass( "sorting sorting_desc sorting_asc" ).addClass( "sorting_disabled" );

           $(this).val('yes');
          }
          else
          {
             $(':input','#allEmailInformation')
  .not('#disableEmailMessage')
  .prop('disabled', false);

             var emailRecipientsTableData  =emailRecipientsTable.rows().data();
              emailRecipientsTable.clear().destroy();

emailRecipientsTable = $('#emailRecipientsTable').DataTable({
           bAutoWidth: false, aoColumns : [{ sWidth: '75%' }, { sWidth: '25%' }],
           columnDefs: [ {targets: [1], orderable: false}],
            data: emailRecipientsTableData
       });

$( "#emailRecipientsTable_filter" ).addClass( "my-5 px-3" );
$( "#emailRecipientsTable_paginate" ).addClass( "my-5 px-3" );
$( "#emailRecipientsTable_length" ).addClass( "my-5 px-3" );

              $(this).val('no');
          }
            });


                  $('#smsSearchInput').on('input', function(event) {
                let smsSearchValue = event.target.value;
                console.log(smsSearchValue);
                let smsSearchResults = fuse.search(smsSearchValue);
                $('#smsSearchResults').empty();

                var select_options = "";

                for(var key in smsSearchResults) {
                    result = smsSearchResults[key];
                    option_value = result.item['recipient_first_name']+" "+result.item['recipient_last_name']+" - "+result.item['recipient_phone_number'];
                    option_visible_content = result.item['recipient_first_name']+" "+result.item['recipient_last_name']+" (phone_number: "+result.item['recipient_phone_number']+")"+" (type: "+result.item['recipient_type']+")"+" (tags: "+result.item['recipient_tags']+")";
                     select_options += '<option value="'+option_value+'">'+option_visible_content+'</option>';
                }
                 $('#smsSearchResults').append(select_options);

            });


     $('#addAsIndividualSMSRecipients').on('click', function(event) {
                var selectedRecipients = $('#smsSearchResults').val();
                for(var key in selectedRecipients) {
                    recipient = selectedRecipients[key];

                    smsRecipientCounter = Number(smsRecipientCounter) + 1;

                    smsRecipientsTable.row.add( ['<span name="recipient">'+recipient+'</span>','<div class="d-flex btn-group justify-content-center"><button type="button"  name="removeSMSRecipient" id="removeSMSRecipient_'+smsRecipientCounter+'" class="btn btn-outline-info btn-sm"><i class="fa-solid fa-stop"></i></button></div>'] ).draw( false );
                     $('#removeSMSRecipient_'+smsRecipientCounter).on('click', function() {
                         smsRecipientsTable.row( $(this).parents('tr')).remove().draw();
                     });
                }
            });

     $('#addAsGroupToSMSRecipients').on('click', function(event) {
                var selectedRecipients = $('#smsSearchResults').val();
                var groupToAddToSMSRecipientsTable = '';
                for(var key in selectedRecipients) {
                    recipient = selectedRecipients[key];
                    groupToAddToSMSRecipientsTable += recipient+',';
                }

                smsRecipientCounter = Number(smsRecipientCounter) + 1;
                smsRecipientsTable.row.add( ['<span name="recipient">'+groupToAddToSMSRecipientsTable+'</span>','<div class="d-flex btn-group justify-content-center"><button type="button"  name="removeSMSRecipient" id="removeSMSRecipient_'+smsRecipientCounter+'" class="btn btn-outline-info btn-sm"><i class="fa-solid fa-stop"></i></button></div>'] ).draw( false );
                     $('#removeSMSRecipient_'+smsRecipientCounter).on('click', function() {
                         smsRecipientsTable.row( $(this).parents('tr')).remove().draw();
                     });
            });


     $('input[name="smsJobType"]').change(function() {

          //alert("there is a change2");

         var jobDetailsHTML = $("#smsJobDetails");
         if ($(this).val() == 'smsDateJob')
         {
             if ($('#smsIntervalJobDetails').is("html *")) {
                  smsIntervalJobDetails =  $("#smsIntervalJobDetails").detach();
             }

             if ($('#smsCronJobDetails').is("html *")) {
                   smsCronJobDetails =  $("#smsCronJobDetails").detach();
             }

        smsDateJobDetails.appendTo("#smsJobDetails");

         }
         else if ($(this).val() == 'smsIntervalJob')
         {

                  if ($('#smsDateJobDetails').is("html *")) {
                  smsDateJobDetails =  $("#smsDateJobDetails").detach();
             }

             if ($('#smsCronJobDetails').is("html *")) {
                   smsCronJobDetails =  $("#smsCronJobDetails").detach();
             }
        smsIntervalJobDetails.appendTo("#smsJobDetails");

         }

         else if ($(this).val() == 'smsCronJob')
         {
                 if ($('#smsIntervalJobDetails').is("html *")) {
                  smsIntervalJobDetails =  $("#smsIntervalJobDetails").detach();
             }

             if ($('#smsDateJobDetails').is("html *")) {
                   smsDateJobDetails =  $("#smsDateJobDetails").detach();
             }
        smsCronJobDetails.appendTo("#smsJobDetails");

         }

     });

     $('#smsResetButton').on('click', function(event) {
         // $("#allSMSInformation:input, #allSMSInformation select")

                $(':input','#allSMSInformation')
  .not(':button, :submit, :reset, :hidden, :radio')
  .val('')
  .prop('checked', false)
  .prop('selected', false);

               $('#smsSearchResults').empty();


                             smsRecipientsTable.clear().destroy();
smsRecipientsTable = $('#smsRecipientsTable').DataTable({
           bAutoWidth: false, aoColumns : [{ sWidth: '75%' }, { sWidth: '25%' }],
           columnDefs: [ {targets: [1], orderable: false}],
       });

$( "#smsRecipientsTable_filter" ).addClass( "my-5 px-3" );
$( "#smsRecipientsTable_paginate" ).addClass( "my-5 px-3" );
$( "#smsRecipientsTable_length" ).addClass( "my-5 px-3" );


            });


      $('#disableSMSMessage').on('click', function(event) {

          if($("#disableSMSMessage").is(':checked'))
          {
           $(':input','#allSMSInformation')
  .not('#disableSMSMessage')
.prop('disabled', true);

           var smsRecipientsTableData  =smsRecipientsTable.rows().data();
              smsRecipientsTable.clear().destroy();

smsRecipientsTable = $('#smsRecipientsTable').DataTable({
           bAutoWidth: false, aoColumns : [{ sWidth: '75%' }, { sWidth: '25%' }],
           columnDefs: [ {targets: [0,1], orderable: false}],
            data: smsRecipientsTableData
       });

$( "#smsRecipientsTable_filter" ).addClass( "my-5 px-3" );
$( "#smsRecipientsTable_paginate" ).addClass( "my-5 px-3" );
$( "#smsRecipientsTable_length" ).addClass( "my-5 px-3" );

           $("#smsRecipientsTable").find("*").attr("disabled", "disabled");
            $("#smsRecipientsTable").find("*").css("background-color", "grey");
             $("#smsRecipientsTable > thead > tr > th").removeClass( "sorting sorting_desc sorting_asc" ).addClass( "sorting_disabled" );

           $(this).val('yes');
          }
          else
          {
             $(':input','#allSMSInformation')
  .not('#disableSMSMessage')
  .prop('disabled', false);

              var smsRecipientsTableData  =smsRecipientsTable.rows().data();
              smsRecipientsTable.clear().destroy();

smsRecipientsTable = $('#smsRecipientsTable').DataTable({
           bAutoWidth: false, aoColumns : [{ sWidth: '75%' }, { sWidth: '25%' }],
           columnDefs: [ {targets: [1], orderable: false}],
            data: smsRecipientsTableData
       });

$( "#smsRecipientsTable_filter" ).addClass( "my-5 px-3" );
$( "#smsRecipientsTable_paginate" ).addClass( "my-5 px-3" );
$( "#smsRecipientsTable_length" ).addClass( "my-5 px-3" );

              $(this).val('no');
          }
            });


       $('#emailCopyOverButton').on('click', function(event) {

           if ($("#disableSMSMessage").is(':checked'))
           {
               alert("Can't copy over as sms fields are disabled.");
           }
           else
           {
                $('#smsFileUploadInput').remove();
                var emailFileUploadInput = $('#emailFileUploadInput').clone(true).attr("id","smsFileUploadInput").attr("name","smsFileUploadInput");
                $(emailFileUploadInput).insertAfter($('#smsFileUploadInputLabel'));


                $('#smsDescription').val($('#emailDescription').val());
                $('#smsSubject').val($('#emailSubject').val());
                $('#smsContent').val($('#emailContent').val());
                $('#smsSearchInput').val($('#emailSearchInput').val());


                let emailSearchValue = $('#emailSearchInput').val();
                let emailSearchResults = fuse.search(emailSearchValue);
                $('#smsSearchResults').empty();
                var select_options = "";
                for(var key in emailSearchResults) {
                    result = emailSearchResults[key];
                    option_value = result.item['recipient_first_name']+" "+result.item['recipient_last_name']+" - "+result.item['recipient_phone_number'];
                    option_visible_content = result.item['recipient_first_name']+" "+result.item['recipient_last_name']+" (phone_number: "+result.item['recipient_phone_number']+")"+" (type: "+result.item['recipient_type']+")"+" (tags: "+result.item['recipient_tags']+")";
                     select_options += '<option value="'+option_value+'">'+option_visible_content+'</option>';
                }
                 $('#smsSearchResults').append(select_options);


                const email_to_phone_number_dict = JSON.parse($("#email_to_phone_number_dict").attr("data-email_to_phone_number_dict"));

              smsRecipientsTable.clear().destroy();

smsRecipientsTable = $('#smsRecipientsTable').DataTable({
           bAutoWidth: false, aoColumns : [{ sWidth: '75%' }, { sWidth: '25%' }],
           columnDefs: [ {targets: [1], orderable: false}],
       });

$( "#smsRecipientsTable_filter" ).addClass( "my-5 px-3" );
$( "#smsRecipientsTable_paginate" ).addClass( "my-5 px-3" );
$( "#smsRecipientsTable_length" ).addClass( "my-5 px-3" );



                  $('#emailRecipientsTable').find('span[name="recipient"]').each(function () {

           thisEmailRecipient =  $(this).text();
groupOfEmailRecipientsIfAny = thisEmailRecipient.split(',')
  if(groupOfEmailRecipientsIfAny)
  {
      var new_item_to_copy = '';
      for (var key in groupOfEmailRecipientsIfAny)
      {
          memberOfEmailGroup = groupOfEmailRecipientsIfAny[key];
          if(memberOfEmailGroup != '')
          {
             thisMemberOfEmailGroup = memberOfEmailGroup.substring(memberOfEmailGroup.indexOf("-")+2);
          thisMemberOfSMSGroup = email_to_phone_number_dict[thisMemberOfEmailGroup];
          new_item_to_copy += memberOfEmailGroup.substring(0,memberOfEmailGroup.indexOf("-")+2)+thisMemberOfSMSGroup;
           if(groupOfEmailRecipientsIfAny.length > 1)
                          {
                              new_item_to_copy +=',';
                          }
          }

      }
  }

            smsRecipientCounter = Number(smsRecipientCounter) + 1;

             smsRecipientsTable.row.add( ['<span name="recipient">'+new_item_to_copy+'</span>','<div class="d-flex btn-group justify-content-center"><button type="button"  name="removeSMSRecipient" id="removeSMSRecipient_'+smsRecipientCounter+'" class="btn btn-outline-info btn-sm"><i class="fa-solid fa-stop"></i></button></div>'] ).draw( false );
                     $('#removeSMSRecipient_'+smsRecipientCounter).on('click', function() {
                         smsRecipientsTable.row( $(this).parents('tr')).remove().draw();
                     });

		});


                if($('#emailDateJob').is(':checked'))
                {
                    $('#smsDateJob').click();
                     $('#sms_run_date_and_time').val($('#email_run_date_and_time').val());
                }

                if($('#emailCronJob').is(':checked'))
                {
                    $('#smsCronJob').prop('checked', true).trigger('change');
                      $('#sms_cron_year').val($('#email_cron_year').val());
                $('#sms_cron_month').val($('#email_cron_month').val());
                $('#sms_cron_week').val($('#email_cron_week').val());
                 $('#sms_cron_day').val($('#email_cron_day').val());
                  $('#sms_cron_day_of_week').val($('#email_cron_day_of_week').val());
                  $('#sms_cron_hour').val($('#email_cron_hour').val());
                $('#sms_cron_minute').val($('#email_cron_minute').val());
                 $('#sms_cron_second').val($('#email_cron_second').val());
                  $('#sms_cron_end_date_and_time').val($('#email_cron_end_date_and_time').val());
                   $('#sms_cron_start_date_and_time').val($('#email_cron_start_date_and_time').val());
                }

                if($('#emailIntervalJob').is(':checked'))
                {
                    $('#smsIntervalJob').prop('checked', true).trigger('change');

                $('#sms_interval_weeks').val($('#email_interval_weeks').val());
                 $('#sms_interval_days').val($('#email_interval_days').val());
                  $('#sms_interval_hours').val($('#email_interval_hours').val());
                $('#sms_interval_minutes').val($('#email_interval_minutes').val());
                 $('#sms_interval_seconds').val($('#email_interval_seconds').val());
                  $('#sms_interval_end_date_and_time').val($('#email_interval_end_date_and_time').val());
                   $('#sms_interval_start_date_and_time').val($('#email_interval_start_date_and_time').val());


                }



           }
            });



        $('#smsCopyOverButton').on('click', function(event) {

           if ($("#disableEmailMessage").is(':checked'))
           {
               alert("Can't copy over as email fields are disabled.");
           }
           else
           {
               //TODO copy over of files breaks when more than one file is being copied
               $('#emailFileUploadInput').remove();
                var smsFileUploadInput = $('#smsFileUploadInput').clone(true).attr("id","emailFileUploadInput").attr("name","emailFileUploadInput");
                $(smsFileUploadInput).insertAfter($('#emailFileUploadInputLabel'));

                $('#emailDescription').val($('#smsDescription').val());
                $('#emailSubject').val($('#smsSubject').val());
                $('#emailContent').val($('#smsContent').val());
                $('#emailSearchInput').val($('#smsSearchInput').val());


                let smsSearchValue = $('#smsSearchInput').val();
                let smsSearchResults = fuse.search(smsSearchValue);
                $('#emailSearchResults').empty();
                var select_options = "";
                for(var key in smsSearchResults) {
                    result = smsSearchResults[key];
                    option_value = result.item['recipient_first_name']+" "+result.item['recipient_last_name']+" - "+result.item['recipient_phone_number'];
                    option_visible_content = result.item['recipient_first_name']+" "+result.item['recipient_last_name']+" (phone_number: "+result.item['recipient_phone_number']+")"+" (type: "+result.item['recipient_type']+")"+" (tags: "+result.item['recipient_tags']+")";
                     select_options += '<option value="'+option_value+'">'+option_visible_content+'</option>';
                }
                 $('#emailSearchResults').append(select_options);


                const phone_number_to_email_dict = JSON.parse($("#phone_number_to_email_dict").attr("data-phone_number_to_email_dict"));

                emailRecipientsTable.clear().destroy();

emailRecipientsTable = $('#emailRecipientsTable').DataTable({
           bAutoWidth: false, aoColumns : [{ sWidth: '75%' }, { sWidth: '25%' }],
           columnDefs: [ {targets: [1], orderable: false}],
       });

$( "#emailRecipientsTable_filter" ).addClass( "my-5 px-3" );
$( "#emailRecipientsTable_paginate" ).addClass( "my-5 px-3" );
$( "#emailRecipientsTable_length" ).addClass( "my-5 px-3" );



                 $('#smsRecipientsTable').find('span[name="recipient"]').each(function () {

thisSMSRecipient =  $(this).text();
groupOfSMSRecipientsIfAny = thisSMSRecipient.split(',')
  if(groupOfSMSRecipientsIfAny)
  {
      var new_item_to_copy = '';
      for (var key in groupOfSMSRecipientsIfAny)
      {
          memberOfSMSGroup = groupOfSMSRecipientsIfAny[key];
          if(memberOfSMSGroup != '')
          {
             thisMemberOfSMSGroup = memberOfSMSGroup.substring(memberOfSMSGroup.indexOf("-")+2);
          thisMemberOfEmailGroup = phone_number_to_email_dict[thisMemberOfSMSGroup];
          new_item_to_copy += memberOfSMSGroup.substring(0,memberOfSMSGroup.indexOf("-")+2)+thisMemberOfEmailGroup;
           if(groupOfSMSRecipientsIfAny.length > 1)
                          {
                              new_item_to_copy +=',';
                          }
          }

      }
  }


emailRecipientCounter = Number(emailRecipientCounter) + 1;

 emailRecipientsTable.row.add( ['<span name="recipient">'+new_item_to_copy+'</span>','<div class="d-flex btn-group justify-content-center"><button type="button"  name="removeEmailRecipient" id="removeEmailRecipient_'+emailRecipientCounter+'" class="btn btn-outline-info btn-sm"><i class="fa-solid fa-stop"></i></button></div>'] ).draw( false );
         $('#removeEmailRecipient_'+emailRecipientCounter).on('click', function() {
             emailRecipientsTable.row( $(this).parents('tr')).remove().draw();
         });

});


                if($('#smsDateJob').is(':checked'))
                {
                    $('#emailDateJob').click();
                     $('#email_run_date_and_time').val($('#sms_run_date_and_time').val());
                }

                if($('#smsCronJob').is(':checked'))
                {
                    $('#emailCronJob').prop('checked', true).trigger('change');
                      $('#email_cron_year').val($('#sms_cron_year').val());
                $('#email_cron_month').val($('#sms_cron_month').val());
                $('#email_cron_week').val($('#sms_cron_week').val());
                 $('#email_cron_day').val($('#sms_cron_day').val());
                  $('#email_cron_day_of_week').val($('#sms_cron_day_of_week').val());
                  $('#email_cron_hour').val($('#sms_cron_hour').val());
                $('#email_cron_minute').val($('#sms_cron_minute').val());
                 $('#email_cron_second').val($('#sms_cron_second').val());
                  $('#email_cron_end_date_and_time').val($('#sms_cron_end_date_and_time').val());
                   $('#email_cron_start_date_and_time').val($('#sms_cron_start_date_and_time').val());
                }

                if($('#smsIntervalJob').is(':checked'))
                {
                    $('#emailIntervalJob').prop('checked', true).trigger('change');

                $('#email_interval_weeks').val($('#sms_interval_weeks').val());
                 $('#email_interval_days').val($('#sms_interval_days').val());
                  $('#email_interval_hours').val($('#sms_interval_hours').val());
                $('#email_interval_minutes').val($('#sms_interval_minutes').val());
                 $('#email_interval_seconds').val($('#sms_interval_seconds').val());
                  $('#email_interval_end_date_and_time').val($('#sms_interval_end_date_and_time').val());
                   $('#email_interval_start_date_and_time').val($('#sms_interval_start_date_and_time').val());


                }



           }
            });


       $('#sendMessagesButton').on('click', function(event) {

           if ($("#disableSMSMessage").is(':checked') && $("#disableEmailMessage").is(':checked'))
           {
               event.preventDefault();
                event.stopPropagation();
               alert("You must enable an sms or email message!");
           }

            });


       window.onload = function(){

        var offset = -5;
           var todayCST = new Date(new Date().getTime() + offset * 3600 * 1000).toISOString();//.split('T')[0];
            var relevant_part_for_setting_min = todayCST.substring(0, todayCST.lastIndexOf(":"));

        document.getElementById("email_run_date_and_time").setAttribute('min', relevant_part_for_setting_min);
        document.getElementById("sms_run_date_and_time").setAttribute('min', relevant_part_for_setting_min);

        emailIntervalJobDetails =  $("#emailIntervalJobDetails").detach();
        emailCronJobDetails =  $("#emailCronJobDetails").detach();
        emailDateJobDetails =  $("#emailDateJobDetails").detach();

        smsIntervalJobDetails =  $("#smsIntervalJobDetails").detach();
        smsCronJobDetails =  $("#smsCronJobDetails").detach();
        smsDateJobDetails =  $("#smsDateJobDetails").detach();

        setUIStateToModify();

        };


       (function () {
'use strict'
const forms = document.querySelectorAll('.needs-validation')
Array.from(forms)
  .forEach(function (form) {
    form.addEventListener('submit', function (event) {
    if (!form.checkValidity()) {
        event.preventDefault()
        event.stopPropagation()
    }

      form.classList.add('was-validated')
    }, false)
  })
})();


       var emailRecipientsTable =  $('#emailRecipientsTable').DataTable({
           bAutoWidth: false, 
  aoColumns : [
    { sWidth: '75%' },
    { sWidth: '25%' }
  ],
           columnDefs: [ {
    targets: [1],
    orderable: false,

 }]
       });

$( "#emailRecipientsTable_filter" ).addClass( "my-5 px-3" );
$( "#emailRecipientsTable_paginate" ).addClass( "my-5 px-3" );
$( "#emailRecipientsTable_length" ).addClass( "my-5 px-3" );


var smsRecipientsTable =  $('#smsRecipientsTable').DataTable({
           bAutoWidth: false,
  aoColumns : [
    { sWidth: '75%' },
    { sWidth: '25%' }
  ],
           columnDefs: [ {
    targets: [1],
    orderable: false,

 }]
       });

$( "#smsRecipientsTable_filter" ).addClass( "my-5 px-3" );
$( "#smsRecipientsTable_paginate" ).addClass( "my-5 px-3" );
$( "#smsRecipientsTable_length" ).addClass( "my-5 px-3" );



function setUIStateToModify() {

     var job_id = $("#job_id").attr("data-job_id");
    var job_ui_state = JSON.parse( $("#job_ui_state").attr("data-job_ui_state"));


    if (job_id && job_ui_state)
    {

         if(job_ui_state['disableSMSMessage'] == 'yes')
        {
         $('#disableSMSMessage').trigger('click');
        }

        if(job_ui_state['disableEmailMessage'] == 'yes')
        {
         $('#disableEmailMessage').trigger('click');
        }

        if(job_ui_state['emailJobType'] == 'emailDateJob')
        {
         $('#emailDateJob').trigger('click');
        }

        if(job_ui_state['emailJobType'] == 'emailIntervalJob')
        {
         $('#emailIntervalJob').trigger('click');
        }

        if(job_ui_state['emailJobType'] == 'emailCronJob')
        {
         $('#emailCronJob').trigger('click');
        }

         if(job_ui_state['smsJobType'] == 'smsDateJob')
        {
         $('#smsDateJob').trigger('click');
        }

        if(job_ui_state['smsJobType'] == 'smsIntervalJob')
        {
         $('#smsIntervalJob').trigger('click');
        }

        if(job_ui_state['smsJobType'] == 'smsCronJob')
        {
         $('#smsCronJob').trigger('click');
        }

                 emailRecipientsTable.clear().destroy();

emailRecipientsTable = $('#emailRecipientsTable').DataTable({
           bAutoWidth: false, aoColumns : [{ sWidth: '75%' }, { sWidth: '25%' }],
           columnDefs: [ {targets: [1], orderable: false}],
       });

$( "#emailRecipientsTable_filter" ).addClass( "my-5 px-3" );
$( "#emailRecipientsTable_paginate" ).addClass( "my-5 px-3" );
$( "#emailRecipientsTable_length" ).addClass( "my-5 px-3" );

if(typeof job_ui_state['allEmailRecipients'] !== "undefined")
{
      var allEmailRecipients = job_ui_state['allEmailRecipients'].split(']\r\n');

        for (let key in allEmailRecipients)
        {
             thisEmailRecipient = allEmailRecipients[key].substring(1);
             groupOfEmailRecipientsIfAny = thisEmailRecipient.split(',');

                  if(thisEmailRecipient.includes('-'))
            {
                emailRecipientCounter = Number(emailRecipientCounter) + 1;

             emailRecipientsTable.row.add( ['<span name="recipient">'+thisEmailRecipient+'</span>','<div class="d-flex btn-group justify-content-center"><button type="button"  name="removeEmailRecipient" id="removeEmailRecipient_'+emailRecipientCounter+'" class="btn btn-outline-info btn-sm"><i class="fa-solid fa-stop"></i></button></div>'] ).draw( false );
                     $('#removeEmailRecipient_'+emailRecipientCounter).on('click', function() {
                         emailRecipientsTable.row( $(this).parents('tr')).remove().draw();
                     });

            }

        }
}

        smsRecipientsTable.clear().destroy();

smsRecipientsTable = $('#smsRecipientsTable').DataTable({
           bAutoWidth: false, aoColumns : [{ sWidth: '75%' }, { sWidth: '25%' }],
           columnDefs: [ {targets: [1], orderable: false}],
       });

$( "#smsRecipientsTable_filter" ).addClass( "my-5 px-3" );
$( "#smsRecipientsTable_paginate" ).addClass( "my-5 px-3" );
$( "#smsRecipientsTable_length" ).addClass( "my-5 px-3" );

if(typeof job_ui_state['allSMSRecipients'] !== "undefined")
{
    var allSMSRecipients = job_ui_state['allSMSRecipients'].split(']\r\n');

        for (let key in allSMSRecipients)
        {
             thisSMSRecipient = allSMSRecipients[key].substring(1);
             groupOfSMSRecipientsIfAny = thisSMSRecipient.split(',');

                  if(thisSMSRecipient.includes('-'))
            {
                smsRecipientCounter = Number(smsRecipientCounter) + 1;

             smsRecipientsTable.row.add( ['<span name="recipient">'+thisSMSRecipient+'</span>','<div class="d-flex btn-group justify-content-center"><button type="button"  name="removeSMSRecipient" id="removeSMSRecipient_'+smsRecipientCounter+'" class="btn btn-outline-info btn-sm"><i class="fa-solid fa-stop"></i></button></div>'] ).draw( false );
                     $('#removeSMSRecipient_'+smsRecipientCounter).on('click', function() {
                         smsRecipientsTable.row( $(this).parents('tr')).remove().draw();
                     });

            }

        }
}



        for (let key in job_ui_state) {

            if(key != 'emailSearchInput' && key != 'smsSearchInput')
            {
                if ( key == 'ids_of_attached_files_if_any' ){
                    var ids_of_attached_files_if_any = job_ui_state[key];
                    for (var item in ids_of_attached_files_if_any)
                    {
                        window.open('/send_attached_file_to_client/'+ids_of_attached_files_if_any[item], "_blank");
                    }
                    //$('#emailFileUploadInput').val(ids_of_attached_files_if_any)
                }
                else
                {
                    console.log(key, job_ui_state[key]);
                     $('#'+key).val(job_ui_state[key]);
                }
            }
        }

    }

}


});
