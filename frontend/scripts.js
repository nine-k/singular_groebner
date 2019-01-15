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

    var post_str = JSON.stringify(message);
    // $.post('http://127.0.0.1:8000/calculations/submit_calculation', post_str, function(data) {}, 'json');
    $.ajax({
      url:'http://127.0.0.1:8000/calculations/submit_calculation',
      type:"POST",
      data: post_str,
      contentType:"application/json",
      dataType:"json",
      success: function(){
        return true;
      }
    });
    console.log(post_str);
}
