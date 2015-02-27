Constants = {};
Constants.STATIC = 'st';
Constants.DYNAMIC = 'dy';

Messages = {};
Messages.RangeWizard = {};
Messages.RangeWizard.NoRanges = [
    'No ranges found.',
    'No ranges found in {0}.',
    'No ranges found in {0}, and {1}.'
];

function getMsg( key, subKey, args ) {
    var msg = Messages[key][subKey][args.length];
    $.each( args, function( index, arg ) {
        msg = msg.replace('{' + index + '}', arg);
    });
    return msg;
}
