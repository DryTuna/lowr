// maintain a list of the products selected, so we can submit them
selectedProductURLs = []
function toggleRowSelect(product_url) {
    product_listing = $(document.getElementById(product_url));
    if(product_listing.hasClass("warning")) {
        product_listing.removeClass("warning");
        selectedProductURLs.splice(selectedProductURLs.indexOf(product_url), 1);
    } else {
        product_listing.addClass("warning");
        selectedProductURLs.push(product_url);
    }
}

function submitItems() {
  $.ajax(("/submititems"), {
        type: 'POST',
        data: JSON.stringify(selectedProductURLs),
        contentType: 'application/json',
        context: document.body,
        success: function(result) {
            location.href = result;
        }
    });
}

// this bit is from Jonathan Sampson on stackoverflow
$body = $("body");
$(document).on({
    ajaxStart: function() { $body.addClass("loading");    },
     ajaxStop: function() { $body.removeClass("loading"); }    
});


$('document').ready(function() {
    $('#search_form').on('submit', function(event) {
          selectedProductURLs = []
          event.preventDefault();
          var search_form =  $(event.target);
          var formJsonData = JSON.stringify($(this).serializeArray());

          $.ajax(("/search"), {
              type: 'POST',
              data: {'data':formJsonData},
              context: search_form,
              success: function(result) {
                  document.getElementById('submit_items_wrapper').style.display = 'block'
                  $('#search_results').html(result)
              }
          });
    });

    // thanks to Rohan Kumar on stackoverflow
    $('#create_form').on('submit',function() {
        if($('#signup_password').val() != $('#signup_password_confirm').val()) {
            alert('Password does not match confirmation');
            return false;
        }
        return true;
    });
})
