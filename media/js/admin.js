$(document).ready( function() {
    var data = $('#view-metadata');
    var searchUserUrl = data.attr( 'data-searchUserUrl' )
    $('#user-searchbox').autocomplete( {
         global: false,
         minLength: 1,
         source: searchUserUrl,
         delay: 400,
         select: function( event, ui ) {
            userPk = ui.item.pk;
            username = ui.item.label;
         }
    });
});

