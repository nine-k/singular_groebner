function init() {
    $('#commutative').attr('onclick', 'set_maxdeg_field();')
    $('#order').attr('onblur', 'assert_order();');
    // add asserts

    $('#order_type').attr('onchange', 'check_orders();');
    $('#calc_inputs').attr('onsubmit', 'send_data(); return false;');
}

function set_maxdeg_field() {
    if ($('#commutative').is(":checked")) {
        $('#max_deg').html('<br>Max monomial degree <br>'+
                           '<input type="text" id="max_deg_input" value="5">'
        )
    } else {
        $('#max_deg').html('')
    }
}

function assert_characteristic() {
    // var str = $('#order').val()

    $('#characteristic_correct').html('<span class="positive"> \✓<\span>');
}

function check_orders() {

}

function send_data() {
    var message = Object();
    message.characteristic = $('#characteristic').val();
    message.vars = $('#vars').val();
    message.basis = $('#basis').val();
    message.order_type = $('#order_type').val();
    message.email = $('#res_email').val();
    if ($('#commutative').is(":checked")) {
        message.request = 'noncommutative_groebner';
        message.max_degree = $('#max_deg_input').val()
    } else {
        message.request = 'commutative_groebner';
    }
    if ($('#hilbert').is(":checked")) {
        message.hilbert = 1;
    } else {
        message.hilbert = 0;
    }

    var post_str = JSON.stringify(message);
    // $.post('http://127.0.0.1:8000/calculations/submit_calculation', post_str, function(data) {}, 'json');
    $.ajax({
      url:'http://127.0.0.1:8000/calculations/submit_calculation',
      type:"POST",
      data: post_str,
      contentType:"application/json",
      dataType:"json",
      success: function(result){
          console.log('a');
          // console.log(result);
      }
    });
    console.log(post_str);
}
