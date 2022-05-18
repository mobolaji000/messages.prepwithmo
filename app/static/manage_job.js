$(document).ready(function() {

var jobsTable = $('#jobsTable').DataTable({
    "order": [[ 3, "desc" ]],
    'columnDefs': [ {
    'targets': [8], /* table column index */
    'orderable': false, /* here set the true or false */

 }]
});
$( "#jobsTable_filter" ).addClass( "my-5 px-3" );
$( "#jobsTable_paginate" ).addClass( "my-5 px-3" );


    $('button[name="pauseJob"]').on('click', function() {

        var job_id = $(this).attr("data-jobId");
        var pauseButton = $(this);
        var resumeButton = pauseButton.siblings('button[name="resumeJob"]');

                $.ajax({
    url: '/pause_job',
    type: "POST",
    data: {
        job_id: job_id,
    },
    dataType: "json",
    async: false,
    success: function (result) {
    if(result.status == 'success'){

        pauseButton.parent().parent().siblings('td[name="jobStatus"]').html(result.job_status);
        if(result.job_status == 'paused'){
         pauseButton.hide();
        resumeButton.show();
         alert(job_id+" paused successfully.");
        }
        else if(result.job_status == 'ended'){
         pauseButton.hide();
          resumeButton.hide();
          if(result.message)
        {
            alert(result.message);
        }
          else
          {
              alert(job_id+" paused and then ended.");
          }

        }
        else
        {
            alert('Weird. Should not come here.');
        }

    }
    else
    {
        alert("Failure in pausing "+job_id);
    }
    },
    error: function (error) {
     alert("Error in pausing "+job_id);
    }
});

    });


    $('button[name="resumeJob"]').on('click', function() {

        var job_id = $(this).attr("data-jobId");
        var resumeButton = $(this);
        var pauseButton = resumeButton.siblings('button[name="pauseJob"]');

                $.ajax({
    url: '/resume_job',
    type: "POST",
    data: {
        job_id: job_id,
    },
    dataType: "json",
    async: false,
    success: function (result) {
    if(result.status == 'success'){

        resumeButton.parent().parent().siblings('td[name="jobStatus"]').html(result.job_status);
        if(result.job_status == 'active'){
         resumeButton.hide();
         pauseButton.show();
         alert(job_id+" resumed successfully.");
        }
         else if(result.job_status == 'ended'){
          resumeButton.hide();
          pauseButton.hide();
          if(result.message)
        {
            alert(result.message);
        }
          else
          {
              alert(job_id+" resumed and then ended.");
          }
        }
        else
        {
            alert('Weird. Should not come here.');
        }

    }
    else
    {
        alert("Failure in resuming "+job_id);
    }
    },
    error: function (error) {
     alert("Error in resuming "+job_id);
    }
});


    });


                 $('button[name="removeJob"]').on('click', function() {

        var job_id = $(this).attr("data-jobId");
        var element = $(this);

                $.ajax({
    url: '/remove_job',
    type: "POST",
    data: {
        job_id: job_id,
    },
    dataType: "json",
    async: false,
    success: function (result) {
    if(result.status == 'success'){
        alert(job_id+" removed successfully.");
         jobsTable.row( element.parents('tr') ).remove().draw();
    }
    else
    {
        alert("Failure in removing "+job_id);
    }
    },
    error: function (error) {
     alert("Error in removing "+job_id);
    }
});


    });



   $('button[name="modifyJob"]').on('click', function() {

        var job_id = $(this).attr("data-jobId");
        var element = $(this);
        var job_medium_being_modified = element.parent().parent().siblings('td[name="jobType"]').text().split('/')[0];
         var status_of_job_being_modified = '';//element.parent().parent().siblings('td[name="jobStatus"]').text();

   $.ajax({
    url: '/get_job_status',
    type: "POST",
    data: {
        job_id: job_id,
    },
    dataType: "json",
    async: false,
    success: function (result) {
    if(result.status == 'success'){
        status_of_job_being_modified = result.job_status;
    }
    else
    {
        alert("Failure in retrieving job status for "+job_id);
    }
    },
    error: function (error) {
     alert("Error in retrieving job status for "+job_id);
    }
});
           window.open('/modify_job/'+job_id+'/'+job_medium_being_modified+'/'+status_of_job_being_modified, "_blank");
    });

   window.onload = function(){

        $('button[name="pauseJob"]').each(function( index ) {
           var current_status = $(this).parent().parent().siblings('td[name="jobStatus"]').text();
           if (current_status == 'paused'){
               $(this).hide();
           }
});

        $('button[name="resumeJob"]').each(function( index ) {
           var current_status = $(this).parent().parent().siblings('td[name="jobStatus"]').text();
           if (current_status == 'active'){
               $(this).hide();
           }
});



        };



});
