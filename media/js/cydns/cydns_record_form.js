$(document).ready(function(){
  var initial_record_type = $('#record_type').attr('value');
  var initial_record_pk = $('#record_pk').attr('value');

  $('#current_form').submit(function (){
          $('#form-message').html("<p>Sending data...</p>");
          var start = new Date().getTime();
          $.post('/cydns/record/',
                  $('#current_form').serialize(),
                  function (data) {
                      $('#current_form_data').empty();
                      $('#current_form_data').append(data);
                      bind_smart_names();
                      bind_record_search_box();
                      var end = new Date().getTime();
                      var time = end - start;
                      $('#action-time').html('('+time/1000+' seconds)');

                  })
          return false;
  }); // end submit()

  function bind_smart_names(){
      // Look for inputs that have id = 'id_fqdn' | 'id_target' | server . Make these smart names.
      var inputs = $('input');
      inputs.length;
      for (var x = 0; x < inputs.length; x++){
          if(inputs[x].id === 'id_fqdn' || inputs[x].id === 'id_target' || inputs[x].id === 'id_server'){
              make_smart_name_get_domains(inputs[x], true)
              $(inputs[x]).css('width', '400px');
          }
      }
  }
  function bind_record_search_box(){
      // We also need bind an auto complete to the search field for this specifc record type.
      $( "#record_search" ).autocomplete({
          minLength: 2,
          source:'/cydns/record/ajax_search/?record_type='+$('#rec_type_select option:selected').attr('value'),
          select: function( event, ui ) {
              // Save the selected pk so we can use it if the user decides to edit the record.
              $('#search-dialog').attr('stage_pk', ui.item.pk);
          }
      });
  }
  function bind_record_soa_search_box(){
      // We also need bind an auto complete to the search field for this specifc record type.
      $( "#soa_search" ).autocomplete({
          minLength: 2,
          source:'/cydns/record/ajax_search/?record_type=SOA',
          select: function( event, ui ) {
              // Save the selected pk so we can use it if the user decides to edit the record.
              console.log('Using: '+ui.item.pk);
              $('#search-soa-dialog').attr('stage_soa_pk', ui.item.pk);
          }
      });
  }
  bind_record_soa_search_box();
  // Setup search
  $('#launch-search').click(function(){
  var s_dialog = $( "#search-dialog" ).dialog({
              title: 'Search '+$('#rec_type_select option:selected').attr('value')+' records',  // Click the selected record
              autoShow: false,
              minWidth: 520,
              buttons: {
                  "Edit Record": function() {
                      //$( this ).dialog( "close" );
                      // Ok, they want to edit the record. Get the saved pk (happened when the user 'selected' from the
                      // drop down, and request that objects form and replace the current form.
                      $.get('/cydns/record/ajax_form/',
                          {
                              'record_type':$('#rec_type_select option:selected').attr('value'),
                              'record_pk': $('#search-dialog').attr('stage_pk'),
                          },
                          function (data) {
                              $('#current_form_data').empty();
                              $('#current_form_data').append(data);
                              $('#record_search').attr('value',''); // Clear the users selection.
                              fix_css();
                              // Notice how we don't call bind_smart_names here. We don't want the autocomplete to get in the way
                              // It's likely that they are just making a small change.
                          });
                      $(this).dialog("close");
                  },
                  cancel: function() {
                      $('#search-dialog').attr('stage_pk', ''), // we don't want this anymore.
                      $(this).dialog("close");
                  }
              }
          });
      s_dialog.show();
  });
  $('#launch-soa-search').click(function(){
      var soa_dialog = $( "#search-soa-dialog" ).dialog({
                  title: 'Search for a BIND file',  // Click the selected record
                  autoShow: true,
                  minWidth: 520,
                  buttons: {
                      "View ZONE file": function() {
                          //$( this ).dialog( "close" );
                          // Ok, they want to edit the record. Get the saved pk (happened when the user 'selected' from the
                          // drop down, and request that objects form and replace the current form.
                          window.open('/cydns/bind/build_debug/'+$('#search-soa-dialog').attr('stage_soa_pk')+'/');
                          $(this).dialog("close");
                      },
                      cancel: function() {
                          $('#search-dialog').attr('stage_soa_pk', ''), // we don't want this anymore.
                          $(this).dialog("close");
                      }
                  }
              });
      soa_dialog.show();
  });
});
