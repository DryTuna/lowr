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
})

// from Sandeep Panda:
// http://www.sitepoint.com/using-the-html5-constraint-api-for-form-validation/
//window.onload = function () {
//    document.getElementById("signup_password").onchange = validatePassword;
//    document.getElementById("signup_password_confirm").onchange = validatePassword;
//}
//function validatePassword(){
//var pass2=document.getElementById("signup_password_confirm").value;
//var pass1=document.getElementById("signup_password").value;
//if(pass1!=pass2)
//    document.getElementById("signup_password_confirm").setCustomValidity("Passwords Don't Match");
//else
//    document.getElementById("signup_password_confirm").setCustomValidity('');
//empty string means no validation error
//}
