$('.lsubmit').on('click', function(e){
  var j = $(this).parent('div').find("input[name='uls']").map(
    function () {
        return JSON.stringify({"key":$(this).val(), 'checked': $(this).prop('checked')});
    }
    ).get();
  var jData = JSON.stringify({'id':$(this).parent('div').attr('id'),'ul':j});
  $.ajax({
    url: $(this).parent('div').attr('action'),
    type: 'post',
    data: jData,
    dataType: 'json',
    contentType: 'application/json',
    dataType: 'text',
  }).done(function(data, textStatus, jqXHR) {
    toastr.info(jqXHR.responseText);
  }).fail(function(jqXHR, textStatus, errorThrown){
    toastr.warning('error status:'+jqXHR.status);
  });
});



$('.swInput').on('click', function(e){
  var jData = JSON.stringify(
      {'id':$(this).parent('div').find('input').attr('id'),
       'follow':$(this).parent('div').find('input').prop('checked')});
  $.ajax({
    url: '/follow',
    type: 'post',
    data: jData,
    dataType: 'json',
    contentType: 'application/json',
    dataType: 'text',
  }).done(function(data, textStatus, jqXHR) {
    toastr.info(jqXHR.responseText);
  }).fail(function(jqXHR, textStatus, errorThrown){
    toastr.warning('error status:'+jqXHR.status);
  });
});

