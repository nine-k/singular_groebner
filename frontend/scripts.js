function init() {
    $('#order').attr('onblur', 'assert_order()');
    // add asserts

    $('#calc_inputs').attr('onsubmit', 'send_data(); return false;');
}

function assert_order() {
    // var str = $('#order').val()

    $('#order_correct').html('<span class="positive"> \✓<\span>');
}

function send_data() {
    var message = Object();
    message.order = $('#order').val();
    message.vars = $('#vars').val();
    message.basis = $('#basis').val();
    message.order = $('#order_type').val();
    message.email = $('#res_email').val();

    var test_str = JSON.stringify(message);
    console.log(test_str);
}
