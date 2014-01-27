var saveSettings = function(e) {
  e.preventDefault()

  var url = $('#url').val()
  var token = $('#token').val()
  var valid = true

  // validate the inputs
  if (token == '') {
      $('#token').focus().parents('.control-group').addClass('error')
      valid = false
  }
  if (url == '') {
      $('#url').focus().parents('.control-group').addClass('error')
      valid = false
  }
  if (!valid) {
      return false
  }

  // feedback while saving details
  $('#save').addClass('loading disabled').html('Saving&hellip;')

  // save details
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
  $('#url, #token').on('change', function(){
      $(this).parents('.control-group').removeClass('error')
  })
})
