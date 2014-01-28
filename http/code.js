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

  // add http:// if they forgot it
  if (!/https?:\/\//.test(url)) {
    url = 'http://' + url
    $('#url').val(url)
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
  }).fail(function(jqXHR, textStatus, errorThrown) {
    $('#save').removeClass('loading disabled').html('Save')
  }).done(settingsSaved)

}

var settingsSaved = function(){
  $('#url, #token').attr('disabled', true)
  $('#save').removeClass('loading disabled').html('Save')
  $('#save').css('display', 'none')
  $('#saved').css('display', 'inline-block')
  setTimeout(function() {
    $('#saved').css('display', 'none')
    $('#edit').css('display', 'inline-block')
  }, 4000)
}

var editSettings = function(e){
  $('#save').css('display', 'inline-block')
  $('#edit').css('display', 'none')
  $('#url, #token').removeAttr('disabled')
  $('#url').focus()
}

$(function(){

  // get current settings
  $.ajax({
    url: 'allSettings.json',
    dataType: 'json'
  }).done(function(settings) {
    $('#url').val(settings.url).attr('disabled', true)
    $('#token').val(settings.token).attr('disabled', true)
    $('#save').css('display', 'none')
    $('#edit').css('display', 'inline-block')
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
  $('#edit').on('click', editSettings)
  $('#settings').on('submit', saveSettings)
  $('#url, #token').on('change', function() {
      $(this).parents('.control-group').removeClass('error')
  })
})
