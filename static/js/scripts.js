// maintain a list of the products selected, so we can submit them
selectedProductURLs = []
function toggleRowSelect(product_url) {
    if($(product_url).hasClass("warning")) {
        $(product_url).removeClass("warning");
        selectedProductURLs.splice(selectedProductURLs.indexOf(product_url), 1);
    } else {
        $(product_url).addClass("warning");
        selectedProductURLs.push(product_url);
    }
}

$('document').ready(function() {
    $('#search_form').on('submit', function(event) {
          event.preventDefault();
          var search_form =  $(event.target);
          var formJsonData = JSON.stringify($(this).serializeArray());
          $('#search_results').html('<img src = "../static/img/gif-load.gif">')


          console.log(formJsonData);

          $.ajax(("/search"), {
              type: 'POST',
              data: {'data':formJsonData},
              context: search_form,
              success: function(result) {
                  console.log("hi");
//                  var parent = $(this).parent();
//                  parent.empty().html(result);
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