$('.qsubmit').on('click', function(e){
  var jData = {
      'query':$(this).parent('div').find('.nq').val(),
      'sample': $(this).parent('div').find('.samq').val(),
      'tocreated': $(this).parent('div').find('.tcrq').val(),
      'tolasttw': $(this).parent('div').find('.tltq').val(),
      'fromcreated': $(this).parent('div').find('.fcrq').val(),
      'fromlasttw': $(this).parent('div').find('.fltq').val(),
      'sort': $(this).parent('div').find('.sorq').val(),
      'ascend': $(this).parent('div').find('.asq').val(),
  };
  $.ajax({
    url: '/get_table',
    type: 'get',
    data: jData,
    dataType: 'html',
  }).done(function(data, textStatus, jqXHR) {
    $('#table').html(data);
  }).fail(function(jqXHR, textStatus, errorThrown){
    toastr.warning('error status:'+jqXHR.status);
  });
});


$('.qmake').on('click', function(e){
  var jData = 
      '?nq=' + $(this).parent('div').find('.nq').val() + 
      '&tcrq='+ $(this).parent('div').find('.tcrq').val() +
      '&tltq='+ $(this).parent('div').find('.tltq').val() +
      '&fcrq='+ $(this).parent('div').find('.fcrq').val() +
      '&fltq='+ $(this).parent('div').find('.fltq').val() +
      '&sorq='+ $(this).parent('div').find('.sorq').val() +
      '&asq='+ $(this).parent('div').find('.asq').val() +
      '&samq='+ $(this).parent('div').find('.samq').val();
  $(this).parent('div').append('<p>http://127.0.0.1:5000'+jData+'</p>');
});

