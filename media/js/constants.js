Constants = {};
Constants.STATIC = 'st';
Constants.DYNAMIC = 'dy';

var Messages = {};

Messages.RangeWizard = {};
Messages.RangeWizard.NoRanges = [
    'No ranges found.',
    'No ranges found in {0}.',
    'No ranges found in {0}, and {1}.'
];

Messages.CtnrDetail = {}
Messages.CtnrDetail.Confirmation = [
    'Are you sure you want to remove this object?',
    'Are you sure you want to remove this object from {0}?',
    'Are you sure you want to remove this {0} from this container?',
    'Are you sure you want to remove {0}, {1}, from {2}?'
];

function getMsg( key, subKey, args ) {
    var msg = Messages[key][subKey][args.length];
    $.each( args, function( index, arg ) {
        msg = msg.replace('{' + index + '}', arg);
    });
    return msg;
}
