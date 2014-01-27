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

  // get current settings
  $.ajax({
    url: 'allSettings.json',
    dataType: 'json'
  }).done(function(settings) {
    $('#url').val(settings.url)
    $('#token').val(settings.token)
  }).fail(function(jqXHR, textStatus, errorThrown){
    if (jqXHR.status == 404) {
      // allSettings.json hasn't been created yet
    } else if (textStatus == 'parsererror') {
      // allSettings.json isn't valid JSON - act like it doesn't exist
    } else {
      var title = 'Something odd happened when we tried to load your settings'
      var message = '<pre>' + jqXHR.status + ' ' + jqXHR.statusText + "\n" + errorThrown + '</pre>'
      scraperwiki.alert(title, message, 'error')
    }
  })

  // handle settings changes
  $('#settings').on('submit', saveSettings)
  $('#url, #token').on('change', function(){
      $(this).parents('.control-group').removeClass('error')
  })
})
