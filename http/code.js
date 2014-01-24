var saveSettings = function(e) {
  e.preventDefault()

  var url = $('#url').val()
  var token = $('#token').val()

  $('#save').addClass('loading disabled').html('Saving&hellip;')

  $.ajax({
    url: '../cgi-bin/save-settings'
  , data: {
      url: url
    , token: token
    }
  , dataType: 'json'
  }).done(function(data) {
    $('#save').removeClass('loading disabled').html('Save')
    $('#saved').show()
    setTimeout(function() {
      $('#saved').fadeOut()
    }, 4000)
  }).fail(function(jqXHR, textStatus, errorThrown) {
    $('#save').removeClass('loading disabled').html('Save')
  })
}

$(function(){
  $('#settings').on('submit', saveSettings)
})
